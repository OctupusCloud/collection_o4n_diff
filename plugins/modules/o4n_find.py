#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

__metaclass__ = type

DOCUMENTATION = """
---
module: o4n_find
short_description: Realiza búsqueda de patrones en un texto en base a expresiones regulares.
description:
  - ejecuta busquedas de patrones en base a expresiones regulares
  - muestra las lineas que coinciden con el patron
  - también indica la posición donde se encontró la coincidencia
version_added: "3.0"
author: "Ed Scrimaglia"
notes:
  - Testeado en linux
requirements:
  - ansible >= 2.10
options:
  exp_reg:
    description:
      expresión regular usada para realizar la búqueda
    required: true
    type: string
  path_file:
    description:
      archivo actual, config file, a comparar contra exp_reg
    required: true
    type: string
"""

EXAMPLES = """
tasks:
  - name: Oction Find Regex
    o4n_find:
      exp_reg: "int[a-z]+\s*[a-zA-z]+\s*[0-9]/[0-9]"
      path_file: "./backup/{{inventory_hostname}}.config"
    register: salidadiff
"""
RETURN = """
output:
    description: retorna un json
    "content": {
        "Diff_Results": {
            "exp_regular": "interfaceXXX",
            "lines_included": [
                "interface GigabitEthernet0/0",
                "interface GigabitEthernet0/1",
                "interface GigabitEthernet0/2"
            ],
            "lines_included_span": {
                "interface GigabitEthernet0/0": [
                    "14950",
                    "14978"
                ],
                "interface GigabitEthernet0/1": [
                    "16117",
                    "16145"
                ],
                "interface GigabitEthernet0/2": [
                    "18589",
                    "18617"
                ]
            },
            "path_file": "../documentacion/modulos/G3_Acceso.device"
        },
        "Total_execution_time": "0:00:00.002101"
    }
"""

# Modulos
from ansible.module_utils.basic import AnsibleModule
from datetime import datetime
from collections import OrderedDict
from ansible_collections.octupus.o4n_diff.plugins.module_utils.cregex import RegMatch as cr

def find_regex(_file: str, _exr: str):
    salida_json = OrderedDict()
    line_inc_dic = OrderedDict()
    lines_included = []
    try:
        reg = cr(_exr)
        file = reg.lector(_file)
        span = reg.finditer(file)

        for match in span:
            line_inc_dic[match.group()] = match.span()

        lines_included = reg.findall(file)

        salida_json['exp_regular'] = _exr
        salida_json['path_file'] = _file
        salida_json["lines_included"] = lines_included
        salida_json["lines_included_span"] = line_inc_dic
        success = True
        ret_msg = "Find algorithm run successfully"
    except IndexError as error:
        success = False
        ret_msg = f"Find algorithm failed, error {error}"

    return salida_json, success, ret_msg

def main():
    module = AnsibleModule(
        argument_spec = dict(
            path_file = dict(required=True),
            exp_reg = dict(required=True)
        )
    )
    path_file = module.params.get("path_file")
    exp_reg = module.params.get("exp_reg")

    # Diff with cregex
    starttime = datetime.now()
    salida_ansible = OrderedDict()
    salida, success, ret_msg = find_regex(path_file, exp_reg)
    # Blocks to modify
    if success:
        salida_ansible["Diff_Results"] = salida
        salida_ansible["Total_execution_time"] = f"{datetime.now() - starttime}"
        module.exit_json(msg=ret_msg, content=salida_ansible)
    else:
        module.fail_json(msg=ret_msg)


if __name__ == "__main__":
    main()
