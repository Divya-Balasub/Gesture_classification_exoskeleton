import serial
import csv
import matplotlib.pyplot as plt
import keyboard
import joblib

from matplotlib.animation import FuncAnimation
import random
import os
import serialNO
import data
import video_audio
import logging
import multiprocessing
import time
import numpy
import tslearn
from tslearn.neighbors import KNeighborsTimeSeriesClassifier
import matplotlib.pyplot as plt

from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn import metrics
import time
import numpy as np

# Configure logging settings
logging.basicConfig(level=logging.DEBUG, filename='../app.log', filemode='a', format='%(message)s')
logging.getLogger('matplotlib').setLevel(logging.CRITICAL)

ser = serial.Serial(data.port, data.baudrate)

os.makedirs(data.parent_folder_path, exist_ok=True)

# Initialize additional_column_value before the update function
additional_column_value = 0

# Initialize serial_number
serial_number = serialNO.read_serialNO()

# Dictionary to store data for each serial number
data_by_serial = {}

# Dictionary to keep track of the counter for each folder
folder_counters = {folder: 1 for folder in data.folder_mapping.values()}

# Variables to keep track of the current folder and file
current_folder = None
current_file = None

fig, axs = plt.subplots(9, 1, figsize=(9, 14))
x_data = [[] for _ in range(9)]  # List to store data for each axis
y_data = [[] for _ in range(9)]  # List to store values for each axis
lines = []



for i in range(9):
    axs[i].set_xlabel('Time')
    axs[i].set_ylabel(f'Value {i + 1}')

    # Create a line object for each axis
    line, = axs[i].plot([], [])
    lines.append(line)


# Mapping of key codes for the German keyboard layout
key_mapping = {
    '1': 18,
    '2': 19,
    '3': 20,
    '4': 21,
    '5': 22,
    '6': 23
}

def detach_motor():
    ser.write(b'd')  # Send 'd' to detach the motor

def attach_motor():
    ser.write(b'a')  # Send 'd' to detach the motor

def create_new_file():
    global current_folder
    global current_file

    # Get the folder name based on the current random number
    current_folder = data.folder_mapping.get(additional_column_value, 'default')
    folder_path = os.path.join(data.parent_folder_path, current_folder)
    os.makedirs(folder_path, exist_ok=True)

    # Find the maximum file counter for existing files in the folder
    file_counter = 1
    for filename in os.listdir(folder_path):
        if filename.startswith(current_folder):
            file_counter += 1

    # Generate the CSV file name based on the folder name and the file counter
    current_file = f"{current_folder}.{data.participant_id}{file_counter:03d}.csv"
    if not (current_file.startswith(data.binFile) or current_file.startswith(data.defaultFile)):
        print(current_file + "\n")
        logging.info(current_file + "\n")

    # Create and write the header to the CSV file
    with open(os.path.join(folder_path, current_file), 'w', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(data.header)


def update(frame):
    global additional_column_value  # Declare additional_column_value as a global variable
    global serial_number
    global current_folder
    global current_file
    global random_number

    if ser.in_waiting > 0:
        readings = ser.readline().decode().strip()
        values = readings.split(',')  # Split the string into individual values

        # Convert the values to floats (if needed)
        values = [float(val) for val in values]

        # if keyboard.is_pressed(18):
        #     random_number = random.randint(1, 6)
        #     time.sleep(0.2)
        #     video_process = multiprocessing.Process(target=video_audio.play_video, args=(random_number,))
        #     video_process.start()
        #
        #     #video_audio.play_video((random_number))
        #
        #     #video_process.join()
        #     # additional_column_value = random_number
        #     # serial_number += 1
        #     # logging.info("Serial Number : " + str(serial_number) + "   File: " + str(additional_column_value))
        #     # seri
        #     alNO.write_serialNO(serial_number)
        #     # create_new_file()

        if keyboard.is_pressed(45): #n
            additional_column_value = 5   #gesture number






            serial_number += 1
            logging.info("Serial Number : " + str(serial_number) + "   File: " + str(additional_column_value))
            serialNO.write_serialNO(serial_number)
            create_new_file()
            time.sleep(0.2)

        elif keyboard.is_pressed(49):
            additional_column_value = 0  #default 0
            logging.info("Serial Number : " + str(serial_number) + "   File: " + str(additional_column_value))
            create_new_file()
            time.sleep(0.2)
        elif keyboard.is_pressed(19):
            additional_column_value = -1
        elif keyboard.is_pressed(20):
            participant_id = 100
            serialNO.delete_latest_readings(serial_number, additional_column_value)
            additional_column_value = 10
            create_new_file()
            # Call the function to delete the latest readings

        if keyboard.is_pressed(47):  # . dot 47
            print("Detaching the motor...")
            detach_motor()
        if keyboard.is_pressed(44):  # underscore -
            print("attaching the motor...")
            attach_motor()


        values.insert(0, additional_column_value)
        values.append(data.participant_id)
        values.append(serial_number)

        # sliding_window = values[-15:]
        #
        # # Print the length of the sliding window
        # print(f"Size of sliding window: {len(sliding_window)}")
        #
        # loaded_rf_classifier = joblib.load('random_forest_model.joblib')
        # # predictions = loaded_rf_classifier.predict(sliding_window)


        # Store the data in the dictionary based on the serial number
        if serial_number not in data_by_serial:
            data_by_serial[serial_number] = []
        data_by_serial[serial_number].append(values)

        # Write the row to the current CSV file
        if current_folder and current_file:
            file_path = os.path.join(data.parent_folder_path, current_folder, current_file)
            with open(file_path, 'a', newline='', encoding='UTF8') as f:
                writer = csv.writer(f)
                writer.writerow(values)

        for i in range(9):  # Update data for each axis
            x_data[i].append(frame)
            y_data[i].append(values[i])

            # Clear the previous plot
            axs[i].cla()

            # Plot the data
            axs[i].plot(x_data[i], y_data[i])

            # Set the y-axis limits to -5 and 5
            if i in [ 2, 3,4,5,6]:
                axs[i].set_ylim(0, 4500)
            else:
                axs[i].set_ylim(-6, 6)

if __name__ == '__main__':

    ani = FuncAnimation(fig, update, blit=False)

    # video_process = multiprocessing.Process(target=video_audio.play_video, args=(2,))
    # video_process.start()
    plt.show()




