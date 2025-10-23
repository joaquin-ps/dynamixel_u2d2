"""
Fake U2D2 Interface for testing Dynamixel motor control.

This module provides a mock implementation of the U2D2Interface for testing
higher-level code without requiring actual hardware.
"""

import struct
import time
import random
from typing import Dict, List, Tuple, Optional
from .base_interface import BaseInterface, MotorMode

# Import constants from the original interface
from .u2d2_interface import (
    ADDR_PRESENT_CURRENT,
    ADDR_PRESENT_VELOCITY, 
    ADDR_PRESENT_POSITION,
    LEN_PRESENT_CURRENT,
    LEN_PRESENT_VELOCITY,
    LEN_PRESENT_POSITION,
    STATE_ADDRESS_MAP,
    BAUDRATE_MAP,
    SCAN_BAUDRATES
)


class FakeU2D2Interface(BaseInterface):
    """
    Fake U2D2 Interface for testing without hardware.
    
    This class provides a mock implementation that simulates motor behavior
    for testing higher-level code without requiring actual Dynamixel hardware.
    """
    
    def __init__(
        self,
        usb_port: str = "/dev/ttyUSB_fake",
        baudrate: int = 4000000,
        motor_ids: Optional[List[int]] = None,
        protocol_version: float = 2.0,
        verbose: bool = False
    ):
        """
        Initialize the fake interface.
        
        Args:
            usb_port: Serial port (ignored for fake interface)
            baudrate: Communication speed (ignored for fake interface)
            motor_ids: List of motor IDs for bulk reads
            protocol_version: Dynamixel protocol version (ignored for fake interface)
            verbose: Print verbose output (default: False)
        """
        super().__init__(usb_port, baudrate, motor_ids, protocol_version, verbose)
        
        # Mock motor state storage
        self._motor_states: Dict[int, Dict[str, int]] = {}
        self._motor_modes: Dict[int, str] = {}
        self._torque_enabled: Dict[int, bool] = {}
        self._goal_positions: Dict[int, int] = {}
        self._goal_currents: Dict[int, int] = {}
        self._velocity_limits: Dict[int, int] = {}
        self._current_limits: Dict[int, int] = {}
        self._pid_gains: Dict[int, Dict[str, int]] = {}
        
        # Initialize motor states if motor_ids provided
        if self.motor_ids:
            for motor_id in self.motor_ids:
                self._initialize_motor_state(motor_id)
        
        self._verbose_log(f"✅ Fake interface initialized with {len(self.motor_ids) if self.motor_ids else 0} motors")
    
    def _initialize_motor_state(self, motor_id: int):
        """Initialize mock state for a motor."""
        self._motor_states[motor_id] = {
            'position': 0,
            'velocity': 0,
            'current': 0
        }
        self._motor_modes[motor_id] = 'position'
        self._torque_enabled[motor_id] = False
        self._goal_positions[motor_id] = 0
        self._goal_currents[motor_id] = 0
        self._velocity_limits[motor_id] = 100
        self._current_limits[motor_id] = 1000
        self._pid_gains[motor_id] = {'p': 0, 'i': 0, 'd': 0}
    
    def _simulate_motor_behavior(self):
        """Simulate motor behavior by updating states based on goals."""
        for motor_id in self._motor_states:
            if not self._torque_enabled.get(motor_id, False):
                continue
            
            # Simple simulation: move towards goal position
            current_pos = self._motor_states[motor_id]['position']
            goal_pos = self._goal_positions.get(motor_id, current_pos)
            
            if self._motor_modes.get(motor_id) == 'position':
                # Simulate position control
                error = goal_pos - current_pos
                if abs(error) > 5:  # Deadband
                    # Simple proportional control simulation
                    velocity = min(max(error * 0.1, -50), 50)  # Limit velocity
                    self._motor_states[motor_id]['velocity'] = velocity
                    self._motor_states[motor_id]['position'] += velocity * 0.01  # Simple integration
                else:
                    self._motor_states[motor_id]['velocity'] = 0
            elif self._motor_modes.get(motor_id) == 'current':
                # Simulate current control
                goal_current = self._goal_currents.get(motor_id, 0)
                self._motor_states[motor_id]['current'] = goal_current
                # In current mode, position can drift
                self._motor_states[motor_id]['position'] += random.randint(-1, 1)
    
    # ============================================================================
    # MOTOR CONFIGURATION
    # ============================================================================
    
    def enable_torque(self, motor_id: int):
        """Enable torque on the specified motor."""
        self._torque_enabled[motor_id] = True
        self._verbose_log(f"✅ Fake torque enabled for motor {motor_id}")
    
    def disable_torque(self, motor_id: int):
        """Disable torque on the specified motor."""
        self._torque_enabled[motor_id] = False
        self._verbose_log(f"✅ Fake torque disabled for motor {motor_id}")
    
    def set_motor_mode(self, motor_id: int, mode: MotorMode):
        """Set the operating mode of a single motor using string parameter."""
        if mode not in ['position', 'current']:
            raise ValueError(f"Invalid mode '{mode}'. Valid modes are: position, current")
        
        self._motor_modes[motor_id] = mode
        self._verbose_log(f"✅ Fake motor {motor_id} set to {mode} mode")
    
    def set_position_p_gain(self, motor_id: int, p_gain: int):
        """Set the Position P Gain for a single motor."""
        self._pid_gains[motor_id]['p'] = p_gain
        self._verbose_log(f"✅ Fake P-Gain {p_gain} set for motor {motor_id}")
    
    def set_position_i_gain(self, motor_id: int, i_gain: int):
        """Set the Position I Gain for a single motor."""
        self._pid_gains[motor_id]['i'] = i_gain
        self._verbose_log(f"✅ Fake I-Gain {i_gain} set for motor {motor_id}")
    
    def set_position_d_gain(self, motor_id: int, d_gain: int):
        """Set the Position D Gain for a single motor."""
        self._pid_gains[motor_id]['d'] = d_gain
        self._verbose_log(f"✅ Fake D-Gain {d_gain} set for motor {motor_id}")
    
    # ============================================================================
    # SYNC BASE OPERATIONS
    # ============================================================================
    
    def init_group_sync_read(self, motor_ids: List[int]):
        """Initialize group sync read parameters for maximum efficiency using contiguous read."""
        for motor_id in motor_ids:
            if motor_id not in self._motor_states:
                self._initialize_motor_state(motor_id)
        self._verbose_log(f"✅ Fake sync read initialized for motors: {motor_ids}")
    
    def sync_read_state(self) -> Tuple[List[int], List[int], List[int]]:
        """Sync read the full state (position, velocity, current) of all motors."""
        if self.motor_ids is None:
            raise RuntimeError("Sync read not configured. Initialize with motor_ids.")
        
        # Simulate motor behavior
        self._simulate_motor_behavior()
        
        positions = []
        velocities = []
        currents = []
        
        for motor_id in self.motor_ids:
            state = self._motor_states.get(motor_id, {'position': 0, 'velocity': 0, 'current': 0})
            positions.append(int(state['position']))
            velocities.append(int(state['velocity']))
            currents.append(int(state['current']))
        
        return positions, velocities, currents
    
    # ============================================================================
    # SYNC WRITE OPERATIONS
    # ============================================================================
    
    def sync_write_positions(self, positions: List[int]):
        """Sync write position commands to all configured motors."""
        if self.motor_ids is None:
            raise RuntimeError("Sync write position not configured. Initialize with motor_ids.")
        
        if len(positions) != len(self.motor_ids):
            raise ValueError(f"positions length ({len(positions)}) must match motor_ids length ({len(self.motor_ids)})")
        
        for motor_id, position in zip(self.motor_ids, positions):
            self._goal_positions[motor_id] = position
            if motor_id not in self._motor_states:
                self._initialize_motor_state(motor_id)
        
        self._verbose_log(f"✅ Fake sync write positions: {dict(zip(self.motor_ids, positions))}")
    
    def sync_write_currents(self, currents: List[int]):
        """Sync write current commands to all configured motors."""
        if self.motor_ids is None:
            raise RuntimeError("Sync write current not configured. Initialize with motor_ids.")
        
        if len(currents) != len(self.motor_ids):
            raise ValueError(f"currents length ({len(currents)}) must match motor_ids length ({len(self.motor_ids)})")
        
        for motor_id, current in zip(self.motor_ids, currents):
            self._goal_currents[motor_id] = current
            if motor_id not in self._motor_states:
                self._initialize_motor_state(motor_id)
        
        self._verbose_log(f"✅ Fake sync write currents: {dict(zip(self.motor_ids, currents))}")
    
    # ============================================================================
    # SYNC SPECIFIC STATE READS
    # ============================================================================
    
    def init_specific_group_sync_read(self, state: str):
        """Initialize group sync read parameters for specific states."""
        if state not in STATE_ADDRESS_MAP.keys():
            raise ValueError(f"Invalid state: {state}")
        
        self._verbose_log(f"✅ Fake specific sync read initialized for state: {state}")
    
    def sync_read_specific(self, state: str) -> List[int]:
        """Sync read only specific state for all configured motors."""
        if self.motor_ids is None:
            raise RuntimeError(f"Specific state sync read not configured. Call init_specific_group_sync_read({state}) first.")
        
        if state not in STATE_ADDRESS_MAP.keys():
            raise ValueError(f"Invalid state: {state}")
        
        # Simulate motor behavior
        self._simulate_motor_behavior()
        
        specific_state = []
        for motor_id in self.motor_ids:
            state_value = self._motor_states.get(motor_id, {'position': 0, 'velocity': 0, 'current': 0})[state]
            specific_state.append(int(state_value))
        
        return specific_state
    
    # ============================================================================
    # BULK BASE OPERATIONS
    # ============================================================================
    
    def bulk_read(self, read_params: List[Tuple[int, int, int]]) -> Dict:
        """Perform bulk read operation for multiple motors."""
        results = {}
        
        for motor_id, address, length in read_params:
            if motor_id not in self._motor_states:
                self._initialize_motor_state(motor_id)
            
            state = self._motor_states[motor_id]
            
            if address == ADDR_PRESENT_POSITION:
                data = struct.pack('<I', int(state['position']))
            elif address == ADDR_PRESENT_VELOCITY:
                data = struct.pack('<I', int(state['velocity']))
            elif address == ADDR_PRESENT_CURRENT:
                data = struct.pack('<H', int(state['current']))
            else:
                data = b'\x00' * length
            
            results[(motor_id, address)] = data
        
        return results
    
    def bulk_write(self, write_params: List[Tuple[int, int, bytes]]):
        """Perform bulk write operation for multiple motors."""
        for motor_id, address, data_bytes in write_params:
            if motor_id not in self._motor_states:
                self._initialize_motor_state(motor_id)
            
            # Simulate different write operations based on address
            if address == 116:  # ADDR_GOAL_POSITION
                position = struct.unpack('<I', data_bytes)[0]
                self._goal_positions[motor_id] = position
            elif address == 102:  # ADDR_GOAL_CURRENT
                current = struct.unpack('<H', data_bytes)[0]
                self._goal_currents[motor_id] = current
        
        self._verbose_log(f"✅ Fake bulk write completed for {len(write_params)} parameters")
    
    # ============================================================================
    # BULK HIGH-LEVEL OPERATIONS
    # ============================================================================
    
    def bulk_write_positions(self, motor_ids: List[int], positions: List[int]):
        """Bulk write position commands to multiple motors."""
        if len(motor_ids) != len(positions):
            raise ValueError("motor_ids and positions must have the same length")
        
        for motor_id, position in zip(motor_ids, positions):
            self._goal_positions[motor_id] = position
            if motor_id not in self._motor_states:
                self._initialize_motor_state(motor_id)
        
        self._verbose_log(f"✅ Fake bulk write positions: {dict(zip(motor_ids, positions))}")
    
    def bulk_write_currents(self, motor_ids: List[int], currents: List[int]):
        """Bulk write current commands to multiple motors."""
        if len(motor_ids) != len(currents):
            raise ValueError("motor_ids and currents must have the same length")
        
        for motor_id, current in zip(motor_ids, currents):
            self._goal_currents[motor_id] = current
            if motor_id not in self._motor_states:
                self._initialize_motor_state(motor_id)
        
        self._verbose_log(f"✅ Fake bulk write currents: {dict(zip(motor_ids, currents))}")
    
    def bulk_read_positions(self, motor_ids: List[int]) -> Dict[int, int]:
        """Bulk read positions from multiple motors."""
        read_params = [(motor_id, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION) for motor_id in motor_ids]
        results = self.bulk_read(read_params)
        
        positions = {}
        for motor_id in motor_ids:
            data = results.get((motor_id, ADDR_PRESENT_POSITION), b'\x00\x00\x00\x00')
            positions[motor_id] = self._parse_position(data)
        
        return positions
    
    def bulk_read_velocities(self, motor_ids: List[int]) -> Dict[int, int]:
        """Bulk read velocities from multiple motors."""
        read_params = [(motor_id, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY) for motor_id in motor_ids]
        results = self.bulk_read(read_params)
        
        velocities = {}
        for motor_id in motor_ids:
            data = results.get((motor_id, ADDR_PRESENT_VELOCITY), b'\x00\x00\x00\x00')
            velocities[motor_id] = self._parse_velocity(data)
        
        return velocities
    
    def bulk_read_currents(self, motor_ids: List[int]) -> Dict[int, int]:
        """Bulk read currents from multiple motors."""
        read_params = [(motor_id, ADDR_PRESENT_CURRENT, LEN_PRESENT_CURRENT) for motor_id in motor_ids]
        results = self.bulk_read(read_params)
        
        currents = {}
        for motor_id in motor_ids:
            data = results.get((motor_id, ADDR_PRESENT_CURRENT), b'\x00\x00')
            currents[motor_id] = self._parse_current(data)
        
        return currents
    
    def bulk_read_states(self, motor_ids: List[int]) -> Dict[int, Dict[str, int]]:
        """Bulk read all states (position, velocity, current) from multiple motors."""
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
    
    def _parse_position(self, data: bytes) -> int:
        """Parse 4-byte position data."""
        if len(data) >= 4:
            value = struct.unpack('<I', data[:4])[0]
            if value > 2147483647:
                value -= 4294967296
            return value
        return 0
    
    def _parse_velocity(self, data: bytes) -> int:
        """Parse 4-byte velocity data."""
        if len(data) >= 4:
            value = struct.unpack('<I', data[:4])[0]
            if value > 2147483647:
                value -= 4294967296
            return value
        return 0
    
    def _parse_current(self, data: bytes) -> int:
        """Parse 2-byte current data."""
        if len(data) >= 2:
            value = struct.unpack('<H', data[:2])[0]
            if value > 32767:
                value -= 65536
            return value
        return 0
    
    # ============================================================================
    # INDIVIDUAL MOTOR OPERATIONS
    # ============================================================================
    
    def set_goal_position(self, motor_id: int, goal: int):
        """Set goal position for a single motor."""
        self._goal_positions[motor_id] = goal
        if motor_id not in self._motor_states:
            self._initialize_motor_state(motor_id)
        self._verbose_log(f"✅ Fake goal position {goal} set for motor {motor_id}")
    
    def set_goal_current(self, motor_id: int, current: int):
        """Set the goal current for a single motor."""
        self._goal_currents[motor_id] = current
        if motor_id not in self._motor_states:
            self._initialize_motor_state(motor_id)
        self._verbose_log(f"✅ Fake goal current {current} set for motor {motor_id}")
    
    def set_velocity_limit(self, motor_id: int, velocity_limit: int):
        """Set the profile velocity limit for a single motor."""
        self._velocity_limits[motor_id] = velocity_limit
        self._verbose_log(f"✅ Fake velocity limit {velocity_limit} set for motor {motor_id}")
    
    def set_current_limit(self, motor_id: int, limit_mA: int):
        """Set the current limit for a single motor."""
        self._current_limits[motor_id] = limit_mA
        self._verbose_log(f"✅ Fake current limit {limit_mA} set for motor {motor_id}")
    
    def get_position(self, motor_id: int) -> int:
        """Return the current position of a motor."""
        if motor_id not in self._motor_states:
            self._initialize_motor_state(motor_id)
        
        # Simulate motor behavior
        self._simulate_motor_behavior()
        
        return int(self._motor_states[motor_id]['position'])
    
    def get_velocity(self, motor_id: int) -> int:
        """Return the current velocity of the motor."""
        if motor_id not in self._motor_states:
            self._initialize_motor_state(motor_id)
        
        # Simulate motor behavior
        self._simulate_motor_behavior()
        
        return int(self._motor_states[motor_id]['velocity'])
    
    def get_current(self, motor_id: int) -> int:
        """Return the present current (signed, in control-table LSB)."""
        if motor_id not in self._motor_states:
            self._initialize_motor_state(motor_id)
        
        # Simulate motor behavior
        self._simulate_motor_behavior()
        
        return int(self._motor_states[motor_id]['current'])
    
    # ============================================================================
    # BAUD RATE AND ID MANAGEMENT
    # ============================================================================
    
    def scan_motors_at_baudrate(self, baudrate: int, scan_range: range = range(0, 253)) -> List[int]:
        """Scan for motors at a specific baud rate."""
        self._verbose_log(f"🔄 Fake scanning at baudrate {baudrate}...")
        
        # Return a random subset of motors for testing
        detected = []
        for motor_id in scan_range:
            if random.random() < 0.1:  # 10% chance of finding a motor
                detected.append(motor_id)
        
        self._verbose_log(f"✅ Fake scan found {len(detected)} motors at {baudrate} baud")
        return detected
    
    def scan_all_baudrates(self, scan_range: range = range(0, 253)) -> Dict[int, int]:
        """Scan for motors at all possible baud rates."""
        self._verbose_log("🔍 Fake scanning for motors at all baud rates...")
        
        detected_motors = {}
        
        for baudrate in SCAN_BAUDRATES:
            detected = self.scan_motors_at_baudrate(baudrate, scan_range)
            for motor_id in detected:
                detected_motors[motor_id] = baudrate
        
        self._verbose_log(f"📊 Fake scan complete: Found {len(detected_motors)} motors total")
        return detected_motors
    
    def change_motor_baudrate(self, motor_id: int, current_baud: int, new_baud: int) -> bool:
        """Change baud rate of a specific motor."""
        if new_baud not in BAUDRATE_MAP:
            self._log(f"❌ Invalid baud rate: {new_baud}. Valid rates: {list(BAUDRATE_MAP.keys())}")
            return False
        
        self._verbose_log(f"✅ Fake motor ID {motor_id}: {current_baud} → {new_baud} baud")
        return True
    
    def change_motors_baudrate(self, motor_baud_map: Dict[int, int], new_baud: int) -> Dict[int, bool]:
        """Change baud rate for multiple motors."""
        if not motor_baud_map:
            self._log(f"❌ No motor IDs provided")
            return {}
        
        results = {}
        for motor_id, current_baud in motor_baud_map.items():
            if current_baud == new_baud:
                results[motor_id] = True
            else:
                results[motor_id] = self.change_motor_baudrate(motor_id, current_baud, new_baud)
        
        return results
    
    def change_motor_id(self, current_id: int, new_id: int, baudrate: int) -> bool:
        """Change the ID of a single motor."""
        if new_id < 0 or new_id > 252:
            self._log(f"❌ Invalid new ID: {new_id}. Must be 0-252")
            return False
        
        self._verbose_log(f"✅ Fake motor ID {current_id} → {new_id}")
        return True
    
    def change_motors_id(self, id_mapping: Dict[int, int], baudrate: int) -> Dict[int, bool]:
        """Change IDs for multiple motors."""
        if not id_mapping:
            self._log(f"❌ No motor ID mappings provided")
            return {}
        
        # Validate all new IDs
        invalid_ids = [new_id for new_id in id_mapping.values() if new_id < 0 or new_id > 252]
        if invalid_ids:
            self._log(f"❌ Invalid new IDs: {invalid_ids}. Must be 0-252")
            return {}
        
        # Check for duplicate new IDs
        new_ids = list(id_mapping.values())
        if len(new_ids) != len(set(new_ids)):
            self._log(f"❌ Duplicate new IDs found. Each motor must have a unique ID.")
            return {}
        
        results = {}
        for current_id, new_id in id_mapping.items():
            if current_id == new_id:
                results[current_id] = True
            else:
                results[current_id] = self.change_motor_id(current_id, new_id, baudrate)
        
        return results
    
    # ============================================================================
    # PORT MANAGEMENT
    # ============================================================================
    
    def close(self):
        """Close the serial port."""
        self._verbose_log("✅ Fake port closed.")
    
    # ============================================================================
    # TESTING UTILITIES
    # ============================================================================
    
    def set_motor_state(self, motor_id: int, position: int = None, velocity: int = None, current: int = None):
        """
        Manually set motor state for testing purposes.
        
        Args:
            motor_id: Motor ID to set state for
            position: Position to set (optional)
            velocity: Velocity to set (optional)
            current: Current to set (optional)
        """
        if motor_id not in self._motor_states:
            self._initialize_motor_state(motor_id)
        
        if position is not None:
            self._motor_states[motor_id]['position'] = position
        if velocity is not None:
            self._motor_states[motor_id]['velocity'] = velocity
        if current is not None:
            self._motor_states[motor_id]['current'] = current
        
        self._verbose_log(f"✅ Fake motor {motor_id} state set: pos={position}, vel={velocity}, cur={current}")
    
    def get_motor_state(self, motor_id: int) -> Dict[str, int]:
        """
        Get the current state of a motor for testing purposes.
        
        Args:
            motor_id: Motor ID to get state for
            
        Returns:
            Dictionary with 'position', 'velocity', 'current'
        """
        if motor_id not in self._motor_states:
            self._initialize_motor_state(motor_id)
        
        return self._motor_states[motor_id].copy()
