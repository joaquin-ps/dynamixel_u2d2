"""
Change Dynamixel motor baud rates with scanning capability.

This script changes motor baud rates. It can either scan for motors first
or use known motor IDs and baud rates.

Usage:
    python change_baud.py --new-baud BAUDRATE [--old-baud BAUDRATE] [--motor-ids ID1,ID2,...] [options]

Examples:
    # Scan all motors and change to 4000000 baud
    python change_baud.py --new-baud 4000000

    # Scan only at 3000000 baud and change all found motors
    python change_baud.py --new-baud 4000000 --old-baud 3000000

    # Change specific motors with known baud rate (no scanning)
    python change_baud.py --new-baud 4000000 --old-baud 3000000 --motor-ids 1,2,3

    # Scan specific baud rates and change all found motors
    python change_baud.py --new-baud 4000000 --scan-bauds 3000000,1000000

    # Scan specific ID range and change all found motors
    python change_baud.py --new-baud 4000000 --scan-id-range 1,10

    # Change specific motors with custom scan parameters
    python change_baud.py --new-baud 4000000 --motor-ids 1,2,3 --scan-bauds 3000000,1000000
"""

import argparse
import sys
from typing import List, Dict, Optional, Tuple

# Import from the package (assumes pip install -e . was run)
from dynamixel_u2d2.u2d2_interface import U2D2Interface


class BaudrateManager:
    """Manager for Dynamixel baud rate operations using U2D2Interface."""
    
    def __init__(self, port: str = "/dev/ttyUSB0", verbose: bool = True):
        """
        Initialize the baud rate manager.
        
        Args:
            port: USB port path
            verbose: Enable verbose output
        """
        self.port = port
        self.verbose = verbose
        self.interface = None
        self.detected_motors = {}  # {motor_id: baudrate}
    
    def scan_all_baudrates(self, scan_bauds: List[int] = None, scan_id_range: range = None) -> Dict[int, int]:
        """
        Scan for motors at specified baud rates using U2D2Interface.
        
        Args:
            scan_bauds: List of baud rates to scan (default: all available)
            scan_id_range: Range of motor IDs to scan (default: 0-252)
            
        Returns:
            Dictionary mapping motor_id to baudrate
        """
        if self.verbose:
            if scan_bauds:
                print(f"🔍 Scanning for motors at baud rates: {scan_bauds}")
            else:
                print("🔍 Scanning for motors at all baud rates...")
            
            if scan_id_range:
                print(f"🔍 Scanning motor IDs: {scan_id_range.start}-{scan_id_range.stop-1}")
        
        try:
            # Create interface for scanning (will be closed after scan)
            interface = U2D2Interface(self.port, 3000000, verbose=self.verbose)
            
            if scan_bauds:
                # Custom baud rate scanning
                self.detected_motors = {}
                for baudrate in scan_bauds:
                    detected = interface.scan_motors_at_baudrate(baudrate, scan_id_range or range(0, 253))
                    for motor_id in detected:
                        self.detected_motors[motor_id] = baudrate
            else:
                # Use default scanning with custom ID range
                self.detected_motors = interface.scan_all_baudrates(scan_id_range or range(0, 253))
            
            interface.close()
            
            return self.detected_motors
            
        except Exception as e:
            print(f"❌ Error during scanning: {e}")
            return {}
    
    def change_motors_baudrate(self, motor_baud_map: Dict[int, int], new_baud: int) -> Dict[int, bool]:
        """
        Change baud rate for multiple motors using U2D2Interface.
        
        Args:
            motor_baud_map: Dictionary mapping motor_id to current baud rate
            new_baud: New baud rate to set
            
        Returns:
            Dictionary mapping motor_id to success status
        """
        if not motor_baud_map:
            print("❌ No motor IDs provided")
            return {}
        
        try:
            # Create interface for baud rate changes
            interface = U2D2Interface(self.port, 3000000, verbose=self.verbose)
            results = interface.change_motors_baudrate(motor_baud_map, new_baud)
            interface.close()
            
            return results
            
        except Exception as e:
            print(f"❌ Error changing baud rates: {e}")
            return {mid: False for mid in motor_baud_map.keys()}


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Change Dynamixel motor baud rates with scanning capability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--new-baud',
        type=int,
        required=True,
        help='New baud rate to set for motors (required)'
    )
    
    parser.add_argument(
        '--old-baud',
        type=int,
        default=None,
        help='Current baud rate of motors (if known, scans only at this rate)'
    )
    
    parser.add_argument(
        '--scan-bauds',
        type=str,
        default=None,
        help='Comma-separated list of baud rates to scan (default: all available rates)'
    )
    
    parser.add_argument(
        '--scan-id-range',
        type=str,
        default=None,
        help='Motor ID range to scan as START,END (e.g., 1,10 for IDs 1-9, default: 0,253 for all)'
    )
    
    parser.add_argument(
        '--motor-ids',
        type=str,
        default=None,
        help='Comma-separated list of motor IDs to change (default: all detected motors)'
    )
    
    parser.add_argument(
        '--port',
        type=str,
        default="/dev/ttyUSB0",
        help='USB port path (default: /dev/ttyUSB0)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=True,
        help='Enable verbose output (default: True)'
    )
    
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt (use with caution)'
    )
    
    args = parser.parse_args()
    
    # Validate baud rates
    if args.new_baud not in U2D2Interface.BAUDRATE_MAP:
        print(f"❌ Error: Invalid new baud rate {args.new_baud}. Valid rates: {list(U2D2Interface.BAUDRATE_MAP.keys())}")
        sys.exit(1)
    
    if args.old_baud is not None and args.old_baud not in U2D2Interface.BAUDRATE_MAP:
        print(f"❌ Error: Invalid old baud rate {args.old_baud}. Valid rates: {list(U2D2Interface.BAUDRATE_MAP.keys())}")
        sys.exit(1)
    
    # Parse motor IDs if provided
    motor_ids = None
    if args.motor_ids:
        try:
            motor_ids = [int(x.strip()) for x in args.motor_ids.split(',')]
        except ValueError:
            print("❌ Error: Invalid motor IDs format. Use comma-separated integers (e.g., 1,2,3)")
            sys.exit(1)
    
    # Parse scan baud rates if provided
    scan_bauds = None
    if args.scan_bauds:
        try:
            scan_bauds = [int(x.strip()) for x in args.scan_bauds.split(',')]
            # Validate baud rates
            invalid_bauds = [b for b in scan_bauds if b not in U2D2Interface.BAUDRATE_MAP]
            if invalid_bauds:
                print(f"❌ Error: Invalid baud rates: {invalid_bauds}. Valid rates: {list(U2D2Interface.BAUDRATE_MAP.keys())}")
                sys.exit(1)
        except ValueError:
            print("❌ Error: Invalid baud rates format. Use comma-separated integers (e.g., 3000000,4000000)")
            sys.exit(1)
    
    # Parse scan ID range if provided
    scan_id_range = range(0, 253)  # Default: scan all IDs 0-252 (253 total)
    if args.scan_id_range:
        try:
            start_str, end_str = args.scan_id_range.split(',')
            start_id = int(start_str.strip())
            end_id = int(end_str.strip())
            if start_id < 0 or end_id > 253 or start_id >= end_id:
                print("❌ Error: Invalid ID range. Start must be < end, and both must be 0-252")
                sys.exit(1)
            scan_id_range = range(start_id, end_id)
        except (ValueError, IndexError):
            print("❌ Error: Invalid ID range format. Use START,END (e.g., 1,10)")
            sys.exit(1)
    
    # Create manager
    manager = BaudrateManager(args.port, args.verbose)
    
    # Determine if we need to scan
    need_to_scan = motor_ids is None
    
    # Scan for motors if needed
    if need_to_scan:
        if args.old_baud is not None:
            # Scan only at the specified old baud rate
            detected_motors = {}
            try:
                interface = U2D2Interface(manager.port, 3000000, verbose=manager.verbose)
                detected = interface.scan_motors_at_baudrate(args.old_baud, scan_id_range)
                interface.close()
                for motor_id in detected:
                    detected_motors[motor_id] = args.old_baud
            except Exception as e:
                print(f"❌ Error during scanning: {e}")
                sys.exit(1)
        else:
            # Scan all baud rates
            detected_motors = manager.scan_all_baudrates(scan_bauds, scan_id_range)
        
        if not detected_motors:
            print("❌ No motors detected")
            sys.exit(1)
    else:
        # Use provided motor IDs with known baud rate
        if args.old_baud is not None:
            detected_motors = {motor_id: args.old_baud for motor_id in motor_ids}
        else:
            print("❌ Error: Must specify --old-baud when using --motor-ids")
            sys.exit(1)
    
    # Determine which motors to change
    if motor_ids is None:
        # Use all detected motors
        target_motors = list(detected_motors.keys())
    else:
        # Use specified motors
        target_motors = motor_ids
    
    # Display change plan
    print("\n" + "="*60)
    print("🔄 BAUD RATE CHANGE PLAN")
    print("="*60)
    print(f"New Baud Rate: {args.new_baud}")
    print(f"Port: {args.port}")
    if args.old_baud:
        print(f"Old Baud Rate: {args.old_baud} (known)")
    else:
        print("Old Baud Rate: (detected via scanning)")
    print()
    print("Motors to change:")
    for motor_id in target_motors:
        current_baud = detected_motors.get(motor_id, "unknown")
        print(f"  Motor ID {motor_id} ({current_baud} → {args.new_baud} baud)")
    print()
    print(f"Total motors to change: {len(target_motors)}")
    print("="*60)
    
    # Confirm before making changes
    if not args.yes:
        print()
        print("⚠️  WARNING: This will permanently change motor baud rates!")
        print("⚠️  Make sure no other programs are using these motors.")
        print()
        confirm = input("Proceed with baud rate changes? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("❌ Operation cancelled")
            sys.exit(0)
    
    # Create motor_baud_map for the target motors
    motor_baud_map = {motor_id: detected_motors[motor_id] for motor_id in target_motors}
    
    # Change baud rates
    results = manager.change_motors_baudrate(motor_baud_map, args.new_baud)
    
    # Report results
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"Successfully changed: {successful}/{total} motors")
    print()
    
    if successful == total:
        print("✅ All motor baud rates changed successfully!")
    else:
        print("❌ Some changes failed:")
        for motor_id, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            current_baud = detected_motors.get(motor_id, "unknown")
            print(f"  Motor ID {motor_id} ({current_baud} → {args.new_baud} baud): {status}")
    
    if successful < total:
        failed_count = total - successful
        print(f"\n⚠️  {failed_count} motor(s) failed to change baud rate")
        print("💡 Troubleshooting tips:")
        print("   - Check if motors are powered on")
        print("   - Verify current baud rate is correct")
        print("   - Ensure no other programs are using the motors")
        print("   - Check USB connection")


if __name__ == "__main__":
    main()
