# Installation Guide

## Local Development Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd dynamixel_u2d2
```

### 2. Install in Development Mode
```bash
pip install -e .
```

This installs the package in "editable" mode, so changes to the source code are immediately available.

### 3. Install with Development Dependencies (Optional)
```bash
pip install -e ".[dev]"
```

This includes tools like Black, Flake8, and MyPy for code quality.

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

After installation, you'll have access to command line tools:

```bash
# Scan for Dynamixel motors
dynamixel-scan

# Change motor ID and baudrate
dynamixel-change-id
```

## Development Commands

```bash
make install        # Install in development mode
make install-dev    # Install with dev dependencies
make test          # Run import test
make clean         # Clean build artifacts
make format        # Format code with Black
make lint          # Lint code with Flake8
make type-check    # Type check with MyPy
make all-checks    # Run all quality checks
```

## Testing

Run the import test to verify installation:
```bash
make test
# or directly:
python tests/test_import.py
```

## Requirements

- Python 3.7+
- Linux (tested on Ubuntu 22.04)
- Dynamixel SDK
- NumPy

## Troubleshooting

### Permission Issues
If you get permission errors, try:
```bash
pip install --user -e .
```

### Missing Dependencies
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### USB Port Access
Make sure your user is in the dialout group:
```bash
sudo usermod -a -G dialout $USER
# Then log out and back in
```