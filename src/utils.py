import json
import time
from typing import Dict, Any


def display_text_to_user(text):
    print(text) 
    time.sleep(1) # wait for it to render before asking for input or it'll never show up.
    
def ask_user_for_input(input_description):
    response = input(input_description)
    return response

def print_messages_so_far(state):
    print("\n------------------------------------------------------------------\n")
    messages = state.get("messages", [])
    for m in messages:
        m.pretty_print()
        print()

def print_formatted_state(state: Dict[str, Any]) -> None:
    # Convert messages to a JSON-serializable format
    serializable_state = state.copy()  # Create a copy to avoid modifying the original state
    if "messages" in serializable_state:
        serializable_state["messages"] = [
            message.dict() for message in serializable_state["messages"]
        ]  # Convert each AnyMessage to a dictionary

    # Convert to indented JSON string
    json_str = json.dumps(serializable_state, indent=4, sort_keys=True)
    print(json_str)
