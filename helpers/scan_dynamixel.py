import sys
from dynamixel_sdk import *  # Import Dynamixel SDK

# Define serial port (Update this if needed)
DEVICENAME = "/dev/ttyUSB0"  # Change if needed

# Define possible baud rates to scan
BAUDRATES = [3000000, 4000000] #[9600, 57600, 115200, 1000000, 2000000, 3000000, 4000000]  # Common Dynamixel baud rates

# Define Dynamixel protocol version
PROTOCOL_VERSION = 2.0  # Change to 1.0 if using older Dynamixels

# Define ID range to scan
SCAN_RANGE = range(0, 120)

# Initialize PortHandler
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open the port
if not portHandler.openPort():
    print("Failed to open port.")
    sys.exit()
print("Opened port successfully!")

found_motors = {}

# Scan through baud rates
for baudrate in BAUDRATES:
    print(f"\nTrying baud rate: {baudrate}")

    # Set baud rate
    if not portHandler.setBaudRate(baudrate):
        print(f"Failed to set baudrate {baudrate}")
        continue

    # Scan for IDs
    for dxl_id in SCAN_RANGE:
        dxl_model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, dxl_id)
        if dxl_comm_result == COMM_SUCCESS:
            print(f"Found motor at ID {dxl_id}, Model Number: {dxl_model_number} on Baud {baudrate}")
            found_motors[dxl_id] = baudrate
        elif dxl_comm_result != COMM_TX_FAIL:  # Ignore timeout errors
            print(f"Error at BAUD: {baudrate}: ID {dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")

# Close the port
portHandler.closePort()

# Print summary
if found_motors:
    print("\nMotors detected:")
    for motor_id, baud in found_motors.items():
        print(f" - ID {motor_id} at Baud {baud}")
else:
    print("No motors detected.")

