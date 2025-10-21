#!/usr/bin/env python3
"""
Sync Position Control Example

Demonstrates the new sync operations for efficient multi-motor control.
Uses sync read/write operations for maximum performance.

Usage:
    python sync_position_command.py
"""

import sys
import os
import time
from pathlib import Path

# Add the parent directory to the path to import dynamixel_u2d2
sys.path.append(str(Path(__file__).parent.parent))

from dynamixel_u2d2 import U2D2Interface

# Motor configuration
MOTOR_IDS = [11, 21]
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

def sync_command_positions(u2d2, positions):
    """Command motors to positions using sync write operations."""
    u2d2.sync_write_positions(positions)
    print(f"Sync commanded motors to positions: {positions}")

def sync_read_states(u2d2):
    """Read and display motor states using sync read operations."""
    # Use the new sync_read_state method for maximum efficiency
    positions, velocities, currents = u2d2.sync_read_state()
    
    # Display results
    print("Motor States (Sync Read):")
    for i, motor_id in enumerate(MOTOR_IDS):
        print(f"  Motor {motor_id}: Pos={positions[i]:4d}, Vel={velocities[i]:4d}, Curr={currents[i]:4d}")

def sync_read_specific_states(u2d2, state_type):
    """Read specific state using sync read operations."""
    # Initialize specific sync read for the state type
    u2d2.init_specific_group_sync_read(state_type)
    
    # Read the specific state
    values = u2d2.sync_read_specific(state_type)
    
    print(f"Motor {state_type.title()} (Sync Read):")
    for i, motor_id in enumerate(MOTOR_IDS):
        print(f"  Motor {motor_id}: {state_type.title()}={values[i]:4d}")

def main():
    """Main function."""
    print("🤖 Sync Position Control Example")
    print(f"USB Port: {USB_PORT}")
    print(f"Motor IDs: {MOTOR_IDS}")
    print("Press Ctrl+C to stop")
    print("-" * 40)
    
    # Check if USB port exists
    if not os.path.exists(USB_PORT):
        print(f"❌ USB port {USB_PORT} not found!")
        return 1
    
    # Initialize U2D2 interface with motor_ids for sync operations
    u2d2 = U2D2Interface(USB_PORT, BAUDRATE, motor_ids=MOTOR_IDS, verbose=True)
    
    try:
        # Set up motors
        setup_motors(u2d2)
        
        # Main loop
        cycle = 0
        while True:
            cycle += 1
            print(f"\nCycle {cycle}")
            
            # Move to neutral position using sync operations
            positions = [NEUTRAL_POSITION] * len(MOTOR_IDS)
            sync_command_positions(u2d2, positions)
            time.sleep(2.0)
            sync_read_states(u2d2)
            
            # Demonstrate specific state reading
            print("\nReading specific states:")
            sync_read_specific_states(u2d2, 'position')
            sync_read_specific_states(u2d2, 'velocity')
            sync_read_specific_states(u2d2, 'current')
            
            # Move to rotated position using sync operations
            positions = [ROTATED_POSITION] * len(MOTOR_IDS)
            sync_command_positions(u2d2, positions)
            time.sleep(2.0)
            sync_read_states(u2d2)
            
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
        print("✅ Done!")

if __name__ == "__main__":
    main()
