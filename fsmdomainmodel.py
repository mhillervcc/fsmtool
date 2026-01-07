###########################################################################
# FSM Domain Model
#
# Data classes representing FSM components:
# - Fsm - This is the top-level FSM class
# - FsmState - Represents a state within the FSM
# - FsmTransition - Represents a transition between states
#
###########################################################################
from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class FsmTransition:
    """Class representing a transition in an FSM. Source state is implicit. Target state is explicit."""
    target_state: str = "No target state set"
    condition: str = "No condition set"
    priority: int = 0
    on_transition_actions: Optional[List[str]] = None

    # Representation method for debugging
    def __repr__(self, indent=0):

        spaces = " " * indent
        result = f"{spaces}- target_state: {self.target_state}\n"
        spaces += "  "
        result += f"{spaces}condition: {self.condition}\n"
        result += f"{spaces}priority: {self.priority}\n"
        result += f"{spaces}on_transition:\n"
        if self.on_transition_actions:
            result += "".join(f"{spaces}- {action}\n" for action in self.on_transition_actions)
       
        return result

@dataclass
class FsmState:
    """Class representing a state in an FSM"""
    name: str = "UnnamedState"
    is_initial: bool = False
    is_final: bool = False
    on_entry_actions: Optional[List[str]] = None
    do_actions: Optional[List[str]] = None
    on_exit_actions: Optional[List[str]] = None
    transitions: List['FsmTransition'] = field(default_factory=list)
    
    # Representation method for debugging
    def __repr__(self, indent=0):

        spaces = " " * indent
        result = f"{spaces}name: {self.name}\n"
        result += f"{spaces}is_initial: {self.is_initial}\n"
        result += f"{spaces}is_final: {self.is_final}\n"
        if self.on_entry_actions:
            result += f"{spaces}on_entry:\n"
            result += "".join(f"{spaces}- {action}\n" for action in self.on_entry_actions)
        if self.do_actions:
            result += f"{spaces}do:\n"
            result += "".join(f"{spaces}- {action}\n" for action in self.do_actions)
        if self.on_exit_actions:
            result += f"{spaces}on_exit:\n"
            result += "".join(f"{spaces}- {action}\n" for action in self.on_exit_actions)
        if self.transitions:
            result += f"{spaces}transitions:"
            for transition in self.transitions:
                result += "\n"
                result += transition.__repr__(indent + 2)
        result += "\n"

        return result 
    
@dataclass
class Fsm:
    """Class representing a Finite State Machine (FSM)"""
    name: str = "UnnamedFSM"
    version: str = "Not set"
    initial_state: str = "Not set"
    states: List[FsmState] = field(default_factory=list)

    # Representation method for debugging
    # This method provides a YAML representation of the FSM
    def __repr__(self, indent=0):

        spaces = " " * indent
        result = "statemachine:\n"
        result += f"{spaces}name: {self.name}"
        spaces += "  "
        result += f"\n{spaces}version: {self.version}"
        result += f"\n{spaces}initial_state: {self.initial_state}"

        if self.states:
            result += f"\n{spaces}states:"
            for state in self.states:
                result += "\n"
                result += state.__repr__(indent + 2)

        return result



