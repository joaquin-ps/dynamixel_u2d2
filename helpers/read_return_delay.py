import sys
from dynamixel_sdk import *  # Uses Dynamixel SDK library

# ====== USER CONFIGURATION ======
DEVICENAME = "/dev/ttyUSB0"         # Update as needed
PROTOCOL_VERSION = 2.0
RETURN_DELAY_ADDR = 9              # EEPROM address for Return Delay Time
RETURN_DELAY_UNIT_US = 2           # 1 unit = 2 microseconds
# =================================

def read_return_delay_time(portHandler, packetHandler, motor_id, baudrate):
    # Open the port
    if not portHandler.openPort():
        print("❌ Failed to open the port.")
        return

    print("✅ Port opened.")

    # Set the baudrate
    if not portHandler.setBaudRate(baudrate):
        print(f"❌ Failed to set baudrate to {baudrate}")
        portHandler.closePort()
        return

    print(f"✅ Baudrate set to {baudrate}")

    # Ping the motor
    model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, motor_id)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"❌ Failed to ping ID {motor_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        portHandler.closePort()
        return

    print(f"✅ Found motor ID {motor_id} (Model Number: {model_number})")

    # Read Return Delay Time
    delay_value, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, motor_id, RETURN_DELAY_ADDR)
    if dxl_comm_result == COMM_SUCCESS:
        print(f"📨 Return Delay Time: {delay_value} units ({delay_value * RETURN_DELAY_UNIT_US} µs)")
    else:
        print(f"❌ Failed to read Return Delay Time: {packetHandler.getTxRxResult(dxl_comm_result)}")

    portHandler.closePort()
    print("🔌 Port closed.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python read_return_delay.py <motor_id> <baudrate>")
        print("Example: python read_return_delay.py 1 4000000")
        sys.exit(1)

    motor_id = int(sys.argv[1])
    baudrate = int(sys.argv[2])

    portHandler = PortHandler(DEVICENAME)
    packetHandler = PacketHandler(PROTOCOL_VERSION)

    read_return_delay_time(portHandler, packetHandler, motor_id, baudrate)
