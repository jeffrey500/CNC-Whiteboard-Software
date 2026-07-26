import time
from pathlib import Path

import serial


def send_gcode(gcode_file: str, port: str):
    # serial connection
    s = serial.Serial(port, 115200)

    # initialize board
    s.write(b"\r\n\r\n")
    time.sleep(2)  # wait for Arduino to reboot/initialize
    s.flushInput()  # clear startup messages

    # open gcode file
    with (open(gcode_file, "r") as file):

        print("opened ", file)

        for line in file:
            # skip empty lines or G-code comments (which start with ; or () )
            if not line or line.startswith(';') or line.startswith('('):
                continue

            # send the command
            print(f"Sending: {line}")
            s.write((line + '\n').encode())  # send command + newline

            # wait for the 'ok' response
            # block the loop until Arduino is ready for the next line
            response = s.readline().decode('utf-8', errors='replace').strip()

            if response == 'ok':
                print("Arduino accepted command.")
            else:
                print(f"Response: {response}")

        # close the serial connection
        s.close()
        print("Plotting finished. Connection closed.")

# filepath = Path(__file__).parent.parent / "data" / "image_gcode_output" / "test3.gcode"
# send_gcode(str(filepath), "/dev/cu.usbserial-110")
