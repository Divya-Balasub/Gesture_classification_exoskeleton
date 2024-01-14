import os
import csv
import data
import logging

def read_serialNO():
    try:
        with open(data.file_path, 'r') as file:
            serial_number_str = file.read().strip()  # Read the data as a string and remove leading/trailing whitespace
            serial_number = int(serial_number_str)
            return serial_number
    except FileNotFoundError:
        print(f"File '{data.file_path}' not found.")
    except IOError:
        print(f"Error reading from the file '{data.file_path}'.")

def write_serialNO(serial_number):
    try:
        with open(data.file_path, 'w') as file:
            file.write(str(serial_number))
    except FileNotFoundError:
        print(f"File '{data.file_path}' not found.")
    except IOError:
        print(f"Error reading from or writing to the file '{data.file_path}'.")

def delete_latest_readings(serial_number, additional_column_value):
    deleted = False
    deleted_files = set()  # Use a set to keep track of deleted files

    logging.info("Deleting...")
    #print("Deleting...", end="")
    if serial_number > 0:
        folder_name = data.folder_mapping.get(additional_column_value, 'default')

        folder_path = os.path.join(data.parent_folder_path, folder_name)
        file_mapping = os.listdir(folder_path)

        for filename in file_mapping:

            if filename.endswith('.csv'):
                file_path = os.path.join(folder_path, filename)

                # Create a temporary list to store rows that do not match the serial number
                temp_rows = []

                with open(file_path, 'r', newline='', encoding='UTF8') as f:
                    reader = csv.reader(f)
                    header = next(reader)  # Read and store the header line

                    for idx, row in enumerate(reader, start=1):  # Start from row 2
                        if int(row[-1]) != serial_number:  # Check if the serial number matches
                            temp_rows.append(row)  # Append the row to temp_rows if serial number doesn't match
                        else:
                            deleted_file = filename
                            deleted = True
                            if deleted_file not in deleted_files:  # Check if file was already deleted
                                if not (deleted_file.startswith(data.binFile) or deleted_file.startswith(data.defaultFile)):
                                    logging.info("Deleted file: " + deleted_file + "\n")
                                    deleted_files.add(deleted_file)  # Add file to set of deleted files


                # Write the filtered rows back to the same file
                with open(file_path, 'w', newline='', encoding='UTF8') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)  # Write back the header line
                    writer.writerows(temp_rows)  # Write the filtered rows back to the file
