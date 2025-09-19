# Dynamixel U2D2 Examples

This directory contains example scripts demonstrating how to use the `u2d2_interface.py` module for controlling Dynamixel motors.

## Requirements

- Python 3.6+
- dynamixel-sdk
- numpy
- U2D2 communication bridge
- Dynamixel X-series motors

## Setup

1. Install dependencies:
   ```bash
   pip install dynamixel-sdk numpy
   ```

2. Connect your U2D2 to a USB port

3. Connect your Dynamixel motors to the U2D2

4. Update the USB port path in the example scripts

5. Run the examples:
   ```bash
   python position_command.py
   ```

## Examples

### `position_command.py`
Demonstrates simple position control with individual motor commands.

**Features:**
- Simple motor setup and configuration
- Position control mode
- Commands both motors to the same position simultaneously
- Real-time state reading (position, velocity, current)
- Individual motor read/write operations
- Proper error handling and cleanup

**Usage:**
```bash
python position_command.py
```

### `bulk_position_command.py`
Demonstrates efficient position control using bulk read/write operations.

**Features:**
- Same functionality as position_command.py but with bulk operations
- More efficient communication for multiple motors
- Bulk position commands and state reading
- Reduced communication overhead
- Better performance for multi-motor systems

**Usage:**
```bash
python bulk_position_command.py
```

**Configuration:**
- Update `USB_PORT` to match your U2D2 device path
- Modify `MOTOR_IDS` to match your motor IDs
- Adjust position values and control parameters as needed

## Troubleshooting

- **Port not found**: Check that the U2D2 is connected and update the `USB_PORT` variable
- **Motor not responding**: Verify motor IDs and connections
- **Permission denied**: You may need to add your user to the dialout group:
  ```bash
  sudo usermod -a -G dialout $USER
  ```
  Then log out and back in.
