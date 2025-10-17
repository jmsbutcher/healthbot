

import time


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

