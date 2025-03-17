# Ansible Collection - octupus.o4n_diff

## Octupus Collection

Collection o4n_diff helps developers to find advanced diff in 2 text files.  
By Ed Scrimaglia - Manuel Saldivar - Marcos Schonfeld - Randy Rozo

## Required

Ansible >= 2.10

## Modules

o4n_diff
The module allows to find and displays the differences between two files in the context of configurartions compliance. o4n_diff works either comparing two configuration files (config mode) or a block of sentences against a configuration file or a part of a configuration file called contexts (context mode).  

o4n_find
Based on regular expressions, the module returns words or lines of words from a configuration file.  
The return includes the position where the words or line of words are located in the configuration file.  

o4n_split_config
This module extracts blocks of code from a configuration file, for example: interface configuration blocks and writes those blocks as files and then applies the o4n_diff module to find differences against contexts.  
