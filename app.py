

# Helper functions

import time


def display_text_to_user(text):
    print(text) 
    time.sleep(1) # wait for it to render before asking for input or it'll never show up.
    
def ask_user_for_input(input_description):
    response = input(input_description)
    return response

def print_messages_so_far(state):
    print("\n#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#\n")
    for m in state["messages"]:
        m.pretty_print()
        print()
        



# Model

from model import get_model

model = get_model("openai")



# Tools

from tools import get_tools

tools = get_tools()



search_model = model.bind_tools(tools)








def main():
    print("test")


if __name__ == "__main__":
    main()


