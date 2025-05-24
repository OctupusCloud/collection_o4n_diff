#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Ansible module for splitting device configuration into separate text files.
"""

from __future__ import print_function, unicode_literals
__metaclass__ = type

DOCUMENTATION = r"""
---
module: o4n_split_config
short_description: Split device configuration into separate text files by blocks
description:
  - Searches for configuration blocks based on start and end parameters
  - Optionally filters blocks by keyword
  - Saves each matching block as a separate text file
  - Preserves original indentation and formatting
version_added: "2.1"
author: "Manuel Saldivar (@msaldivar) & Randy Rozo (@randyrozo)"
notes:
  - Tested on Linux
  - Tested with Cisco devices
requirements:
  - ansible >= 2.10
  - python >= 3.6
  - Establecer `ansible_python_interpreter` a Python 3 si es necesario.
options:
  file_cfg:
    description:
      - Source configuration file path
    required: true
    type: str
  parameter_start:
    description:
      - Pattern marking the start of a configuration block
    required: true
    type: str
  parameter_end:
    description:
      - Pattern marking the end of a configuration block
    required: false
    default: '!'
    type: str
  keyword:
    description:
      - Optional keyword to filter blocks (only blocks containing this will be processed)
      - Use empty string or space to process all blocks
    required: false
    default: " "
    type: str
  path_file:
    description:
      - Destination directory for output files
      - Will be created if it doesn't exist
    required: false
    default: "./"
    type: str
  hostname:
    description:
      - Device hostname to include in output filenames
    required: true
    type: str
  ext:
    description:
      - File extension for output files
    required: false
    default: "txt"
    type: str
"""

EXAMPLES = r"""
# Extract all interface configurations
- name: Extract interface configurations
  o4n_split_config:
    file_cfg: "./configs/{{ inventory_hostname }}.cfg"
    parameter_start: "interface"
    parameter_end: "!"
    path_file: "./interfaces/"
    hostname: "{{ inventory_hostname }}"
    ext: "intf"

# Extract only access switchport configurations
- name: Extract access switchports
  o4n_split_config:
    file_cfg: "./configs/{{ inventory_hostname }}.cfg"
    parameter_start: "interface"
    parameter_end: "!"
    keyword: "switchport mode access"
    path_file: "./access_ports/"
    hostname: "{{ inventory_hostname }}"
    ext: "port"

# Extract OSPF configurations
- name: Extract OSPF process configs
  o4n_split_config:
    file_cfg: "./configs/{{ inventory_hostname }}.cfg"
    parameter_start: "router ospf"
    parameter_end: "!"
    path_file: "./routing/"
    hostname: "{{ inventory_hostname }}"
    ext: "ospf"
"""

RETURN = r"""
msg:
    description: Status message
    type: str
    returned: always
    sample: "Configuration blocks successfully extracted"
content:
    description: Detailed results of the operation
    type: dict
    returned: always
    contains:
        Total_execution_time:
            description: Total execution time in seconds
            type: str
            sample: "0:00:00.134"
        file_names:
            description: List of generated filenames
            type: list
            sample:
                - "ROUTER1_interface_GigabitEthernet0-1.intf"
                - "ROUTER1_interface_GigabitEthernet0-2.intf"
        sections_list:
            description: List of extracted sections with details
            type: list
            sample:
                - instance_name: "GigabitEthernet0/1"
                  filename: "ROUTER1_interface_GigabitEthernet0-1.intf"
                  section_text: ["interface GigabitEthernet0/1", " description WAN Link", " ip address 192.168.1.1 255.255.255.0"]
    sample:
        "content": {
            "Total_execution_time": "0:00:00.134",
            "file_names": [
                "ROUTER1_interface_GigabitEthernet0-1.intf",
                "ROUTER1_interface_GigabitEthernet0-2.intf"
            ],
            "sections_list": [
                {
                    "instance_name": "GigabitEthernet0/1",
                    "filename": "ROUTER1_interface_GigabitEthernet0-1.intf",
                    "section_text": [
                        "interface GigabitEthernet0/1",
                        " description WAN Link",
                        " ip address 192.168.1.1 255.255.255.0"
                    ]
                },
                {
                    "instance_name": "GigabitEthernet0/2",
                    "filename": "ROUTER1_interface_GigabitEthernet0-2.intf",
                    "section_text": [
                        "interface GigabitEthernet0/2",
                        " description LAN Link",
                        " ip address 10.0.0.1 255.255.255.0"
                    ]
                }
            ]
        }
"""

import os
import re
from datetime import datetime
from ansible.module_utils.basic import AnsibleModule


def read_configuration_file(file_path):
    """
    Read a configuration file and return its contents.
    
    Args:
        file_path (str): Path to the configuration file
        
    Returns:
        tuple: (content, success, message)
            - content (str): File content if successful, empty string otherwise
            - success (bool): True if operation was successful
            - message (str): Descriptive message about the operation
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            if not content:
                return "", False, f"File '{file_path}' is empty"
            return content, True, f"Successfully read '{file_path}'"
    except FileNotFoundError:
        return "", False, f"File not found: '{file_path}'"
    except PermissionError:
        return "", False, f"Permission denied: '{file_path}'"
    except Exception as e:
        return "", False, f"Error reading '{file_path}': {str(e)}"


def find_configuration_blocks(config_text, start_pattern, end_pattern):
    """
    Find all configuration blocks in the text based on start and end patterns.
    
    Args:
        config_text (str): Full configuration text
        start_pattern (str): Pattern marking the beginning of a block
        end_pattern (str): Pattern marking the end of a block
        
    Returns:
        list: List of tuples containing (start_position, end_position, block_text, block_id)
    """
    # Create a regex pattern that captures from start_pattern to end_pattern
    # Preserve all original formatting
    pattern = re.compile(
        r'^' + re.escape(start_pattern) + r'\s*([^\n]*)' +
        r'\n(.*?)' +
        r'(?:(?=' + re.escape(start_pattern) + r')|' + re.escape("\n"+end_pattern) + r')',
        re.DOTALL | re.MULTILINE
    )
    
    # Find all matches and extract block information
    blocks = []
    for match in pattern.finditer(config_text):
        # Extract the block identifier (e.g., interface name)
        block_id = match.group(1).strip()
        # Get the complete block text with original formatting
        block_text = match.group(0)
        blocks.append((match.start(), match.end(), block_text, block_id))
    
    return blocks


def create_output_directory(directory_path):
    """
    Ensure the output directory exists, creating it if necessary.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        tuple: (success, message)
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return True, f"Directory ready: '{directory_path}'"
    except Exception as e:
        return False, f"Failed to create directory '{directory_path}': {str(e)}"


def sanitize_filename(text):
    """
    Convert text to a safe filename by replacing invalid characters.
    
    Args:
        text (str): Original text
        
    Returns:
        str: Sanitized filename-safe text
    """
    # Replace characters not allowed in filenames with underscore
    return re.sub(r'[^\w\-_.]', '_', text)


def extract_matching_blocks(blocks, start_pattern, keyword, path, hostname, extension):
    """
    Process matching blocks, filtering by keyword and saving to files.
    
    Args:
        blocks (list): List of block tuples from find_configuration_blocks
        start_pattern (str): Start pattern (used for filename)
        keyword (str): Keyword to filter blocks (empty for all blocks)
        path (str): Output directory path
        hostname (str): Device hostname for filename
        extension (str): File extension
        
    Returns:
        tuple: (file_names, sections_list, message)
    """
    # Ensure path ends with slash
    if not path.endswith('/') and path:
        path += '/'
        
    # Ensure output directory exists
    success, message = create_output_directory(path)
    if not success:
        return [], [], message
    
    file_names = []
    sections_list = []
    
    for _, _, block_text, block_id in blocks:
        # Skip blocks not containing the keyword (unless keyword is empty/space)
        if keyword.strip() and keyword not in block_text:
            continue
            
        # Create sanitized filename components
        safe_id = sanitize_filename(block_id)
        safe_pattern = sanitize_filename(start_pattern)
        
        # Build the complete filename
        filename = f"{path}{hostname}_{safe_pattern}_{safe_id}.{extension}"
        file_names.append(filename)
        
        # Store section information
        section_info = {
            "instance_name": block_id,
            "filename": filename,
            "section_text": block_text.strip().splitlines()
        }
        sections_list.append(section_info)
        
        # Write the configuration block to file
        try:
            with open(filename, 'w') as file:
                file.write(block_text)
        except Exception as e:
            return (
                file_names, 
                sections_list,
                f"Error writing file '{filename}': {str(e)}"
            )
    
    return file_names, sections_list, "All files written successfully"


def main():
    """
    Main function - entry point for the Ansible module.
    """
    # Define module arguments
    module_args = dict(
        file_cfg=dict(type='str', required=True),
        parameter_start=dict(type='str', required=True),
        parameter_end=dict(type='str', default='!'),
        keyword=dict(type='str', default=" "),
        path_file=dict(type='str', default="./"),
        hostname=dict(type='str', required=True),
        ext=dict(type='str', default="txt"),
    )
  
    # Initialize result structure
    result = {
        "changed": False,
        "msg": "",
        "content": {}
    }

    # Create module instance
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Start execution timer
    start_time = datetime.now()

    # Handle check mode
    if module.check_mode:
        # Read configuration file (even in check mode)
        config_text, success, message = read_configuration_file(file_cfg)
        if not success:
            module.fail_json(msg=f"Error reading configuration: {message}")
        
        # Find configuration blocks without saving them
        blocks = find_configuration_blocks(config_text, parameter_start, parameter_end)
        
        # Filter blocks by keyword if specified
        matching_blocks = []
        for block in blocks:
            _, _, block_text, block_id = block
            if keyword.strip() == " " or keyword in block_text:
                matching_blocks.append(block_id)
        
        module.exit_json(
            changed=False,
            msg=f"Check mode: Found {len(matching_blocks)} matching blocks",
            content={
                "Total_execution_time": str(datetime.now() - start_time),
                "would_process_blocks": matching_blocks
            }
        )



    # Extract parameters
    file_cfg = module.params['file_cfg']
    parameter_start = module.params['parameter_start']
    parameter_end = module.params['parameter_end']
    keyword = module.params['keyword']
    path_file = module.params['path_file']
    hostname = module.params['hostname']
    ext = module.params['ext']


    # Read configuration file
    config_text, success, message = read_configuration_file(file_cfg)
    if not success:
        module.fail_json(msg=f"Error reading configuration: {message}")


    # Find configuration blocks
    blocks = find_configuration_blocks(config_text, parameter_start, parameter_end)
    if not blocks:
        module.exit_json(
            changed=False,
            msg=f"No configuration blocks found matching '{parameter_start}'",
            content={"Total_execution_time": str(datetime.now() - start_time)}
        )
    
    # Process and save matching blocks
    file_names, sections_list, message = extract_matching_blocks(
        blocks, parameter_start, keyword, path_file, hostname, ext
    )

    if not file_names:
        module.exit_json(
            changed=False,
            msg=f"No matching blocks found. Message: {message}",
            content={"Total_execution_time": str(datetime.now() - start_time)}
        )
    
    # Complete execution and return results
    result["changed"] = True
    result["msg"] = f"Successfully extracted {len(file_names)} configuration blocks"
    result["content"] = {
        "Total_execution_time": str(datetime.now() - start_time),
        "file_names": file_names,
        "sections_list": sections_list,
    }
    
    module.exit_json(**result)


if __name__ == "__main__":
    main()
