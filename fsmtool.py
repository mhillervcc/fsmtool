###########################################################################
# FSM Tool
#
# A command-line tool for working with finite state machines (FSMs).
# It can parse FSM definitions from YAML files and generate various outputs
# such as PlantUML diagrams, C code for AUTOSAR Classic SW-Cs, C++ code for
# HPP Application Framework, Simulink models and perform graph analysis.
#
# The tool uses a the FSM Parser to read the FSM definitions and
# a number of generators to create the desired outputs.
#
############################################################################

# Import necessary standard modules
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
import argparse
import sys

# Import domain model and generators
from fsmdomainmodel import *

# Import FSM parser
from fsmparser import FSMParser

# Import generators
from fsm2yaml import *
from fsm2stateflow import *
from fsm2plantuml import *


###########################################################################
# Command Line Interface
#
# Sets up the command-line interface for the FSM tool using argparse.
# 
# The supported commands are:
# --plantuml : Generate PlantUML state diagram
# --autosar-c : Generate C code for AUTOSAR Classic SW-Cs
# --hpp-cpp : Generate C++ code for HPP Application Framework
# --stateflow : Generate a Matlab script to create a Simulink/Stateflow model
# --yaml : Generate the corresponding YAML file
# --analyze : Show detailed analysis of the FSM
#
###########################################################################
def setup_argparser():
    """Set up the argument parser for command-line usage"""
    # import argparse

    parser_cli = argparse.ArgumentParser(
        description='Parse FSM files and generate whatever your heart desires...',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a FSM file and generate a PlantUML diagram
  python fsmtool.py fsm.yaml -p/--plantuml [FILE]
  
  # Parse a FSM file and generate C code for AUTOSAR Classic SW-Cs
  python fsmtool.py fsm.yaml -c/--autosar-c [FILE]
  
  # Parse a FSM file and generate C++ code for HPP Application Framework
  python fsmtool.py fsm.yaml -b/--hpp-cpp [FILE]
  
  # Parse a FSM file and generate the corresponding Simulink/Stateflow model
  python fsmtool.py fsm.yaml -s/--stateflow [FILE]
  
  # Parse a FSM file and generate the corresponding YAML file
  python fsmtool.py fsm.yaml -y/--yaml [FILE]

  # Parse a FSM file and do graph analysis
  python fsmtool.py fsm.yaml -a/--analyze [FILE]
  
Note: If FILE is not specified, output will be printed to stdout.
Use "-" as the input file to read from stdin.

        """
    )
    
    parser_cli.add_argument(
        'file',
        help='YAML file to parse (use "-" for stdin)'
    )
    
    parser_cli.add_argument(
        '-p', '--plantuml',
        metavar='FILE',
        nargs='?',
        const=True,
        help='Generate a PlantUML state diagram, output to FILE or stdout if not specified'
    )
   
    parser_cli.add_argument(
        '-c', '--autosar-c',
        metavar='FILE',
        nargs='?',
        const=True,
        help='Generate C code for AUTOSAR Classic SW-Cs, output to FILE or stdout if not specified'
    )
    
    parser_cli.add_argument(
        '-b', '--hpp-cpp',
        metavar='FILE',
        nargs='?',
        const=True,
        help='Generate C++ code for HPP Application Framework, output to FILE or stdout if not specified'
    )
    
    parser_cli.add_argument(
        '-s', '--stateflow',
        metavar='FILE',
        nargs='?',
        const=True,
        help='Generate Simulink/Stateflow model, output to FILE or stdout if not specified'
    )
    
    parser_cli.add_argument(
        '-y', '--yaml',
        metavar='FILE',
        nargs='?',
        const=True,
        help='Generate the corresponding YAML file, output to FILE or stdout if not specified'
    )

    parser_cli.add_argument(
        '-a', '--analyze',
        metavar='FILE',
        nargs='?',
        const=True,
        help='Show detailed analysis of the FSM, output to FILE or stdout if not specified'
    )       
    
    return parser_cli

###########################################################################
# Main Function
###########################################################################

def main():
    
    """Main function for command-line usage"""
    # Set up argument parser
    parser_cli = setup_argparser()

    # Parse arguments
    args = parser_cli.parse_args()

    # Create parser instance
#    yaml_parser = YAMLASTParser()
    fsm_parser = FSMParser()

    try:
        # Parse input
        if args.file == '-':
            # Read from stdin
            yaml_content = sys.stdin.read()
            fsm = fsm_parser.parse_string(yaml_content)
        else:
            # Read from file
            fsm = fsm_parser.parse_file(args.file)

        # Generate outputs based on arguments
        if args.plantuml:
            plantuml_generator = FSM2PlantUMLGenerator()
            plantuml_generator.generate(fsm, args.plantuml if isinstance(args.plantuml, str) else None)

        if args.autosar_c:
            print("AUTOSAR C code generation not supported yet.\n")
        
        if args.hpp_cpp:
            print("HPP C++ code generation not supported yet.\n")
        
        if args.stateflow:
            stateflow_generator = FSM2StateflowGenerator()
            stateflow_generator.generate(fsm, args.stateflow if isinstance(args.stateflow, str) else None)

        if args.yaml:
            yaml_generator = FSM2YAMLGenerator()
            yaml_generator.generate(fsm, args.yaml if isinstance(args.yaml, str) else None)
        
        if args.analyze:
            print("FSM analysis not supported yet.\n")

        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1        
    
###############################################################################
# Entry Point
#
# Calls the main function only when the script is executed directly. This
# allows the script to be used both as a standalone tool and as an importable
# module.
#
###############################################################################
if __name__ == "__main__":
    main()