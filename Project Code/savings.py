import PySimpleGUI as sg
from tools import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from stocks import main as stocks_main


def main(personal_number):
    option = 0
    while(option != 5):
        option = main_menu()
        match(option):
            case 1:
                display_savings(personal_number)

            case 2:
                savings_account(personal_number)

            case 3:
                invest,years,calculation = calculate_savings()
                
            case 4:
                stocks_main(personal_number)

            case 5:
                option = 5
                
            case _:
                pass


def main_menu_gui():
    button_size = (13,2)
    layout = [[sg.Button('View interest accounts', size=button_size)],
              [sg.Button('Create new savings', size=button_size)],
              [sg.Button('Interest calculator', size=button_size)],
              [sg.Button('Stocks', size=button_size)],
              [sg.Button('Back', size=button_size)]]
    return sg.Window('Savings', layout)


def main_menu():
    window = main_menu_gui()
    option = None
   
    event, value = window.read()

    match event:
        case 'View interest accounts':
            option = 1
            window.close()

        case 'Create new savings':
            option = 2
            window.close()

        case 'Interest calculator':
            option = 3
            window.close()


        case 'Stocks':
            option = 4
            window.close()


        case 'Back':
            option = 5
            window.close()

        case sg.WIN_CLOSED:
            option = 5

    window.close()
    return option



def create_savings_account(personal_number, addyears, money_after):
    """Creates or appends a savings account entry."""
    today = datetime.now().date()
    deadline = today + relativedelta(years=addyears)
    new_savings = {"date": str(deadline), "amount": money_after}

    # Read existing data
    data = read_data("./data/savings.json")

    # Add or append savings for the user
    data.setdefault(personal_number, []).append(new_savings)

    # Write the updated data back to the file
    update_data(data, "./data/savings.json")
    sg.popup_no_border(f"Savings account updated for {personal_number}.")


def savings_account(personal_number):
    initial_amount, years, expected_savings = calculate_savings()
    while initial_amount != 0:
        users = read_data("./data/users.json")
        if users[personal_number]['balance'] < initial_amount:
            sg.popup_no_border("You don't have enough money in your balance.")
            initial_amount, years, expected_savings = calculate_savings()
        else:
            confirm = sg.popup_ok_cancel("Are you sure you want to proceed?")
            if confirm == "OK":
                create_savings_account(personal_number,years,expected_savings)
                users[personal_number]['balance'] -= initial_amount
                update_data(users,"./data/users.json")
                initial_amount, years, expected_savings = 0,0,0
            else:
                initial_amount, years, expected_savings = calculate_savings()
            


def get_calculator_window():
    layout = [[sg.Text("How much do you want to deposit?"), sg.InputText(key="deposit")],
              [sg.Text("For how many years?"), sg.InputText(key="years")],
              [sg.Button("Calculate"), sg.Button("Back")]]
    return sg.Window("Bank", layout)

def calculate_savings():
    window = get_calculator_window()
    deposit = 0
    years = 0
    calculation = 0
    event, values = window.read()
    calculated = False
    while event != sg.WIN_CLOSED and event != "Back" and calculated != True:

        try:
            deposit = int(values["deposit"])
            years = int(values["years"])

            if deposit <= 0 or years <= 0:
                sg.popup_no_border("Please enter positive numbers.")
            else:
                calculation = calculate_rate(years, deposit, type="savings", down_payment = 0)
                sg.popup(f"The amount of money you will have saved after {years} years is: {calculation}")
                calculated = True
        except Exception:
            sg.popup_no_border("Please enter positive numbers.")
        if calculated == False:
            event, values = window.read()
    window.close()
    if event == sg.WIN_CLOSED or event == "Back":
        return 0,0,0
    else:
        return deposit, years, calculation


def display_savings(personal_number):
    
    data = read_data("./data/savings.json")
    savings_list = []
    if personal_number in data:
        savings_list = data[personal_number]

    savings = [[saving['date'], saving['amount']] for saving in savings_list]

    button_size = (13,2)
    layout = [
        [sg.Text("Savings overview\n", size=button_size)],
        [sg.Table(values=savings, headings=['Date', 'Amount'], max_col_width=25, auto_size_columns=True, justification='center', num_rows=10, alternating_row_color='lightblue', key='-TABLE1-', size=button_size)],
        [sg.Button('Back', size=button_size)]
        ]
    
    window = sg.Window('Saving overview', layout)

    clicked_button = False
    while not clicked_button:
        event, value = window.read()
        if event == 'Back':
            window.close()
            return None, None
        clicked_button = True
