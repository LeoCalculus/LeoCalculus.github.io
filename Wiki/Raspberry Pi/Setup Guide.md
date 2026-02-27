# Raspberry Pi Setup Guide

A comprehensive guide to setting up your Raspberry Pi for development projects.

## Initial Setup

1. Download Raspberry Pi OS from the [official website](https://www.raspberrypi.com/software/)
2. Flash the image to an SD card using Raspberry Pi Imager
3. Insert the SD card and power on

## Enable SSH

Create an empty file named `ssh` in the boot partition to enable headless access:

```bash
touch /Volumes/boot/ssh
```

Then connect via SSH:

```bash
ssh pi@raspberrypi.local
```

> [!warning] Security
> Change the default password immediately after first login using `passwd`.

## GPIO Pinout

The Raspberry Pi has a 40-pin GPIO header. All GPIO pins operate at:

$$V_{logic} = 3.3\text{V}$$

> [!important] Important
> Never connect 5V signals directly to GPIO pins! Use a level shifter or voltage divider.

The voltage divider formula for level shifting:

$$V_{out} = V_{in} \times \frac{R_2}{R_1 + R_2}$$

For example, to shift 5V down to 3.3V with $R_2 = 2.2k\Omega$:

$R_1 = R_2 \left(\frac{V_{in}}{V_{out}} - 1\right) = 2.2k \times \left(\frac{5}{3.3} - 1\right) \approx 1.13k\Omega$

## Python GPIO Example

A simple LED blink script using the RPi.GPIO library:

```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

try:
    while True:
        GPIO.output(18, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(18, GPIO.LOW)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
```

> [!tip] Tip
> Consider using `gpiozero` for a more Pythonic API: `from gpiozero import LED`.

## I2C Configuration

Enable I2C via `raspi-config`:

```bash
sudo raspi-config
# Navigate to: Interface Options -> I2C -> Enable
```

Scan for connected I2C devices:

```bash
sudo i2cdetect -y 1
```

The I2C clock speed can be adjusted. The default is $f_{SCL} = 100\text{kHz}$ (standard mode), but you can set it to $400\text{kHz}$ (fast mode) by editing `/boot/config.txt`.

## Useful Commands

| Command | Description |
|---------|-------------|
| `vcgencmd measure_temp` | Check CPU temperature |
| `df -h` | Check disk usage |
| `free -m` | Check memory usage |
| `htop` | Process monitor |
| `pinout` | Display GPIO pinout diagram |

> [!note] Performance
> For CPU-intensive tasks, ensure adequate cooling. The Pi will ==thermal throttle== at $85°C$.
