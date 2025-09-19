import sys
from dynamixel_sdk import *  # Dynamixel SDK

# Define serial port (Update if needed)
DEVICENAME = "/dev/ttyUSB0"  # Change based on your system

# Protocol Version
PROTOCOL_VERSION = 2.0  # Change to 1.0 if using older Dynamixel models

# Control table addresses
ADDR_ID = 7  # ID address in EEPROM
ADDR_BAUD_RATE = 8  # Baud rate address in EEPROM

# Baudrate mapping for Dynamixel
BAUDRATE_MAP = {3000000: 5, 4000000: 6} #{9600: 0, 57600: 1, 115200: 2, 1000000: 3, 2000000: 4, 3000000: 5, 4000000: 6}
BAUDRATES = list(BAUDRATE_MAP.keys())  # List of baud rates to try

# Range of IDs to scan
SCAN_RANGE = range(0, 120)


def scan_motors(portHandler, packetHandler):
    """ Scan for Dynamixel motors on the given baud rate """
    print("\nScanning for motors...")
    detected_motors = []

    for dxl_id in SCAN_RANGE:
        dxl_model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, dxl_id)
        if dxl_comm_result == COMM_SUCCESS:
            print(f"Found motor at ID {dxl_id}, Model Number: {dxl_model_number}")
            detected_motors.append(dxl_id)
        elif dxl_comm_result != COMM_TX_FAIL:  # Ignore timeout errors
            print(f"Error at ID {dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")

    return detected_motors


def change_motor_id(portHandler, packetHandler, current_id, new_id):
    """ Change Dynamixel motor ID """
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, current_id, ADDR_ID, new_id)
    if dxl_comm_result == COMM_SUCCESS:
        print(f"✅ Motor ID {current_id} changed to {new_id}")
        return True
    else:
        print(f"❌ Failed to change ID {current_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        return False


def change_baudrate(portHandler, packetHandler, motor_id, new_baudrate):
    """ Change Dynamixel motor baud rate """
    if new_baudrate not in BAUDRATE_MAP:
        print(f"❌ Invalid baud rate: {new_baudrate}")
        return False

    baudrate_code = BAUDRATE_MAP[new_baudrate]
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, motor_id, ADDR_BAUD_RATE, baudrate_code)
    
    if dxl_comm_result == COMM_SUCCESS:
        print(f"✅ Baudrate of ID {motor_id} changed to {new_baudrate}")
        return True
    else:
        print(f"❌ Failed to change baudrate for ID {motor_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        return False


def try_scan_at_multiple_baudrates(portHandler, packetHandler):
    """ Try scanning for motors at different baud rates """
    for baudrate in BAUDRATES:
        print(f"\n🔄 Trying baudrate: {baudrate}...")
        if portHandler.setBaudRate(baudrate):
            detected_motors = scan_motors(portHandler, packetHandler)
            if detected_motors:
                print(f"✅ Motors detected at baudrate {baudrate}")
                return baudrate, detected_motors
        else:
            print(f"❌ Failed to set baudrate {baudrate}")

    print("❌ No motors found at any baudrate.")
    return None, []


def main():
    """ Main function to scan and change motor settings """
    CURRENT_IDS = [11, 111] # List of current motor IDs
    NEW_IDS = None #[12]  # List of new IDs to assign
    NEW_BAUDRATE = 4000000  # Desired new baud rate

    if NEW_IDS is not None and len(CURRENT_IDS) != len(NEW_IDS):
        print("❌ Error: The number of current IDs must match the number of new IDs!")
        return

    # Initialize port and packet handlers
    portHandler = PortHandler(DEVICENAME)
    packetHandler = PacketHandler(PROTOCOL_VERSION)

    # Open port
    if not portHandler.openPort():
        print("❌ Failed to open port.")
        return
    print("✅ Opened port successfully!")

    # Try scanning at multiple baudrates
    current_baudrate, detected_motors = try_scan_at_multiple_baudrates(portHandler, packetHandler)

    if not detected_motors:
        portHandler.closePort()
        return

    # Ask for user confirmation before changing settings
    print("\nThe following changes will be made:")
    if NEW_IDS is not None:
        for curr_id, new_id in zip(CURRENT_IDS, NEW_IDS):
            print(f"  - ID {curr_id} ➝ {new_id}")
    else:
        print("  - No ID changes")
    print(f"  - Changing baudrate to {NEW_BAUDRATE}")

    confirm = input("\nProceed with changes? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Operation aborted.")
        portHandler.closePort()
        return

    # Change motor IDs
    if NEW_IDS is not None:
        for curr_id, new_id in zip(CURRENT_IDS, NEW_IDS):
            if curr_id in detected_motors:
                change_motor_id(portHandler, packetHandler, curr_id, new_id)
            else:
                print(f"❌ ID {curr_id} not found, skipping.")
    else:
        print("❌ No new IDs provided, skipping ID change.")

    # Change baudrate
    for motor_id in detected_motors:
        change_baudrate(portHandler, packetHandler, motor_id, NEW_BAUDRATE)

    # Close the port
    portHandler.closePort()
    print("\n✅ Process completed!")


if __name__ == "__main__":
    main()
