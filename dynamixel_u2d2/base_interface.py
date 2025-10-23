"""
Base Interface for Dynamixel motor control.

This module defines the abstract base class that both U2D2Interface and FakeU2D2Interface
inherit from, ensuring a consistent API for hardware and testing implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Literal, Optional

# Motor mode types for type hints
MotorMode = Literal['position', 'current']

class BaseInterface(ABC):
    """
    Abstract base class for Dynamixel motor control interfaces.
    
    This class defines the interface that both hardware (U2D2Interface) and 
    testing (FakeU2D2Interface) implementations must follow.
    """
    
    def __init__(
        self,
        usb_port: str,
        baudrate: int = 4000000,
        motor_ids: Optional[List[int]] = None,
        protocol_version: float = 2.0,
        verbose: bool = False
    ):
        """
        Initialize the interface.
        
        Args:
            usb_port: Serial port (e.g., '/dev/ttyUSB0')
            baudrate: Communication speed (57600, 1000000, etc.)
            motor_ids: List of motor IDs for bulk reads (optional for utility functions)
            protocol_version: Dynamixel protocol version (usually 2.0)
            verbose: Print verbose output (default: False)
        """
        self.usb_port = usb_port
        self.baudrate = baudrate
        self.motor_ids = motor_ids
        self.protocol_version = protocol_version
        self.verbose = verbose
    
    # ============================================================================
    # MOTOR CONFIGURATION
    # ============================================================================
    
    @abstractmethod
    def enable_torque(self, motor_id: int):
        """Enable torque on the specified motor."""
        pass
    
    @abstractmethod
    def disable_torque(self, motor_id: int):
        """Disable torque on the specified motor."""
        pass
    
    @abstractmethod
    def set_motor_mode(self, motor_id: int, mode: MotorMode):
        """
        Set the operating mode of a single motor using string parameter.
        
        Args:
            motor_id: Motor ID
            mode: Operating mode string - one of:
                - 'position': Position control mode
                - 'current': Current control mode  
        """
        pass
    
    @abstractmethod
    def set_position_p_gain(self, motor_id: int, p_gain: int):
        """Set the Position P Gain for a single motor."""
        pass
    
    @abstractmethod
    def set_position_i_gain(self, motor_id: int, i_gain: int):
        """Set the Position I Gain for a single motor."""
        pass
    
    @abstractmethod
    def set_position_d_gain(self, motor_id: int, d_gain: int):
        """Set the Position D Gain for a single motor."""
        pass
    
    # ============================================================================
    # SYNC BASE OPERATIONS
    # ============================================================================
    
    @abstractmethod
    def init_group_sync_read(self, motor_ids: List[int]):
        """Initialize group sync read parameters for maximum efficiency using contiguous read."""
        pass
    
    @abstractmethod
    def sync_read_state(self) -> Tuple[List[int], List[int], List[int]]:
        """Sync read the full state (position, velocity, current) of all motors."""
        pass
    
    # ============================================================================
    # SYNC WRITE OPERATIONS
    # ============================================================================
    
    @abstractmethod
    def sync_write_positions(self, positions: List[int]):
        """
        Sync write position commands to all configured motors.
        
        Args:
            positions: List of position values (must match self.motor_ids length)
        """
        pass
    
    @abstractmethod
    def sync_write_currents(self, currents: List[int]):
        """
        Sync write current commands to all configured motors.
        
        Args:
            currents: List of current values (must match self.motor_ids length)
        """
        pass
    
    # ============================================================================
    # SYNC SPECIFIC STATE READS
    # ============================================================================
    
    @abstractmethod
    def init_specific_group_sync_read(self, state: str):
        """Initialize group sync read parameters for specific states."""
        pass
    
    @abstractmethod
    def sync_read_specific(self, state: str) -> List[int]:
        """
        Sync read only specific state for all configured motors.
        More efficient than reading all states when only one state is needed.
        
        Args:
            state: State to read ('position', 'velocity', 'current')
        
        Returns:
            List of state values in same order as self.motor_ids
        """
        pass
    
    # ============================================================================
    # BULK BASE OPERATIONS
    # ============================================================================
    
    @abstractmethod
    def bulk_read(self, read_params: List[Tuple[int, int, int]]) -> Dict:
        """
        Perform bulk read operation for multiple motors.
        
        Args:
            read_params: List of tuples (motor_id, address, length)
        
        Returns:
            Dict with keys (motor_id, address) and byte values
        """
        pass
    
    @abstractmethod
    def bulk_write(self, write_params: List[Tuple[int, int, bytes]]):
        """
        Perform bulk write operation for multiple motors.
        
        Args:
            write_params: List of tuples (motor_id, address, data_bytes)
        """
        pass
    
    # ============================================================================
    # BULK HIGH-LEVEL OPERATIONS
    # ============================================================================
    
    @abstractmethod
    def bulk_write_positions(self, motor_ids: List[int], positions: List[int]):
        """
        Bulk write position commands to multiple motors.
        
        Args:
            motor_ids: List of motor IDs
            positions: List of position values (must match motor_ids length)
        """
        pass
    
    @abstractmethod
    def bulk_write_currents(self, motor_ids: List[int], currents: List[int]):
        """
        Bulk write current commands to multiple motors.
        
        Args:
            motor_ids: List of motor IDs
            currents: List of current values (must match motor_ids length)
        """
        pass
    
    @abstractmethod
    def bulk_read_positions(self, motor_ids: List[int]) -> Dict[int, int]:
        """
        Bulk read positions from multiple motors.
        
        Args:
            motor_ids: List of motor IDs to read
            
        Returns:
            Dict mapping motor_id to position value
        """
        pass
    
    @abstractmethod
    def bulk_read_velocities(self, motor_ids: List[int]) -> Dict[int, int]:
        """
        Bulk read velocities from multiple motors.
        
        Args:
            motor_ids: List of motor IDs to read
            
        Returns:
            Dict mapping motor_id to velocity value
        """
        pass
    
    @abstractmethod
    def bulk_read_currents(self, motor_ids: List[int]) -> Dict[int, int]:
        """
        Bulk read currents from multiple motors.
        
        Args:
            motor_ids: List of motor IDs to read
            
        Returns:
            Dict mapping motor_id to current value
        """
        pass
    
    @abstractmethod
    def bulk_read_states(self, motor_ids: List[int]) -> Dict[int, Dict[str, int]]:
        """
        Bulk read all states (position, velocity, current) from multiple motors.
        Optimized to use a single bulk read operation.
        
        Args:
            motor_ids: List of motor IDs to read
            
        Returns:
            Dict mapping motor_id to state dict with 'position', 'velocity', 'current'
        """
        pass
    
    # ============================================================================
    # INDIVIDUAL MOTOR OPERATIONS
    # ============================================================================
    
    @abstractmethod
    def set_goal_position(self, motor_id: int, goal: int):
        """Set goal position for a single motor."""
        pass
    
    @abstractmethod
    def set_goal_current(self, motor_id: int, current: int):
        """Set the goal current for a single motor."""
        pass
    
    @abstractmethod
    def set_velocity_limit(self, motor_id: int, velocity_limit: int):
        """Set the profile velocity limit for a single motor."""
        pass
    
    @abstractmethod
    def set_current_limit(self, motor_id: int, limit_mA: int):
        """Set the current limit for a single motor."""
        pass
    
    @abstractmethod
    def get_position(self, motor_id: int) -> int:
        """Return the current position of a motor."""
        pass
    
    @abstractmethod
    def get_velocity(self, motor_id: int) -> int:
        """Return the current velocity of the motor."""
        pass
    
    @abstractmethod
    def get_current(self, motor_id: int) -> int:
        """Return the present current (signed, in control-table LSB)."""
        pass
    
    # ============================================================================
    # BAUD RATE AND ID MANAGEMENT
    # ============================================================================
    
    @abstractmethod
    def scan_motors_at_baudrate(self, baudrate: int, scan_range: range = range(0, 253)) -> List[int]:
        """
        Scan for motors at a specific baud rate.
        
        Args:
            baudrate: Baud rate to scan at
            scan_range: Range of motor IDs to scan (default: 0-252)
            
        Returns:
            List of detected motor IDs
        """
        pass
    
    @abstractmethod
    def scan_all_baudrates(self, scan_range: range = range(0, 253)) -> Dict[int, int]:
        """
        Scan for motors at all possible baud rates.
        
        Args:
            scan_range: Range of motor IDs to scan (default: 0-252)
            
        Returns:
            Dictionary mapping motor_id to baudrate
        """
        pass
    
    @abstractmethod
    def change_motor_baudrate(self, motor_id: int, current_baud: int, new_baud: int) -> bool:
        """
        Change baud rate of a specific motor.
        
        Args:
            motor_id: Motor ID to change
            current_baud: Current baud rate of the motor
            new_baud: New baud rate to set
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def change_motors_baudrate(self, motor_baud_map: Dict[int, int], new_baud: int) -> Dict[int, bool]:
        """
        Change baud rate for multiple motors.
        
        Args:
            motor_baud_map: Dictionary mapping motor_id to current baud rate
            new_baud: New baud rate to set
            
        Returns:
            Dictionary mapping motor_id to success status
        """
        pass
    
    @abstractmethod
    def change_motor_id(self, current_id: int, new_id: int, baudrate: int) -> bool:
        """
        Change the ID of a single motor.
        
        Args:
            current_id: Current motor ID
            new_id: New motor ID to set
            baudrate: Baud rate to use for communication
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def change_motors_id(self, id_mapping: Dict[int, int], baudrate: int) -> Dict[int, bool]:
        """
        Change IDs for multiple motors.
        
        Args:
            id_mapping: Dictionary mapping current_id to new_id
            baudrate: Baud rate to use for communication
            
        Returns:
            Dictionary mapping current_id to success status
        """
        pass
    
    # ============================================================================
    # PORT MANAGEMENT
    # ============================================================================
    
    @abstractmethod
    def close(self):
        """Close the serial port."""
        pass
    
    # ============================================================================
    # UTILS
    # ============================================================================
    
    def _log(self, msg: str):
        """Log a message."""
        print(f"[BaseInterface] {msg}")
    
    def _verbose_log(self, msg: str):
        """Log a message if verbose is True."""
        if self.verbose:
            self._log(msg)
