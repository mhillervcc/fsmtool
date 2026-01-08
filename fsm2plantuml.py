###########################################################################
# FSM to PlantUML Generator
#
# This module provides functionality to generate PlantUML representation
# of a Finite State Machine (FSM) domain model.
#
############################################################################
from fsmdomainmodel import *
from typing import Optional, TextIO
from datetime import datetime
import sys

class FSM2PlantUMLGenerator:
    """Class to generate PlantUML from FSM domain model"""
    
    def __init__(self):
        self.indent_level = 0
        self.indent_str = "    "

    def generate(self, fsm: Fsm, output_file: Optional[str] = None):
        """Generates PlantUML for the state machine"""
        if output_file:
            with open(output_file, 'w') as f:
                self._generate_to_stream(fsm, f)
            print(f"Generated PlantUML file: {output_file}")
        else:
            self._generate_to_stream(fsm, sys.stdout)
    
    def _generate_to_stream(self, fsm: Fsm, stream: TextIO):
        """Generates PlantUML for the FSM"""
        self.stream = stream
        self._generate_header(fsm)
        self._generate_fsm(fsm)
        self._generate_footer(fsm)

    def _generate_header(self, fsm: Fsm):
        """Generates PlantUML header for the FSM"""
        generation_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        self._write("/'" + "'" * 80)
        self._write("PlantUML description of FSM.")
        self._write(f"State machine: {fsm.name}")
        self._write(f"Version: {fsm.version}")
        self._write(f"Description: {fsm.description}")
        self._write(f"Generated on: {generation_time}")
        self._write("'" * 80 + "'/")
        self._write("")
        self._write("@startuml")
        self._write("hide empty description")
        self._write("")

    def _generate_footer(self, fsm: Fsm):
        """Generates PlantUML footer for the FSM"""
        self._write("/'" + "'" * 80)
        self._write(f" End of Finite State Machine: {fsm.name}")
        self._write("'" * 80 + "'/")
        self._write("")
        self._write("@enduml")

    def _generate_fsm(self, fsm: Fsm):
        """Generates PlantUML for the FSM"""

        self._write(f"title State diagram for {fsm.name}, version {fsm.version}")
        self._write("")
        if fsm.states:
            for state in fsm.states:
                self._generate_state(state)


    def _generate_state(self, state: FsmState):
        # This method provides a PlantUML representation of the state
        """Generates PlantUML representation of a state."""
        
        self._write("/'" + "'" * 80)
        self._write(f" State: {state.name}")
        self._write("'" * 80 + "'/")

        # Start with all the transitions
        if state.is_initial:
            self._write(f"[*] --> {state.name}")

        for transition in state.transitions:
            self._generate_transition(transition, state.name)
        
        if state.is_final:
            self._write(f"{state.name} --> [*]")

        # Now add the state description if it exists
        if state.description and state.description != "No description":
            self._write(f"{state.name} : {state.description}")
            self._write("")

        # Now add actions as comments in the state
        if state.on_entry_actions:
            self._write(f"{state.name} : \\nOn entry actions:")
            for on_entry_action in (state.on_entry_actions):
                self._write(f"{state.name} : {on_entry_action}")
            self._write("")
        
        if state.do_actions:
            self._write(f"{state.name} : \\nDo actions:")
            for do_action in (state.do_actions):
                self._write(f"{state.name} : {do_action}")
            self._write("")
        
        if state.on_exit_actions:
            self._write(f"{state.name} : \\nOn exit actions:")
            for on_exit_action in (state.on_exit_actions):
                self._write(f"{state.name} : {on_exit_action}")
            self._write("")
        
        self._write("")

    def _generate_transition(self, transition: FsmTransition, source_state: str):
        """Generates PlantUML for a transition."""
        self._write(f"{source_state} --> {transition.target_state} : Condition: {transition.condition}"\
                        + (f"\\n Description: {transition.description}" if transition.description and transition.description != "No description" else "")\
                        + (f"\\n Priority: {transition.priority}" if transition.priority is not None else "")\
                        + (f"\\n Actions: {', '.join(transition.on_transition_actions)}" if transition.on_transition_actions else ""))
     
        self._write("")

    def _write(self, line: str):
        """Write a line with indentation"""
        indent = self.indent_str * self.indent_level
        self.stream.write(f"{indent}{line}\n")

###########################################################################
# Main Function
###########################################################################

def main():
    
    """Main function for command-line usage"""

    print("FSM to PlantUML Generator can only be used as a package in other Python scripts.")
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