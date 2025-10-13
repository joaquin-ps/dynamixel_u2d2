"""
Simple U2D2 Port Scanner and Latency Timer Setter

Scans for U2D2 ports and sets the latency timer to improve performance.

Usage:
    python3 u2d2_port_timer.py [--latency-timer LATENCY]
    dynamixel-port [--latency-timer LATENCY]
    
Examples:
    python3 u2d2_port_timer.py                       # Scan and display ports
    python3 u2d2_port_timer.py --latency-timer 2    # Set to 2ms
    python3 u2d2_port_timer.py --latency-timer 1    # Set to 1ms
    python3 u2d2_port_timer.py --latency-timer 4    # Set to 4ms
    dynamixel-port                                    # Scan and display ports
    dynamixel-port --latency-timer 2                 # Using console command
"""

import argparse
import os
import glob
import subprocess
import stat
import sys
from pathlib import Path

def find_u2d2_ports():
    """Find available U2D2 ports."""
    ports = []
    for pattern in ['/dev/ttyUSB*', '/dev/ttyACM*']:
        ports.extend(glob.glob(pattern))
    
    # Filter to only character devices
    u2d2_ports = []
    for port in ports:
        if os.path.exists(port) and stat.S_ISCHR(os.stat(port).st_mode):
            u2d2_ports.append(port)
    
    return sorted(u2d2_ports)

def get_latency_timer(port):
    """Get current latency timer for a port."""
    if not port.startswith('/dev/ttyUSB'):
        return None
    
    latency_path = f"/sys/bus/usb-serial/devices/{os.path.basename(port)}/latency_timer"
    try:
        with open(latency_path, 'r') as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return None

def set_latency_timer(port, latency):
    """Set latency timer for a port."""
    if not port.startswith('/dev/ttyUSB'):
        print(f"⚠️  {port}: Latency timer only available for /dev/ttyUSB* ports")
        return False
    
    latency_path = f"/sys/bus/usb-serial/devices/{os.path.basename(port)}/latency_timer"
    
    if not os.path.exists(latency_path):
        print(f"❌ {port}: Latency timer path not found")
        return False
    
    try:
        result = subprocess.run(
            ['sudo', 'tee', latency_path],
            input=str(latency),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {port}: Set to {latency}ms")
            return True
        else:
            print(f"❌ {port}: Failed to set latency timer")
            return False
    except Exception as e:
        print(f"❌ {port}: Error - {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="U2D2 Port Scanner and Latency Timer Setter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --latency-timer 2    # Set to 2ms
  %(prog)s --latency-timer 1    # Set to 1ms
  %(prog)s --latency-timer 4    # Set to 4ms
        """
    )
    
    parser.add_argument(
        '--latency-timer',
        type=int,
        help='Latency timer value in milliseconds (must be positive integer). If not provided, only scans and displays ports.'
    )
    
    args = parser.parse_args()
    
    # Check if latency timer is provided
    if args.latency_timer is not None:
        # Validate latency
        if args.latency_timer < 1:
            print("❌ Latency timer must be a positive integer")
            sys.exit(1)
        latency = args.latency_timer
        print(f"🔍 Scanning for U2D2 ports...")
        print(f"🎯 Target latency: {latency}ms")
        print()
    else:
        # Just scan and display ports
        print(f"🔍 Scanning for U2D2 ports...")
        print()
    
    # Find ports
    ports = find_u2d2_ports()
    
    if not ports:
        print("❌ No U2D2 ports found")
        print("💡 Make sure U2D2 devices are connected and powered on")
        sys.exit(1)
    
    print(f"Found {len(ports)} U2D2 port(s):")
    
    if args.latency_timer is None:
        # Scan-only mode - just display ports
        for port in ports:
            current = get_latency_timer(port)
            if current is not None:
                print(f"  {port}: {current}ms")
            else:
                print(f"  {port}: N/A (latency timer not available)")
        print()
        print("💡 Use --latency-timer to configure port latency")
        return
    
    # Configure mode - proceed with latency timer setting
    ports_to_change = []
    for port in ports:
        current = get_latency_timer(port)
        if current is not None:
            status = "✅" if current == latency else "⚠️"
            print(f"  {port}: {current}ms {status}")
            if current != latency:
                ports_to_change.append(port)
        else:
            print(f"  {port}: N/A")
    
    if not ports_to_change:
        print("\n✅ All ports already configured correctly!")
        return
    
    print(f"\n⚠️  {len(ports_to_change)} port(s) need to be changed to {latency}ms")
    print("This requires sudo privileges.")
    
    # Ask for confirmation
    while True:
        response = input(f"\nProceed with changing latency timer to {latency}ms? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            break
        elif response in ['n', 'no']:
            print("❌ Cancelled by user")
            return
        else:
            print("Please enter 'y' or 'n'")
    
    print()
    
    # Configure ports
    success_count = 0
    for port in ports_to_change:
        if set_latency_timer(port, latency):
            success_count += 1
    
    # Show status for ports that didn't need changes
    for port in ports:
        if port not in ports_to_change:
            current = get_latency_timer(port)
            if current == latency:
                print(f"✅ {port}: Already set to {latency}ms")
                success_count += 1
            else:
                print(f"⚠️  {port}: Cannot set latency timer")
    
    print()
    print(f"📊 Configured {success_count}/{len(ports)} ports successfully")

if __name__ == "__main__":
    main()
