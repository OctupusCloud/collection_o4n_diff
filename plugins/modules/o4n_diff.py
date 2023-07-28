#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

DOCUMENTATION = """
---
module: o4n_diff
short_description: Ejecuta algoritmo Diff para analizar compliances.
description:
  - ejecuta algorintmo Diff para configuraciones o bloques de comandos (contexts)
  - muestra las lineas que fueron agregadas o eliminadas
  - muestra las lineas que hay que agregar o eliminar
version_added: "3.0"
author: "Ed Scrimaglia"
notes:
  - Testeado en linux
requirements:
  - ansible >= 2.10
options:
    original:
        description:
          archivo origen o master config a comparar
        required: true
        type: string
    current:
        description:
          archivo actual, config file o config context, a comparar contra original
        required: true
        type: string
    type_diff:
        description:
          tipo de diff a ejecutar.
        required: false
        choices:
          - config: ejecuta Diff, analiza lines to add y lines to remove contra Config Master
          - context: ejecuta Diff, analiza solo lines in context contra Config Master
        type: string
    match_type:
        description:
          tipo de match que el algorithm Diff ejecutara (type_diff=context)
        required: false
        choices:
          - full: Diff algorithm verifica que las lineas del Contexto existan exactamente en Device Configuracion
          - include: Diff algorithm verifica que las lineas de Contexto esten inlcuidas en Device Configuracion
        type: string
    lines_in_context:
        description:
          cantidad de lineas que apareceran en el bloque contexto formado por @@ -XY, +XY @@
        required: false
        type: string
        
"""

RETURN = """
output:
  description: Retorna un objeto JSON cuyo conteniendo sigue uno de los siguientes formato (ejemplo)
  type: dict
  returned: allways
  sample:
    output_config: {
        "salidadiff": {
            "changed": false,
            "content": {
                "Diff_Results": {
                    "diff": "--- original\n+++ current\n@@ -36,12 +36,12 @@\n !\n !\n spanning-tree mode pvst\n-spanning-tree extend system-id\n !\n+interface loopback 0\n+ ip address 10.54.1.1 255.255.255.0\n+\n interface GigabitEthernet0/0\n  no switchport\n- ip address 10.54.154.151 255.255.255.224\n- negotiation auto\n !\n interface GigabitEthernet0/1\n  switchport trunk allowed vlan 1,3-4094",
                    "lines_to_delete": "interface loopback 0\n ip address 10.54.1.1 255.255.255.0\n",
                    "lines_to_add": "spanning-tree extend system-id\n ip address 10.54.154.151 255.255.255.224\n negotiation auto",
                    "block_to_add": "spanning-tree extend system-id\ninterface GigabitEthernet0/0\n ip address 10.54.154.151 255.255.255.224\n negotiation auto",
                    "block_to_del": "interface loopback 0\n ip address 10.54.1.1 255.255.255.0"
                },
                "Total_execution_time": "0:00:00.000876"
            },
            "failed": false,
            "msg": true
        }
    }

    output_context: {
        "salidadiff": {
            "changed": false,
            "content": {
                "Diff_Results": {
                    "original_context": [
                        "ip route 0.0.0.0 0.0.0.0 10.0.0.254",
                        "ip route 0.0.0.0 0.0.0.0 10.182.0.1",
                        "ip route 0.0.0.0 0.0.0.0 10.2.0.254",
                        "ip ssh version 2",
                        "ip ssh server algorithm encryption aes128-ctr aes192-ctr aes256-ctr",
                        "ip ssh client algorithm encryption aes128-ctr aes192-ctr aes256-ctr",
                        "ip scp server enable"
                    ]
                    "lines_to_add_config_file": [],
                },
                "Total_execution_time": "0:00:00.000216"
            },
            "failed": false,
            "msg": "Diff algorithm run successfully"
        }
    }

    output_include_context: {
        "salidadiff": {
            "changed": false,
            "content": {
                "Diff_Results": {
                    "orginal_context": [
                        "ip route 0.0.0.0 0.0.0.0",
                        "aes128-ctr aes192-ctr aes256-ctr",
                        "ip ppp point-to-point"
                    ],
                    "lines_included": {
                        "ip route 0.0.0.0 0.0.0.0": [
                            "Line included in config line: ip route 0.0.0.0 0.0.0.0 10.0.0.254",
                            "Line included in config line: ip route 0.0.0.0 0.0.0.0 10.182.0.1",
                            "Line included in config line: ip route 0.0.0.0 0.0.0.0 10.2.0.254"
                        ],
                        "aes128-ctr aes192-ctr aes256-ctr": [
                            "Line included in config line: ip ssh server algorithm encryption aes128-ctr aes192-ctr aes256-ctr",
                            "Line included in config line: ip ssh client algorithm encryption aes128-ctr aes192-ctr aes256-ctr"
                        ]
                    },
                    "lines_to_add_config_file": [
                        "ip ppp point-to-point"
                    ]
                },
                "Total_execution_time": "0:00:00.000268"
            }
        }
    }
"""

EXAMPLES = """
tasks:
  - name: Oction Diff Files
    o4n_diff:
        original: "./backup/\{\{ inventory_hostname }}.mongo"
        current: "./backup/{{inventory_hostname}}.config"
        type_diff: config
        lines_in_context: "{{Service_Model.Diff_Context.lines}}" 
    register: salidadiff

tasks:
  - name: Oction Diff Files
    o4n_diff:
        original: "./backup/\{\{ inventory_hostname }}.mongo"
        current: "./backup/{{inventory_hostname}}_context.master"
        type_diff: context
        match_type: full
        lines_in_context: "{{Service_Model.Diff_Context.lines}}" 
    register: salidadiff

tasks:
  - name: Oction Diff Files
    o4n_diff:
        original: "./backup/\{\{ inventory_hostname }}.mongo"
        current: "./backup/{{inventory_hostname}}_context.master"
        type_diff: context
        match_type: include
        lines_in_context: "{{Service_Model.Diff_Context.lines}}" 
    register: salidadiff
"""

# Modulos
from ansible.module_utils.basic import AnsibleModule
from datetime import datetime
from collections import OrderedDict
import difflib
import json

def open_files(_original, _current):
    str2 = ""
    str1 = ""
    success_origin_current = False
    try:
        f = open(_original, 'r')
    except Exception as error:
        ret_msg = f"No se pudo abrir el archivo {_original}, error {error}"
        success_origin = False
    else:
        str1 = f.read().strip().splitlines()
        f.close()
        ret_msg = f"Archivos {_original} abiertos correctamente"
        success_origin = True

    if success_origin:
        try:
            f = open(_current, 'r')
        except Exception as error:
            ret_msg = f"No se pudo abrir el archivo {_current}, error {error}"
            success_origin_current = False
        else:
            str2 = f.read().strip().splitlines()
            f.close()
            if len(str1) > 0 and len(str2) > 0:
                ret_msg = f"Archivos {_original} y {_current} abiertos correctamente"
                success_origin_current = True
            else:
                ret_msg = f"Archivos {_original} o {_current} sin contenido"
                success_origin_current = False

    return str1, str2, success_origin_current, ret_msg


def find_block_of_config_to_modify(_block="", _lines_to_add="",_lines_to_delete=""):
    ret_msg = ""
    block_list = _block.splitlines() if _block else []
    new_block_list = [i for i in block_list if not i.startswith("---")] if len(block_list) >0 else []
    new_block_list = [i for i in new_block_list if not i.startswith("+++")] if len(new_block_list) >0 else []
    tuplas_new_block_list = list(enumerate((new_block_list)))

    # finding the mayor line in line_to_add (line not indented)
    new_lines_to_add = []
    mayor_line_not_indented = None
    new_lines_to_add_str = None
    try:
        for line_to_add in _lines_to_add:
            line_in_block = tuplas_new_block_list[line_to_add[0]]
            ind_in_bloc = line_in_block[0]
            cmd_in_block = line_in_block[1]
            cmd_in_block_mod = cmd_in_block.replace(cmd_in_block[0], "", 1)
            if cmd_in_block_mod[0] != " " and "!" not in cmd_in_block_mod:
                if mayor_line_not_indented != cmd_in_block_mod:
                    new_lines_to_add.append(cmd_in_block)
                    mayor_line_not_indented = cmd_in_block_mod
            elif "!" not in cmd_in_block_mod:
                for line in tuplas_new_block_list[ind_in_bloc::-1]:
                    cmd_line = line[1]
                    cmd_line_mod = cmd_line.replace(cmd_line[0], "", 1)
                    if cmd_line_mod[0] != ' ':
                        if mayor_line_not_indented != cmd_line_mod:
                            new_lines_to_add.append(" "+cmd_line)
                            mayor_line_not_indented = cmd_line_mod
                        new_lines_to_add.append(cmd_in_block)
                        break
        new_lines_to_add_str = '\n'.join(new_lines_to_add) if len(new_lines_to_add) > 0 else False
    except Exception as error:
        ret_msg = "Error finding block to add, {}".format(error)
        new_lines_to_add_str = False

    # finding the mayor line in line_to_del (line not indented)
    new_lines_to_del_str = None
    mayor_line_not_indented = None
    new_lines_to_del = []
    try:
        for line_to_del in _lines_to_delete:
            line_in_block = tuplas_new_block_list[line_to_del[0]]
            ind_in_bloc = line_in_block[0]
            cmd_in_block = line_in_block[1]
            cmd_in_block_mod = cmd_in_block.replace(cmd_in_block[0], "", 1)
            if cmd_in_block_mod[0] != " " and "!" not in cmd_in_block_mod:
                if mayor_line_not_indented != cmd_in_block_mod:
                    new_lines_to_del.append(cmd_in_block)
                    mayor_line_not_indented = cmd_in_block_mod
            elif "!" not in cmd_in_block_mod:
                for line in tuplas_new_block_list[ind_in_bloc::-1]:
                    cmd_line = line[1]
                    cmd_line_mod = cmd_line.replace(cmd_line[0], "", 1)
                    if cmd_line_mod[0] != ' ':
                        if mayor_line_not_indented != cmd_line_mod:
                            new_lines_to_del.append(" "+cmd_line)
                            mayor_line_not_indented = cmd_line_mod
                        new_lines_to_del.append(cmd_in_block)
                        break
        new_lines_to_del_str = '\n'.join(new_lines_to_del) if len(new_lines_to_del) > 0 else False
    except Exception as error:
        ret_msg = "Error finding block to Delete, {}".format(error)
        new_lines_to_del_str = False

    return ret_msg, new_lines_to_add_str, new_lines_to_del_str


def find_context_included(_str1: list, _str2: list, _context_name: str, _match_type: str):
    salida_json = OrderedDict()
    line_inc_dic = OrderedDict()
    lines_not_included = []
    try:
        for line_in_context in _str2:
            lines_included = []
            for line_in_conf in _str1:
                if line_in_context in line_in_conf:
                    line = f"Line included in config line: {line_in_conf}"
                    lines_included.append(line)
            if len(lines_included) >= 1:
                line_inc_dic[line_in_context] = lines_included
            else:
                lines_not_included.append(line_in_context)
        salida_json['match_type'] = _match_type
        salida_json['context_name'] = _context_name
        salida_json['original_context'] = _str2
        salida_json["lines_included"] = line_inc_dic
        salida_json["lines_to_add_config_file"] = lines_not_included
        success = True
        ret_msg = "Diff algorithm run successfully"
    except IndexError as error:
        success = False
        ret_msg = f"Diff algorithm failed, error {error}"

    return salida_json, success, ret_msg


def find_context_diff(_str1: list, _str2: list, _context_name: str, _match_type: str, _lines_in_context=3):
    salida_json = OrderedDict()
    try:
        diff = difflib.unified_diff(_str1, _str2, fromfile='original', tofile='current', n=_lines_in_context, lineterm='')
        lines_to_add_config_file = [ele for ele in diff if not ele.startswith("-") and not ele.startswith("+++ current")
            and ele.startswith("+")]
        salida_json['match_type'] = _match_type
        salida_json['context_name'] = _context_name
        salida_json['original_context'] = _str2
        salida_json["lines_to_add_config_file"] = lines_to_add_config_file
        success = True
        ret_msg = "Diff algorithm run successfully"
    except Exception as error:
        success = False
        ret_msg = f"Diff algorithm failed, error {error}"

    return salida_json, success, ret_msg


def find_config_diff(_str1: list, _str2: list, _lines_in_context=3):
    salida_json = OrderedDict()
    added = []
    diff = difflib.unified_diff(_str1, _str2, fromfile='original', tofile='current', n=_lines_in_context, lineterm='')
    salida_json["diff"] = '\n'.join([str(elem) for elem in diff])
    diff = difflib.unified_diff(_str1, _str2, fromfile='original', tofile='current', n=_lines_in_context, lineterm='')
    lines = list(diff)[2:]
    if (len(lines) == 0):
        salida_json["diff"] = []
    list_enum_lines = list(enumerate(lines))
    added = [line for line in list_enum_lines if line[1][0] == '+']
    removed = [line for line in list_enum_lines if line[1][0] == '-']
    success = True

    if len(added) > 0:
        salida_json["lines_to_delete"] = added
        ret_msg = "Differences found"
    else:
        salida_json["lines_to_delete"] = []
        ret_msg = "No differences found"

    if len(removed) > 0:
        salida_json["lines_to_add"] = removed
        ret_msg = "Differences found"
    else:
        salida_json["lines_to_add"] = []
        ret_msg = "No differences found"

    return salida_json, success, ret_msg


def main():
    module = AnsibleModule(
        argument_spec=dict(
            original=dict(required=True),
            current=dict(requiered=True),
            type_diff=dict(requiered=False, type="str", choices=["config","context"], default="config"),
            match_type=dict(requiered=False, type="str", choices=["include","full"], default="full"),
            lines_in_context=dict(requiered=False,  type="str", default="3")
        )
    )
    original = module.params.get("original")
    current = module.params.get("current")
    type_diff = module.params.get("type_diff")
    match_type = module.params.get("match_type")
    lines_in_context=int(module.params.get("lines_in_context"))
    
    # Open Files
    config_orig, config_current, success_origin_current, ret_msg = open_files(original, current)

    # Diff
    if success_origin_current:
        starttime = datetime.now()
        salida_ansible = OrderedDict()
        if type_diff.lower() == "config":
            salida, success, ret_msg = find_config_diff(config_orig, config_current,lines_in_context)
            # Blocks to modify
            if success:
                salida_ansible["Diff_Results"] = salida
                # find block of lines to replace (add or delete)
                lines_to_add_snd = salida_ansible['Diff_Results']['lines_to_add']
                lines_to_del_snd = salida_ansible['Diff_Results']['lines_to_delete']
                block_snd = salida_ansible['Diff_Results']['diff']
                ret_msg, block_lines_to_add, block_lines_to_del = find_block_of_config_to_modify(block_snd,
                                                                                        lines_to_add_snd,
                                                                                        lines_to_del_snd)
                salida_ansible['Diff_Results']['lines_to_add'] = '\n'.join([cmd[1] for cmd in lines_to_add_snd]) if \
                    len(salida_ansible['Diff_Results']['lines_to_add']) > 0 else False
                salida_ansible['Diff_Results']['lines_to_delete'] = '\n'.join([cmd[1] for cmd in lines_to_del_snd]) if \
                    len(salida_ansible['Diff_Results']['lines_to_delete'])> 0 else False
                salida_ansible['Diff_Results']['block_to_add'] = block_lines_to_add
                salida_ansible['Diff_Results']['block_to_del'] = block_lines_to_del
                salida_ansible["Total_execution_time"] = f"{datetime.now() - starttime}"
                module.exit_json(msg=ret_msg, content=salida_ansible)
            else:
                module.fail_json(msg=ret_msg)
        else:
            if match_type.lower() == "include":
                salida, success, ret_msg = find_context_included(config_orig, config_current, current, match_type)
            elif match_type.lower() == "full":
                salida, success, ret_msg = find_context_diff(config_orig, config_current, current, match_type, lines_in_context)
            if success:
                salida_ansible["Diff_Results"] = salida
                salida_ansible["Total_execution_time"] = f"{datetime.now() - starttime}"
                module.exit_json(msg=ret_msg, content=salida_ansible)
            else:
                module.fail_json(msg=ret_msg)
    else:
        module.fail_json(msg=ret_msg)
if __name__ == "__main__":
    main()
