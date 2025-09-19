#!/usr/bin/env python3
"""
Simple Motor Control Example

Commands two motors to the same position in a loop.

Usage:
    python single_motor_example.py
"""

import sys
import os
import time
from pathlib import Path

# Add the parent directory to the path to import u2d2_interface
sys.path.append(str(Path(__file__).parent.parent))

from u2d2_interface import U2D2Interface

# Motor configuration
MOTOR_IDS = [111, 112]
USB_PORT = "/dev/ttyUSB0"  # Change this to your U2D2 port
BAUDRATE = 4000000

# Position settings (in encoder units)
NEUTRAL_POSITION = 2048  # Center position
ROTATED_POSITION = 1500  # Rotated position

# Control parameters
VELOCITY_LIMIT = 100
P_GAIN = 200

def setup_motors(u2d2):
    """Set up motors for position control."""
    print("🔧 Setting up motors...")
    
    for motor_id in MOTOR_IDS:
        print(f"\n  Motor {motor_id}: Setting up...")

        # Disable torque to change operating mode
        u2d2.disable_torque(motor_id)
        print(f"  Torque disabled")
        
        # Set operating mode to position control
        u2d2.set_motor_mode(motor_id, 'position')
        print(f"  Set to position control mode")
        
        # Set velocity limit and P gain 
        u2d2.set_velocity_limit(motor_id, VELOCITY_LIMIT)
        u2d2.set_position_p_gain(motor_id, P_GAIN)
        
        # Enable torque
        u2d2.enable_torque(motor_id)
        print(f"  Torque enabled")
    
    print("\n ✅ All motors set up successfully!")

def command_position(u2d2, position):
    """Command motors to the same position."""
    for motor_id in MOTOR_IDS:
        u2d2.set_goal_position(motor_id, position)
    print(f"Commanded motors to position {position}")

def read_states(u2d2):
    """Read and display motor states."""
    for motor_id in MOTOR_IDS:
        position = u2d2.get_position(motor_id)
        velocity = u2d2.get_velocity(motor_id)
        current = u2d2.get_current(motor_id)
        print(f"  Motor {motor_id}: Pos={position:4d}, Vel={velocity:4d}, Curr={current:4d}")

def main():
    """Main function."""
    print("🤖 Simple Motor Control Example")
    print(f"USB Port: {USB_PORT}")
    print(f"Motor IDs: {MOTOR_IDS}")
    print("Press Ctrl+C to stop")
    print("-" * 40)
    
    # Check if USB port exists
    if not os.path.exists(USB_PORT):
        print(f"❌ USB port {USB_PORT} not found!")
        return 1
    
    # Initialize U2D2 interface
    u2d2 = U2D2Interface(USB_PORT, BAUDRATE, verbose=True)
    
    try:
        # Set up motors
        setup_motors(u2d2)
        
        # Main loop
        cycle = 0
        while True:
            cycle += 1
            print(f"\nCycle {cycle}")
            
            # Move to neutral position
            command_position(u2d2, NEUTRAL_POSITION)
            time.sleep(2.0)
            read_states(u2d2)
            
            # Move to rotated position
            command_position(u2d2, ROTATED_POSITION)
            time.sleep(2.0)
            read_states(u2d2)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup
        print("🧹 Disabling torque...")
        for motor_id in MOTOR_IDS:
            u2d2.disable_torque(motor_id)
        u2d2.close()
        print("🧹 Done!")

if __name__ == "__main__":
    main()