#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
---
module: o4n_diff
short_description: Analiza compliance entre configuraciones de red, ejecutando algoritmo Diff
description:
  - Realiza análisis de compliance entre configuraciones de dispositivos de red
  - Soporta comparación completa de configuraciones (config)
  - Soporta comparación de contextos específicos (context)
  - Permite diferentes estrategias de matching para contextos
  - Maneja casos especiales como ACLs y variables en templates
version_added: "3.0"
author: 
  - "Ed Scrimaglia"
notes:
  - Soporta Context tipo 'var' solo para dispositivos Cisco IOS/IOS-XE
  - Testeado en Linux
requirements:
  - ansible >= 2.10
  - python >= 3.6
  - diffios
options:
  original:
    description:
      - Archivo que contiene la configuración master o template de contexto
      - Para type_diff=config, es la golden config
      - Para type_diff=context, es el template de contexto
    required: true
    type: str
  current:
    description:
      - Archivo que contiene la configuración actual del dispositivo
    required: true
    type: str
  type_diff:
    description:
      - Tipo de análisis de compliance a realizar
    required: false
    choices:
      - config: Compara configuración completa contra master config
      - context: Compara un contexto específico contra la config del dispositivo
    default: config
    type: str
  match_type:
    description:
      - Estrategia de matching para comparación de contextos
      - Solo aplica cuando type_diff=context
    required: false
    choices:
      - full: Verifica coincidencia exacta de las líneas
      - include: Verifica que las líneas del contexto estén incluidas en la config
      - var: Permite variables tipo {{ var }} en el contexto
    default: full
    type: str
  lines_in_context:
    description:
      - Número de líneas de contexto a mostrar en el diff
    required: false
    default: "3"
    type: str
  list_char_ignore:
    description:
      - Lista de caracteres a ignorar en la comparación
    required: false
    default: ['!', '#']
    type: list
  var_diff:
    description:
      - Offset para cálculo de posiciones en ACLs
      - Solo aplica para ACLs cuando match_type=var
    required: false
    choices: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    default: 5
    type: int
"""

EXAMPLES = """
# Comparación completa contra master config
- name: Verificar compliance contra master config
  o4n_diff:
    original: "./master_configs/device1_master.txt"
    current: "./device_configs/device1_current.txt"
    type_diff: config
  register: compliance_result
  # Master config ejemplo:
  # interface GigabitEthernet0/1
  #  description UPLINK TO CORE
  #  ip address 10.1.1.1 255.255.255.0
  #  no shutdown

# Verificar contexto específico (match exacto)
- name: Verificar contexto de interfaces
  o4n_diff:
    original: "./contexts/interface_context.txt"
    current: "./device_configs/device1_current.txt"
    type_diff: context
    match_type: full
  register: interface_compliance
  # Contexto ejemplo:
  # interface GigabitEthernet0/1
  #  description UPLINK TO CORE
  #  spanning-tree portfast
  #  no shutdown

# Verificar contexto con matching inclusivo
- name: Verificar configuración de seguridad en interfaces
  o4n_diff:
    original: "./contexts/security_context.txt"
    current: "./device_configs/device1_current.txt"
    type_diff: context
    match_type: include
  register: security_compliance
  # Contexto ejemplo:
  # interface GigabitEthernet0/1
  #  storm-control broadcast
  #  ip verify unicast source
  #  spanning-tree bpduguard enable

# Verificar contexto con variables
- name: Verificar template de interfaz
  o4n_diff:
    original: "./contexts/interface_template.txt"
    current: "./device_configs/device1_current.txt"
    type_diff: context
    match_type: var
    var_diff: 5
  register: interface_var_compliance
  # Template ejemplo:
  # interface {{ INTERFACE }}
  #  description {{ DESC }}
  #  ip address {{ IP_ADDRESS }} {{ MASK }}
  #  no ip proxy-arp
  #  no shutdown

# Ignorar caracteres específicos
- name: Verificar compliance ignorando comentarios
  o4n_diff:
    original: "./master_configs/device1_master.txt"
    current: "./device_configs/device1_current.txt"
    type_diff: config
    list_char_ignore: ['!', '#', '*']
  register: compliance_no_comments
  # Ejemplo con comentarios:
  # ! Interface principal
  # interface GigabitEthernet0/1
  # # Uplink to core
  #  description UPLINK TO CORE
  #  ip address 10.1.1.1 255.255.255.0
"""

RETURN = """
msg:
    description: Mensaje indicando el resultado de la operación
    type: str
    returned: always
    sample: "Compliance analysis completed successfully"
content:
    description: Resultados del análisis de compliance
    type: dict
    returned: always
    contains:
        Diff_Results:
            description: Detalles del análisis de compliance
            type: dict
            returned: always
            contains:
                match_type:
                    description: Tipo de matching usado
                    type: str
                    returned: when type_diff=context
                    sample: "var"
                context_name:
                    description: Nombre del contexto analizado
                    type: str
                    returned: when type_diff=context
                    sample: "interface_context"
                original_context:
                    description: Contexto/template original
                    type: tuple
                    returned: when type_diff=context
                    sample: [
                        "interface {{ INTERFACE }}",
                        " description {{ DESC }}",
                        " ip address {{ IP }} {{ MASK }}",
                        " no shutdown"
                    ]
                lines_to_add_config_file:
                    description: Líneas que faltan en la configuración
                    type: list
                    returned: always
                    sample: [
                        "interface GigabitEthernet0/1",
                        " description UPLINK TO CORE",
                        " no shutdown"
                    ]
                diff:
                    description: Diferencias completas en formato unificado
                    type: str
                    returned: when type_diff=config
                    sample: "--- original\n+++ current\n@@ -1,6 +1,6 @@\n interface GigabitEthernet0/1\n- description UPLINK TO CORE\n- ip address 10.1.1.1 255.255.255.0\n- no shutdown\n+ description BACKUP LINK\n+ ip address 10.1.1.2 255.255.255.0\n+ shutdown"
                block_to_add:
                    description: Bloques completos de configuración que deben agregarse
                    type: str
                    returned: when type_diff=config
                    sample: "interface GigabitEthernet0/1\n description UPLINK TO CORE\n ip address 10.1.1.1 255.255.255.0\n no shutdown"
                block_to_del:
                    description: Bloques completos de configuración que deben eliminarse
                    type: str
                    returned: when type_diff=config
                    sample: "interface GigabitEthernet0/1\n description BACKUP LINK\n ip address 10.1.1.2 255.255.255.0\n shutdown"
                lines_to_delete:
                    description: Líneas que deben eliminarse
                    type: list
                    returned: when type_diff=config
                    sample: [
                        "interface GigabitEthernet0/1",
                        " description BACKUP LINK",
                        " shutdown"
                    ]
                lines_included:
                    description: Líneas encontradas y dónde
                    type: dict
                    returned: when match_type=include
                    sample: {
                        "interface GigabitEthernet0/1": [
                            "Line included in config line: interface GigabitEthernet0/1"
                        ],
                        " no ip proxy-arp": [
                            "Line included in config line:  no ip proxy-arp"
                        ]
                    }
                lines_difference:
                    description: Diferencias encontradas
                    type: list
                    returned: when match_type=var
                    sample: [
                        "interface GigabitEthernet0/1",
                        " description UPLINK TO CORE",
                        " ip address 10.1.1.1 255.255.255.0"
                    ]
                delta_results:
                    description: Resultados del diff
                    type: str
                    returned: when match_type=var
                    sample: "--- baseline\n+++ comparison\n@@ -1,4 +1,4 @@\n interface GigabitEthernet0/1\n- description UPLINK TO CORE\n+ description BACKUP LINK\n  ip address 10.1.1.1 255.255.255.0\n  no shutdown"
                compliance_rate:
                    description: Porcentaje de cumplimiento
                    type: float
                    returned: always
                    sample: 75.0
                compliance_status:
                    description: Estado del compliance (OK/Failed)
                    type: str
                    returned: always
                    sample: "Failed"
        Total_execution_time:
            description: Tiempo total de ejecución
            type: str
            returned: always
            sample: "0:00:00.123456"
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime
from collections import OrderedDict
import difflib
import diffios
import re
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from ansible.module_utils.basic import AnsibleModule



class ComplianceType(Enum):
    """
    Define los tipos de compliance soportados por el módulo.

    Attributes:
        CONFIG: Para comparación completa de configuraciones master vs device
        CONTEXT: Para comparación de contextos específicos contra device
    """
    CONFIG = "config"
    CONTEXT = "context"

class MatchStrategy(Enum):
    """
    Define las estrategias de comparación para contextos.

    Attributes:
        FULL: Comparación exacta línea por línea
        INCLUDE: Verifica si las líneas del contexto están incluidas en la configuración
        VAR: Permite el uso de variables en el contexto (formato {{ variable }})
    """
    FULL = "full" 
    INCLUDE = "include"
    VAR = "var"

@dataclass
class ComplianceConfig:
    """
    Configuración para el análisis de compliance.

    Attributes:
        original_file: Ruta al archivo de configuración master o contexto
        current_file: Ruta al archivo de configuración del dispositivo
        compliance_type: Tipo de compliance a realizar (CONFIG o CONTEXT)
        match_strategy: Estrategia de comparación para contextos
        context_lines: Número de líneas de contexto para el diff
        ignore_chars: Lista de caracteres a ignorar en la comparación
        var_offset: Offset para posicionamiento en ACLs
    """
    original_file: str
    current_file: str
    compliance_type: ComplianceType
    match_strategy: MatchStrategy = MatchStrategy.FULL
    context_lines: int = 3
    ignore_chars: List[str] = None
    var_offset: int = 5


class ConfigurationReader:
    """
    Clase responsable de leer archivos de configuración.
    Separa la responsabilidad de lectura de archivos del resto de la lógica.
    """

    @staticmethod
    def read_config(filename: str) -> List[str]:
        """
        Lee y valida un archivo de configuración.

        Args:
            filename: Ruta al archivo de configuración a leer

        Returns:
            Lista de líneas del archivo de configuración

        Raises:
            ValueError: Si el archivo está vacío
            IOError: Si hay error al leer el archivo
        """
        try:
            with open(filename, 'r') as f:
                content = f.read().strip().splitlines()
                if not content:
                    raise ValueError(f"El archivo {filename} está vacío")
                return content
        except Exception as e:
            raise IOError(f"Error al leer {filename}: {str(e)}")


class ACLProcessor:
    """
    Procesador especializado para Access Control Lists (ACLs).
    Maneja la limpieza y cálculo de posiciones relativas en ACLs.
    """
    
    
    def __init__(self, position_offset: int = 5):
        """
        Args:
            position_offset: Valor de offset para el cálculo de posiciones
        """

        self.position_offset = position_offset

    def clean_positions(self, config_lines: List[str]) -> List[str]:
        """
        Limpia los números de secuencia de las ACLs.

        Args:
            config_lines: Lista de líneas de configuración

        Returns:
            Lista de líneas con los números de secuencia removidos
        
        Example:
            Input: " 10 permit ip any any"
            Output: " permit ip any any"
        """

        cleaned = config_lines.copy()
        for idx, line in enumerate(cleaned):
            if re.match(r"^\s+\d+\s+permit.+$|^\s+\d+\s+deny.+$", line):
                parts = line.split()
                cleaned[idx] = f" {parts[2]} {' '.join(parts[3:])}"
        return cleaned

    def calculate_positions(self, missing_lines: List[str], context_lines: List[str]) -> List[str]:
        """
        Calcula las posiciones relativas para las reglas de ACL.

        Args:
            missing_lines: Líneas que faltan en la configuración
            context_lines: Líneas del contexto original

        Returns:
            Lista de líneas con posiciones calculadas
        """

        result = []
        current_acl = None
        
        for line in missing_lines:
            if re.match(r"^ip access-list.+|^!", line):
                current_acl = line
                result.append(line)
            elif re.match(r".+permit\s+.+|.+deny\s+.+", line) and current_acl:
                try:
                    acl_start = context_lines.index(current_acl)
                    rule_pos = context_lines.index(line, acl_start)
                    relative_pos = ((rule_pos - acl_start) * 10) - self.position_offset
                    result.append(f" {relative_pos} {line.lstrip()}")
                except ValueError:
                    result.append(line)
            else:
                result.append(line)
                
        return result


class ConfigBlockProcessor:
    """
    Procesador de bloques de configuración.
    Maneja la identificación y procesamiento de bloques jerárquicos de configuración.
    """

    def process_blocks(self, block_content: str, lines_to_add: List[Tuple], 
                      lines_to_delete: List[Tuple], ignore_chars: List[str]) -> Dict[str, str]:
        """
        Procesa bloques de configuración manteniendo la jerarquía padre-hijo.
        
        Args:
            block_content: Contenido completo del bloque a procesar
            lines_to_add: Lista de tuplas (índice, línea) de líneas a agregar
            lines_to_delete: Lista de tuplas (índice, línea) de líneas a eliminar
            ignore_chars: Lista de caracteres a ignorar en el procesamiento
            
        Returns:
            Dict con bloques procesados
        """
        # Limpia el contenido del bloque
        clean_lines = [
            line for line in block_content.splitlines()
            if not line.startswith(('---', '+++'))
        ]

        indexed_lines = list(enumerate(clean_lines))

        # Procesa bloques para agregar y eliminar
        add_blocks = self._process_hierarchical_block(indexed_lines, lines_to_add, ignore_chars)
        delete_blocks = self._process_hierarchical_block(indexed_lines, lines_to_delete, ignore_chars)

        return {
            'block_to_add': add_blocks,
            'block_to_del': delete_blocks
        }

    def _process_hierarchical_block(self, 
                                  indexed_lines: List[Tuple[int, str]], 
                                  change_lines: List[Tuple],
                                  ignore_chars: List[str]) -> List[str]:
        """
        Procesa un bloque manteniendo la jerarquía de comandos.

        Args:
            block_lines: Líneas del bloque a procesar
            change_lines: Líneas con cambios a procesar
            ignore_chars: Caracteres a ignorar

        Returns:
            Lista de líneas procesadas manteniendo la jerarquía
        """

        processed_lines = []
        mayor_line_not_indented = None

        try:
            for orig_line in change_lines:
                line_in_block = indexed_lines[orig_line[0]]
                ind_in_bloc = line_in_block[0]
                cmd_in_block = line_in_block[1]
                cmd_in_block_mod = cmd_in_block.replace(cmd_in_block[0], "", 1)
                cmd_in_block_mod_list = [char for char in cmd_in_block_mod if char]
                exist_ignored_char = [ele for ele in ignore_chars if ele in cmd_in_block_mod_list]

                # Verificar si es línea principal (no indentada)
                if not cmd_in_block_mod.startswith(" ") and not exist_ignored_char:
                    if mayor_line_not_indented != cmd_in_block_mod:
                        processed_lines.append(cmd_in_block[1:])
                        mayor_line_not_indented = cmd_in_block_mod
                
                # Si es línea indentada
                elif not exist_ignored_char:
                    # Buscar su línea padre
                    for prev_idx in indexed_lines[ind_in_bloc::-1]:
                        prev_line = prev_idx[1]
                        prev_line_mod = prev_line.replace(prev_line[0], "", 1)
                        
                        if not prev_line_mod.startswith(" "):
                            if mayor_line_not_indented != prev_line_mod:
                                processed_lines.append(prev_line[1:])
                                mayor_line_not_indented = prev_line_mod
                            processed_lines.append(cmd_in_block[1:])
                            break

            return '\n'.join(processed_lines) if processed_lines else False
            
        except Exception:
            return False


class ComplianceStrategy(ABC):
    """
    Interfaz base para todas las estrategias de compliance.
    Define el contrato que deben cumplir todas las estrategias de comparación.
    """
    
    @abstractmethod
    def compare(self, original: List[str], current: List[str], **kwargs) -> Dict:
        """
        Método abstracto para realizar la comparación según la estrategia.

        Args:
            original: Lista de líneas de la configuración master/contexto
            current: Lista de líneas de la configuración del dispositivo
            **kwargs: Argumentos adicionales según la estrategia

        Returns:
            Diccionario con los resultados de la comparación
        """
        pass

class FullConfigComplianceStrategy(ComplianceStrategy):
    """
    Estrategia para comparación completa de configuraciones.
    Compara la configuración completa del dispositivo contra una master config.
    """

    def __init__(self):
        """Inicializa el procesador de bloques para esta estrategia"""
        self.block_processor = ConfigBlockProcessor()
    
    def compare(self, current: List[str], original: List[str], **kwargs) -> Dict:
        """
        Realiza la comparación completa de configuraciones.

        Args:
            current: Configuración del dispositivo
            original: Configuración master
            **kwargs: Argumentos adicionales (context_lines, ignore_chars)

        Returns:
            Diccionario con resultados incluyendo diff, bloques y compliance rate
        """

        context_lines = kwargs.get('context_lines', 3)
        ignore_chars = kwargs.get('list_char_ignore', ['!', '#'])
        
        diff = difflib.unified_diff(
            original, current,
            fromfile='original',
            tofile='current',
            n=context_lines,
            lineterm=''
        )
        
        diff_lines = list(diff)
        added = []
        removed = []
        
        for idx, line in enumerate(diff_lines[2:]):
            if line.startswith('+'):
                added.append((idx, line))
            elif line.startswith('-'):
                removed.append((idx, line))
        
        # Procesa los bloques de configuración
        block_results = self.block_processor.process_blocks(
            '\n'.join(diff_lines),
            removed,  # Para agregar (estaban en original)
            added,    # Para eliminar (están en current)
            ignore_chars
        )

        total_lines = len(original)
        total_changes_needed = len(added) + len(removed)
        
        if total_changes_needed == 0:  # Si no hay cambios necesarios
            compliance_rate = 100.0
            compliance_status = "OK"
        else:
            compliance_rate = ((total_lines - total_changes_needed) / total_lines) * 100
            compliance_rate = max(0, round(compliance_rate, 2))
            compliance_status = "Failed"

        return OrderedDict({
            'diff': '\n'.join(diff_lines),
            'lines_to_delete': added,    # Líneas a eliminar (están en current)
            'lines_to_add': removed,     # Líneas a agregar (estaban en original)
            'block_to_add': block_results['block_to_add'],
            'block_to_del': block_results['block_to_del'],
            'compliance_rate': compliance_rate,
            'compliance_status': compliance_status
        })


class ContextFullComplianceStrategy(ComplianceStrategy):
    """
    Estrategia para comparación exacta de contextos.
    Verifica que el contexto exista exactamente en la configuración del dispositivo.
    """

    def compare(self, current: List[str], original: List[str], **kwargs) -> Dict:
        """
        Compara un contexto con la configuración del dispositivo.

        Args:
            current: Configuración del dispositivo
            original: Contexto a verificar
            **kwargs: Argumentos adicionales (context_lines, context_name)

        Returns:
            Diccionario con resultados incluyendo líneas faltantes y compliance rate
        """

        diff = difflib.unified_diff(
            original,   # context_template
            current,    # device_config
            fromfile='original',
            tofile='current',
            n=kwargs.get('context_lines', 3),
            lineterm=''
        )
        
        diff_lines = list(diff)[2:]
        to_add = []
        header = 0
        
        # Buscamos líneas con '-' que son las que están en el contexto pero no en el dispositivo
        for line in diff_lines:
            if line.startswith('-'):
                if re.search(r"\{\{\s*.*?\s*\}\}", line[1:]):
                    header = 1
                to_add.append(line[1:])

        # Cálculo del compliance rate
        total_lines = len(original)  # Total de líneas en el contexto
        missing_lines = len(to_add) - header  # Líneas que faltan
        
        if missing_lines == 0:  # Si no faltan líneas
            compliance_rate = 100.0
            compliance_status = "OK"
        else:
            compliance_rate = ((total_lines - missing_lines) / total_lines) * 100
            compliance_rate = round(compliance_rate, 2)
            compliance_status = "Failed"

        return OrderedDict({
            'match_type': 'full',
            'context_name': kwargs.get('context_name', '').split('/')[-1].split('.')[0],
            'original_context': tuple(original),
            'lines_to_add_config_file': to_add if compliance_status == "Failed" else "",
            'compliance_rate': compliance_rate,
            'compliance_status': compliance_status
        })


class ContextIncludeComplianceStrategy(ComplianceStrategy):
    """
    Estrategia para verificación de inclusión de contextos
    Args:
        original: El contexto a buscar
        current: La configuración del dispositivo
    """
    
    def compare(self, current: List[str], original: List[str], **kwargs) -> Dict:
        """
        Verifica la inclusión de líneas del contexto.

        Args:
            current: Configuración del dispositivo
            original: Contexto a verificar
            **kwargs: Argumentos adicionales (context_name)

        Returns:
            Diccionario con resultados incluyendo líneas incluidas y no incluidas
        """

        included_lines = OrderedDict()
        not_included = []
        header = 0

        for context_line in original:
            matches = []
            for config_line in current:
                if context_line in config_line:
                    matches.append(f"Line included in config line: {config_line}")
            
            if matches:
                included_lines[context_line] = matches

            else:
                # Se busca linea header en el contexto
                if re.search(r"\{\{\s*.*?\s*\}\}", context_line):
                    header = 1
                not_included.append(context_line)
        
         # Cálculo del compliance rate
        total_lines = len(original)
        not_included_count = len(not_included) - header
        
        if not_included_count == 0:  # Si no hay líneas faltantes
            compliance_rate = 100.0
            compliance_status = "OK"
        else:
            compliance_rate = ((total_lines - not_included_count) / total_lines) * 100
            compliance_rate = round(compliance_rate, 2)
            compliance_status = "Failed"

        return OrderedDict({
            'match_type': 'include',
            'context_name': kwargs.get('context_name', '').split('/')[-1].split('.')[0],
            'original_context': tuple(original),
            'lines_included': included_lines,
            'lines_to_add_config_file': not_included if compliance_status == "Failed" else [],
            'compliance_rate': compliance_rate,
            'compliance_status': compliance_status
        })


class ContextVarComplianceStrategy(ComplianceStrategy):
    """
    Estrategia para comparación de contextos con variables.
    Permite el uso de variables en formato {{ variable }} en los contextos
    y maneja casos especiales como ACLs.
    """
    
    def __init__(self, acl_processor: ACLProcessor):
        """
        Args:
            acl_processor: Procesador para manejo especial de ACLs
        """

        self.acl_processor = acl_processor

    def _is_acl_config(self, config_lines: List[str]) -> bool:
        """
        Determina si una configuración es una ACL.

        Args:
            config_lines: Líneas de configuración a analizar

        Returns:
            True si es una ACL, False en caso contrario
        """

        for line in config_lines:
            if line.strip().startswith("ip access-list"):
                return True
        return False

    def compare(self, current: List[str], original: List[str], **kwargs) -> Dict:
        """
        Realiza la comparación usando diffios, con procesamiento especial para ACLs.
        Args:
            original: El contexto/template con variables
            current: La configuración del dispositivo
        """
        try:
            if self._is_acl_config(current):
                # Si es una ACL, aplica el procesamiento especial
                cleaned_original = self.acl_processor.clean_positions(original)
                cleaned_current = self.acl_processor.clean_positions(current)
                
                diff = diffios.Compare(cleaned_original, cleaned_current)
                missing = diff.pprint_missing().split('\n')
                
                # Procesa las posiciones para ACLs
                processed_lines = self.acl_processor.calculate_positions(
                    missing, cleaned_original
                )
            else:
                # Si no es ACL, usa diffios directamente
                diff = diffios.Compare(original, current)
                processed_lines = diff.pprint_missing().split('\n')
            
            # Filtramos líneas vacías y obtenemos líneas que faltan
            real_missing_lines = [line for line in processed_lines if line.strip()]
            total_real_missing_lines = len(real_missing_lines)

            # Filtramos líneas vacías y obtenemos lineas del contexto original
            total_config_lines = len([line for line in original 
                                      if line.strip()])

            if total_real_missing_lines == 0:
                compliance_rate = 100.0
                compliance_status = "OK"
            else:
                compliance_rate = max(0, min(100, 
                    ((total_config_lines - total_real_missing_lines) / total_config_lines) * 100))
                compliance_rate = round(compliance_rate, 2)
                compliance_status = "Failed"

            return OrderedDict({
                'lines_to_add_config_file': real_missing_lines,
                'match_type': 'var',
                'context_name': kwargs.get('context_name', '').split('/')[-1].split('.')[0],
                'original_context': tuple(original),
                'lines_difference': diff.pprint_additional().split('\n'),
                'delta_results': diff.delta(),
                'compliance_rate': compliance_rate,
                'compliance_status': compliance_status
            })  

        except Exception as e:
            raise RuntimeError(f"Error en comparación: {str(e)}")


class ComplianceStrategyFactory:
    """
    Fábrica para crear estrategias de compliance.
    Implementa el patrón Factory para instanciar la estrategia apropiada
    según el tipo de compliance y estrategia de matching requerida.
    """

    def __init__(self):
        """Inicializa la fábrica con un procesador de ACLs compartido"""
        self.acl_processor = ACLProcessor()

    def create_strategy(self, compliance_type: ComplianceType,
                       match_strategy: MatchStrategy = None) -> ComplianceStrategy:
        """
        Crea y retorna la estrategia apropiada según los parámetros.

        Args:
            compliance_type: Tipo de compliance a realizar (CONFIG o CONTEXT)
            match_strategy: Estrategia de matching para contextos (FULL, INCLUDE, VAR)

        Returns:
            Una instancia de la estrategia apropiada

        Raises:
            ValueError: Si el tipo de compliance no está soportado
        """
        if compliance_type == ComplianceType.CONFIG:
            return FullConfigComplianceStrategy()

        if compliance_type == ComplianceType.CONTEXT:
            if match_strategy == MatchStrategy.INCLUDE:
                return ContextIncludeComplianceStrategy()
            elif match_strategy == MatchStrategy.VAR:
                return ContextVarComplianceStrategy(self.acl_processor)
            else:  # FULL por defecto
                return ContextFullComplianceStrategy()

        raise ValueError(f"Tipo de compliance no soportado: {compliance_type}")

class ComplianceAnalyzer:
    """
    Analizador principal de compliance.
    Coordina el proceso completo de análisis de compliance usando
    la estrategia apropiada según la configuración proporcionada.
    """
    
    def __init__(self, config: ComplianceConfig):
        """
        Args:
            config: Configuración completa para el análisis
        """
        self.config = config
        self.strategy_factory = ComplianceStrategyFactory()

    def analyze(self) -> Dict:
        """
        Realiza el análisis completo de compliance.

        Returns:
            Diccionario con los resultados del análisis

        Raises:
            RuntimeError: Si ocurre un error durante el análisis
            
        Example:
            analyzer = ComplianceAnalyzer(config)
            results = analyzer.analyze()
            # results contiene compliance_rate, líneas faltantes, etc.
        """
        try:
            current_config = ConfigurationReader.read_config(self.config.current_file)
            original_config = ConfigurationReader.read_config(self.config.original_file)

            strategy = self.strategy_factory.create_strategy(
                self.config.compliance_type,
                self.config.match_strategy
            )

            result = strategy.compare(
                current_config,
                original_config,
                context_name=self.config.original_file,
                context_lines=self.config.context_lines,
                ignore_chars=self.config.ignore_chars,
                var_offset=self.config.var_offset
            )


            return result

        except Exception as e:
            raise RuntimeError(f"Error en análisis de compliance: {str(e)}")


def main():
    """
    Punto de entrada principal para el módulo de Ansible.
    Configura el módulo, procesa los parámetros y ejecuta el análisis.

    La función maneja:
    - Validación de parámetros
    - Creación de la configuración
    - Ejecución del análisis
    - Formateo de resultados para Ansible
    - Manejo de errores
    """
    module = AnsibleModule(
        argument_spec=dict(
            current=dict(required=True, type='str'),
            original=dict(required=True, type='str'),
            type_diff=dict(required=False, type='str', 
                         choices=['config', 'context'], 
                         default='config'),
            match_type=dict(required=False, type='str',
                          choices=['include', 'full', 'var'],
                          default='full'),
            lines_in_context=dict(required=False, type='str', default='3'),
            list_char_ignore=dict(required=False, type='list', 
                                default=['!', '#']),
            var_diff=dict(required=False, type='int',
                         choices=range(10), default=5)
        )
    )

    try:
        start_time = datetime.now()
        
        # Crea la configuración desde los parámetros de Ansible
        config = ComplianceConfig(
            current_file=module.params['current'],
            original_file=module.params['original'],
            compliance_type=ComplianceType(module.params['type_diff']),
            match_strategy=MatchStrategy(module.params['match_type']),
            context_lines=int(module.params['lines_in_context']),
            ignore_chars=module.params['list_char_ignore'],
            var_offset=module.params['var_diff']
        )

        # Ejecuta el análisis
        analyzer = ComplianceAnalyzer(config)
        result = analyzer.analyze()

        execution_time = datetime.now() - start_time

        # Retorna el resultado exitoso
        module.exit_json(
            msg="Compliance analysis completed successfully",
            content={
                'Diff_Results': result,
                'Total_execution_time': str(execution_time)
            }
        )

    except Exception as e:
        # Retorna el error
        module.fail_json(msg=f"Error during compliance analysis: {str(e)}")

if __name__ == '__main__':
    main()
