############################################################################
# FSM Parser
# 
# Parses FSM definitions from YAML files into the FSM domain model. It uses
# the standard PyYAML library to read the file and then converts the parsed
# data into the FSM data classes.
#
############################################################################

# Import necessary standard modules
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
import yaml

# Import domain model
from fsmdomainmodel import *

###########################################################################
# FSM Parser Classes
###########################################################################

class FSMParseError(Exception):
    """Raised when FSM file structure is invalid"""
    pass


class FSMParser:
    """
    FSM Parser that uses PyYAML to read FSM definitions
    and converts them into the FSM domain model.
    """

    def __init__(self):
        self.current_file = None
        self.formatversion = None

    def parse_file(self, filename: str) -> Fsm:
        """Parse an FSM from a file"""
        self.current_file = filename
        
        try:
            with open(filename, 'r') as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            raise FSMParseError(f"File not found: {filename}")
        except yaml.YAMLError as e:
            raise FSMParseError(f"Invalid YAML: {e}")
        
        return self._convert_to_fsm(data)

    def parse_string(self, yaml_string: str) -> Fsm:
        """Parse an FSM from a string"""
        self.current_file = "<string>"
        
        try:
            data = yaml.safe_load(yaml_string)
        except yaml.YAMLError as e:
            raise FSMParseError(f"Invalid YAML: {e}")
        
        return self._convert_to_fsm(data)
    
    def _convert_to_fsm(self, data: Dict) -> Fsm:
        """Convert the parsed YAML dictionary to FSM domain model"""
        if not data:
            raise FSMParseError("Empty FSM file")
        
        if not isinstance(data, dict):
            raise FSMParseError("FSM file must contain a mapping at root")
        
        return self._parse_fsm_beginning(data)

    def _parse_fsm_beginning(self, data: Dict) -> Fsm:
        """Parse the beginning of the FSM structure to get name, version, and initial state"""
        
        # Check if we have the 'fsmformat' key
        if 'fsmformat' not in data:
            self.formatversion = '0.1'
        else:
            self.formatversion = str(data['fsmformat'])

        # Check that we have the 'statemachine' key
        if 'statemachine' not in data:
            raise FSMParseError("FSM definition must start with the 'statemachine' key")
            
        # Get the statemachine data
        fsm_data = data['statemachine']
    
        if not isinstance(fsm_data, dict):
            raise FSMParseError("FSM definition must be a mapping")
        
        return self._parse_fsm(fsm_data)

    def _parse_fsm(self, data: Dict) -> Fsm:
        """Parse the top-level FSM structure"""
        
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
            name=data['name'],
            version=str(data['version']),
            description=data.get('description', 'No description'),
            initial_state=data['initial_state'],
            states=[]
        )
    
        # Parse states
        states_data = data.get('states', [])
        if not isinstance(states_data, list):
            raise FSMParseError("'states' field must be a list")
        
        for state_data in states_data:
            if isinstance(state_data, dict):
                fsm_state = self._parse_state(state_data)
                if fsm_state.name == fsm.initial_state:
                    fsm_state.is_initial = True
                fsm.states.append(fsm_state)

        return fsm
    
    def _parse_state(self, data: Dict) -> FsmState:
        """Parse a state from a dictionary"""
        
        # Required fields
        if 'name' not in data:
            raise FSMParseError("A state must have a 'name' field")
        
        state = FsmState(
            name=data.get('name', 'UnnamedState'),
            description=data.get('description', 'No description'),
            is_initial=data.get('is_initial', False),
            is_final=data.get('is_final', False),
            on_entry_actions=data.get('on_entry', []),
            do_actions=data.get('do', []),
            on_exit_actions=data.get('on_exit', []),
            transitions=[]
        )
        
        # Ensure action lists are actually lists
        if not isinstance(state.on_entry_actions, list):
            state.on_entry_actions = [state.on_entry_actions] if state.on_entry_actions else []
        if not isinstance(state.do_actions, list):
            state.do_actions = [state.do_actions] if state.do_actions else []
        if not isinstance(state.on_exit_actions, list):
            state.on_exit_actions = [state.on_exit_actions] if state.on_exit_actions else []
        
        # Parse transitions
        transitions_data = data.get('transitions', [])
        if not isinstance(transitions_data, list):
            raise FSMParseError(f"'transitions' field in state '{state.name}' must be a list")
        
        for transition_data in transitions_data:
            if isinstance(transition_data, dict):
                state.transitions.append(self._parse_transition(transition_data, state))
        
        return state
    
    def _parse_transition(self, data: Dict, source_state: FsmState) -> FsmTransition:
        """Parse a transition from a dictionary"""
        
        # Required fields
        if 'target_state' not in data:
            raise FSMParseError(f"Transition in state '{source_state.name}' must have a 'target_state' field")
        if 'condition' not in data:
            raise FSMParseError(f"Transition in state '{source_state.name}' must have a 'condition' field")
        if 'priority' not in data:
            raise FSMParseError(f"Transition in state '{source_state.name}' must have a 'priority' field")
        
        # Get on_transition actions
        on_transition_actions = data.get('on_transition', [])
        if not isinstance(on_transition_actions, list):
            on_transition_actions = [on_transition_actions] if on_transition_actions else []
        
        transition = FsmTransition(
            target_state=data.get('target_state', 'No target state set'),
            condition=data.get('condition', 'No condition set'),
            description=data.get('description', 'No description'),
            priority=data.get('priority', 0),
            on_transition_actions=on_transition_actions
        )
        
        return transition


###########################################################################
# Main Function
###########################################################################

def main():
    """Main function for command-line usage"""
    print("FSM Parser can only be used as a package in other Python scripts.")
    return 0
    

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