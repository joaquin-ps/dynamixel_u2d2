"""
U2D2 Interface for Dynamixel motor control with bulk operations support.

This module provides a clean interface for controlling Dynamixel motors through
the U2D2 communication bridge, with support for bulk read/write operations
and various control modes.

Requirements:
    pip install dynamixel-sdk numpy
"""

import struct
from typing import Dict, List, Tuple, Literal
from enum import Enum
from dynamixel_sdk import *  # Dynamixel SDK

# ============================================================================
# CONTROL TABLE ADDRESSES AND CONSTANTS
# ============================================================================

# Control table addresses for X-series motors
ADDR_OPERATING_MODE = 11
ADDR_POSITION_P_GAIN = 84
ADDR_POSITION_I_GAIN = 82
ADDR_POSITION_D_GAIN = 80
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_CURRENT = 102
ADDR_GOAL_POSITION = 116
ADDR_PROFILE_VELOCITY = 112
ADDR_PRESENT_POSITION = 132
ADDR_PRESENT_VELOCITY = 128
ADDR_PRESENT_CURRENT = 126
ADDR_CURRENT_LIMIT = 38

# Control modes
POSITION_CONTROL = 3
CURRENT_BASED_POSITION_CONTROL = 5
CURRENT_CONTROL_MODE = 0

# Data lengths for bulk operations
LEN_GOAL_CURRENT = 2
LEN_GOAL_POSITION = 4
LEN_PRESENT_POSITION = 4
LEN_PRESENT_VELOCITY = 4
LEN_PRESENT_CURRENT = 2

# Motor mode types for type hints
MotorMode = Literal['position', 'current', 'current_based_position', 'velocity', 'extended_position', 'pwm']


class U2D2Interface:
    """
    U2D2 Interface with bulk read/write support for Dynamixel motors.
    
    This class provides a high-level interface for controlling Dynamixel motors
    through the U2D2 communication bridge, with efficient bulk operations for
    multi-motor control scenarios.
    """
    
    def __init__(self, usb_port: str, baudrate: int = 3000000, verbose: bool = False):
        """
        Initialize the U2D2 interface.
        
        Args:
            usb_port: USB port path (e.g., '/dev/ttyUSB0' on Linux)
            baudrate: Communication baudrate (default: 3000000)
            verbose: Print verbose output (default: False)

        Raises:
            Exception: If port opening or baudrate setting fails
        """
        self.packetHandler = PacketHandler(2.0)
        self.portHandler = PortHandler(usb_port)
        self.verbose = verbose
        
        # Open port
        if not self.portHandler.openPort():
            raise Exception("Failed to open the serial port!")
        
        # Set baudrate
        if not self.portHandler.setBaudRate(baudrate):
            raise Exception(f"Failed to set baudrate to {baudrate}!")
        
        if self.verbose:
            print("[U2D2Interface] ✅ Interface Initialized!")
    
    # ============================================================================
    # MOTOR CONFIGURATION
    # ============================================================================
    
    def enable_torque(self, motor_id: int):
        """Enable torque on the specified motor."""
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, motor_id, ADDR_TORQUE_ENABLE, 1
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Torque Enable Error ({motor_id}): {self.packetHandler.getTxRxResult(dxl_comm_result)}")
    
    def disable_torque(self, motor_id: int):
        """Disable torque on the specified motor."""
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, motor_id, ADDR_TORQUE_ENABLE, 0
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Torque Disable Error ({motor_id}): {self.packetHandler.getTxRxResult(dxl_comm_result)}")
    
    def _set_operating_mode(self, motor_id: int, mode: int):
        """
        Set the operating mode of a single motor.
        
        Args:
            motor_id: Motor ID
            mode: Operating mode (POSITION_CONTROL, CURRENT_CONTROL_MODE, etc.)
        """
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, motor_id, ADDR_OPERATING_MODE, mode
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Failed to set mode for motor {motor_id}")
        else:
            if self.verbose: print(f"[U2D2Interface] ✅ Set motor {motor_id} to mode {mode}")
    
    def set_motor_mode(self, motor_id: int, mode: MotorMode):
        """
        Set the operating mode of a single motor using string parameter.
        Wrapper for _set_operating_mode method.
        
        Args:
            motor_id: Motor ID
            mode: Operating mode string - one of:
                - 'position': Position control mode
                - 'current': Current control mode  
                - 'current_based_position': Current-based position control mode
                - 'velocity': Velocity control mode
                - 'extended_position': Extended position control mode
                - 'pwm': PWM control mode
        """
        mode_map = {
            'position': POSITION_CONTROL,
            'current': CURRENT_CONTROL_MODE,
            'current_based_position': CURRENT_BASED_POSITION_CONTROL,
            'velocity': 1,  # VELOCITY_CONTROL
            'extended_position': 4,  # EXTENDED_POSITION_CONTROL
            'pwm': 16,  # PWM_CONTROL
        }
        
        if mode not in mode_map:
            valid_modes = ', '.join(mode_map.keys())
            raise ValueError(f"Invalid mode '{mode}'. Valid modes are: {valid_modes}")
        
        mode_value = mode_map[mode]
        self._set_operating_mode(motor_id, mode_value)
    
    def set_position_p_gain(self, motor_id: int, p_gain: int):
        """Set the Position P Gain for a single motor."""
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
            self.portHandler, motor_id, ADDR_POSITION_P_GAIN, p_gain
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Failed to set P-Gain for motor {motor_id}")
        else:
            if self.verbose: print(f"[U2D2Interface] ✅ Set P-Gain {p_gain} for motor {motor_id}")
    
    def set_position_i_gain(self, motor_id: int, i_gain: int):
        """Set the Position I Gain for a single motor."""
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
            self.portHandler, motor_id, ADDR_POSITION_I_GAIN, i_gain
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Failed to set I-Gain for motor {motor_id}")
        else:
            if self.verbose: print(f"[U2D2Interface] ✅ Set I-Gain {i_gain} for motor {motor_id}")
    
    def set_position_d_gain(self, motor_id: int, d_gain: int):
        """Set the Position D Gain for a single motor."""
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
            self.portHandler, motor_id, ADDR_POSITION_D_GAIN, d_gain
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Failed to set D-Gain for motor {motor_id}")
        else:
            if self.verbose: print(f"[U2D2Interface] ✅ Set D-Gain {d_gain} for motor {motor_id}")
    
    # ============================================================================
    # BULK BASE OPERATIONS
    # ============================================================================
    
    def bulk_read(self, read_params: List[Tuple[int, int, int]]) -> Dict:
        """
        Perform bulk read operation for multiple motors.
        
        Args:
            read_params: List of tuples (motor_id, address, length)
        
        Returns:
            Dict with keys (motor_id, address) and byte values
        """
        # Create new bulk read handler
        groupBulkRead = GroupBulkRead(self.portHandler, self.packetHandler)
        
        # Add parameters for bulk read
        for motor_id, address, length in read_params:
            dxl_addparam_result = groupBulkRead.addParam(motor_id, address, length)
            if not dxl_addparam_result:
                print(f"[U2D2Interface] [ID:{motor_id}] groupBulkRead addParam failed")
        
        # Perform bulk read
        dxl_comm_result = groupBulkRead.txRxPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] Bulk read error: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            return {}
        
        # Extract results
        results = {}
        for motor_id, address, length in read_params:
            if groupBulkRead.isAvailable(motor_id, address, length):
                data = groupBulkRead.getData(motor_id, address, length)
                # Convert to bytes
                if length == 2:
                    results[(motor_id, address)] = struct.pack('<H', data)
                elif length == 4:
                    results[(motor_id, address)] = struct.pack('<I', data)
                else:
                    results[(motor_id, address)] = data.to_bytes(length, 'little')
            else:
                results[(motor_id, address)] = b'\x00' * length
        
        # Clear bulk read
        groupBulkRead.clearParam()
        
        return results
    
    def bulk_write(self, write_params: List[Tuple[int, int, bytes]]):
        """
        Perform bulk write operation for multiple motors.
        
        Args:
            write_params: List of tuples (motor_id, address, data_bytes)
        """
        if not write_params:
            return
        
        # Create new bulk write handler
        groupBulkWrite = GroupBulkWrite(self.portHandler, self.packetHandler)
        
        # Add parameters for bulk write
        for motor_id, address, data_bytes in write_params:
            # Convert bytes to integer array for SDK
            data_array = list(data_bytes)
            dxl_addparam_result = groupBulkWrite.addParam(motor_id, address, len(data_bytes), data_array)
            if not dxl_addparam_result:
                print(f"[U2D2Interface] [ID:{motor_id}] groupBulkWrite addParam failed")
        
        # Perform bulk write
        dxl_comm_result = groupBulkWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] Bulk write error: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        
        # Clear bulk write
        groupBulkWrite.clearParam()
    
    # ============================================================================
    # BULK HIGH-LEVEL OPERATIONS
    # ============================================================================
    
    def bulk_write_positions(self, motor_ids: List[int], positions: List[int]):
        """
        Bulk write position commands to multiple motors.
        
        Args:
            motor_ids: List of motor IDs
            positions: List of position values (must match motor_ids length)
        """
        if len(motor_ids) != len(positions):
            raise ValueError("motor_ids and positions must have the same length")
        
        write_params = []
        for motor_id, position in zip(motor_ids, positions):
            position_bytes = struct.pack('<I', int(position))
            write_params.append((motor_id, ADDR_GOAL_POSITION, position_bytes))
        
        self.bulk_write(write_params)
    
    def bulk_write_currents(self, motor_ids: List[int], currents: List[int]):
        """
        Bulk write current commands to multiple motors.
        
        Args:
            motor_ids: List of motor IDs
            currents: List of current values (must match motor_ids length)
        """
        if len(motor_ids) != len(currents):
            raise ValueError("motor_ids and currents must have the same length")
        
        write_params = []
        for motor_id, current in zip(motor_ids, currents):
            # Handle negative values with two's complement
            current_value = int(current)
            if current_value < 0:
                current_value = (1 << 16) + current_value
            current_bytes = struct.pack('<H', current_value)
            write_params.append((motor_id, ADDR_GOAL_CURRENT, current_bytes))
        
        self.bulk_write(write_params)
    
    def bulk_read_positions(self, motor_ids: List[int]) -> Dict[int, int]:
        """
        Bulk read positions from multiple motors.
        
        Args:
            motor_ids: List of motor IDs to read
            
        Returns:
            Dict mapping motor_id to position value
        """
        read_params = [(motor_id, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION) for motor_id in motor_ids]
        results = self.bulk_read(read_params)
        
        positions = {}
        for motor_id in motor_ids:
            data = results.get((motor_id, ADDR_PRESENT_POSITION), b'\x00\x00\x00\x00')
            positions[motor_id] = self.parse_position(data)
        
        return positions
    
    def bulk_read_velocities(self, motor_ids: List[int]) -> Dict[int, int]:
        """
        Bulk read velocities from multiple motors.
        
        Args:
            motor_ids: List of motor IDs to read
            
        Returns:
            Dict mapping motor_id to velocity value
        """
        read_params = [(motor_id, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY) for motor_id in motor_ids]
        results = self.bulk_read(read_params)
        
        velocities = {}
        for motor_id in motor_ids:
            data = results.get((motor_id, ADDR_PRESENT_VELOCITY), b'\x00\x00\x00\x00')
            velocities[motor_id] = self.parse_velocity(data)
        
        return velocities
    
    def bulk_read_currents(self, motor_ids: List[int]) -> Dict[int, int]:
        """
        Bulk read currents from multiple motors.
        
        Args:
            motor_ids: List of motor IDs to read
            
        Returns:
            Dict mapping motor_id to current value
        """
        read_params = [(motor_id, ADDR_PRESENT_CURRENT, LEN_PRESENT_CURRENT) for motor_id in motor_ids]
        results = self.bulk_read(read_params)
        
        currents = {}
        for motor_id in motor_ids:
            data = results.get((motor_id, ADDR_PRESENT_CURRENT), b'\x00\x00')
            currents[motor_id] = self.parse_current(data)
        
        return currents
    
    def bulk_read_states(self, motor_ids: List[int]) -> Dict[int, Dict[str, int]]:
        """
        Bulk read all states (position, velocity, current) from multiple motors.
        
        Args:
            motor_ids: List of motor IDs to read
            
        Returns:
            Dict mapping motor_id to state dict with 'position', 'velocity', 'current'
        """
        positions = self.bulk_read_positions(motor_ids)
        velocities = self.bulk_read_velocities(motor_ids)
        currents = self.bulk_read_currents(motor_ids)
        
        states = {}
        for motor_id in motor_ids:
            states[motor_id] = {
                'position': positions[motor_id],
                'velocity': velocities[motor_id],
                'current': currents[motor_id]
            }
        
        return states
    
    # ============================================================================
    # BULK UTILS
    # ============================================================================
    
    def _parse_2byte_signed(self, data: bytes) -> int:
        """Parse 2-byte signed data with two's complement handling."""
        if len(data) >= 2:
            value = struct.unpack('<H', data[:2])[0]
            # Handle two's complement for signed 16-bit
            if value > 32767:
                value -= 65536
            return value
        return 0
    
    def _parse_4byte_signed(self, data: bytes) -> int:
        """Parse 4-byte signed data with two's complement handling."""
        if len(data) >= 4:
            value = struct.unpack('<I', data[:4])[0]
            # Handle two's complement for signed 32-bit
            if value > 2147483647:
                value -= 4294967296
            return value
        return 0
    
    def parse_position(self, data: bytes) -> int:
        """Parse 4-byte position data."""
        return self._parse_4byte_signed(data)
    
    def parse_velocity(self, data: bytes) -> int:
        """Parse 4-byte velocity data."""
        return self._parse_4byte_signed(data)
    
    def parse_current(self, data: bytes) -> int:
        """Parse 2-byte current data."""
        return self._parse_2byte_signed(data)
    
    # ============================================================================
    # INDIVIDUAL MOTOR OPERATIONS
    # ============================================================================
    
    def set_goal_position(self, motor_id: int, goal: int):
        """Set goal position for a single motor."""
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler, motor_id, ADDR_GOAL_POSITION, goal
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Command Position Error ({motor_id}): {self.packetHandler.getTxRxResult(dxl_comm_result)}")
    
    def set_goal_current(self, motor_id: int, current: int):
        """Set the goal current for a single motor."""
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
            self.portHandler, motor_id, ADDR_GOAL_CURRENT, int(current)
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Failed to set goal current for motor {motor_id}")
    
    def set_velocity_limit(self, motor_id: int, velocity_limit: int):
        """Set the profile velocity limit for a single motor."""
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler, motor_id, ADDR_PROFILE_VELOCITY, velocity_limit
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Set Velocity Limit Error ({motor_id}): {self.packetHandler.getTxRxResult(dxl_comm_result)}")
    
    def set_current_limit(self, motor_id: int, limit_mA: int):
        """Set the current limit for a single motor."""
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
            self.portHandler, motor_id, ADDR_CURRENT_LIMIT, limit_mA
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Failed to set current limit for motor {motor_id}")
        else:
            if self.verbose: print(f"[U2D2Interface] ✅ Set current limit {limit_mA}LSB for motor {motor_id}")
    
    def get_position(self, motor_id: int) -> int:
        """Return the current position of a motor."""
        dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
            self.portHandler, motor_id, ADDR_PRESENT_POSITION
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Get Position Error ({motor_id}): {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        return dxl_present_position
    
    def get_velocity(self, motor_id: int) -> int:
        """Return the current velocity of the motor."""
        dxl_present_velocity, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
            self.portHandler, motor_id, ADDR_PRESENT_VELOCITY
        )
        
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Get Velocity Error ({motor_id}): {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            return 0
        
        # Handle two's complement for negative velocity values
        if dxl_present_velocity > 2147483647:
            dxl_present_velocity -= 4294967296
        
        return dxl_present_velocity
    
    def get_current(self, motor_id: int) -> int:
        """Return the present current (signed, in control-table LSB)."""
        dxl_present_current, dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(
            self.portHandler, motor_id, ADDR_PRESENT_CURRENT
        )
        
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[U2D2Interface] ❌ Get Current Error ({motor_id}): {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            return 0
        
        if dxl_error != 0:
            print(f"[U2D2Interface] Error in motor {motor_id}: {self.packetHandler.getRxPacketError(dxl_error)}")
            return 0
        
        # Handle two's complement for negative current values
        if dxl_present_current > 32767:
            dxl_present_current -= 65536
        
        # Check for saturation
        if dxl_present_current == 0xFFFF:
            print(f"[U2D2Interface] ⚠️ Current saturation detected on motor {motor_id}")
            return 0
        
        return dxl_present_current
    
    # ============================================================================
    # PORT MANAGEMENT
    # ============================================================================
    
    def close(self):
        """Close the serial port."""
        self.portHandler.closePort()
        if self.verbose: print("[U2D2Interface] ✅ Port closed.")