import serial
import csv
import time
import os
import re
from datetime import datetime

# ============================================================
# SETTINGS
# ============================================================

PORT = "COM3"
BAUD_RATE = 115200

# Your Wio sensor outputs approximately 10 samples/sec
SAMPLE_INTERVAL_MS = 100

# Default number of sensor readings
DEFAULT_SAMPLES = 100

# Folder for collected CSV files
OUTPUT_FOLDER = "edge_impulse_data"


# ============================================================
# CLEAN FILE/LABEL NAME
# ============================================================

def clean_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_-]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
# ASK FOR LABEL
# ============================================================

print()
print("=" * 60)
print("        AI NOSE - EDGE IMPULSE DATA COLLECTOR")
print("=" * 60)
print()

raw_label = input(
    "Enter substance name "
    "(example: clean_air, camphor, coffee): "
).strip()

label = clean_name(raw_label)

if not label:
    print("ERROR: Invalid substance name.")
    raise SystemExit(1)


# ============================================================
# ASK FOR SAMPLE COUNT
# ============================================================

sample_input = input(
    f"Number of readings [{DEFAULT_SAMPLES}]: "
).strip()

if sample_input == "":
    num_samples = DEFAULT_SAMPLES
else:
    try:
        num_samples = int(sample_input)

        if num_samples <= 0:
            raise ValueError

    except ValueError:
        print("ERROR: Enter a positive whole number.")
        raise SystemExit(1)


# ============================================================
# FILE NAME
# ============================================================

file_timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

filename = os.path.join(
    OUTPUT_FOLDER,
    f"{label}_{file_timestamp}.csv"
)


# ============================================================
# INFORMATION
# ============================================================

print()
print(f"Port        : {PORT}")
print(f"Baud rate   : {BAUD_RATE}")
print(f"Label       : {label}")
print(f"Readings    : {num_samples}")
print(f"Frequency   : 10 Hz")
print(f"Output file : {filename}")
print()

print("IMPORTANT")
print("1. Close Arduino Serial Monitor.")
print("2. Keep the sensor position unchanged.")
print("3. Keep the sample at the same distance.")
print("4. Use the same airflow/setup for every class.")
print()

input("Press ENTER to start recording...")


# ============================================================
# OPEN SERIAL PORT
# ============================================================

try:
    ser = serial.Serial(
        PORT,
        BAUD_RATE,
        timeout=2
    )

except serial.SerialException as error:
    print()
    print("ERROR: Could not open serial port.")
    print(error)
    print()
    print("Check the current COM port with:")
    print("python -m serial.tools.list_ports")
    raise SystemExit(1)


# Opening the serial port can reset the Wio Terminal.
time.sleep(3)

# Remove old serial data.
ser.reset_input_buffer()


# ============================================================
# COUNTDOWN
# ============================================================

print()
print("Starting in...")
print()

for number in range(3, 0, -1):
    print(number)
    time.sleep(1)

print()
print("RECORDING")
print("-" * 60)


# ============================================================
# DATA COLLECTION
# ============================================================

samples_collected = 0

try:

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.writer(csv_file)

        # IMPORTANT:
        # NO text label column.
        # Edge Impulse expects numeric sensor columns.
        writer.writerow([
            "timestamp",
            "gas1",
            "gas2",
            "gas3",
            "gas4"
        ])

        while samples_collected < num_samples:

            # Read one line from Wio Terminal
            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            # Expected:
            # 359,386,50,386

            parts = line.split(",")

            # Ignore startup messages / prediction messages
            if len(parts) != 4:
                continue

            try:
                gas1 = float(parts[0])
                gas2 = float(parts[1])
                gas3 = float(parts[2])
                gas4 = float(parts[3])

            except ValueError:
                continue

            # Timestamp in milliseconds
            timestamp_ms = (
                samples_collected *
                SAMPLE_INTERVAL_MS
            )

            # Write ONLY numeric values
            writer.writerow([
                timestamp_ms,
                gas1,
                gas2,
                gas3,
                gas4
            ])

            samples_collected += 1

            percent = (
                samples_collected /
                num_samples
            ) * 100

            print(
                f"\r"
                f"[{samples_collected:4d}/{num_samples}] "
                f"{percent:6.1f}%  "
                f"gas1={gas1:.0f}  "
                f"gas2={gas2:.0f}  "
                f"gas3={gas3:.0f}  "
                f"gas4={gas4:.0f}",
                end="",
                flush=True
            )

except KeyboardInterrupt:

    print()
    print()
    print("Recording stopped manually.")

finally:
    ser.close()


# ============================================================
# COMPLETE
# ============================================================

print()
print()
print("=" * 60)
print("                RECORDING COMPLETE")
print("=" * 60)
print()

print(f"Label      : {label}")
print(f"Readings   : {samples_collected}")
print(f"CSV file   : {filename}")
print()

if samples_collected == num_samples:
    print("STATUS: SUCCESS")
    print("CSV is ready for Edge Impulse.")
else:
    print("STATUS: INCOMPLETE")

print()
