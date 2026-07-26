import time
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
            clean_line = line.strip()

            if ';' in clean_line:
                clean_line = clean_line.split(';')[0].strip()
            if '(' in clean_line:
                clean_line = clean_line.split('(')[0].strip()

            # skip empty lines or G-code comments (which start with ; or () )
            if not clean_line:
                continue

            # send the command
            print(f"Sending: {clean_line}")
            s.write((clean_line + '\n').encode())  # send command + newline

            # wait for the 'ok' response
            # block the loop until Arduino is ready for the next line
            while True:
                response = s.readline().decode('utf-8', errors='replace').strip()

                if response == 'ok':
                    print("Arduino accepted command.")
                    break
                elif response.startswith('error'):
                    print(f"Response: {response}")
                    break
                elif response:
                    print(f"Response: {response}")

        # close the serial connection
        s.close()
        print("Plotting finished. Connection closed.")