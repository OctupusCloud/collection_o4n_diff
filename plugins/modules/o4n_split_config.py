#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

__metaclass__ = type

DOCUMENTATION = """
---
module: o4n_split_config
short_description: Separa la configuración de un dispositivo en Bloques de archivos de texto.
description:
  - en base a un parametro inicial y final realiza la busqueda en toda la config y luego separa secuencialmente en bloques de texto
  - opcionalmente se puede realizar la busqueda de una keyword dentro de ese bloque para tener o no en cuenta el bloque
  - cada bloque de texto se entrega en un file txt
version_added: "2.0"
author: "Manuel Saldivar"
notes:
  - Testeado en linux
  - Testeado con Cisco
requirements:
  - ansible >= 2.10
options:
  file_cfg:
    description:
      archivo origen o master config en el cual se realizara la busqueda
    required: true
    type: string
  parameter_start:
    description:
      parámetro o palabra sobre la cual se realizará la búqueda, superior
    required: true
    type: string
  parameter_start:
    description:
      parámetro o palabra sobre la cual se realizará la búqueda, inferior, default !
    required: false
    type: string
  keyword:
    description:
      palabra clave o cadena de caracteres que debe incluir el bloque
    required: false
    type: string
  path_file:
    description:
      path de destino donde se almacenaran los bloques en cfg
    required: false
    type: string
  hostname:
    description:
      hostname para renombrar los txt de destino
    required: false
    type: string
"""

EXAMPLES = """
  - name: Call cfg block config, to separate interface config
    o4n_cfg_block:
      file_cfg: "../{{ files_d }}/{{ inventory_hostname }}.device"
      parameter_start: "interface"
      parameter_end: "!"
      keyword: "switchport mode access"
      path_file: "../{{ files_d }}/"
      hostname: "{{ inventory_hostname }}"
      ext: "interface"
    register: salida_cfg_block

"""

RETURN = """
msg:
    description: retorna un JSON. (ejemplo truncado)
    "content": {
        "Total_execution_time": "0:00:00.001394",
        "file_names": [
            "G3_Acceso_interface_GigabitEthernet0-1.interface",
            "G3_Acceso_interface_GigabitEthernet0-2.interface",
            "G3_Acceso_interface_GigabitEthernet0-3.interface"
        ],
        "sec_names": [
            "GigabitEthernet0/1",
            "GigabitEthernet0/2",
            "GigabitEthernet0/3"
        ]
    }
"""

# Modulos
from ansible.module_utils.basic import AnsibleModule
from datetime import datetime
from collections import OrderedDict


def open_files(_original):
    str1 = ""
    try:
        f = open(_original, 'r')
    except Exception as error:
        ret_msg = f"File could not be opened {_original}, error {error}"
    else:
        str1 = f.read()
        f.close()
        ret_msg = f"file {_original} open correctly"

    if len(str1) > 0 :
        ret_msg = f"file {_original} open correctly"
        success_origin_current = True
    else:
        ret_msg = f"file {_original} without content"
        success_origin_current = False

    return str1, success_origin_current, ret_msg

def find_all(_str1, _parameter_start, _parameter_end):
	positions = []
	position_st = 0
	position_end = 0
	
	while position_st != -1:
		position_st = _str1.find(_parameter_start,position_st)
		if position_st != -1:
			position_end = _str1.find(_parameter_end,position_st)
			if position_st < position_end:
				positions.append(position_st)
				positions.append(position_end)
				position_st = position_end + 1

	return positions

def find_section_config(_positions,_parameter,_keyword, _str1, path_file, hostname, ext):
    file_names = []
    sec_names = []
    _success = False
    for position in range(len(_positions)):
        try:
            t1=_str1[_positions[position]:_positions[position+1]]
        except:
            t1=_str1[_positions[position]:_positions[-1]]

        if t1.find(_keyword) != -1:
            namefile=t1.split('\n')[0].split(' ')
            sec_names.append(namefile[-1])
            if namefile[-1].find('/') != -1:
                namefile=namefile[-1].replace('/', '-')
            else:
                namefile=namefile[-1]
            pc = open(path_file+hostname+'_'+_parameter+'_'+namefile+"."+ext, 'w')
            file_names.append(hostname+'_'+_parameter+'_'+namefile+"."+ext)
            pc.write(t1)
            pc.close()
        elif _keyword == " ":
            namefile=t1.split('\n')[0].split(' ')
            sec_names.append(namefile[-1])
            if namefile[-1].find('/') != -1:
                namefile=namefile[-1].replace('/', '-')
            else:
                namefile=namefile[-1]
            pc = open(path_file+hostname+'_'+_parameter+'_'+namefile+"."+ext, 'w')
            file_names.append(hostname+'_'+_parameter+'_'+namefile+"."+ext)
            pc.write(t1)
            pc.close()

    ret_msg="File successfully split"
    _success = True

    return _success, ret_msg, file_names, sec_names 


def main():
    module = AnsibleModule(
        argument_spec=dict(
            file_cfg=dict(required=True),
            parameter_start=dict(required=True),
            parameter_end=dict(required=False, type='str', default='!'),
            keyword=dict(required=False, type="str", default=" "),
            path_file=dict(required=False, type="str", default=" "),
            hostname=dict(required=False, type="str", default=" "),
            ext=dict(required=False, type="str", default="txt")
        )
    )
    file_cfg = module.params.get("file_cfg")
    parameter_start = module.params.get("parameter_start")
    parameter_end = module.params.get("parameter_end")
    keyword = module.params.get("keyword")
    path_file = module.params.get("path_file")
    hostname = module.params.get("hostname")
    ext = module.params.get("ext")

    # Open Files
    config_orig, success_origin_current, ret_msg = open_files(file_cfg)
    
    parameter_startf = '\n' + parameter_start
    parameter_endf = '\n' + parameter_end

    # Get CFG block config
    if success_origin_current:
        starttime = datetime.now()
        salida_ansible = OrderedDict()
        positions = find_all(config_orig, parameter_startf, parameter_endf)
        if len(positions) > 1:
            success, ret_msg, file_names, sec_names = find_section_config(positions, parameter_start, keyword, config_orig, path_file, hostname, ext)
            
        else:
            ret_msg="Separation error, check search parameters"

    if success:
        salida_ansible['sec_names'] = sec_names
        salida_ansible['file_names'] = file_names
        salida_ansible["Total_execution_time"] = f"{datetime.now() - starttime}"
        module.exit_json(msg=ret_msg, content=salida_ansible)
    else:
        module.fail_json(msg=ret_msg)


if __name__ == "__main__":
    main()