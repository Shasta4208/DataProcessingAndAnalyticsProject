import os
import time
import schedule
import subprocess
from xml_processor.file_handler import get_files
from xml_processor.xml_converter import parse_xml, extract_data, write_csv, write_combined_csv

file_path = 'C:/Users/larso/OneDrive/Documents/Project/TestFile/Test1'
controller_output_dir = 'C:/Users/larso/OneDrive/Documents/Project/ControllerOutput'
node_output_dir = 'C:/Users/larso/OneDrive/Documents/Project/NodeOutput'
controller_script = 'C:/Users/larso/OneDrive/Documents/Project/ControllerSQLConv.py'
node_script = 'C:/Users/larso/OneDrive/Documents/Project/NodeSQLConv.py'

# Initialize run count and combined data lists
run_count = 0
combined_controller_data = []
combined_node_data = []

# Function to run the additional controller and node scripts as background processes
def run_additional_scripts():
    controller_process = subprocess.Popen(['python', controller_script], shell=True)
    node_process = subprocess.Popen(['python', node_script], shell=True)
    return controller_process, node_process

# Function to process XML files and extract controller and node data
def convert_xml():
    global run_count
    start_time = time.time()
    first_run = (run_count == 0)

    print(f"Run count: {run_count}, First run: {first_run}")

    # Get the list of XML files to process 
    files_to_process = get_files(file_path, first_run)

    # Process each XML file
    for full_file_path in files_to_process:
        print(f"Processing file: {full_file_path}")
        root_element = parse_xml(full_file_path)
        if root_element is not None:
            try:
                # Extract controller and node data from the XML
                ControllerCounter, NodeCounter = extract_data(root_element)

                # Append the extracted data to the global lists
                combined_controller_data.extend(ControllerCounter)
                combined_node_data.extend(NodeCounter)

                # Generate output file names based on the input file name
                controller_output_path = os.path.splitext(os.path.basename(full_file_path))[0] + "_ControlOut"
                node_output_path = os.path.splitext(os.path.basename(full_file_path))[0] + "_NodeOut"

                # Write individual CSV files for the controller and node data
                write_csv(controller_output_dir, controller_output_path, ControllerCounter, "measObjLdn,,p,max_value,avg_value,beginTime,endTime")
                write_csv(node_output_dir, node_output_path, NodeCounter, "measObjLdn,p,max_value,avg_value,beginTime,endTime")

            # Handle potential errors that might arise during processing
            except ValueError as e:
                print(f"ValueError: {e} - File: {full_file_path}")
            except Exception as e:
                print(f"Unexpected error: {e} - File: {full_file_path}")
        else:
            print(f"Skipping file due to parse error or missing element: {full_file_path}")

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time taken: {total_time:.2f} seconds")

    run_count += 1

    # Write combined data from all runs into summary CSV files for both controllers and nodes
    write_combined_csv(controller_output_dir, combined_controller_data, "ControllerCounter_All", "measObjLdn,,p,max_value,avg_value,beginTime,endTime")
    write_combined_csv(node_output_dir, combined_node_data, "NodeCounter_All", "measObjLdn,p,max_value,avg_value,beginTime,endTime")

schedule.every(1).minute.do(convert_xml)

# Run the additional controller and node scripts as background processes
controller_process, node_process = run_additional_scripts()

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    controller_process.terminate()
    node_process.terminate()
    print("Terminated additional scripts.")