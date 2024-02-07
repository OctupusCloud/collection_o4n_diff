#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

__metaclass__ = type

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
      - full: Diff algorithm verifica que las lineas del Contexto existan exactamente en Device Configuration
      - include: Diff algorithm verifica que las lineas de Contexto esten inlcuidas en Device Configuration
      - var: Diffios algorithm verifica que las lineas de Contexto esten incluidas en Device Configuration, pueden incluirse variables en la comparacion
    type: string
  lines_in_context:
    description:
      "cantidad de lineas que apareceran en el bloque contexto formado por @@ -XY, +XY @@"
    required: false
    type: string
  list_char_ignore:
    description:
      "lista con caracteres especiales a ignorar en la comparación"
    required: false
    type: list
  var_diff:
    description:
      "diferencia a aplicar a los elementos de las acls, valor entre 0 y 9, predet 5"
    required: false
    type: int
"""

EXAMPLES = """
tasks:
  - name: Oction Diff Files
    o4n_diff:
      original: "./backup/{{inventory_hostname}}.mongo"
      current: "./backup/{{inventory_hostname}}.config"
      type_diff: config
      lines_in_context: "{{Service_Model.Diff_Context.lines}}"
    register: salidadiff

  - name: Oction Diff Files
    o4n_diff:
      original: "./backup/{{ inventory_hostname }}.mongo"
      current: "./backup/{{inventory_hostname}}_context.master"
      type_diff: context
      match_type: full
      lines_in_context: "{{Service_Model.Diff_Context.lines}}"
    register: salidadiff

  - name: Oction Diff Files
    o4n_diff:
      original: "./backup/{{ inventory_hostname }}.mongo"
      current: "./backup/{{inventory_hostname}}_context.master"
      type_diff: context
      match_type: include
      lines_in_context: "{{Service_Model.Diff_Context.lines}}"
    register: salidadiff

  - name: Oction Diff Files
    o4n_diff:
      original: "./backup/{{ inventory_hostname }}.mongo"
      current: "./backup/{{inventory_hostname}}_context.master"
      type_diff: context
      match_type: var
      list_char_ignore: [!, #]
      lines_in_context: "{{Service_Model.Diff_Context.lines}}"
    register: salidadiff
"""
RETURN = """
output:
    "description": 
        - "1_ salida type diff config"
        - "2_ salida type diff context match full"
        - "3_ salida type diff context match include"
        - "4_ salida type diff context match var"
        - (salidas truncadas)
    "salidadiff_config": {
        "msg": "",
        "content": {
        "Diff_Results": {
            "diff": '--- original\n +++ current\n @@ -1,8 +1,8 @@\n Building configuration...\n \n-Current configuration with default configurations exposed ',
            "lines_to_delete": "+Current configuration with default configurations exposed : 49759 bytes\n",
            "lines_to_add": "-Current configuration with default configurations exposed : 49852 bytes\n-!\n",
            "block_to_add": "-Current configuration with default configurations exposed : 49852 bytes\n-ip cef load-sharing algorithm universal CC1B726F\n",
            "block_to_del": "+Current configuration with default configurations exposed : 49759 bytes\n+ip cef load-sharing algorithm universal ECC34684\n+ipv6",
            },
            "Total_execution_time": "0:00:00.016707"
        }
    }
    "salidadiff_common_context_match_full": {
      "results": [
        {
          "msg": "Diff algorithm run successfully",
          "content": {
            "Diff_Results": {
              "match_type": "full",
              "context_name": "../files/G3_Acceso_Script_general.txt",
              "original_context": [
                "no service pad",
                "",
                "service timestamps debug datetime msec localtime show-timezone",
                "service timestamps log datetime msec localtime show-timezone",
                "service password-encryption",
                "trunk...",
              ],
              "lines_to_add_config_file": [
                "+",
                "+service sequence-numbers",
                "+",
                "+",
                "+aaa group server tacacs+ ISET",
                "+ server name ISET1",
                "+ server name ISET2",
                "trunk...",
              ]
            },
            "Total_execution_time": "0:00:00.009611"}
        }
        ]
    }
    "salidadiff_common_context_match_include": {
    "results": [
      {
        "msg": "Diff algorithm run successfully",
        "content": {
          "Diff_Results": {
            "match_type": "include",
            "context_name": "../files/G3_Acceso_Script_general.txt",
            "original_context": [
              "no service pad",
              "",
              "service timestamps debug datetime msec localtime show-timezone",
              "service timestamps log datetime msec localtime show-timezone",
              "trunk...",
            ],
            "lines_included": {
              "no service pad": [
                "Line included in config line: no service pad to-xot",
                "Line included in config line: no service pad from-xot",
                "Line included in config line: no service pad cmns",
                "Line included in config line: no service pad",
                "trunk...",
              ],
              "": [
                "Line included in config line: Building configuration...",
                "Line included in config line: ",
                "Line included in config line: Current configuration with default configurations exposed : 49759 bytes",
                "Line included in config line: !",
              ],
            },
            "lines_to_add_config_file": [
              "aaa group server tacacs+ ISET",
              " server name ISET1",
              " server name ISET2",
              "trunk...",
            ]
          },
          "Total_execution_time": "0:00:00.050088"}
      }
      ]
    }
    "salidadiff_common_context_match_var": {
      "results": [
        {
          "msg": "Diff algorithm run successfully",
          "content": {
            "Diff_Results": {
              "lines_to_add_config_file": "",
              "match_type": "var",
              "context_name": "../files/G3_Acceso_Script_general_labo.txt",
              "original_context": [
                "no service pad",
                "",
                "service timestamps debug datetime msec localtime show-timezone",
                "service timestamps log datetime msec localtime show-timezone",
                "service password-encryption",
                "",
                "logging buffered 65535 informational",
                " ",
                "trunk...",
              ],
              "lines_difference": [
                "* Cisco in writing.                                                      *",
                "",
                "Building configuration...",
                "",
                "Current configuration with default configurations exposed : 49759 bytes",
                "",
                "access-session vlan-assignment ignore-errors",
                "",
                "trunk...",
                "",
              
              ],
              "delta_results": "--- baseline\n+++ comparison\n\n\n+   1: * Cisco in writing.                                                      *\n+   2: * IOSv is strictly limited to use for evaluation, demonstration and IOS  *\n+   3: * Technical Advisory Center. Any use or disclosure, in whole or in part, *\n+   4: * education. IOSv is provided as-is and is not supported by Cisco's      *\n+   5: * of the IOSv Software or Documentation to any third party for any       *\n+   6: * purposes is expressly prohibited except as otherwise authorized by     *\n+   7: **************************************************\n+   8: **************************************************************************\n+   9: **************************************************************************^C\n+  10: Building configuration...\n+  11: Current configuration with default configurations exposed : 49759 bytes\n+  12: access-session vlan-assignment ignore-errors\n+  13: alias exec h help\n+  14: alias exec lo logout\n+  15: alias exec p ping\n+  16: alias exec r resume\n+  17: alias exec s show\n+  18: alias exec u undebug\n+  19: alias exec un undebug\n+  20: alias exec w where\n+  21: archive\n+ trunk...",
            },
          "Total_execution_time": "0:00:00.261768",
          }
        }
        ]
    }
"""

# Modulos
from ansible.module_utils.basic import AnsibleModule
from datetime import datetime
from collections import OrderedDict
import difflib
import diffios
import re


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


def clr_pos(_strcl:list):
#this func clean acl position, because in comparision with acl template we can have a same element but different position
    for line_str in _strcl:
      positioni = _strcl.index(line_str)
      if re.match(r"^\s+\d+\s+permit.+$|^\s+\d+\s+deny.+$", line_str):
          line_strs = line_str.split(' ')
          for line_sp in line_strs:
              if line_strs.index(line_sp) == 2:
                  line_str = ' ' + line_sp
              elif line_strs.index(line_sp) != 0 or line_strs.index(line_sp) != 1 or line_strs.index(line_sp) != 2:
                  line_str = line_str + ' ' + line_sp
          _strcl[positioni] = line_str

    return _strcl


def find_block_of_config_to_modify(_list_char_ignore, _block="", _lines_to_add="", _lines_to_delete=""):
    ret_msg = ""
    block_list = _block.splitlines() if _block else []
    new_block_list = [i for i in block_list if not i.startswith("---")] if len(block_list) > 0 else []
    new_block_list = [i for i in new_block_list if not i.startswith("+++")] if len(new_block_list) > 0 else []
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
            cmd_in_block_mod_list = [char for char in cmd_in_block_mod if char]
            exist_ignored_char = [ele for ele in _list_char_ignore if ele in cmd_in_block_mod_list]
            if cmd_in_block_mod[0] != " " and len(exist_ignored_char) == 0:
                if mayor_line_not_indented != cmd_in_block_mod:
                    new_lines_to_add.append(cmd_in_block)
                    mayor_line_not_indented = cmd_in_block_mod
            elif len(exist_ignored_char) == 0:
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
            cmd_in_block_mod_list = [char for char in cmd_in_block_mod if char]
            exist_ignored_char = [ele for ele in _list_char_ignore if ele in cmd_in_block_mod_list]
            if cmd_in_block_mod[0] != " " and len(exist_ignored_char) == 0:
                if mayor_line_not_indented != cmd_in_block_mod:
                    new_lines_to_del.append(cmd_in_block)
                    mayor_line_not_indented = cmd_in_block_mod
            elif len(exist_ignored_char) == 0:
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


def find_context_var(_str1: list, _str2: list, _context_name: str, _match_type: str, _var=5): #_current_cfg, _template, _match_type, _var
    tpl = tuple(_str2)
    _str1 = clr_pos(_str1)
    _str2c = clr_pos(_str2)
    salida_json = OrderedDict()
    delta_results = ""
    missing_commands = ""
    difference_commands = ""
    try:
      diff = diffios.Compare(_str2c, _str1)
      delta_results = diff.delta()
      missing_commands = diff.pprint_missing()
      difference_commands = diff.pprint_additional()
      list_r = missing_commands.split('\n')
      if len(missing_commands)<1:
          salida_json["lines_to_add_config_file"] = ""
      else:
          #with this algorithm we take a relative position of lost element in acl.
          for line_acl in list_r:
              if re.match(r"^ip access-list.+|^!", line_acl):
                  try:
                      position1 = _str2c.index(line_acl)
                  except ValueError:
                      position1 = None
              if re.match(r".+permit\s+.+|.+deny\s+.+", line_acl) and position1 != None :
                  position2 = _str2c.index(line_acl)
                  line_acl_old = line_acl
                  if position2 < position1:
                      while position2 < position1:
                          try:
                              position2 = _str2c.index(line_acl, position2 + 1)
                          except ValueError:
                              break
                  lineposition = ((position2 - position1) * 10) - _var
                  line_acl = ' ' + str(lineposition) + ' ' + line_acl
                  position4 = list_r.index(line_acl_old)
                  list_r[position4] = line_acl
          salida_json["lines_to_add_config_file"] = list_r
      salida_json['match_type'] = _match_type
      salida_json['context_name'] = _context_name
      salida_json['original_context'] = tpl
      salida_json["lines_difference"] = difference_commands.split('\n')
      salida_json["delta_results"] = delta_results
      _success = True
      ret_msg= "Diff algorithm run successfully"  
    except Exception as error:
        _success = False
        ret_msg = f"Diff algorithm failed, error {error}"

    return salida_json, _success, ret_msg

def main():
    module = AnsibleModule(
        argument_spec=dict(
            original=dict(required=True),
            current=dict(required=True),
            type_diff=dict(required=False, type="str", choices=["config", "context"], default="config"),
            match_type=dict(required=False, type="str", choices=["include", "full", "var"], default="full"),
            lines_in_context=dict(required=False,  type="str", default="3"),
            list_char_ignore=dict(required=False,  type="list", default=["!","#"]),
            var_diff=dict(required=False,  type="int", choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 0], default=5)
        )
    )
    original = module.params.get("original")
    current = module.params.get("current")
    type_diff = module.params.get("type_diff")
    match_type = module.params.get("match_type")
    lines_in_context = int(module.params.get("lines_in_context"))
    list_char_ignore = module.params.get("list_char_ignore")
    var_diff = int(module.params.get("var_diff"))

    # Open Files
    config_orig, config_current, success_origin_current, ret_msg = open_files(original, current)

    # Diff
    if success_origin_current:
        starttime = datetime.now()
        salida_ansible = OrderedDict()
        if type_diff.lower() == "config":
            salida, success, ret_msg = find_config_diff(config_orig, config_current, lines_in_context)
            # Blocks to modify
            if success:
                salida_ansible["Diff_Results"] = salida
                # find block of lines to replace (add or delete)
                lines_to_add_snd = salida_ansible['Diff_Results']['lines_to_add']
                lines_to_del_snd = salida_ansible['Diff_Results']['lines_to_delete']
                block_snd = salida_ansible['Diff_Results']['diff']
                ret_msg, block_lines_to_add, block_lines_to_del = find_block_of_config_to_modify(list_char_ignore,
                                                                                                 block_snd,
                                                                                                 lines_to_add_snd,
                                                                                                 lines_to_del_snd)
                salida_ansible['Diff_Results']['lines_to_add'] = '\n'.join([cmd[1] for cmd in lines_to_add_snd]) if \
                    len(salida_ansible['Diff_Results']['lines_to_add']) > 0 else False
                salida_ansible['Diff_Results']['lines_to_delete'] = '\n'.join([cmd[1] for cmd in lines_to_del_snd]) if \
                    len(salida_ansible['Diff_Results']['lines_to_delete']) > 0 else False
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
            elif match_type.lower() == "var":
                salida, success, ret_msg = find_context_var(config_orig, config_current, current, match_type, var_diff)
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
