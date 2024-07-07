# def send_data(angle1, angle2, speed):
def send_data(ser, relativeHorizontalAngle, relativeVerticalAngle):
    # data = f"{relativeHorizontalAngle},{relativeVerticalAngle},{speed}\n"
    data = f"{relativeHorizontalAngle},{relativeVerticalAngle}\n"
    ser.write(data.encode())
    # print(f"Sent: {data.strip()}")
