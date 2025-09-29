#!/usr/bin/env python3
"""
Change Dynamixel motor IDs with validation and confirmation.

This script allows you to change motor IDs by specifying current IDs and their
corresponding new IDs, along with the baud rate to use for communication.

Usage:
    python change_id.py --baud BAUDRATE --current-ids ID1,ID2,... --new-ids NEW1,NEW2,... [--port PORT]

Examples:
    # Change motor IDs 1,2,3 to 10,11,12 at 3000000 baud
    python change_id.py --baud 3000000 --current-ids 1,2,3 --new-ids 10,11,12

    # Change single motor ID 1 to 5 at 4000000 baud
    python change_id.py --baud 4000000 --current-ids 1 --new-ids 5

    # Change with custom port
    python change_id.py --baud 3000000 --current-ids 1,2 --new-ids 10,11 --port /dev/ttyUSB1
"""

import argparse
import sys
from typing import List, Dict, Optional

# Import from the package (assumes pip install -e . was run)
from dynamixel_u2d2.u2d2_interface import U2D2Interface


class IDManager:
    """Manager for Dynamixel ID operations using U2D2Interface."""
    
    def __init__(self, port: str = "/dev/ttyUSB0", verbose: bool = True):
        """
        Initialize the ID manager.
        
        Args:
            port: USB port path
            verbose: Enable verbose output
        """
        self.port = port
        self.verbose = verbose
    
    def change_motors_id(self, current_ids: List[int], new_ids: List[int], baudrate: int) -> Dict[int, bool]:
        """
        Change IDs for multiple motors using U2D2Interface.
        
        Args:
            current_ids: List of current motor IDs
            new_ids: List of new motor IDs (must match current_ids length)
            baudrate: Baud rate to use for communication
            
        Returns:
            Dictionary mapping current_id to success status
        """
        if len(current_ids) != len(new_ids):
            print("❌ Error: current_ids and new_ids must have the same length")
            return {}
        
        # Create ID mapping
        id_mapping = dict(zip(current_ids, new_ids))
        
        if self.verbose:
            print(f"🔄 Changing motor IDs at {baudrate} baud...")
            print("ID Mappings:")
            for current_id, new_id in id_mapping.items():
                print(f"  {current_id} → {new_id}")
        
        try:
            # Create interface for ID changes
            interface = U2D2Interface(self.port, baudrate, verbose=self.verbose)
            results = interface.change_motors_id(id_mapping, baudrate)
            interface.close()
            
            return results
            
        except Exception as e:
            print(f"❌ Error changing motor IDs: {e}")
            return {current_id: False for current_id in current_ids}


def validate_id_lists(current_ids: List[int], new_ids: List[int]) -> bool:
    """
    Validate the current and new ID lists.
    
    Args:
        current_ids: List of current motor IDs
        new_ids: List of new motor IDs
        
    Returns:
        True if valid, False otherwise
    """
    # Check lengths match
    if len(current_ids) != len(new_ids):
        print("❌ Error: current_ids and new_ids must have the same length")
        return False
    
    # Check for empty lists
    if not current_ids:
        print("❌ Error: No motor IDs provided")
        return False
    
    # Validate current IDs
    invalid_current = [id for id in current_ids if id < 0 or id > 252]
    if invalid_current:
        print(f"❌ Error: Invalid current IDs: {invalid_current}. Must be 0-252")
        return False
    
    # Validate new IDs
    invalid_new = [id for id in new_ids if id < 0 or id > 252]
    if invalid_new:
        print(f"❌ Error: Invalid new IDs: {invalid_new}. Must be 0-252")
        return False
    
    # Check for duplicate current IDs
    if len(current_ids) != len(set(current_ids)):
        print("❌ Error: Duplicate current IDs found. Each motor must have a unique current ID.")
        return False
    
    # Check for duplicate new IDs
    if len(new_ids) != len(set(new_ids)):
        print("❌ Error: Duplicate new IDs found. Each motor must have a unique new ID.")
        return False
    
    # Check for overlapping IDs (current and new)
    overlap = set(current_ids) & set(new_ids)
    if overlap:
        print(f"❌ Error: Overlapping IDs found: {overlap}. Current and new IDs must be distinct.")
        return False
    
    return True


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Change Dynamixel motor IDs with validation and confirmation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--baud',
        type=int,
        required=True,
        help='Baud rate to use for communication (required)'
    )
    
    parser.add_argument(
        '--current-ids',
        type=str,
        required=True,
        help='Comma-separated list of current motor IDs (required)'
    )
    
    parser.add_argument(
        '--new-ids',
        type=str,
        required=True,
        help='Comma-separated list of new motor IDs (required)'
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
    
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt (use with caution)'
    )
    
    args = parser.parse_args()
    
    # Validate baud rate
    if args.baud not in U2D2Interface.BAUDRATE_MAP:
        print(f"❌ Error: Invalid baud rate {args.baud}. Valid rates: {list(U2D2Interface.BAUDRATE_MAP.keys())}")
        sys.exit(1)
    
    # Parse current IDs
    try:
        current_ids = [int(x.strip()) for x in args.current_ids.split(',')]
    except ValueError:
        print("❌ Error: Invalid current IDs format. Use comma-separated integers (e.g., 1,2,3)")
        sys.exit(1)
    
    # Parse new IDs
    try:
        new_ids = [int(x.strip()) for x in args.new_ids.split(',')]
    except ValueError:
        print("❌ Error: Invalid new IDs format. Use comma-separated integers (e.g., 10,11,12)")
        sys.exit(1)
    
    # Validate ID lists
    if not validate_id_lists(current_ids, new_ids):
        sys.exit(1)
    
    # Set verbose mode
    verbose = args.verbose and not args.quiet
    
    # Create ID mapping for display
    id_mapping = dict(zip(current_ids, new_ids))
    
    # Display the planned changes
    print("="*60)
    print("🔄 MOTOR ID CHANGE PLAN")
    print("="*60)
    print(f"Baud Rate: {args.baud}")
    print(f"Port: {args.port}")
    print()
    print("ID Changes:")
    for current_id, new_id in id_mapping.items():
        print(f"  Motor ID {current_id} → {new_id}")
    print()
    print(f"Total motors to change: {len(id_mapping)}")
    print("="*60)
    
    # Confirmation prompt
    if not args.yes:
        print()
        print("⚠️  WARNING: This will permanently change motor IDs!")
        print("⚠️  Make sure no other programs are using these motors.")
        print()
        confirm = input("Proceed with ID changes? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("❌ Operation cancelled")
            sys.exit(0)
    
    # Create manager and perform changes
    manager = IDManager(args.port, verbose)
    
    try:
        results = manager.change_motors_id(current_ids, new_ids, args.baud)
        
        # Report results
        print("\n" + "="*60)
        print("📊 RESULTS")
        print("="*60)
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        print(f"Successfully changed: {successful}/{total} motors")
        print()
        
        if successful == total:
            print("✅ All motor IDs changed successfully!")
        else:
            print("❌ Some changes failed:")
            for current_id, success in results.items():
                status = "✅ Success" if success else "❌ Failed"
                new_id = id_mapping[current_id]
                print(f"  {current_id} → {new_id}: {status}")
        
        if successful < total:
            failed_count = total - successful
            print(f"\n⚠️  {failed_count} motor(s) failed to change ID")
            print("💡 Troubleshooting tips:")
            print("   - Check if motors are powered on")
            print("   - Verify baud rate is correct")
            print("   - Ensure no other programs are using the motors")
            print("   - Check USB connection")
    
    except Exception as e:
        print(f"❌ Error during ID changes: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
