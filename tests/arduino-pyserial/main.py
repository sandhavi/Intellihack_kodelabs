import serial
import time

# Replace 'COM5' with your Arduino's serial port
ser = serial.Serial('COM5', 9600, timeout=1)
time.sleep(2) # Give some time for the connection to establish


# def send_data(angle1, angle2, speed):
def send_data(angle1, angle2):
    # data = f"{angle1},{angle2},{speed}\n"
    data = f"{angle1},{angle2}\n"
    ser.write(data.encode())
    print(f"Sent: {data.strip()}")

try:
    # Example values to send
    angle1 = 40  # Move 10 degrees from center (90 + 10 = 100 degrees on the servo)
    angle2 = 40 # Move -10 degrees from center (90 - 10 = 80 degrees on the servo)
    # speed = 0.5  # Speed from 0.0 to 1.0

    # send_data(angle1, angle2, speed)
    send_data(angle1, angle2)
except KeyboardInterrupt:
    print("Program interrupted")

ser.close()
