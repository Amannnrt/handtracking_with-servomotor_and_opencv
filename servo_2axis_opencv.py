import network
import socket
from machine import Pin, PWM
import time

# Wi-Fi connection
ssid = ''     #your ssid
password = '' #your passowrd

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

# Open socket
addr = socket.getaddrinfo('0.0.0.0', 8769)[0][-1]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(addr)
print('listening on', addr)

# Set up PWM for servo control
servo_x_pin = Pin(15)  # GP15 for X axis
servo_y_pin = Pin(6)  # GP14 for Y axis
pwm_x = PWM(servo_x_pin)
pwm_y = PWM(servo_y_pin)
pwm_x.freq(50)
pwm_y.freq(50)

def set_servo_angle(servo_pwm, angle):
    # Adjust duty cycle mapping as needed
    duty = int(angle / 180 * 65535 / 20 + 4000)  # Example mapping
    servo_pwm.duty_u16(duty)

while True:
    data, addr = s.recvfrom(1024)
    print(f"Received data: {data} from {addr}")  # Debugging print
    try:
        center_x, center_y, frame_width, frame_height = map(int, data.decode().split(','))
        
        # Calculate servo angles (0-180 degrees)
        angle_x = (center_x / frame_width) * 180 +10
        angle_y = (center_y / frame_height) * 180 +20
        print(f"Angle X: {angle_x}, Angle Y: {angle_y}")

        # Set servo positions
        set_servo_angle(pwm_x, angle_x)
        set_servo_angle(pwm_y, angle_y)

    except ValueError as e:
        print("Error parsing data:", e)

    time.sleep(0.01)  # Small delay to avoid overwhelming the Pico W
