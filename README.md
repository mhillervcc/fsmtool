# fsmtool

Exploring how to generate ASTs from yaml files and then create data structures for FSM specifications for subsequent generation of different artefacts.

The main parts of this tool are the following:
- ```fsmdomainmodel.py``` - Data classes represwenting an FSM and its states and transitions. 
- ```fsm2yaml.py``` - a Generator to create YAML files from an FSM domain model representation. 
- ```fsm2stateflow.py``` - a Generator to create Matlab scripts for generating Stateflow daigrams from an FSM domain model representation. 
- ```fsm2plantuml.py``` - a Generator to create PlantUML files from an FSM domain model representation. 
- ```yaml_ast_parser.py``` - a general YAML parser that creates an abstract syntax tree of the file contents. 
- ```fsmtool.py``` - a parser for the YAML-based FSM specification format. It uses the yaml_ast_parser to create a general AST of the YAML file and then builds an FSM domain-specific data structure/AST (from ```fsmdomainmodel.py```) based on the general YAML AST. Based on this FSM AST, a number of different outputs can be generated (see below). Each output type has its own generator.

# How to use fsmtool.py
The script can be used form the command line or in other scripts. The script requires an input file and talkes an optional output filename. If no filename is given, output will be to stdout.

The following commands are envisioned (but not all yet implemented):

```
# Help 
python fsmtool.py -h/--help

# Generates PlantUML state diagram description
python fsmtool.py fsm.yaml -p/--plantuml [FILE]

# Generate AUTOSAR Classic compatible C code - NOT IMPLEMENTED YET
python fsmtool.py fsm.yaml -c/--autosar-c [FILE]

# Generate C++ code for HPP Application Framework - NOT IMPLEMENTED YET
python fsmtool.py fsm.yaml -b/--hpp-cpp [FILE]
  
# Generate the corresponding Stateflow model - NOT FULLY IMPLEMENTED YET
python fsmtool.py fsm.yaml -s/--stateflow [FILE]

# Generate the corresponding YAML file
python fsmtool.py fsm.yaml -y/--yaml [FILE]

# Perform graph analysis - NOT IMPLEMENTED YET
python fsmtool.py fsm.yaml -a/--analyze [FILE]
```

Note: If FILE is not specified, output will be printed to stdout. Use "-" as the input file to read from stdin.
