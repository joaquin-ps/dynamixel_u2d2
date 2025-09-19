#!/bin/bash

# Checking if the port is connected:
if [ ! -c /dev/ttyUSB0 ]; then
    echo "❌ Port /dev/ttyUSB0 is not connected"
    return 1
fi

# Checking the latency timer and letting user know the value:
latency_timer=$(cat /sys/bus/usb-serial/devices/ttyUSB0/latency_timer)
echo "The latency timer is set to $latency_timer"

# Ask user what to change it to, if blank it sets to 2:
while true; do
    read -p "What to change it to? (default is 2): " new_latency_timer
    if [ -z "$new_latency_timer" ]; then
        new_latency_timer=2
        break
    elif [[ "$new_latency_timer" =~ ^[0-9]+$ ]]; then
        break
    else
        echo "❌ Please enter a valid integer"
    fi
done

# Set the latency timer to the specified value for the USB port
echo "Setting latency timer to $new_latency_timer for the USB port"
echo $new_latency_timer | sudo tee /sys/bus/usb-serial/devices/ttyUSB0/latency_timer

# Checking the latency timer again and letting user know the value:
latency_timer=$(cat /sys/bus/usb-serial/devices/ttyUSB0/latency_timer)
echo "The latency timer is set to $latency_timer"

echo "Done!"