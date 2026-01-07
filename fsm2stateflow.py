###########################################################################
# FSM to Simulink Generator
#
# This module provides functionality to generate a Matlab script that
# creates a Stateflow model representation of a Finite State Machine (FSM)
# domain model.
#
############################################################################
from fsmdomainmodel import *
from typing import List, Optional, TextIO
from datetime import datetime
import sys

class FSM2StateflowGenerator:
    """Class to generate a Matlab script that creates a Stateflow model from FSM domain model"""
    
    def __init__(self):
        self.indent_level = 0
        self.indent_str = "    "

    def generate(self, fsm: Fsm, output_file: Optional[str] = None):
        """Generate Stateflow model for the state machine"""
        if output_file:
            with open(output_file, 'w') as f:
                self._generate_to_stream(fsm, f)
            print(f"Generated Matlab file: {output_file}")
        else:
            self._generate_to_stream(fsm, sys.stdout)
    
    def _generate_to_stream(self, fsm: Fsm, stream: TextIO):
        """Generate MATLAB script to create Stateflow diagram of the FSM"""
        self.stream = stream
        
        # Generate script header
        self._generate_header(fsm)
        
        # Create model and chart
        self._generate_model_creation(fsm)
        
        # Create states
        self._generate_states(fsm)
        
        # Create transitions
        self._generate_transitions(fsm)
        
        # Set initial state
        self._generate_initial_state(fsm)
        
        # Finalize
        self._generate_footer(fsm)
        

    def _generate_header(self, fsm: Fsm):
        generation_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        self._write("%" * 80)
        self._write("%% Stateflow Chart Generation Script")
        self._write(f"%% State Machine: {fsm.name}")
        self._write(f"%% Version: {fsm.version}")
        self._write(f"%% Generated on: {generation_time}")
        self._write("%" * 80)
        self._write("")
        self._write("% Clean up workspace")
        self._write("close all;")
        self._write("bdclose all;")
        self._write("")
    
    def _generate_model_creation(self, fsm: Fsm):
        """Generate model and chart creation code"""       
        
        self._write(f"%% Create new Simulink model")
        self._write(f"modelName = '{fsm.name}';")
        self._write("if bdIsLoaded(modelName)")
        self.indent_level += 1
        self._write("close_system(modelName, 0);")
        self.indent_level -= 1
        self._write("end")
        self._write("new_system(modelName);")
        self._write("open_system(modelName);")
        self._write("")
        
        self._write("%% Add Stateflow chart")
        self._write(f"chart = add_block('sflib/Chart', [modelName '/StateChart']);")
        self._write("set_param(chart, 'Position', [100 100 600 500]);")
        self._write("")
        
        self._write("%% Get chart object")
        self._write("rt = sfroot;")
        self._write("model = rt.find('-isa', 'Simulink.BlockDiagram', 'Name', modelName);")
        self._write("chartObj = model.find('-isa', 'Stateflow.Chart');")
        self._write("")
    
    def _generate_states(self, fsm: Fsm):
        """Generate state creation code"""
        self._write("%% Create states")
        
        # Calculate positions for states in a grid layout
        cols = 3 # Number of columns in the grid
        x_start = 50 # Starting x position
        y_start = 50 # Starting y position
        width = 150 # State width
        height = 120 # State height
        x_spacing = 200 # Horizontal spacing
        y_spacing = 180 # Vertical spacing
        
        for i, state in enumerate(fsm.states):
            # Layout states in a grid with 'cols' columns
            row = i // cols
            col = i % cols
            x = x_start + col * x_spacing
            y = y_start + row * y_spacing
            
            self._write(f"%% State: {state.name}")
            
            # Create state
            state_var = f"state_{state.name}"
            self._write(f"{state_var} = Stateflow.State(chartObj);")
            self._write(f"{state_var}.Name = '{state.name}';")
            self._write(f"{state_var}.Position = [{x} {y} {width} {height}];")
            
            # Build state label with entry/during/exit actions
            label_parts = []
            
            # Entry actions
            if state.on_entry_actions:
                entry_actions = self._format_actions(state.on_entry_actions)
                label_parts.append(f"entry: {entry_actions}")
            
            # Do actions
            if state.do_actions:
                during_actions = self._format_actions(state.do_actions)
                label_parts.append(f"during: {during_actions}")
            
            # Exit actions
            if state.on_exit_actions:
                exit_actions = self._format_actions(state.on_exit_actions)
                label_parts.append(f"exit: {exit_actions}")
            
            if label_parts:
                label = "\\n".join(label_parts)
                # Escape special characters for MATLAB string
                label = label.replace("'", "''")
                self._write(f"{state_var}.LabelString = '{label}';")
            
            self._write("")
        
        self._write("")
    
    def _generate_transitions(self, fsm: Fsm):
        """Generate transition creation code"""
        self._write("%% Create transitions")
        
        trans_id = 0
        for state in fsm.states:
            state_var = f"state_{state.name}"
            
            for transition in state.transitions:
                trans_id += 1
                trans_var = f"trans_{trans_id}"
                target_var = f"state_{transition.target_state}"
                
                self._write(f"%% Transition: {state.name} -> {transition.target_state}")
                self._write(f"{trans_var} = Stateflow.Transition(chartObj);")
                self._write(f"{trans_var}.Source = {state_var};")
                self._write(f"{trans_var}.Destination = {target_var};")
                
                # Build transition label
                label_parts = []
                
                # Condition
                if transition.condition and transition.condition != "true":
                    condition = self._convert_condition(transition.condition)
                    label_parts.append(f"[{condition}]")
                
                # Transition actions
                if transition.on_transition_actions:
                    actions = self._format_actions(transition.on_transition_actions)
                    if label_parts:
                        label_parts.append(f"/{actions}")
                    else:
                        label_parts.append(actions)
                
                if label_parts:
                    label = "".join(label_parts)
                    label = label.replace("'", "''")
                    self._write(f"{trans_var}.LabelString = '{label}';")
                
                self._write("")
        
        self._write("")
    
    def _generate_initial_state(self, fsm: Fsm):
        """Generate default transition to initial state"""
        self._write("%% Set initial state")
        self._write(f"defaultTrans = Stateflow.Transition(chartObj);")
        self._write(f"defaultTrans.Destination = state_{fsm.initial_state};")
        self._write(f"defaultTrans.DestinationOClock = 9;")
        self._write(f"defaultTrans.SourceEndpoint = [state_{fsm.initial_state}.Position(1)-50, state_{fsm.initial_state}.Position(2)+{60}];")
        self._write(f"defaultTrans.MidPoint = [state_{fsm.initial_state}.Position(1)-25, state_{fsm.initial_state}.Position(2)+{60}];")
        self._write("")

    def _generate_footer(self, fsm: Fsm):
        """Generate script footer"""
        self._write("%% Arrange chart layout")
        self._write("Stateflow.Root;")
        self._write("")
        self._write("%% Save model")
        self._write(f"save_system('{fsm.name}');")
        self._write("")
        self._write(f"disp('Stateflow model created: {fsm.name}.slx');")
        self._write(f"disp('Open the model and double-click the Chart block to view.');")
        self._write("")
        self._write("%" * 80)
        self._write(f"% End of Finite State Machine: {fsm.name}")
        self._write("%" * 80)

    def _generate_fsm(self, fsm: Fsm):
        """Generate Stateflow model for the FSM"""
        self._write("StateMachine:")
        self.indent_level += 1
        self._write(f"Name: {fsm.name}")
    
    def _format_actions(self, actions: List[str]) -> str:
        """Format list of actions for Stateflow label"""
        if not actions:
            return ""
        
        # Join actions with semicolons, remove trailing semicolons
        formatted = []
        for action in actions:
            action = action.strip()
            if action.endswith(';'):
                action = action[:-1]
            formatted.append(action)
        
        return "; ".join(formatted)
        
    def _convert_condition(self, condition: str) -> str:
        """Convert condition syntax to Stateflow compatible format"""
        # Replace Python/C boolean operators with MATLAB equivalents
        condition = condition.replace("==", "==")
        condition = condition.replace("&&", "&")
        condition = condition.replace("||", "|")
        condition = condition.replace("True", "true")
        condition = condition.replace("False", "false")
        return condition
    
    def _write(self, line: str):
        """Write a line with indentation"""
        indent = self.indent_str * self.indent_level
        self.stream.write(f"{indent}{line}\n")

###########################################################################
# Main Function
###########################################################################

def main():
    
    """Main function for command-line usage"""

    print("FSM to Matlab/Stateflow Generator can only be used as a package in other Python scripts.")
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