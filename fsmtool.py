###########################################################################
# FSM Tool
#
# A command-line tool for working with finite state machines (FSMs).
# It can parse FSM definitions from YAML files and generate various outputs
# such as PlantUML diagrams, C code for AUTOSAR Classic SW-Cs, C++ code for
# HPP Application Framework, Simulink models and perform graph analysis.
#
# The tool uses a generic YAML AST parser to read the FSM definitions and
# converts them into a domain model represented by data classes.
#
############################################################################

# Import necessary standard modules
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
import argparse
import sys
from datetime import datetime

# Import yaml_ast_parser and its components
from yaml_ast_parser import (
    YAMLASTParser,
    StreamNode,
    DocumentNode,
    MappingNode,
    SequenceNode,
    ScalarNode,
    KeyValuePair
)

# Import domain model and generators
from fsmdomainmodel import *
from fsm2yaml import *
from fsm2stateflow import *
from fsm2plantuml import *


############################################################################
# FSM Parser
# 
# Parses FSM definitions from YAML files into the FSM domain model. It uses
# a generic YAML AST parser to read the file and then converts the AST into
# the FSM data classes.
#
############################################################################

class FSMParseError(Exception):
    """Raised when FSM file structure is invalid"""
    pass

class FSMParser:

    # FSM Parser that uses YAML AST parser to read FSM definitions
    # and converts them into the FSM domain model.

    def __init__(self):
        self.yaml_parser = YAMLASTParser()
        self.current_file = None
        self.formatversion = None

    def parse_file(self, filename: str) -> Fsm:
        """Parse an FSM from a file"""
        self.current_file = filename
        ast = self.yaml_parser.parse_file(filename)
        return self._convert_ast_to_fsm(ast)

    def parse_string(self, data: str) -> Fsm:
        """Parse an FSM from a string"""
        self.current_file = "<string>"
        ast = self.yaml_parser.parse_string(data)
        return self._convert_ast_to_fsm(ast)
    
    def _convert_ast_to_fsm(self, ast: StreamNode) -> Fsm:
        """Convert the generic YAML AST to FSM domain model"""
        if not ast.documents:
            raise FSMParseError("Empty FSM file")
        
        doc = ast.documents[0]
        if not doc.root or not isinstance(doc.root, MappingNode):
            raise FSMParseError("FSM file must contain a mapping at root")
        
        return self._parse_fsm_beginning(doc.root)

    def _parse_fsm_beginning(self, mapping: MappingNode) -> Fsm:
        """Parse the beginning of the FSM structure to get name, version, and initial state"""
        data = self._mapping_to_dict(mapping)
        
        # Check if we have the 'fsmformat' key
        if 'fsmformat' not in data:
            self.formatversion = '0.1'
        else:
            self.formatversion = str(data['fsmformat'])

        # Check that we have the 'statemachine' key
        if 'statemachine' not in data:
            raise FSMParseError("FSM definition must start with the 'statemachine' key")
            
        # Let's parse the FSM now. If we have the fsmformat key, the FSM is under 'statemachine'
        # which is the second key, otherwise it's the first key.
        if 'fsmformat' in data:
            fsm_node = mapping.pairs[1].value
        else:
            fsm_node = mapping.pairs[0].value
    
        if not isinstance(fsm_node, MappingNode):
            raise FSMParseError("FSM definition must be a mapping")
        return self._parse_fsm(fsm_node)

    def _parse_fsm(self, mapping: MappingNode) -> Fsm:
        """Parse the top-level FSM structure"""
        data = self._mapping_to_dict(mapping)
        
        # Required fields
        if 'name' not in data:
            raise FSMParseError("FSM must have a 'name' field")
        if 'version' not in data:
            raise FSMParseError("FSM must have a 'version' field")
        if 'initial_state' not in data:
            raise FSMParseError("FSM must have an 'initial_state' field")
        if 'states' not in data:
            raise FSMParseError("FSM must have a 'states' field")
        
        # Create FSM instance
        fsm = Fsm(
            name = data['name'],
            version = str(data['version']),
            initial_state = data['initial_state'],
            states=[])
    
        # Parse states
        states_node = self._find_value_by_key(mapping, 'states')
        if isinstance(states_node, SequenceNode):
            # Parse each state in the list
            for state_node in states_node.elements:
                if isinstance(state_node, MappingNode):
                    fsm_state = self._parse_state(state_node)
                    if fsm_state.name == fsm.initial_state:
                        fsm_state.is_initial = True
                    fsm.states.append(fsm_state)

        return fsm
    
    def _parse_state(self, mapping: MappingNode) -> FsmState:
        """Parse a state from a mapping node"""
        data = self._mapping_to_dict(mapping)
        
        # Required fields
        if 'name' not in data:
            raise FSMParseError("A state must have a 'name' field")
        
        state = FsmState(
            name = data.get('name', 'UnnamedState'),
            is_initial = data.get('is_initial', False),
            is_final = data.get('is_final', False),
            on_entry_actions = data.get('on_entry', []),
            do_actions = data.get('do', []),
            on_exit_actions = data.get('on_exit', []),
            transitions = []
        )
        
        # Parse transitions
        transitions_node = self._find_value_by_key(mapping, 'transitions')
        if isinstance(transitions_node, SequenceNode):
            for transition_node in transitions_node.elements:
                if isinstance(transition_node, MappingNode):
                    state.transitions.append(self._parse_transition(transition_node, state))
        
        return state
    

    def _parse_transition(self, mapping: MappingNode, source_state: FsmState) -> FsmTransition:
        """Parse a transition from a mapping node"""
        data = self._mapping_to_dict(mapping)
                
        # Required fields
        if 'target_state' not in data:
            raise FSMParseError("Transition must have a 'target_state' field")
        if 'condition' not in data:
            raise FSMParseError("Transition must have a 'condition' field")
        if 'priority' not in data:
            raise FSMParseError("Transition must have a 'priority' field")
        
        transition = FsmTransition(
            target_state = data.get('target_state', 'No target state set'),
            condition = data.get('condition', 'No condition set'),
            priority = data.get('priority', 0),
            on_transition_actions = data.get('on_transition', [])
        )
        
        return transition
    
    ###########################################################################
    # Helper methods for AST traversal
    ###########################################################################
    
    def _mapping_to_dict(self, mapping: MappingNode) -> Dict[str, Any]:
        """Convert a MappingNode to a Python dictionary"""
        result = {}
        for pair in mapping.pairs:
            if isinstance(pair.key, ScalarNode):
                key = pair.key.value
                value = self._node_to_python(pair.value)
                result[key] = value
        return result
    
    def _node_to_python(self, node) -> Any:
        """Convert any AST node to Python primitive types"""
        if isinstance(node, ScalarNode):
            return node.value
        elif isinstance(node, SequenceNode):
            return [self._node_to_python(elem) for elem in node.elements]
        elif isinstance(node, MappingNode):
            return self._mapping_to_dict(node)
        return None
    
    def _find_value_by_key(self, mapping: MappingNode, key: str):
        """Find the value node for a specific key in a mapping"""
        for pair in mapping.pairs:
            if isinstance(pair.key, ScalarNode) and pair.key.value == key:
                return pair.value
        return None


###########################################################################
# Command Line Interface
#
# Sets up the command-line interface for the FSM tool using argparse.
# 
# The supported commands are:
# --plantuml : Generate PlantUML state diagram
# --autosar-c : Generate C code for AUTOSAR Classic SW-Cs
# --hpp-cpp : Generate C++ code for HPP Application Framework
# --simulink : Generate Simulink/Stateflow model
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
  python fsmtool.py fsm.yaml -s/--simulink [FILE]
  
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
# Helper Functions
###########################################################################

def write_output(content: str, filepath: Optional[str]):
    """Write content to file or stdout"""
    if filepath:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Output written to: {filepath}")
    else:
        print(content)

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
#            yamlast = yaml_parser.parse_string(yaml_content)
            fsm = fsm_parser.parse_string(yaml_content)
        else:
            # Read from file
#            yamlast = yaml_parser.parse_file(args.file)
            fsm = fsm_parser.parse_file(args.file)
                
        # print(fsm) # For debugging
        # yaml_generator.generate(fsm) # For debugging

        # Generate outputs based on arguments
        if args.plantuml:
            plantuml_generator = FSM2PlantUMLGenerator()
            plantuml_generator.generate(fsm, args.plantuml if isinstance(args.plantuml, str) else None)

        if args.autosar_c:
            write_output("AUTOSAR C code generation not supported yet.\n", None)
        
        if args.hpp_cpp:
            write_output("HPP C++ code generation not supported yet.\n", None)
        
        if args.stateflow:
            stateflow_generator = FSM2StateflowGenerator()
            stateflow_generator.generate(fsm, args.stateflow if isinstance(args.stateflow, str) else None)

        if args.yaml:
            yaml_generator = FSM2YAMLGenerator()
            yaml_generator.generate(fsm, args.yaml if isinstance(args.yaml, str) else None)
        
        if args.analyze:
            write_output("FSM analysis not supported yet.\n", None)

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