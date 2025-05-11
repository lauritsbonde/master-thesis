import serial
import serial.tools.list_ports
import time

def list_ports():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial devices found.")
        exit(1)

    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} - {port.description}")

    return ports

def select_port(ports):
    while True:
        try:
            index = int(input("Enter the number of the port to connect to: "))
            if 0 <= index < len(ports):
                return ports[index].device
            else:
                print("Invalid number. Try again.")
        except ValueError:
            print("Please enter a valid number.")

ports = list_ports()
selected_port = select_port(ports)

print(f"\nConnecting to {selected_port}...\n")
ser = serial.Serial(selected_port, 9600)
time.sleep(2)  # Give the device time to reset

filename = "uwb_log.csv"
with open(filename, "w") as f:
    print(f"Logging to {filename}. Press Ctrl+C to stop.")
    # Write headers to file
    f.write("Timestamp (s),Raw-A-0 (m),Raw-A-1 (m),KF-A-0 (m),KF-A-1 (m),MiddlePoint (m),Expected (m), Method, Mode \n")
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            print(line)
            if line.startswith("DataEntry - "):
                # Extract the relevant part of the line
                data = line.split(" - ")[1]
                # Write to file
                f.write(data + "\n")
        except KeyboardInterrupt:
            print("\nLogging stopped by user.")
            break
