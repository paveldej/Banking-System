import json
import re
from datetime import datetime
import shutil
import os
from datetime import datetime
import PySimpleGUI as sg

def determine_leap_year(year):
    is_leap_year = False
    if year % 4 == 0 and year % 100 != 0:
        is_leap_year = True
    elif year % 400 == 0:
        is_leap_year = True

    return is_leap_year

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


def sync():
    deadline = 25
    today = datetime.now().date()
    if not (today.day == deadline):
        return
    data = read_data("./data/users.json")
    if not ("dates" in data.keys()):
        data ["dates"] = []
    if not (str(today) in data["dates"]):
        data["dates"].append(str(today))
        update_data(data,"./data/users.json")
        sync_loan()
        synchronize_income()
        synchronize_savings()

def update_users(variable):
    """Function to Update User Information / users.json"""
    with open("./data/users.json", "w", encoding="UTF-8") as file:
        json.dump(variable, file, indent=4)

# ------------------------------------------------------------------------------------ #
#this is only used in login register, could be replaced with read_data() - Matt
def open_users():
    """Function to Open User Information / users.json"""
    with open(f"./data/users.json", "r", encoding="UTF-8") as file:
        return json.load(file)

# ------------------------------------------------------------------------------------ #

def read_data(file_name):
    """Function for reading file content, can fit each task"""
    try:
        with open(file=file_name, encoding="utf-8", mode="r") as file:
            return json.load(file)
    except FileNotFoundError as error:
        print(f"Error occurred: {error}")
    except json.JSONDecodeError as error:
        print(f"Error occurred: {error}")
    # Return an empty dictionary if an error occurs
    return {}

# ------------------------------------------------------------------------------------ #

# Loging functionality

def stopping_function():
    """make the stop system to make system more efficient to read the output"""
    input("Press 'Enter' to continue...")

# ------------------------------------------------------------------------------------ #

def get_validated_input(prompt, validation_func, error_message="Invalid input. Please try again."):
    """Prompt the user and validate input using the provided function."""
    while True:
        user_input = input(prompt)
        if validation_func(user_input):
            return user_input
        print(error_message)

# ------------------------------------------------------------------------------------ #

def confirm_action(prompt="proceed: "):
    """Ask for user confirmation and return True for 'y', False for 'n'."""
    layout = [[sg.Text(prompt), sg.Button("yes"), sg.Button("no")]]
    window = sg.Window("error",layout)
    event, values = window.read()
    window.close()
    if event == "yes":
        return True
    else:
        return False


# ------------------------------------------------------------------------------------ #

def valid_name(name):
    """Validate that the name follows the 'Name Lastname' format."""
    pattern = r"^[A-Z][a-zÀ-ÖØ-öø-ÿ]+ [A-Z][a-zÀ-ÖØ-öø-ÿ]+$"
    return re.match(pattern, name) is not None

# ------------------------------------------------------------------------------------ #

def strong_password(password):
    """Check if the password is strong."""
    match_pattern = re.compile(r"""
                        # Validate password: 2 upper, 1 special, 2 digit, 1 lower, 8 chars.
                        ^                        # Anchor to start of string.
                        (?=(?:[^A-Z]*[A-Z]){2})  # At least two uppercase.
                        (?=[^!@#$&*]*[!@#$&*])   # At least one "special".
                        (?=(?:[^0-9]*[0-9]){2})  # At least two digit.
                        .{8,}                    # Password length is 8 or more.
                        $                        # Anchor to end of string.
                        """, re.VERBOSE)
    return re.match(match_pattern, password) is not None

# ------------------------------------------------------------------------------------ #

def calculate_rate(years, price, type, down_payment = 0):
    try:
        if type == "savings":
            """ A = p * (1 + r)^t """
            """ A = Total balance      p = price      r = annual interest     t = years """
            savings_interest = round(price * (1 + 0.02)**years, 2)
            #print(f"After {years}, your balance will be {savings_interest}")
            return savings_interest
        
        elif type == "house_loan":
            """ Monthly Payment inc interest = ( p * r * (1+r)^n ) / ( (1 + r)^n - 1 ) """
            """ m = monthly payment       p = price      r = monthly interest rate       n = number of months payment"""
            new_price = price - down_payment
            m = round(((new_price * (0.05/12) * (1 + (0.05/12))**(years*12)) / ((1 + (0.05/12))**(years*12) - 1)), 2)

            """ Total interest of payment = ( m * n ) - p """
            t_interest = round(((m * (years*12)) - price), 2)

            """ Total amount of payment = m * n """
            t_payment = round((m * (years*12)), 2)
            #print(f"You will pay {m} SEK monthly. The total amount of interest is {t_interest} and total amount of payment will be {t_payment}.")
            return t_payment
        
        elif type == "expense loan":
            m_exp = round(((price * (0.08/12) * (1 + (0.08/12))**(years*12)) / ((1 + (0.08/12))**(years*12) - 1)), 2)
            t_interest_exp = round(((m_exp * (years*12)) - price), 2)
            t_payment_exp = round((m_exp * (years*12)), 2)
            #print(f"You will pay {m_exp} SEK monthly. The total amount of interest is {t_interest_exp} and total amount of payment will be {t_payment_exp}.")
            return m_exp, t_interest_exp, t_payment_exp
    
    except Exception:
        print("Invalid input.")
        return
    
# ------------------------------------------------------------------------------------ #

def update_data(data,path:str) -> bool:
    """Overrides json file with new data\n
    Parameters:\n
        data: new information you want to override file with.\n
        path: file path.\n
    In case if an error occures during overriding, the old content will be restored."""
    
    temp_file_path = path.replace(".json", "_temp.json")
    shutil.copy(path,temp_file_path)
    
    is_updated = False
    try:
        with open(path,encoding='utf-8',mode='w') as file:
            json.dump(data,file,indent=4)
        is_updated = True
    except FileNotFoundError as ex:
        print(f"Error occured: {ex}")
    except json.JSONDecodeError as ex:
        print(f"Error occured: {ex.msg}")
    except Exception as ex:
        print(f"Unexpected error ocuured: {ex}")
    finally:
        if not is_updated:
            shutil.copy(temp_file_path,path)
        os.remove(temp_file_path)
    
    return is_updated



def update_balance(personal_number:str, amount:float):
    try:
        data = read_data("./data/users.json")
        current_balance = data[personal_number]["balance"]
        new_balance =  float(current_balance) + amount
        data[personal_number]["balance"] = new_balance #updates dict to have add the amount
    
        update_data(data, "./data/users.json") 
        return data
    
    except KeyError:
        return None
    
def synchronize_savings():
    data = read_data(f"./data/savings.json")
    try:
        current_date = datetime.now().date()
        index=-1
        for personal_number, savings in data.items():
            dictionaries_to_delete = []
            for saving in savings:
                index+=1
                year = int(saving["date"][0:4])
                month = int(saving["date"][5:7])
                day = int(saving["date"][8:10])
                savings_release_date = datetime(year, month, day).date()
                if savings_release_date <= current_date:
                    update_balance(personal_number, float(saving["amount"]))
                    dictionaries_to_delete.append(index)

        #this deletes the dictionaries in the list, that are past the release date
            for x in reversed(dictionaries_to_delete):
                print(data[personal_number][x])
                del data[personal_number][x]
            #here we reset the index, so it becomes relative to each person
            index=-1
        update_data(data, "./data/savings.json") #saves modified json

    except KeyError:
        return None
    except ValueError:
        return None
    except TypeError: 
        return None
    

def synchronize_income():
    data = read_data("./data/users.json")
    for key,attribute in data.items():
       if check_personal_number(key):
        attribute["balance"] += attribute["income"]
    update_data(data, "./data/users.json")



def sync_loan():
    """Checks all users. AutoGiro payments and applies penalties for overdue loans."""
    """ used .get() as fastest way of error handling -> to avoid missing data which could lead to Error, if it is happen program continue to work by replacing variables with empty parts"""
    today = datetime.now().date()

    # Main function
    #print("Starting loan synchronization...")
    users = read_data("./data/users.json")

    for personal_number, user_data in users.items():
        loans = user_data.get("loans", {})
        balance = user_data.get("balance", 0)

        for loan_key, loan_details in list(loans.items()):
            if isinstance(loan_details, dict): # if there is no loan_details in list(loans.items()) then it will return empty dictionary
                auto_giro = loan_details.get("auto_giro", {})

                if isinstance(auto_giro, dict) and auto_giro.get("status", False): # here should be True and True to work (in our json we sadly doesn't have new version of set_autogiro execution)
                    giro_amount = auto_giro.get("amount", 0)
                    if giro_amount > 0 and balance >= giro_amount:
                        user_data["balance"] -= giro_amount
                        loan_details["amount"] -= giro_amount

                        if loan_details["amount"] <= 0:
                            overpayment = abs(loan_details["amount"]) # for returning money back if overpayment -> abs() <- was used for making neg. int into pos. int
                            user_data["balance"] += overpayment
                            del loans[loan_key]
                    

            loan_date = datetime.strptime(loan_details["date"], "%Y-%m-%d").date()


            # Penalty application
            if today > loan_date:
                penalty = loan_details["amount"] * 0.05
                if penalty:
                    loan_details["amount"] += penalty
                new_due_date = loan_date.replace(year=loan_date.year + 1)
                loan_details["date"] = new_due_date.strftime("%Y-%m-%d")

        user_data["loans"] = loans
        users[personal_number] = user_data

    update_data(users, "./data/users.json") # Save Json

