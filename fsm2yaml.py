###########################################################################
# FSM to YAML Generator
#
# This module provides functionality to generate YAML representation
# of a Finite State Machine (FSM) domain model.
#
############################################################################
from fsmdomainmodel import *
from typing import Optional, TextIO
from datetime import datetime
import sys

class FSM2YAMLGenerator:
    """Class to generate YAML from FSM domain model"""
    
    def __init__(self):
        self.indent_level = 0
        self.indent_str = "    "

    def generate(self, fsm: Fsm, output_file: Optional[str] = None):
        """Generate YAML for the state machine"""
        if output_file:
            with open(output_file, 'w') as f:
                self._generate_to_stream(fsm, f)
            print(f"Generated YAML file: {output_file}")
        else:
            self._generate_to_stream(fsm, sys.stdout)
    
    def _generate_to_stream(self, fsm: Fsm, stream: TextIO):
        """Generate YAML for the FSM"""
        self.stream = stream
        self._generate_header(fsm)
        self._generate_fsm(fsm)
        self._generate_footer(fsm)

    def _generate_header(self, fsm: Fsm):
        generation_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        self._write("#" * 80)
        self._write(f"# Generated on {generation_time}")
        self._write("#" * 80)
        self._write("")
        self._write("%YAML 1.2")
        self._write("---")
        self._write("")
        self._write("#" * 80)
        self._write(f"# Start of Finite State Machine: {fsm.name}")
        self._write("#" * 80)

    def _generate_footer(self, fsm: Fsm):
        self._write("#" * 80)
        self._write(f"# End of Finite State Machine: {fsm.name}")
        self._write("#" * 80)

    def _generate_fsm(self, fsm: Fsm):
        """Generate YAML for the FSM"""
        self._write("statemachine:")
        self.indent_level += 1
        self._write(f"name: {fsm.name}")
        self._write(f"version: {fsm.version}")
        self._write(f"description: {fsm.description}")
        self._write(f"initial_state: {fsm.initial_state}")

        if fsm.states:
            self._write("states:")
            for state in fsm.states:
                self._write("")
                self._generate_state(state)

        self.indent_level -= 1

    def _generate_state(self, state: FsmState):
        """Generate YAML for a state"""        
        self._write(f"#" + "#" * (80 - len(self.indent_str * self.indent_level) - 1))
        self._write(f"# State {state.name}")
        self._write(f"#" + "#" * (80 - len(self.indent_str * self.indent_level) - 1))
        self._write(f"-   name: {state.name}")
        self.indent_level += 1
        self._write(f"description: {state.description}")
        self._write(f"is_initial: {state.is_initial}")
        self._write(f"is_final: {state.is_final}")
        if state.on_entry_actions:
            self._write("on_entry:")
            for action in state.on_entry_actions:
                self._write(f"- {action}")
        if state.do_actions:
            self._write("do:")
            for action in state.do_actions:
                self._write(f"- {action}")
        if state.on_exit_actions:
            self._write("on_exit:")
            for action in state.on_exit_actions:
                self._write(f"- {action}")
        if state.transitions:
            self._write("transitions:")
            for transition in state.transitions:
                self._write("")
                self._generate_transition(transition, state.name)
        self._write("")
        self.indent_level -= 1

    def _generate_transition(self, transition: FsmTransition, source_state: str):
        """Generate YAML for a transition"""
       
        self._write(f"#" + "-" * (80 - len(self.indent_str * self.indent_level) - 1))
        self._write(f"# Transtition {source_state} --> {transition.target_state}")
        self._write(f"#" + "-" * (80 - len(self.indent_str * self.indent_level) - 1))
        self._write(f"-   target_state: {transition.target_state}")
        self.indent_level += 1
        self._write(f"condition: {transition.condition}")
        self._write(f"description: {transition.description}")
        self._write(f"priority: {transition.priority}")

        if transition.on_transition_actions:
            self._write("on_transition:")
            for action in transition.on_transition_actions:
                self._write(f"-   {action}")
       
        self._write("")
        self.indent_level -= 1

    def _write(self, line: str):
        """Write a line with indentation"""
        indent = self.indent_str * self.indent_level
        self.stream.write(f"{indent}{line}\n")

###########################################################################
# Main Function
###########################################################################

def main():
    
    """Main function for command-line usage"""

    print("FSM to YAML Generator can only be used as a package in other Python scripts.")
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