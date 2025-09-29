# Installation Guide

## Prerequisites

- Python 3.7 or higher
- Linux (tested on Ubuntu 22.04)

## Installation Methods

### Method 1: Development Installation (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd dynamixel_u2d2

# Install in development mode
pip install -e .
```

This installs the package in "editable" mode, so changes to the source code are immediately available.

### Method 2: Dependencies Only

```bash
pip install dynamixel-sdk numpy
```

**Note**: This method only installs dependencies. You'll need to add the package to your Python path to use it.

## Usage After Installation

Once installed, you can use the package from anywhere:

```python
from dynamixel_u2d2 import U2D2Interface

# Initialize and use
u2d2 = U2D2Interface('/dev/ttyUSB0')
u2d2.set_motor_mode(11, 'position')
u2d2.close()
```

## Command Line Tools

After installation, you'll have access to helper scripts in two ways:

### Method 1: Direct Python Scripts
```bash
# Scan for Dynamixel motors
python helpers/scan_dynamixel.py

# Change motor baud rates
python helpers/change_baud.py --new-baud 4000000

# Change motor IDs
python helpers/change_id.py --baud 4000000 --current-ids 1,2,3 --new-ids 10,11,12
```

### Method 2: Console Commands (if installed with pip install -e .)
```bash
# Scan for Dynamixel motors
dynamixel-scan

# Change motor baud rates
dynamixel-change-baud --new-baud 4000000

# Change motor IDs
dynamixel-change-id --baud 4000000 --current-ids 1,2,3 --new-ids 10,11,12
```

**Note**: For detailed usage instructions, see the [Helper Scripts documentation](helpers/HELPERS.md).


## Testing

Run the import test to verify installation:
```bash
python tests/test_import.py
```

## Dependencies

The package automatically installs these dependencies:
- `dynamixel-sdk>=3.7.0`
- `numpy>=1.19.0`

## Troubleshooting

### Permission Issues
If you get permission errors, try:
```bash
pip install --user -e .
```

### USB Port Access
If you can't access the USB port:
```bash
# Check if user is in dialout group
groups $USER

# If not, add user to dialout group
sudo usermod -a -G dialout $USER
# Then log out and back in
```

### Port Not Found
If the U2D2 port is not found:
```bash
# Check available USB devices
ls /dev/ttyUSB*

# Use the correct port in your code
u2d2 = U2D2Interface('/dev/ttyUSB1', baudrate=3000000)  # Use correct port
```