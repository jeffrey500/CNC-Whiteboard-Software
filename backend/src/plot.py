import time
import serial

def send_gcode(gcode_file: str, port: str):
    s = serial.Serial(port, 115200)
    s.write(b"\r\n\r\n")
    time.sleep(2)  # Wait for Arduino to reboot/initialize
    s.flushInput()  # Clear startup messages

    with open("./temp/commands.gcode", "r") as file:

        print(file)

        for i in range(10,len(file)):
            # 1. Send the command
            print(f"Sending: {file[i]}")
            s.write((file[i] + '\n').encode())  # Send command + newline

            # 2. WAIT for the 'ok' response
            # This blocks the loop until Arduino is ready for the next line
            response = s.readline().decode().strip()
            if response == 'ok':
                print("Arduino accepted command.")
            else:
                print(f"Error: {response}")

        s.close()