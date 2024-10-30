import xml.etree.ElementTree as ET
import os
import csv
import numpy as np

def parse_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root_element = tree.getroot()
        return root_element
    except ET.ParseError as e:
        print(f"ParseError: {e} - File: {file_path}")
        return None

def calculate_avg_ignoring_zeros(data):
    filtered_data = [x for x in data if x != 0]
    if filtered_data:
        return sum(filtered_data) / len(filtered_data)
    else:
        return 0

def extract_data(root_element):
    beginTime_element = root_element.find('.//{*}fileHeader/{*}measCollec')
    if beginTime_element is None or 'beginTime' not in beginTime_element.attrib:
        raise ValueError("Cannot find beginTime attribute")
    beginTime = beginTime_element.get('beginTime')

    endTime_element = root_element.find('.//{*}fileFooter/{*}measCollec')
    if endTime_element is None or 'endTime' not in endTime_element.attrib:
        raise ValueError("Cannot find endTime attribute")
    endTime = endTime_element.get('endTime')

    ControllerCounter = []
    NodeCounter = []

    for measValue in root_element.findall('.//{*}measValue'):
        measObjLdn_full = measValue.get('measObjLdn')
        if measObjLdn_full is None:
            raise ValueError("Cannot find measObjLdn attribute")
        measObjLdn = measObjLdn_full.split(',')[1] if ',' in measObjLdn_full else measObjLdn_full

        for r in measValue.findall('.//{*}r'):
            p = r.get('p')
            values_text = r.text.strip()
            try:
                if '[' in values_text and ']' in values_text:
                    values_list = [int(x) for x in values_text.strip('[]').split()]
                    max_value = max(values_list)
                    avg_value = calculate_avg_ignoring_zeros(values_list) 
                else:
                    values = int(values_text)
                    max_value = values
                    avg_value = values if values != 0 else 0 
            except ValueError:
                raise ValueError(f"Invalid format in measValue: {values_text}")


            if int(p) <= 261:
                ControllerCounter.append([measObjLdn, "", p, max_value, avg_value, beginTime, endTime])
            else:
                NodeCounter.append([measObjLdn, p, max_value, avg_value, beginTime, endTime])

    return ControllerCounter, NodeCounter

def write_csv(output_dir, name, data, headers):
    if data:
        output_path = os.path.join(output_dir, f"{name}.csv")
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers.split(","))
            for row in data:
                writer.writerow(row)

def write_combined_csv(output_dir, combined_data, name, headers):
    if combined_data:
        output_path = os.path.join(output_dir, f"{name}.csv")
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers.split(","))
            for row in combined_data:
                writer.writerow(row)