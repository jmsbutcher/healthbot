

# # Load in the OpenAI key and Tavily key.
# # In the project folder, create a file named 'config.env'
# # ensure your .env file contains keys named OPENAI_API_KEY="your key" and TAVILY_API_KEY="your key"
# from dotenv import load_dotenv
# import os 

# load_dotenv('.env')
# assert os.getenv('OPENAI_API_KEY') is not None
# assert os.getenv('TAVILY_API_KEY') is not None





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





def main():
    print("test")


if __name__ == "__main__":
    main()


