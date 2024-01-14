import os
import csv

# Function to count the number of rows in a CSV file
def count_csv_rows(file_path):
    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        row_count = sum(1 for row in csvreader)
    return row_count

# Function to count the number of CSV files in a folder
def count_csv_files(folder_path):
    csv_count = sum(1 for file in os.listdir(folder_path) if file.endswith('.csv'))
    return csv_count

# Directory containing the dataset and subfolders
dataset_folder = 'Default'

# Traverse through all subfolders and their files
for root, dirs, files in os.walk(dataset_folder):
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(root, file)
            row_count = count_csv_rows(file_path)
            if row_count < 5:
                os.remove(file_path)
                print(f"Deleted {file_path} with {row_count} rows.")

    # Count and print the number of CSV files in the current subfolder
    csv_count = count_csv_files(root)
    print(f"Subfolder: {root}, CSV Files: {csv_count}")

print("Deletion process completed.")
