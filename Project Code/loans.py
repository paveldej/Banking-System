import json
from tools import *
import PySimpleGUI as sg


def main(personal_number):
    # Define the layout for the menu
    finished = False
    while not finished:
        layout = [
            [sg.Text("Choose an option by clicking the button:", justification="center", size=(30, 1))],
            [sg.Button("Housing Loan", size=(20, 1))],
            [sg.Button("Expense Loan", size=(20, 1))],
            [sg.Button("Payback", size=(20, 1))],
            [sg.Button("Set AutoGiro", size=(20, 1))],
            [sg.Button("Display Loans", size=(20, 1))],
            [sg.Button("Back", size=(20, 1))]
        ]

        # Create the window
        Loan_window = sg.Window("Loans Menu", layout, element_justification="center")
        event, values = Loan_window.read()
        match event:
            case sg.WIN_CLOSED:
                Loan_window.close() 
                finished = True    
            
            case "Back":
                Loan_window.close() 
                finished = True    
            
            case "Housing Loan":
                Loan_window.close() 
                house_loan(personal_number)
        
            case "Expense Loan":
                Loan_window.close() 
                expenses_loan(personal_number)
         
            case "Payback":
                Loan_window.close() 
                payback(personal_number)
          
            case "Set AutoGiro":
                Loan_window.close() 
                set_autogiro(personal_number)

            case "Display Loans":
                Loan_window.close() 
                display_loans(personal_number)


def check_balance(personal_number, down_payment):
    users = read_data("./data/users.json")
    balance = users[personal_number]["balance"]
    if balance >= down_payment:
        return True
    elif balance < down_payment:
        return False
    else:
        return None


def get_income(personal_number):
    try:
        users = read_data("./data/users.json")
        income = users[personal_number]["income"]
        return income
    except Exception:
        return None


def house_loan(personal_number):
    if check_loan_exists(personal_number, "house_loan"):
        sg.popup_no_border("You already have a mortgage and cannot apply for a new one.")

    else:
        layout = [[sg.Text("House Price SEK"), sg.InputText()],
            [sg.Text("Down Payment SEK"), sg.InputText()],
            [sg.Text("Loan Duration in years"), sg.InputText()],
            [sg.Button("Back")],  
            [sg.Button("OK")]  
            ]
        window = sg.Window("Mortgage Application", layout)

        loan_complete = False
        while not loan_complete:
            try:
                option, values = window.read()
                
                if option == "Back" or option == sg.WIN_CLOSED:
                    window.close()
                    loan_complete = True
                
                if option == "OK":
                    price = values[0]
                    down_payment = values[1]
                    duration = values[2]
                
    
                    if not price.isdigit():
                        sg.popup_no_border("Invalid price entered. Please try again.")

                    elif float (price) <= 0:
                        sg.popup_no_border("Invalid price entered. Please enter a positive amount.")

                    elif not down_payment.isdigit():
                        sg.popup_no_border("Invalid down payment entered. Please try again.")

                    elif float (down_payment) < float (price) * 0.15 or float (down_payment) > float (price) * 0.8:
                        sg.popup_no_border("Invalid down payment entered. Down payment must be between 15-80% of the house price.")

                    elif not check_balance(personal_number, float (down_payment)):
                        sg.popup_no_border("you do not have enough balance for the down payment.")

                    elif not duration.isdigit():
                        sg.popup_no_border("Invalid duration entered. Please try again.")

                    elif int (duration) < 1 or int (duration) > 50:
                        sg.popup_no_border("Invalid duration entered. Please enter a number between 1 and 50 years.")
 
                    else:
                        price = float (price)
                        down_payment = float (down_payment)
                        duration = int (duration)

                        income = get_income(personal_number)
                        total_payment = calculate_rate(duration, price, "house_loan", down_payment)
                        monthly_mortgage = total_payment / duration / 12
                        if monthly_mortgage > income * 0.6:
                            sg.popup_no_border("You dont have enough income to pay for this loan.")
                        else:
                            prompt = f"""House Price: {price} SEK
Down Payment: {down_payment} SEK
Duration: {duration} Years
Mortgage: {total_payment} SEK
Monthly Payback: {monthly_mortgage} SEK

Do you wish to confirm this loan?"""
                            
                            if sg.popup_ok_cancel(prompt) == 'OK':
                            # Calculate the loan end date by adding the duration (in years) to the current date
                                start_date = datetime.now()
                                end_date = start_date.replace(start_date.year + duration)

                                # Update balance and loans with the new structure
                                update_balance(personal_number, -down_payment)

                                loan_details = {
                                    "amount": total_payment,
                                    "date": end_date.strftime("%Y-%m-%d")
                                }

                                update_dept(loan_details, personal_number, "house_loan")
                                window.close()
                                loan_complete = True
                                sg.popup_no_border("Loan has been added to our system.")
                                
            except Exception:
                sg.popup_no_border("Something went wrong.")


def update_dept(loan_details, personal_number, loan_type):
    users = read_data("./data/users.json")
    if not users[personal_number].get("loans"):
        users[personal_number]['loans'] = {}

        # Update the loan details for the specified loan type
    users[personal_number]['loans'][loan_type] = loan_details

    # Save updated data back to the JSON file
    update_data(users, "./data/users.json")
 

def expenses_loan(personal_number):
    if check_loan_exists(personal_number, "expenses"):
        sg.popup_no_border("You already have an expense loan and cannot apply for a new one.")

    else:
        layout = [[sg.Text("Amount SEK"), sg.InputText()],
            [sg.Text("Duration in years"), sg.InputText()],
            [sg.Button("Back")],  
            [sg.Button("OK")]  
            ]
        window = sg.Window("Expense Loan Application", layout)
        loan_complete = False
        while not loan_complete:
            try:
                option, values = window.read()
                
                if option == "Back" or option == sg.WIN_CLOSED:
                    window.close()
                    loan_complete = True
                
                if option == "OK":
                    amount = values[0]
                    duration = values[1]
                    if not amount.isdigit():
                        sg.popup_no_border("Invalid amount entered. Please try again.")
                
                    elif float (amount) < 10000 or float (amount) > 200000:
                        sg.popup_no_border("Invalid amount entered. Please enter an amount between 10,000 and 200,000 SEK.")

                    elif not duration.isdigit():
                        sg.popup_no_border("Invalid duration entered. Please try again.")

                    elif int (duration) < 1 or int (duration) > 10:
                        sg.popup_no_border("Invalid duration entered. Please enter a number between 1 and 10 years.")
                    
                    else:
                        amount = float (amount)
                        duration = int (duration)
                        monthly_payment, interest_amount, total_payment = calculate_rate(duration, amount, "expense loan")
                        income = get_income(personal_number)
                        if monthly_payment > income * 0.4:  # check to see if the monthly repayment amount is less than 40% of the user's monthly income
                            sg.popup_no_border("Your income is not enough to cover this loan.")
                           
                        else:
                            prompt = f"""Loan Amount: {amount} SEK
Loan Duration: {duration} Years
Payback Amount: {total_payment} SEK
Monthly Payback: {monthly_payment} SEK
Interest Amount: {interest_amount} SEK

Do you wish to confirm this loan?"""
                            
                            if sg.popup_ok_cancel(prompt) == 'OK':
                                # Calculate the loan end date by adding the duration (in years) to the current date
                                start_date = datetime.now()
                                end_date = start_date.replace(start_date.year + duration)

                                # Update balance and loans with the new structure
                                update_balance(personal_number, amount)
                
                                loan_details = {
                                    "amount": total_payment,
                                    "date": end_date.strftime("%Y-%m-%d")
                                }

                                update_dept(loan_details, personal_number, "expenses")
                                window.close()
                                loan_complete = True
                                sg.popup_no_border("Loan has been added to our system.")

            except Exception:
                sg.popup_no_border("Something went wrong. ")
               


def check_loan_exists(personal_number, type):
    try:
        users = read_data("./data/users.json")
        if not users[personal_number].get("loans"):
            return False
        elif not users[personal_number]["loans"].get(type):
            return False
        else:
            return True
    except FileNotFoundError as error:
        print(f"Error occured: {error}")
    except json.JSONDecodeError as error:
        print(f"Error occured: {error.msg}")
    except Exception as error:
        print(f"Unexpected error occured: {error}")  # Problem here :) pls fix ur try except



def set_autogiro(personal_number):
    users = read_data("./data/users.json")
    user = users.get(personal_number)
    loans = user.get("loans", {})
    loan_keys = list(loans.keys())
    
    if not loans:
        sg.popup("Cannot find any loans on your account.", text_color="red", font=("Helvetica", 12, "bold"))
        
    else:
        finished = False
        while not finished:
            # Create the main loan selection window
            layout = [
                [sg.Text("Select a loan:")],
                [sg.Button(loan) for loan in loan_keys],  # dynamically create buttons for each loan if there exist some
                [sg.Button("Close")]
            ]

            set_autogiro_window = sg.Window("Loan Menu", layout)
            event, _ = set_autogiro_window.read()
            match event:
                case sg.WINDOW_CLOSED:
                    set_autogiro_window.close()
                    finished = True
                
                case "Close":
                    set_autogiro_window.close()
                    finished = True

                case _:
                    selected_loan = event
                    loan = loans[selected_loan]
                    set_autogiro_window.close()
                    
                    # Show loan details and AutoGiro status
                    layout_info = [
                        [sg.Text(f"Name: {selected_loan}")],
                        [sg.Text(f"Date: {loan['date']}")],
                        [sg.Text(f"Amount: {loan['amount']}")],
                        [sg.Text(f"AutoGiro Status: {'ON' if loan.get('auto_giro', {}).get('status', False) else 'OFF'}")],
                        [sg.Text(f"Amount: {loan.get('auto_giro', {}).get('amount', 'N/A') if loan.get('auto_giro', {}).get('status', False) else 'N/A'}")],
                        [sg.Button("Back")],
                        [sg.Button("Enable AutoGiro") if loan.get('auto_giro', {}).get('status', False) == False else sg.Button("Disable AutoGiro")]
                    ]

                    window_info = sg.Window(f"Loan Information for {selected_loan}", layout_info)

                    event_info, _ = window_info.read()
                    while event_info != sg.WINDOW_CLOSED and event_info != "Back":

                        if event_info == sg.WINDOW_CLOSED or event_info == "Back":
                            window_info.close()

                        elif event_info == "Enable AutoGiro":
                            try:
                                amount = sg.popup_get_text(f"Enter the AutoGiro amount for loan {selected_loan}:")
                                if amount != sg.WIN_CLOSED and amount != "Cancel":
                                    amount = float(amount)
                                    if amount <= 0:
                                        raise ValueError("Amount must be a positive number.")
                                    elif amount > loan["amount"]:
                                        sg.popup_no_border("Autogiro amount cannot be more than the loan amount.")
                                    else:
                                        loans[selected_loan]["auto_giro"] = {"status": True, "amount": amount}
                                        update_data(users, "./data/users.json")
                                        sg.popup(f"AutoGiro enabled with an amount of {amount} for loan {selected_loan}")
                                    
                                    window_info.close()
                            except ValueError:
                                sg.popup_error("Invalid amount, please enter a positive number.")

                        elif event_info == "Disable AutoGiro":
                            loans[selected_loan]["auto_giro"] = {"status": False}
                            update_data(users, "./data/users.json")
                            sg.popup(f"AutoGiro disabled for loan {selected_loan}")
                            window_info.close()

                        event_info, _ = window_info.read()
                    window_info.close()  # Close the details window when done


def get_payback_window(house_loan, expense_loan):
    layout = [
        [sg.Text("Your loans:")],
        [sg.Text("House loan: "), sg.Text(f"{house_loan['amount']} SEK due {house_loan['date']}" if house_loan else "No loan")],
        [sg.Text("Expense loan: "), sg.Text(f"{expense_loan['amount']} SEK due {expense_loan['date']}" if expense_loan else "No loan")],
        [sg.Text("Select the loan you want to pay back: "), sg.Combo(['house loan', 'expense loan'], key="-LOAN-")],
        [sg.Text("Enter the amount you want to pay back: "), sg.InputText(key="-AMOUNT-")],
        [sg.Button("Pay"), sg.Button("Cancel")]
    ]
    window = sg.Window("Payback", layout)
    return window


def payback(personal_number):
    users = open_users()
    user = users.get(personal_number)
    loans = user.get("loans")
    
    if loans is None:
        sg.popup_no_border("You have no loans in our bank.")
        return
    
    house_loan = loans.get("house_loan" , None)
    expens_loan = loans.get("expenses" , None)
    
    window = get_payback_window(house_loan, expens_loan)
    
    balance = user.get("balance")
    amount = 0
    is_button_pressed = False
    while not is_button_pressed:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED or event == "Cancel":
            is_button_pressed = True
        
        try:
            amount = float(values["-AMOUNT-"])
        except Exception:
            continue
        
        if event == "Pay":
            if values["-LOAN-"] == "house loan":
                if house_loan != None:
                    if amount > house_loan['amount']: 
                        sg.popup_no_border("This amount is more than your remaining loan.")
                    elif amount <= 0:
                        sg.popup_no_border("Invalid amount entered. Please enter a positive amount.")
                    else:
                        if check_balance(personal_number , amount):
                            update_balance(personal_number , balance-amount)
                            if amount == house_loan['amount']:
                                del users[personal_number]["loans"]["house_loan"] 
                            else:
                                users[personal_number]["loans"]["house_loan"]['amount'] = house_loan['amount'] - amount
                            update_data(users , "data/users.json")
                            sg.popup_no_border("Thank you for your payment.")
                            is_button_pressed = True
                        else:
                            sg.popup_no_border("You don't have enough money for this payment.")
                else:
                    sg.popup_no_border("You don't have a house loan.")
            elif values["-LOAN-"] == "expense loan":
                if expens_loan != None:
                    if amount > expens_loan['amount']: 
                        sg.popup_no_border("This amount is more than your remaining loan.")
                    elif amount <= 0:
                        sg.popup_no_border("Invalid amount entered. Please enter a positive amount.")
                    else:
                        if check_balance(personal_number , amount):
                            update_balance(personal_number , balance-amount)
                            if amount == expens_loan['amount']:
                                del users[personal_number]["loans"]["expenses"]
                            else:
                                users[personal_number]["loans"]["expenses"]['amount'] = expens_loan['amount'] - amount
                            update_data(users , "data/users.json")
                            sg.popup_no_border("Thank you for your payment.")
                            is_button_pressed = True
                        else:
                            sg.popup_no_border("You don't have enough money for this payment.")
            else:
                sg.popup_no_border("Please select a loan to pay back.")
                
    window.close()    



def display_loans(personal_number):
    users = open_users()
    user = users.get(personal_number)
    loans = user.get("loans")
    

    '''Notification before starting'''
    if loans is None:
        sg.popup("Cannot find any loans on your account.", font=("Helvetica", 12, "bold"))
    else:
        loan_data = [
        (loan, details) for loan, details in loans.items()
                 ]
        layout = [
        [sg.Text("My Loans", font=("Helvetica", 16), justification="center", expand_x=True)],
        [sg.Text("          TYPE                         ", font=("Helvetica", 12, "bold"), pad=((10, 50), (5, 5))),
        sg.Text("DATE                     ", font=("Helvetica", 12, "bold"), pad=((10, 50), (5, 5))),
        sg.Text("AMOUNT", font=("Helvetica", 12, "bold"), pad=((10, 50), (5, 5)))],
        [
            sg.Column(
                [[
                    sg.Text(loan, size=(15, 1), justification="left", font=("Helvetica", 11)),
                    sg.Text(details['date'], size=(15, 1), justification="center", font=("Helvetica", 11)),
                    sg.Text(details['amount'], size=(15, 1), justification="right", font=("Helvetica", 11)),
                ] for loan, details in loan_data],scrollable=True,vertical_scroll_only=True,justification='center',size=(450, 200),  background_color="white"
            )
        ],
        [sg.HorizontalSeparator()],
        [sg.Button("Exit", key="-EXIT-", size=(10, 1), pad=(5, 10))]]
        display_loans_window = sg.Window("My loans", layout)
        event,values = display_loans_window.read()
        while event != "-EXIT-" and event != sg.WINDOW_CLOSED:
            event,values = display_loans_window.read()
        display_loans_window.close()


