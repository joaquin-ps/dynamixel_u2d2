"""
Scan for Dynamixel motors with flexible baud rate and ID range options.

This script scans for Dynamixel motors at different baud rates and motor ID ranges,
providing detailed information about detected motors.

Usage:
    python scan_dynamixel.py [--scan-bauds BAUDS] [--scan-id-range START,END] [--port PORT]

Examples:
    # Scan all motors at all baud rates
    python scan_dynamixel.py

    # Scan only specific baud rates
    python scan_dynamixel.py --scan-bauds 3000000,4000000

    # Scan only specific motor ID range
    python scan_dynamixel.py --scan-id-range 1,10

    # Scan with custom baud rates and ID range
    python scan_dynamixel.py --scan-bauds 3000000,4000000 --scan-id-range 1,20
"""

import argparse
import sys
from typing import List, Dict, Optional

# Import from the package (assumes pip install -e . was run)
from dynamixel_u2d2.u2d2_interface import U2D2Interface


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Scan for Dynamixel motors with flexible options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
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
        '--quiet',
        action='store_true',
        help='Suppress verbose output (overrides --verbose)'
    )
    
    args = parser.parse_args()
    
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
    
    # Set verbose mode
    verbose = args.verbose and not args.quiet
    
    # Create interface for scanning
    try:
        interface = U2D2Interface(args.port, 3000000, verbose=verbose)
    except Exception as e:
        print(f"❌ Error: Failed to initialize interface: {e}")
        sys.exit(1)
    
    try:
        # Scan for motors
        if scan_bauds:
            # Custom baud rate scanning
            detected_motors = {}
            for baudrate in scan_bauds:
                if verbose:
                    print(f"🔄 Scanning at baudrate {baudrate}...")
                detected = interface.scan_motors_at_baudrate(baudrate, scan_id_range)
                for motor_id in detected:
                    detected_motors[motor_id] = baudrate
        else:
            # Use default scanning with custom ID range
            detected_motors = interface.scan_all_baudrates(scan_id_range)
        
        # Print results
        print("\n" + "="*50)
        print("🔍 SCAN RESULTS")
        print("="*50)
        
        if detected_motors:
            print(f"✅ Found {len(detected_motors)} motor(s):")
            print()
            
            # Group by baud rate for better display
            by_baud = {}
            for motor_id, baud in detected_motors.items():
                if baud not in by_baud:
                    by_baud[baud] = []
                by_baud[baud].append(motor_id)
            
            for baud in sorted(by_baud.keys()):
                motor_ids = sorted(by_baud[baud])
                print(f"📡 Baud Rate {baud}:")
                for motor_id in motor_ids:
                    print(f"   - Motor ID {motor_id}")
                print()
            
            # Summary
            print("📊 Summary:")
            print(f"   Total motors found: {len(detected_motors)}")
            print(f"   Baud rates used: {len(by_baud)}")
            print(f"   ID range scanned: {scan_id_range.start}-{scan_id_range.stop-1}")
            
        else:
            print("❌ No motors detected")
            print()
            print("💡 Troubleshooting tips:")
            print("   - Check USB connection")
            print("   - Verify port path (try --port /dev/ttyUSB1, /dev/ttyUSB2, etc.)")
            print("   - Ensure motors are powered on")
            print("   - Try different baud rates with --scan-bauds")
            print("   - Try different ID range with --scan-id-range")
    
    except Exception as e:
        print(f"❌ Error during scanning: {e}")
        sys.exit(1)
    
    finally:
        interface.close()


if __name__ == "__main__":
    main()