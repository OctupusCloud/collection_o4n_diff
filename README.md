# Ansible Collection - octupus.o4n_diff

## Octupus Collection

Collection o4n_diff helps developers to take diff with 2 text files.  
By Ed Scrimaglia - Manuel Saldivar

## Required

Ansible >= 2.10

## Modules

o4n_diff
The module allows to find and displays the differences between two files in the context of configurartions compliance. o4n_diff works either comparing two configurations files (config) or a block of sentences against a configuration file or a part of a configuration file called contexts (templates).  

o4n_find
Based on regular expresions, the module returns words or line of words from a configutation file.  
The return includes the positiion where the words or line of words are in the configuration file.

o4n_split_config
This module extract blocks of code from a configuration file, ej: interfaces configuration blocks and write those blocks down as files in order to later apply the o4n_diff module to find diferences against contexts.
