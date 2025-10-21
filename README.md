# U2D2 Interface Documentation

A high-level interface for controlling Dynamixel motors through the U2D2 communication bridge, with support for both individual motor operations and efficient bulk operations.

**🔧 Helper Scripts**: For quick motor management tasks like scanning, changing baud rates, and changing motor IDs, see the [Helper Scripts documentation](helpers/HELPERS.md).

Tested on: Ubuntu 22.04

## Quick Setup (Linux)

Before using the U2D2 interface, make sure your U2D2 device is properly configured:

1. **Check U2D2 Connection**: Run the provided setup script to verify connection and configure USB latency:
   ```bash
   source u2d2_port.sh
   ```
   This script will:
   - Check if `/dev/ttyUSB0` is connected
   - Display current USB latency timer
   - Allow you to set optimal latency (default: 2ms)

2. **Verify Port Path**: The script assumes `/dev/ttyUSB0`. If your U2D2 is on a different port, update the script or use the correct path in your code.

## Table of Contents

- [Overview](#overview)
- [Helper Scripts](#helper-scripts)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [Motor Configuration](#motor-configuration)
  - [Sync Operations](#sync-operations)
  - [Bulk Base Operations](#bulk-base-operations)
  - [Bulk High-Level Operations](#bulk-high-level-operations)
  - [Bulk Utils](#bulk-utils)
  - [Individual Motor Operations](#individual-motor-operations)
  - [Port Management](#port-management)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [Performance](#performance)

## Overview

The `U2D2Interface` class provides a comprehensive interface for controlling Dynamixel X-series motors through the U2D2 communication bridge. It supports both individual motor operations and efficient bulk operations for multi-motor control scenarios.

### Key Features

- **Clean API**: Simple, intuitive method names
- **Sync Operations**: Maximum efficiency for multi-motor control
- **Bulk Operations**: Efficient multi-motor control
- **Type Safety**: Full type hints and validation
- **Error Handling**: Comprehensive error reporting
- **Flexible**: Support for all Dynamixel X-series control modes

## Helper Scripts

For users who need quick motor management tasks without writing Python code, this package includes three powerful command-line helper scripts:

- **`scan_dynamixel.py`**: Scan for motors at different baud rates and ID ranges
- **`change_baud.py`**: Change motor baud rates with flexible scanning options
- **`change_id.py`**: Change motor IDs with validation and confirmation

These scripts provide a user-friendly interface for common Dynamixel management tasks and are perfect for:
- Initial motor setup and configuration
- Troubleshooting communication issues
- Batch operations on multiple motors
- Quick motor discovery and identification

📖 **See the [Helper Scripts documentation](helpers/HELPERS.md) for detailed usage instructions and examples.**

## Installation

### Option 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd dynamixel_u2d2

# Install in development mode
pip install -e .
```

### Option 2: Install Dependencies Only

```bash
pip install dynamixel-sdk numpy
```

**Note**: Option 1 is recommended as it provides access to the helper scripts and proper package structure.

## Quick Start

```python
from dynamixel_u2d2 import U2D2Interface

# Initialize interface
u2d2 = U2D2Interface('/dev/ttyUSB0', baudrate=3000000)

# Configure motor
u2d2.disable_torque(11)
u2d2.set_motor_mode(11, 'position')
u2d2.set_position_p_gain(11, 100)
u2d2.enable_torque(11)

# Control motor
u2d2.set_goal_position(11, 2048)  # Move to center position
position = u2d2.get_position(11)  # Read current position

# Cleanup
u2d2.close()
```

## API Reference

### Motor Configuration

#### `enable_torque(motor_id: int)`
Enable torque on the specified motor.

**Parameters:**
- `motor_id` (int): Motor ID to enable torque

**Example:**
```python
u2d2.enable_torque(11)
```

#### `disable_torque(motor_id: int)`
Disable torque on the specified motor.

**Parameters:**
- `motor_id` (int): Motor ID to disable torque

**Example:**
```python
u2d2.disable_torque(11)
```

#### `set_motor_mode(motor_id: int, mode: str)`
Set the operating mode of a motor using string parameter.

**Parameters:**
- `motor_id` (int): Motor ID
- `mode` (str): Operating mode - one of:
  - `'position'`: Position control mode
  - `'current'`: Current control mode
  - `'current_based_position'`: Current-based position control mode
  - `'velocity'`: Velocity control mode
  - `'extended_position'`: Extended position control mode
  - `'pwm'`: PWM control mode

**Example:**
```python
u2d2.set_motor_mode(11, 'position')
```

#### `set_position_p_gain(motor_id: int, p_gain: int)`
Set the Position P Gain for a motor.

**Parameters:**
- `motor_id` (int): Motor ID
- `p_gain` (int): P gain value

**Example:**
```python
u2d2.set_position_p_gain(11, 100)
```

#### `set_position_i_gain(motor_id: int, i_gain: int)`
Set the Position I Gain for a motor.

**Parameters:**
- `motor_id` (int): Motor ID
- `i_gain` (int): I gain value

**Example:**
```python
u2d2.set_position_i_gain(11, 10)
```

#### `set_position_d_gain(motor_id: int, d_gain: int)`
Set the Position D Gain for a motor.

**Parameters:**
- `motor_id` (int): Motor ID
- `d_gain` (int): D gain value

**Example:**
```python
u2d2.set_position_d_gain(11, 5)
```

### Sync Operations

The sync operations provide the highest efficiency for multi-motor control by using a single packet to read or write to multiple motors simultaneously. These operations are ideal for real-time control applications.

#### `init_group_sync_read(motor_ids: List[int])`
Initialize group sync read parameters for maximum efficiency.

**Parameters:**
- `motor_ids` (List[int]): List of motor IDs to configure for sync read

**Example:**
```python
u2d2.init_group_sync_read([11, 12, 111, 112])
```

#### `sync_read_state() -> Tuple[List[int], List[int], List[int]]`
Sync read the full state (position, velocity, current) of all configured motors.

**Returns:**
- `Tuple[List[int], List[int], List[int]]`: Tuple of (positions, velocities, currents)

**Example:**
```python
positions, velocities, currents = u2d2.sync_read_state()
for i, motor_id in enumerate([11, 12, 111, 112]):
    print(f"Motor {motor_id}: Pos={positions[i]}, Vel={velocities[i]}, Curr={currents[i]}")
```

#### `sync_write_positions(positions: List[int])`
Sync write position commands to all configured motors.

**Parameters:**
- `positions` (List[int]): List of position values (must match motor_ids length)

**Example:**
```python
positions = [2048, 1500, 2048, 1500]
u2d2.sync_write_positions(positions)
```

#### `sync_write_currents(currents: List[int])`
Sync write current commands to all configured motors.

**Parameters:**
- `currents` (List[int]): List of current values (must match motor_ids length)

**Example:**
```python
currents = [100, -50, 100, -50]
u2d2.sync_write_currents(currents)
```

#### `init_specific_group_sync_read(state: str)`
Initialize group sync read parameters for specific states.

**Parameters:**
- `state` (str): State to read ('position', 'velocity', 'current')

**Example:**
```python
u2d2.init_specific_group_sync_read('position')
```

#### `sync_read_specific(state: str) -> List[int]`
Sync read only specific state for all configured motors.

**Parameters:**
- `state` (str): State to read ('position', 'velocity', 'current')

**Returns:**
- `List[int]`: List of state values in same order as motor_ids

**Example:**
```python
u2d2.init_specific_group_sync_read('position')
positions = u2d2.sync_read_specific('position')
```

### Bulk Base Operations

#### `bulk_read(read_params: List[Tuple[int, int, int]]) -> Dict`
Perform bulk read operation for multiple motors.

**Parameters:**
- `read_params` (List[Tuple[int, int, int]]): List of tuples (motor_id, address, length)

**Returns:**
- `Dict`: Dictionary with keys (motor_id, address) and byte values

**Example:**
```python
read_params = [
    (11, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION),
    (12, ADDR_PRESENT_CURRENT, LEN_PRESENT_CURRENT)
]
results = u2d2.bulk_read(read_params)
```

#### `bulk_write(write_params: List[Tuple[int, int, bytes]])`
Perform bulk write operation for multiple motors.

**Parameters:**
- `write_params` (List[Tuple[int, int, bytes]]): List of tuples (motor_id, address, data_bytes)

**Example:**
```python
write_params = [
    (11, ADDR_GOAL_POSITION, struct.pack('<I', 2048)),
    (12, ADDR_GOAL_CURRENT, struct.pack('<H', 100))
]
u2d2.bulk_write(write_params)
```

### Bulk High-Level Operations

#### `bulk_write_positions(motor_ids: List[int], positions: List[int])`
Bulk write position commands to multiple motors.

**Parameters:**
- `motor_ids` (List[int]): List of motor IDs
- `positions` (List[int]): List of position values (must match motor_ids length)

**Example:**
```python
motor_ids = [11, 12, 111, 112]
positions = [2048, 1500, 2048, 1500]
u2d2.bulk_write_positions(motor_ids, positions)
```

#### `bulk_write_currents(motor_ids: List[int], currents: List[int])`
Bulk write current commands to multiple motors.

**Parameters:**
- `motor_ids` (List[int]): List of motor IDs
- `currents` (List[int]): List of current values (must match motor_ids length)

**Example:**
```python
motor_ids = [11, 12]
currents = [100, -50]
u2d2.bulk_write_currents(motor_ids, currents)
```

#### `bulk_read_positions(motor_ids: List[int]) -> Dict[int, int]`
Bulk read positions from multiple motors.

**Parameters:**
- `motor_ids` (List[int]): List of motor IDs to read

**Returns:**
- `Dict[int, int]`: Dictionary mapping motor_id to position value

**Example:**
```python
motor_ids = [11, 12, 111, 112]
positions = u2d2.bulk_read_positions(motor_ids)
print(f"Motor 11 position: {positions[11]}")
```

#### `bulk_read_velocities(motor_ids: List[int]) -> Dict[int, int]`
Bulk read velocities from multiple motors.

**Parameters:**
- `motor_ids` (List[int]): List of motor IDs to read

**Returns:**
- `Dict[int, int]`: Dictionary mapping motor_id to velocity value

**Example:**
```python
velocities = u2d2.bulk_read_velocities([11, 12])
```

#### `bulk_read_currents(motor_ids: List[int]) -> Dict[int, int]`
Bulk read currents from multiple motors.

**Parameters:**
- `motor_ids` (List[int]): List of motor IDs to read

**Returns:**
- `Dict[int, int]`: Dictionary mapping motor_id to current value

**Example:**
```python
currents = u2d2.bulk_read_currents([11, 12])
```

#### `bulk_read_states(motor_ids: List[int]) -> Dict[int, Dict[str, int]]`
Bulk read all states (position, velocity, current) from multiple motors.

**Parameters:**
- `motor_ids` (List[int]): List of motor IDs to read

**Returns:**
- `Dict[int, Dict[str, int]]`: Dictionary mapping motor_id to state dict with 'position', 'velocity', 'current'

**Example:**
```python
states = u2d2.bulk_read_states([11, 12])
for motor_id, state in states.items():
    print(f"Motor {motor_id}: Pos={state['position']}, Vel={state['velocity']}, Curr={state['current']}")
```

### Bulk Utils

#### `parse_position(data: bytes) -> int`
Parse 4-byte position data.

**Parameters:**
- `data` (bytes): Raw position data

**Returns:**
- `int`: Parsed position value

#### `parse_velocity(data: bytes) -> int`
Parse 4-byte velocity data.

**Parameters:**
- `data` (bytes): Raw velocity data

**Returns:**
- `int`: Parsed velocity value

#### `parse_current(data: bytes) -> int`
Parse 2-byte current data.

**Parameters:**
- `data` (bytes): Raw current data

**Returns:**
- `int`: Parsed current value

### Individual Motor Operations

#### `set_goal_position(motor_id: int, goal: int)`
Set goal position for a single motor.

**Parameters:**
- `motor_id` (int): Motor ID
- `goal` (int): Target position

**Example:**
```python
u2d2.set_goal_position(11, 2048)  # Move to center
```

#### `set_goal_current(motor_id: int, current: int)`
Set the goal current for a single motor.

**Parameters:**
- `motor_id` (int): Motor ID
- `current` (int): Target current

**Example:**
```python
u2d2.set_goal_current(11, 100)  # Set current to 100
```

#### `set_velocity_limit(motor_id: int, velocity_limit: int)`
Set the profile velocity limit for a single motor.

**Parameters:**
- `motor_id` (int): Motor ID
- `velocity_limit` (int): Velocity limit value

**Example:**
```python
u2d2.set_velocity_limit(11, 100)
```

#### `set_current_limit(motor_id: int, limit_mA: int)`
Set the current limit for a single motor.

**Parameters:**
- `motor_id` (int): Motor ID
- `limit_mA` (int): Current limit in mA

**Example:**
```python
u2d2.set_current_limit(11, 500)  # 500mA limit
```

#### `get_position(motor_id: int) -> int`
Return the current position of a motor.

**Parameters:**
- `motor_id` (int): Motor ID

**Returns:**
- `int`: Current position

**Example:**
```python
position = u2d2.get_position(11)
print(f"Current position: {position}")
```

#### `get_velocity(motor_id: int) -> int`
Return the current velocity of the motor.

**Parameters:**
- `motor_id` (int): Motor ID

**Returns:**
- `int`: Current velocity

**Example:**
```python
velocity = u2d2.get_velocity(11)
print(f"Current velocity: {velocity}")
```

#### `get_current(motor_id: int) -> int`
Return the present current of the motor.

**Parameters:**
- `motor_id` (int): Motor ID

**Returns:**
- `int`: Current value

**Example:**
```python
current = u2d2.get_current(11)
print(f"Current: {current}")
```

### Port Management

#### `close()`
Close the serial port.

**Example:**
```python
u2d2.close()
```

## Examples

### Basic Position Control

```python
from dynamixel_u2d2 import U2D2Interface

# Initialize
u2d2 = U2D2Interface('/dev/ttyUSB0', baudrate=3000000)

try:
    # Setup motor
    u2d2.disable_torque(11)
    u2d2.set_motor_mode(11, 'position')
    u2d2.set_position_p_gain(11, 100)
    u2d2.enable_torque(11)
    
    # Control motor
    u2d2.set_goal_position(11, 2048)  # Move to center
    
    # Read state
    position = u2d2.get_position(11)
    velocity = u2d2.get_velocity(11)
    current = u2d2.get_current(11)
    
    print(f"Position: {position}, Velocity: {velocity}, Current: {current}")
    
finally:
    u2d2.close()
```

### Sync Operations

```python
from dynamixel_u2d2 import U2D2Interface

# Initialize with motor_ids for sync operations
motor_ids = [11, 12, 111, 112]
u2d2 = U2D2Interface('/dev/ttyUSB0', baudrate=3000000, motor_ids=motor_ids)

try:
    # Setup motors
    for motor_id in motor_ids:
        u2d2.disable_torque(motor_id)
        u2d2.set_motor_mode(motor_id, 'position')
        u2d2.set_position_p_gain(motor_id, 100)
        u2d2.enable_torque(motor_id)
    
    # Sync control - single packet for all motors
    positions = [2048, 1500, 2048, 1500]
    u2d2.sync_write_positions(positions)
    
    # Sync read - single packet for all states
    positions, velocities, currents = u2d2.sync_read_state()
    for i, motor_id in enumerate(motor_ids):
        print(f"Motor {motor_id}: Pos={positions[i]}, Vel={velocities[i]}, Curr={currents[i]}")
    
    # Specific state reading
    u2d2.init_specific_group_sync_read('position')
    positions = u2d2.sync_read_specific('position')
    print(f"Positions: {positions}")
        
finally:
    u2d2.close()
```

### Bulk Operations

```python
from dynamixel_u2d2 import U2D2Interface

# Initialize
u2d2 = U2D2Interface('/dev/ttyUSB0', baudrate=3000000)

try:
    motor_ids = [11, 12, 111, 112]
    
    # Setup all motors
    for motor_id in motor_ids:
        u2d2.disable_torque(motor_id)
        u2d2.set_motor_mode(motor_id, 'position')
        u2d2.set_position_p_gain(motor_id, 100)
        u2d2.enable_torque(motor_id)
    
    # Bulk control
    positions = [2048, 1500, 2048, 1500]
    u2d2.bulk_write_positions(motor_ids, positions)
    
    # Bulk read states
    states = u2d2.bulk_read_states(motor_ids)
    for motor_id, state in states.items():
        print(f"Motor {motor_id}: {state}")
        
finally:
    u2d2.close()
```

## Error Handling

The interface provides comprehensive error handling:

- **Communication Errors**: Automatically detected and reported
- **Invalid Parameters**: Type checking and validation
- **Motor Errors**: Individual motor error reporting
- **Bulk Operation Errors**: Graceful handling of partial failures

### Common Error Messages

- `❌ Torque Enable Error`: Failed to enable motor torque
- `❌ Failed to set mode`: Invalid operating mode
- `❌ Command Position Error`: Position command failed
- `⚠️ Current saturation detected`: Motor current saturated

## Performance

### Performance Comparison

| Operation | Individual | Bulk | Sync | Improvement |
|-----------|------------|------|------|-------------|
| 4 Motors Position | 4 packets | 1 packet | 1 packet | 4x faster |
| 4 Motors State Read | 12 packets | 3 packets | 1 packet | 12x faster |
| 8 Motors Position | 8 packets | 1 packet | 1 packet | 8x faster |
| 8 Motors State Read | 24 packets | 6 packets | 1 packet | 24x faster |

**Sync Operations** provide the highest efficiency by using a single packet for all operations, making them ideal for real-time control applications.

### Best Practices

1. **Use sync operations** for maximum efficiency in real-time control
2. **Use bulk operations** for multi-motor control when sync is not available
3. **Configure motors once** at startup
4. **Read states in bulk** when possible
5. **Handle errors gracefully** with try/except blocks
6. **Always close the interface** when done

## Troubleshooting

### Common Issues

1. **Port not found**: Check USB connection and port path
2. **Permission denied**: Add user to dialout group
3. **Motor not responding**: Verify motor ID and connections
4. **Bulk operations failing**: Check for duplicate motor IDs in same operation

### Debug Mode

Enable verbose output for debugging:

```python
u2d2 = U2D2Interface('/dev/ttyUSB0', verbose=True)
```

This will print detailed information about all operations.
