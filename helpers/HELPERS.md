# Helper Scripts

These scripts provide easy-to-use command-line tools for scanning, changing baud rates, and changing motor IDs.

## Quick Start

1. **Install the package**: `pip install -e .` (from the project root)
2. **Configure U2D2 ports**: `python3 u2d2_port_simple.py`
3. **Scan for motors**: `python3 scan_dynamixel.py`
4. **Change baud rates**: `python3 change_baud.py --new-baud 4000000`
5. **Change motor IDs**: `python3 change_id.py --baud 4000000 --current-ids 1,2,3 --new-ids 10,11,12`

---

## 🔧 Port Management

### 🚀 u2d2_port_timer.py

**Purpose**: U2D2 port scanner and latency timer setter.

#### Basic Usage

```bash
# Scan and display U2D2 ports (no changes)
dynamixel-port

# Set all U2D2 ports to 2ms latency
dynamixel-port --latency-timer 2

# Set all U2D2 ports to 1ms latency
dynamixel-port --latency-timer 1

# Set all U2D2 ports to 4ms latency
dynamixel-port --latency-timer 4

# Show help
dynamixel-port --help

# Alternative: Run directly from helpers directory
python3 u2d2_port_timer.py                    # Scan only
python3 u2d2_port_timer.py --latency-timer 2  # Configure
python3 u2d2_port_timer.py --help             # Help
```

#### Command Line Options

| Option | Description | Required |
|--------|-------------|----------|
| `--latency-timer` | Latency timer value in milliseconds (must be positive integer) | No |
| `--help` | Show help message and exit | No |

#### Features

- ✅ Automatically finds all U2D2 ports (`/dev/ttyUSB*`, `/dev/ttyACM*`)
- ✅ Shows current latency timer for each port
- ✅ Sets latency timer to specified value
- ✅ Validates that latency is a positive integer
- ✅ Only affects `/dev/ttyUSB*` ports (where latency timer is available)
- ✅ Asks for user confirmation before making changes
- ✅ Proper command-line interface with help
- ✅ Simple, focused functionality

#### Example Output

**Scan-only mode:**
```
🔍 Scanning for U2D2 ports...

Found 2 U2D2 port(s):
  /dev/ttyUSB0: 1ms
  /dev/ttyUSB1: 1ms

💡 Use --latency-timer to configure port latency
```

**Configure mode:**
```
🔍 Scanning for U2D2 ports...
🎯 Target latency: 2ms

Found 2 U2D2 port(s):
  /dev/ttyUSB0: 1ms ⚠️
  /dev/ttyUSB1: 1ms ⚠️

⚠️  2 port(s) need to be changed to 2ms
This requires sudo privileges.

Proceed with changing latency timer to 2ms? (y/n): y

✅ /dev/ttyUSB0: Set to 2ms
✅ /dev/ttyUSB1: Set to 2ms

📊 Configured 2/2 ports successfully
```

---

## 📡 scan_dynamixel.py

**Purpose**: Scan for Dynamixel motors at different baud rates and motor ID ranges.

### Basic Usage

```bash
# Scan all motors at all baud rates
python scan_dynamixel.py

# Scan with custom port
python scan_dynamixel.py --port /dev/ttyUSB1

# Quiet mode (minimal output)
python scan_dynamixel.py --quiet
```

### Advanced Options

```bash
# Scan only specific baud rates
python scan_dynamixel.py --scan-bauds 3000000,4000000

# Scan only specific motor ID range
python scan_dynamixel.py --scan-id-range 1,10

# Combine options
python scan_dynamixel.py --scan-bauds 3000000,4000000 --scan-id-range 1,20 --port /dev/ttyUSB1
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--scan-bauds` | Comma-separated baud rates to scan | All available rates |
| `--scan-id-range` | Motor ID range as START,END | 0,253 (all IDs) |
| `--port` | USB port path | /dev/ttyUSB0 |
| `--verbose` | Enable verbose output | True |
| `--quiet` | Suppress verbose output | False |

### Example Output

```
==================================================
🔍 SCAN RESULTS
==================================================
✅ Found 2 motor(s):

📡 Baud Rate 3000000:
   - Motor ID 1
   - Motor ID 2

📡 Baud Rate 4000000:
   - Motor ID 3

📊 Summary:
   Total motors found: 3
   Baud rates used: 2
   ID range scanned: 0-252
```

---

## 🔄 change_baud.py

**Purpose**: Change Dynamixel motor baud rates with flexible scanning and validation.

### Basic Usage

```bash
# Scan all motors and change to 4000000 baud
python change_baud.py --new-baud 4000000

# Change specific motors with known baud rate (no scanning)
python change_baud.py --new-baud 4000000 --old-baud 3000000 --motor-ids 1,2,3

# Scan only at specific baud rate and change all found motors
python change_baud.py --new-baud 4000000 --old-baud 3000000
```

### Advanced Options

```bash
# Scan specific baud rates and change all found motors
python change_baud.py --new-baud 4000000 --scan-bauds 3000000,1000000

# Scan specific ID range and change all found motors
python change_baud.py --new-baud 4000000 --scan-id-range 1,10

# Skip confirmation prompt (use with caution)
python change_baud.py --new-baud 4000000 --yes
```

### Command Line Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--new-baud` | New baud rate to set | ✅ Yes | - |
| `--old-baud` | Current baud rate (if known) | No | None (scans all) |
| `--motor-ids` | Comma-separated motor IDs to change | No | All detected |
| `--scan-bauds` | Comma-separated baud rates to scan | No | All available |
| `--scan-id-range` | Motor ID range as START,END | No | 0,253 |
| `--port` | USB port path | No | /dev/ttyUSB0 |
| `--verbose` | Enable verbose output | No | True |
| `--yes` | Skip confirmation prompt | No | False |

### Supported Baud Rates

- 9600
- 57600
- 115200
- 1000000
- 2000000
- 3000000
- 4000000

### Example Output

```
============================================================
🔄 BAUD RATE CHANGE PLAN
============================================================
New Baud Rate: 4000000
Port: /dev/ttyUSB0
Old Baud Rate: 3000000 (known)

Motors to change:
  Motor ID 1 (3000000 → 4000000 baud)
  Motor ID 2 (3000000 → 4000000 baud)

Total motors to change: 2
============================================================

⚠️  WARNING: This will permanently change motor baud rates!
⚠️  Make sure no other programs are using these motors.

Proceed with baud rate changes? (yes/no): yes

============================================================
📊 RESULTS
============================================================
Successfully changed: 2/2 motors

✅ All motor baud rates changed successfully!
```

---

## 🆔 change_id.py

**Purpose**: Change Dynamixel motor IDs with validation and confirmation.

### Basic Usage

```bash
# Change motor IDs 1,2,3 to 10,11,12 at 3000000 baud
python change_id.py --baud 3000000 --current-ids 1,2,3 --new-ids 10,11,12

# Change single motor ID 1 to 5 at 4000000 baud
python change_id.py --baud 4000000 --current-ids 1 --new-ids 5

# Skip confirmation prompt
python change_id.py --baud 3000000 --current-ids 1,2 --new-ids 10,11 --yes
```

### Advanced Options

```bash
# Use custom port
python change_id.py --baud 3000000 --current-ids 1,2 --new-ids 10,11 --port /dev/ttyUSB1

# Quiet mode
python change_id.py --baud 3000000 --current-ids 1 --new-ids 5 --quiet
```

### Command Line Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--baud` | Baud rate to use for communication | ✅ Yes | - |
| `--current-ids` | Comma-separated current motor IDs | ✅ Yes | - |
| `--new-ids` | Comma-separated new motor IDs | ✅ Yes | - |
| `--port` | USB port path | No | /dev/ttyUSB0 |
| `--verbose` | Enable verbose output | No | True |
| `--quiet` | Suppress verbose output | No | False |
| `--yes` | Skip confirmation prompt | No | False |

### Validation Rules

- ✅ Motor IDs must be 0-252 (Dynamixel Protocol 2.0 range)
- ✅ Current and new ID lists must have the same length
- ✅ No duplicate IDs in current or new lists
- ✅ Current and new IDs must be distinct (no overlap)
- ✅ Baud rate must be supported

### Example Output

```
============================================================
🔄 MOTOR ID CHANGE PLAN
============================================================
Baud Rate: 3000000
Port: /dev/ttyUSB0

ID Changes:
  Motor ID 1 → 10
  Motor ID 2 → 11
  Motor ID 3 → 12

Total motors to change: 3
============================================================

⚠️  WARNING: This will permanently change motor IDs!
⚠️  Make sure no other programs are using these motors.

Proceed with ID changes? (yes/no): yes

============================================================
📊 RESULTS
============================================================
Successfully changed: 3/3 motors

✅ All motor IDs changed successfully!
```

### Best Practices

- Always scan first to see current configuration
- Use `--yes` flag only in automated scripts
- Test communication after changes
- Keep backup of working configurations

### Troubleshooting

| Problem | Solution |
|---------|----------|
| "No motors detected" | Check USB connection, power, and port path |
| "Failed to open port" | Try different port (`--port /dev/ttyUSB1`) |
| "Invalid baud rate" | Use supported baud rates only |
| "Duplicate IDs" | Ensure all IDs are unique |
| "Overlapping IDs" | Current and new IDs must be different |

---

## 📚 Additional Resources

- **Dynamixel Protocol 2.0**: [Official Documentation](https://emanual.robotis.com/docs/en/dxl/protocol2/)
- **U2D2 Interface**: [ROBOTIS e-Manual](https://emanual.robotis.com/docs/en/parts/interface/u2d2/)
- **Motor ID Range**: 0-252 (253 total IDs)
- **Supported Baud Rates**: 9600, 57600, 115200, 1000000, 2000000, 3000000, 4000000

---