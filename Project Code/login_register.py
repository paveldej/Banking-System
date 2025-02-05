import json, re, random
from tools import *
import PySimpleGUI as sg
# Register functionality

def create_empty_transactions(personal_number):
    data = {
        "in":{},
        "out":{}
    }
    with open (f"./data/{personal_number}_transactions.json", "w") as file:
        json.dump(data, file, indent=4)
    

def create_empty_expenses(personal_number):
    data = {
        
    }
    with open (f"./data/{personal_number}_expenses.json", "w") as file:
        json.dump(data, file, indent=4)


def check_password(password):
    is_correct = False
    match_pattern = re.compile(r"""
                # Validate password: 2 upper, 1 special, 2 digit, 1 lower, 8 chars.
                ^                        # Anchor to start of string.
                (?=(?:[^A-Z]*[A-Z]){2})  # At least two uppercase.
                (?=[^!@#$&*]*[!@#$&*])   # At least one "special".
                (?=(?:[^0-9]*[0-9]){2})  # At least two digit.
                .{8,}                    # Password length is 8 or more.
                $                        # Anchor to end of string.
                """, re.VERBOSE)

    my_list = re.findall(match_pattern, password)

    if len(my_list) != 0:
        is_correct = True
    return is_correct


def check_username(username):
    is_correct = False
    # regex pattern matches all words that start with uppercase and
    # are followed by lowercase and some boundary like space
    match_pattern = r"\b[A-Z]{1}[a-z]+\b"
    name_list = re.findall(match_pattern, username)
    if len(name_list) == len(username.split(" ")):
        is_correct = True

    return is_correct


def determine_leap_year(year):
    is_leap_year = False
    if year % 4 == 0 and year % 100 != 0:
        is_leap_year = True
    elif year % 400 == 0:
        is_leap_year = True

    return is_leap_year


def save_user_info(personal_number, username, password, account_number):
    # careful! this function ovverrides,
    # if you do not check whether the personal number already exists
    json_data = open_users()
    user_info = {
        personal_number: {
            "name": username,
            "password": password,
            "income": 0,
            "balance": 0,
            "account_number": account_number,
            "cards":[]
        }
    }
    json_data.update(user_info)
    update_users(json_data)  


def is_registered(personal_number):
    data = open_users()
    try:
        attribute = data[personal_number]
        return True
    except KeyError:
        return False


def check_personal_number(personal_number):
    is_correct = False
    try:
        year = int(personal_number[:4])
        month_first_digit = int(personal_number[4])
        month_last_digit = int(personal_number[5])
        # regex pattern matches a valid birthday followed by '-' and 4 numbers

        # months that are 31 days long
        if month_last_digit < 8 and month_last_digit % 2 == 1:
            match_pattern = r"^[12]\d{3}(0[1-9]|1[0-2])(0[1-9]|1[1-9]|2[1-9]|3[01])-\d{4}$"

        elif month_last_digit == 8 or month_first_digit == 1 and month_last_digit % 2 == 0:
            match_pattern = r"^[12]\d{3}(0[1-9]|1[0-2])(0[1-9]|1[1-9]|2[1-9]|3[01])-\d{4}$"

        # accounting for february, which can be up to 29 days long
        elif month_last_digit == 2:
            if determine_leap_year(year) == True:
                match_pattern = r"^[12]\d{3}(0[1-9]|1[0-2])(0[1-9]|1[1-9]|2[1-9])-\d{4}$"
            else:
                match_pattern = r"^[12]\d{3}(0[1-9]|1[0-2])(0[1-9]|1[1-9]|2[1-8])-\d{4}$"

        # months that are 30 days long
        else:
            match_pattern = r"^[12]\d{3}(0[1-9]|1[0-2])(0[1-9]|1[1-9]|2[1-9]|30)-\d{4}$"

        id_list = re.findall(match_pattern, personal_number)
        if len(id_list) != 0:
            is_correct = True

    except ValueError:
        is_correct = False

    return is_correct

def generate_account_number(length:int):
    #this generates a number not exceeding the given digit length
    random_number = random.randint(1,(length*10)-1)
    account_nr = f"{random_number:0>{length}}" # formats it to be exactly 'length' digits
    users = open_users()
    is_found = False

    for attribute in users.values():
        if attribute["account_number"] == account_nr:
            is_found = True

    if is_found is False:
        return account_nr
    else:
        return generate_account_number(length) 
        # recursion, it loops until there are no identical account nums in the json file

def save_account_number(account_number:str, personal_number:str):
    template={
        account_number : personal_number
    }

    json_data = read_data("./data/accounts.json")
    json_data.update(template)
    update_data(json_data, "./data/accounts.json",)

def register(): 
    personal_number, user_name, password = return_registering_information()
    if personal_number == None:
        return None,None
    account_number = generate_account_number(length=8)
    #creates and appends to json files
    save_user_info(personal_number, user_name, password, account_number)
    create_empty_expenses(personal_number)
    create_empty_transactions(personal_number)
    save_account_number(account_number, personal_number)
    return user_name, personal_number


def main_menu():
    main_window = create_main_menu()
    name, personal_number = None, None
    event, values = main_window.read()

    while not(event in (sg.WIN_CLOSED, "Exit")) and personal_number == None:
        if event in (sg.WIN_CLOSED, "Exit"):
            main_window.close()

        elif event == "Register":
            main_window.close()
            name, personal_number = register()
            if personal_number == None:
                main_window = create_main_menu()
                event, values = main_window.read()

        elif event == "Login":
            main_window.close()
            name, personal_number = login()
            if personal_number == None:
                main_window = create_main_menu()
                event, values = main_window.read()

    return personal_number, name

# Login Menu GUI
def login():
    layout = [[sg.Text('Login', font=(48), expand_x=True, justification='center')],
              [sg.Text('Personal number: ', font=(32)),sg.Sizer(20), sg.Input(font=(32), s=30, key='-INPUT pn-', default_text="YYYYMMDD-XXXX")],
              [sg.Text('Password: ', font=(32)), sg.Sizer(62.5), sg.Input(font=(32), s=30, key='-INPUT pass-', password_char='*')],
              [sg.Button('Confirm', font=(32)), sg.Button('Back', font=(32))]]

    window = sg.Window('Login', layout)
    name = None
    persson_number = None
    event, values = window.read()
    valid_input = False
    while event != 'Back' and valid_input == False:
        stored_data = open_users()
        if event == 'Confirm':
            if values['-INPUT pn-'] in stored_data and stored_data[values['-INPUT pn-']]['password'] == values['-INPUT pass-']:
                persson_number = values['-INPUT pn-']
                name = stored_data[values['-INPUT pn-']]['name']
                valid_input = True
            else:
                sg.popup_no_border('Wrong personal number or password! Please try again!')
                event, values = window.read()
        if event == sg.WIN_CLOSED:
            quit()

        
    window.close()
    return name, persson_number




def create_main_menu():
    layout = [
        [sg.Text("Welcome to our Bank!", font=("Helvetica", 28, "bold"), justification="center", size=(40, 0), pad=(10, 20))],
        [sg.Button("Login", size=(15, 1)),sg.Button("Register", size=(15, 1))],]
    return sg.Window("Main Menu", layout, element_justification="center")

def create_register_window():
    layout = []
    return
            
def return_registering_information():
    layout = [[sg.Push(), sg.Text("Register a new account", font=("Helvetica", 14, "bold"), key="HEADER"), sg.Push()],
        [sg.VPush()],
        [sg.Text("Personal number:", key="PN_TEXT"), sg.Push(), sg.Input(key="PN", default_text="YYYYMMDD-XXXX", enable_events=True, text_color="black", size=(20, 1))],
        [sg.Text("Full Name:", key="NAME_TEXT"), sg.Push(), sg.Input(key="NAME", size=(20, 1))],
        [sg.Text("Password:",key="PASSWORD_TEXT"), sg.Push(), sg.Input(password_char="*", key="PASSWORD", size=(20, 1))],
        [sg.VPush()],
        [sg.Button("Cancel", key="CANCEL_BUTTON", expand_x=True),  sg.Button("Register", key="REGISTER_BUTTON", disabled=False, size=(20, 1), expand_x=True)],
        ]
    #sg.Push() aligns them vertically, sg.VPush() horizontally
    window = sg.Window("Registration", layout, resizable=True, finalize=True, 
                       enable_window_config_events=True, grab_anywhere=True)
    
    is_running = True
    personal_number,user_name,password = None, None, None
    while is_running:
        event, values = window.read()
        # Adjust font size proportionally based on window width
        #Adjusts all UI elements in the case of changing the window size
        if event == sg.WINDOW_CONFIG_EVENT:
            width, height = window.size
            new_size = max(12, width // 60) # 12 is min size, 60 is max size

            window["HEADER"].update(font=("Helvetica", new_size))

            window["PN_TEXT"].update(font=("Helvetica", new_size))
            window["PN"].update(font=("Helvetica", new_size))

            window["NAME_TEXT"].update(font=("Helvetica", new_size))
            window["NAME"].update(font=("Helvetica", new_size))

            window["PASSWORD_TEXT"].update(font=("Helvetica", new_size))
            window["PASSWORD"].update(font=("Helvetica", new_size))

        # if the event is the cancel button or manual window close, the window is destroyed
        if event == "CANCEL_BUTTON":
            is_running=False # goes back to login/register option menu
        if event == sg.WIN_CLOSED:
            quit()
        if event == "REGISTER_BUTTON":
            personal_number = values["PN"]
            user_name = values["NAME"]  
            password = values["PASSWORD"]

            if check_personal_number(personal_number) == False:
                sg.popup("Invalid personal number.")
            elif check_username(user_name) == False:
                sg.popup("Incorrect username format!")
            elif is_registered(personal_number) == True:
                sg.popup(f"A user with personal number '{personal_number}' is already reigstered.")
            elif check_password(password) == False:
                sg.popup("Password must contain 7 characters, digits, uppercase and lowercase letters and a special symbol.")
            else:
                sg.popup("Account successfully registered.")
                is_running = False
    window.close()
    return personal_number, user_name, password  
# ---------------------------------------------------------------------------- #