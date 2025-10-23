"""
Dynamixel U2D2 Interface Package

A clean, high-level interface for controlling Dynamixel motors through the U2D2 
communication bridge, with support for both individual motor operations and 
efficient bulk operations.

Main Classes:
    U2D2Interface: Main interface class for motor control

Example:
    from dynamixel_u2d2 import U2D2Interface
    
    u2d2 = U2D2Interface('/dev/ttyUSB0')
    u2d2.set_motor_mode(11, 'position')
    u2d2.set_goal_position(11, 2048)
    u2d2.close()
"""

from .u2d2_interface import U2D2Interface
from .fake_u2d2_interface import FakeU2D2Interface

__version__ = "1.0.0"
__author__ = "Finger Aloha Team"
__email__ = "jbp2157@columbia.edu"

__all__ = [
    "U2D2Interface",
    "FakeU2D2Interface",
]
