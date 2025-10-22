"""
Echo Dynamixel motor encoder positions continuously.

This script connects to specified Dynamixel motors and continuously reads
and displays their encoder positions. Torque is kept disabled for safety.

Usage:
    python echo_encoder.py --baud BAUDRATE --motor-ids ID1,ID2,...

Examples:
    # Echo positions for motors 1,2,3 at 3000000 baud
    python echo_encoder.py --baud 3000000 --motor-ids 1,2,3

    # Echo positions for single motor at 4000000 baud
    python echo_encoder.py --baud 4000000 --motor-ids 1

    # Use custom port
    python echo_encoder.py --baud 3000000 --motor-ids 1,2 --port /dev/ttyUSB1
"""

import argparse
import sys
import time
import signal
from typing import List

# Import from the package (assumes pip install -e . was run)
from dynamixel_u2d2.u2d2_interface import U2D2Interface


class EncoderEcho:
    """Continuous encoder position reader for Dynamixel motors."""
    
    def __init__(self, port: str, baudrate: int, motor_ids: List[int], verbose: bool = True):
        """
        Initialize the encoder echo.
        
        Args:
            port: USB port path
            baudrate: Communication baud rate
            motor_ids: List of motor IDs to monitor
            verbose: Enable verbose output
        """
        self.port = port
        self.baudrate = baudrate
        self.motor_ids = motor_ids
        self.verbose = verbose
        self.interface = None
        self.running = True
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals for graceful shutdown."""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.running = False
    
    def connect(self):
        """Connect to the U2D2 interface and verify motor communication."""
        try:
            self.interface = U2D2Interface(self.port, self.baudrate, verbose=self.verbose)
            
            # Verify all motors are reachable
            print(f"🔍 Verifying connection to {len(self.motor_ids)} motor(s)...")
            unreachable_motors = []
            
            for motor_id in self.motor_ids:
                try:
                    # Try to read position to verify communication
                    position = self.interface.get_position(motor_id)
                    if self.verbose:
                        print(f"✅ Motor {motor_id}: Connected (position: {position})")
                except Exception as e:
                    unreachable_motors.append(motor_id)
                    if self.verbose:
                        print(f"❌ Motor {motor_id}: Failed to connect - {e}")
            
            if unreachable_motors:
                print(f"❌ Error: Could not connect to motors: {unreachable_motors}")
                return False
            
            # Ensure torque is disabled for all motors
            print("🔒 Ensuring torque is disabled for all motors...")
            for motor_id in self.motor_ids:
                try:
                    self.interface.disable_torque(motor_id)
                    if self.verbose:
                        print(f"✅ Motor {motor_id}: Torque disabled")
                except Exception as e:
                    print(f"⚠️  Motor {motor_id}: Could not disable torque - {e}")
            
            print("✅ All motors connected and ready for position monitoring")
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to interface: {e}")
            return False
    
    def echo_positions(self):
        """Continuously read and display motor positions."""
        if not self.interface:
            print("❌ Interface not connected")
            return
        
        print("\n" + "="*60)
        print("📊 CONTINUOUS POSITION MONITORING")
        print("="*60)
        print("Press Ctrl+C to stop")
        print("="*60)
        
        try:
            while self.running:
                # Build display content first, then clear and show all at once
                display_lines = []
                display_lines.append("📊 Dynamixel Encoder Echo")
                display_lines.append(f"Port: {self.port} | Baud: {self.baudrate}")
                display_lines.append(f"Motors: {', '.join(map(str, self.motor_ids))}")
                display_lines.append("="*60)
                
                # Read positions for all motors
                positions = {}
                for motor_id in self.motor_ids:
                    try:
                        position = self.interface.get_position(motor_id)
                        positions[motor_id] = position
                    except Exception as e:
                        positions[motor_id] = f"ERROR: {e}"
                
                # Add position data to display
                for motor_id in self.motor_ids:
                    pos = positions[motor_id]
                    if isinstance(pos, int):
                        display_lines.append(f"Motor {motor_id:2d}: Position = {pos:6d}")
                    else:
                        display_lines.append(f"Motor {motor_id:2d}: {pos}")
                
                display_lines.append("="*60)
                display_lines.append("Press Ctrl+C to stop")
                
                # Clear screen and display all content at once
                print("\033[2J\033[H", end="")  # Clear screen and move cursor to top
                for line in display_lines:
                    print(line)
                
                # Small delay to prevent overwhelming the interface
                time.sleep(0.05)  # Reduced delay for smoother updates
                
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
        except Exception as e:
            print(f"\n❌ Error during monitoring: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.interface:
            try:
                self.interface.close()
                if self.verbose:
                    print("✅ Interface closed")
            except Exception as e:
                print(f"⚠️  Error closing interface: {e}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Echo Dynamixel motor encoder positions continuously",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--baud',
        type=int,
        required=True,
        help='Communication baud rate (required)'
    )
    
    parser.add_argument(
        '--motor-ids',
        type=str,
        required=True,
        help='Comma-separated list of motor IDs to monitor (required)'
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
    
    # Validate baud rate
    if args.baud not in U2D2Interface.BAUDRATE_MAP:
        print(f"❌ Error: Invalid baud rate {args.baud}. Valid rates: {list(U2D2Interface.BAUDRATE_MAP.keys())}")
        sys.exit(1)
    
    # Parse motor IDs
    try:
        motor_ids = [int(x.strip()) for x in args.motor_ids.split(',')]
        if not motor_ids:
            print("❌ Error: No motor IDs provided")
            sys.exit(1)
        
        # Validate motor IDs
        for motor_id in motor_ids:
            if not (0 <= motor_id <= 252):
                print(f"❌ Error: Invalid motor ID {motor_id}. Must be 0-252")
                sys.exit(1)
        
        # Check for duplicates
        if len(motor_ids) != len(set(motor_ids)):
            print("❌ Error: Duplicate motor IDs found")
            sys.exit(1)
            
    except ValueError:
        print("❌ Error: Invalid motor IDs format. Use comma-separated integers (e.g., 1,2,3)")
        sys.exit(1)
    
    # Set verbose mode
    verbose = args.verbose and not args.quiet
    
    # Create encoder echo instance
    echo = EncoderEcho(args.port, args.baud, motor_ids, verbose)
    
    # Connect and start monitoring
    if echo.connect():
        echo.echo_positions()
    else:
        print("❌ Failed to connect to motors")
        sys.exit(1)


if __name__ == "__main__":
    main()
