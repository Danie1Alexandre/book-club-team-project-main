from datetime import datetime

def input_positive_integer(prompt: str):
    while True:
        user_input = input(prompt)
        try:
            integer = int(user_input)
            if integer > 0:
                return integer
            else:
                print("Input must be a positive integer, try again.")
        except:
            print("Invalid input, try again.")

def input_integer_between(min: int, max: int, prompt: str):
    while True:
        user_input = input(prompt)
        try:
            integer = int(user_input)
            if integer >= min and integer <= max:
                return integer
            elif min == max:
                print(f"Input must be an integer equal to {min}, try again.")
            else:
                print(f"Input must be an integer between {min} and {max}, try again.")
        except:
            print("Invalid input, try again.")

def input_date(prompt="Enter a date, formatted as YYYY-MM-DD: ", format="%Y-%m-%d") -> str:
    while True:
        date = input(prompt).strip()
        try:
            valid_date = datetime.strptime(date, format)
            return valid_date.strftime(format)
        except:
            print("Invalid date, try again.")

def input_optional_date(prompt="Enter a date, formatted as YYYY-MM-DD: ", format="%Y-%m-%d") -> str | None:
    while True:
        date = input(prompt).strip()
        if date == "":
            return None
        try:
            valid_date = datetime.strptime(date, format)
            return valid_date.strftime(format)
        except:
            print("Invalid date, try again.")

