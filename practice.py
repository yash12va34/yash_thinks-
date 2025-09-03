import time,re,json

def sort_help(prompt: str):  
    return "i can fetch weather , wiki_summary , or create_todos"

print("enter request")
user_input = input()

def handle_user_input(user_input: str):

    if "help" in user_input.lower():
        return'sort_help(prompt=user_input)'     
    elif "weather" in user_input.lower():
        return 'plan: get_weather(city=extract_city()) format: friendly'
    elif "wiki" in user_input.lower():
        return 'plan: wiki_summary(topic = extract_topic()) format: bullet'
    elif "todo" in user_input.lower():
        return 'plan: create_todo() format: confirmation'
    else:
        return 'plan: chat(reply=sort_help()) format: plain'

result = handle_user_input(user_input)
print(result)

           


