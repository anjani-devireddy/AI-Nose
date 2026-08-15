import serial
import csv
import time
import os
from datetime import datetime

# ============================================================
# SETTINGS
# ============================================================

PORT = "COM3"
BAUD = 115200

# Your Wio Terminal sends data at approximately 10 Hz
# 100 ms = 10 readings per second
SAMPLE_INTERVAL_MS = 100

# Default number of readings
DEFAULT_SAMPLES = 100

# Folder for all collected datasets
OUTPUT_FOLDER = "edge_impulse_data"


# ============================================================
# SETUP
# ============================================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print()
print("=" * 55)
print("        AI NOSE - EDGE IMPULSE DATA COLLECTOR")
print("=" * 55)
print()

label = input(
    "Enter label name"
    "(example: clean_air, camphor, coffee): "
).strip()

if not label:
    print("ERROR: Substance name cannot be empty.")
    raise SystemExit


# Ask number of samples
samples_input = input(
    f"Number of readings [{DEFAULT_SAMPLES}]: "
).strip()

if samples_input == "":
    NUM_SAMPLES = DEFAULT_SAMPLES
else:
    try:
        NUM_SAMPLES = int(samples_input)

        if NUM_SAMPLES <= 0:
            raise ValueError

    except ValueError:
        print("ERROR: Enter a positive whole number.")
        raise SystemExit


# ============================================================
# FILE NAME
# ============================================================

recording_time = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

filename = os.path.join(
    OUTPUT_FOLDER,
    f"{label}_{recording_time}.csv"
)


# ============================================================
# CONNECT TO WIO TERMINAL
# ============================================================

print()
print(f"Port       : {PORT}")
print(f"Baud rate  : {BAUD}")
print(f"Substance  : {label}")
print(f"Readings   : {NUM_SAMPLES}")
print(f"Frequency  : 10 Hz")
print(f"Output     : {filename}")
print()

print("IMPORTANT:")
print("1. Close Arduino Serial Monitor.")
print("2. Place the substance in the same position.")
print("3. Keep the sensor setup unchanged.")
print()

input("Press ENTER to start recording...")


try:

    ser = serial.Serial(
        PORT,
        BAUD,
        timeout=1
    )

except serial.SerialException as e:

    print()
    print("ERROR: Could not open the serial port.")
    print(e)
    print()
    print("Make sure:")
    print("- Wio Terminal is connected")
    print("- COM3 is correct")
    print("- Arduino Serial Monitor is closed")

    raise SystemExit


# Give Wio Terminal time to reset
time.sleep(2)

# Remove old data from serial buffer
ser.reset_input_buffer()


# ============================================================
# COUNTDOWN
# ============================================================

print()
print("Starting recording...")

for i in range(3, 0, -1):

    print(f"{i}...")

    time.sleep(1)

print()
print("RECORDING")
print("-" * 55)


# ============================================================
# OPEN CSV
# ============================================================

samples_collected = 0

try:

    with open(
        filename,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        # Edge Impulse-style CSV
        writer.writerow([
            "timestamp",
            "gas1",
            "gas2",
            "gas3",
            "gas4",
            "label"
        ])


        # ====================================================
        # DATA COLLECTION
        # ====================================================

        while samples_collected < NUM_SAMPLES:

            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()


            # Ignore empty lines
            if not line:
                continue


            # Expected Wio output:
            #
            # 353,391,46,390

            parts = line.split(",")


            # We only accept exactly four gas values
            if len(parts) != 4:
                continue


            # Check that all four values are numbers
            try:

                gas1 = float(parts[0])
                gas2 = float(parts[1])
                gas3 = float(parts[2])
                gas4 = float(parts[3])

            except ValueError:

                # Ignore startup messages or other text
                continue


            # Timestamp relative to beginning
            timestamp = (
                samples_collected *
                SAMPLE_INTERVAL_MS
            )


            # Write data
            writer.writerow([
                timestamp,
                gas1,
                gas2,
                gas3,
                gas4,
                label
            ])


            samples_collected += 1


            # Progress
            percentage = (
                samples_collected /
                NUM_SAMPLES
            ) * 100


            print(
                f"\r"
                f"[{samples_collected:4d}/{NUM_SAMPLES}] "
                f"{percentage:6.1f}%  "
                f"gas1={gas1:7.1f}  "
                f"gas2={gas2:7.1f}  "
                f"gas3={gas3:7.1f}  "
                f"gas4={gas4:7.1f}",
                end=""
            )


            # Wait for next 100 ms reading
            time.sleep(
                SAMPLE_INTERVAL_MS / 1000
            )


except KeyboardInterrupt:

    print()
    print()
    print("Recording stopped manually.")


finally:

    ser.close()


# ============================================================
# FINISHED
# ============================================================

print()
print()
print("=" * 55)
print("             RECORDING COMPLETE")
print("=" * 55)

print()
print(f"Substance : {label}")
print(f"Readings  : {samples_collected}")
print(f"File      : {filename}")
print()

if samples_collected == NUM_SAMPLES:

    print("STATUS: SUCCESS")
    print()
    print("The CSV is ready for Edge Impulse.")

else:

    print("STATUS: INCOMPLETE")
    print()
    print(
        f"Only {samples_collected} of "
        f"{NUM_SAMPLES} readings were collected."
    )

print()