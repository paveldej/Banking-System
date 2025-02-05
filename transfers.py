from converter import main as converter
import random
from tools import *
import PySimpleGUI as sg

def main(personal_number):
    users = read_data("./data/users.json")
    expenses = read_data(f"./data/{personal_number}_expenses.json")
    transactions = read_data(f"./data/{personal_number}_transactions.json")
    accounts = read_data(f"./data/accounts.json")
    finished = False
    while not finished:
        format = [[sg.Button("Transfer Bank to Bank")],
                [sg.Button("International Transfer")],
                [sg.Button("Converter")],
                [sg.Button("Back")]]
        window = sg.Window("Transfer Menu" , format)
        event , value = window.read()
        match event :
            case sg.WIN_CLOSED:
                window.close()
                finished = True
            
            case "Back" :
                window.close()
                finished = True
            
            case "Transfer Bank to Bank" :
                window.close()
                transfer_bank_to_bank(personal_number , users, expenses, transactions, accounts)
            
            case "International Transfer":
                window.close()
                international_transfer(personal_number , users , expenses , transactions)
            
            case "Converter":
                window.close()
                converter()
            

def international_transfer(personal_number, users, expenses, transactions):
    transaction_complete = False
    layout = [[sg.Text("Receiver"), sg.InputText()],
                  [sg.Text("IBAN"), sg.InputText(default_text="GB12ABCD10203012345678")],
                  [sg.Text("SWIFT/BIC"), sg.InputText(default_text="AAAABBCCDDD")],
                  [sg.Text("Amount SEK"), sg.InputText()],
                  [sg.Text("Category"), sg.InputText()],
                  [sg.Button("Back")],  
                  [sg.Button("OK")]  
                 ]
    window = sg.Window("Edit Password", layout)
    while not transaction_complete:
        try:
            option, values = window.read()
            
            if option == "Back" or option == sg.WIN_CLOSED:
                window.close()
                transaction_complete = True
                
            if option == "OK":
                receiver = values[0]
                iban = values[1]
                swift = values[2]
                amount = values[3]
                category = values[4]
                
                if not re.fullmatch(r"\b[A-Z]{1}[a-z]+\b", receiver):
                    sg.popup_no_border("Invalid name entered. Please try again.")

                elif not re.fullmatch(r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$', iban):
                    sg.popup_no_border("Invalid IBAN entered. Please try again.")
                
                elif not re.fullmatch(r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$', swift):
                    sg.popup_no_border("Invalid SWIFT/BIC entered. Please try again.")
                
                elif float (amount) <= 0:
                    sg.popup_no_border("Invalid amount entered. Please try again.")

                elif not check_balance(personal_number, users, float (amount)):
                    sg.popup_no_border("You don't have enough balance for this transaction.")

                elif not category:
                    sg.popup_no_border("Please enter a category.")
               
                else:
                    amount = float (amount)
                    if sg.popup_ok_cancel(f"Confirm {amount} SEK transfer to {receiver} for {category}?") == 'OK':
                        users[personal_number]["balance"] -= amount
                        transaction_id = generate_transcation_id(users, transactions, personal_number)
                        transactions["out"][transaction_id] = {"to": iban, "amount": amount, "category": category}
                        add_expenses(expenses, category, amount)
                        update_sender_file(personal_number, users, expenses, transactions)
                        window.close()
                        sg.popup_no_border("Transfer completed successfully.")
                        transaction_complete = True

        except ValueError:
            sg.popup_no_border("Invalid amount entered. Please try again.")
        except json.JSONDecodeError:
            sg.popup_no_border("There is something wrong with the JSON.")
        except FileNotFoundError:
            sg.popup_no_border("File not found.")
            

def generate_transcation_id(users, sender_transactions, sender_pn = None, receiver_pn = None):
    transactions_list = []
    name = users[sender_pn]["name"]

    for id in sender_transactions["in"].keys():
        transactions_list.append(id)    
    for id in sender_transactions["out"].keys():
        transactions_list.append(id)
    sender_out_trans = sender_transactions["out"]
    if receiver_pn == None:
        receiver_in_trans = []
    else:
        receiver_transactions = read_data(f"./data/{receiver_pn}_transactions.json")
        for id in receiver_transactions["in"].keys():
            transactions_list.append(id)    
        for id in receiver_transactions["out"].keys():
            transactions_list.append(id)
    id_created = False
    while not id_created:
        new_id = f"{name[0:3]}" + str(random.randint(0, 9999999))
        new_id = f"{name[0:3]}" + str(random.randint(0, 9999999))
        if new_id not in transactions_list:
            id_created = True
    return new_id
        

def update_sender_file(personal_number, users, expenses, transactions):
    update_data(users, "./data/users.json")
    update_data(expenses, f"./data/{personal_number}_expenses.json")
    update_data(transactions, f"./data/{personal_number}_transactions.json")


def transfer_bank_to_bank(personal_number, users, expenses, transactions, accounts): 
    layout = [  [sg.Text("Reciever Account Number ", size=(20, 1)), sg.InputText(key='reciever', default_text="00000000")],
                [sg.Text("Amount SEK", size=(20, 1)), sg.InputText(key='amount')],
                [sg.Text("Catagory ",size=(20, 1)), sg.InputText(key='category')],
        [sg.Button('Send'), sg.Button('Cancel')] ]
    window = sg.Window("Transfer Money",layout)
    event,values = window.read()
    valid_input = False
    while event != "Cancel" and valid_input != True and event != sg.WIN_CLOSED:
        try:
            reciever_check = int(values["reciever"])
            reciever = values["reciever"]
            amount = float(values["amount"])
            category = values["category"]

            confirm_layout = [[sg.Text('Are you sure you want to proceed?'), sg.Button("YES"), sg.Button("NO")]]
            confirm_window = sg.Window("error",confirm_layout)
            event, values = confirm_window.read()
            confirm_window.close()
            confirmation = event
                # if yes, checks if everything is okay and if so, updates
            if confirmation == "YES":
                if not check_balance(personal_number,users,amount) :
                    error_layout = [[sg.Text("you don't have enough much money"), sg.Button("Continue")]]
                    error_window = sg.Window("error",error_layout)
                    event, values = error_window.read()
                    error_window.close()
                    event,values = window.read() 
                else:
                    users[personal_number]["balance"] -= amount
                    add_expenses(expenses , category , amount)
                    if check_reciever(reciever , accounts):
                        reciever_personal_number = get_reciever_personal_number(reciever , accounts)
                        users[reciever_personal_number]["balance"] += amount
                        tr_id = generate_transcation_id(users, transactions, personal_number, reciever_personal_number)
                        if reciever_personal_number:
                            try:
                                reciever_transactions = read_data(f"./data/{reciever_personal_number}_transactions.json")
                            except Exception:
                                reciever_transactions = {}  
                            reciever_transactions["in"].update({
                                tr_id : {
                                "from": personal_number,
                                "amount": amount,
                                "category": category
                                }})
                        transactions["out"].update({
                            tr_id : {
                            "to": reciever_personal_number,
                            "amount": amount,
                            "category": category
                            }})
                        update_riciever_file(reciever_personal_number ,users , reciever_transactions)
                        update_sender_file(personal_number, users, expenses, transactions)
                    else:
                        tr_id = generate_transcation_id(users, transactions, personal_number)
                        transactions["out"].update({tr_id : {
                            "to": "unknown",
                            "amount": amount,
                            "category": category
                            }})
                        update_sender_file(personal_number, users, expenses, transactions)
                    error_layout = [[sg.Text('Sucessfull transaction'), sg.Button("Continue")]]
                    error_window = sg.Window("error",error_layout)
                    event, values = error_window.read()
                    error_window.close()
                    valid_input = True
        except ValueError:
            error_layout = [[sg.Text('You have entered an invalid value'), sg.Button("OK")]]
            error_window = sg.Window("error",error_layout)
            event, values = error_window.read()
            error_window.close()
            event,values = window.read() 
    window.close()



def check_balance(pr , users , amount):
    balance = users[pr]["balance"]
    if amount <= balance:
        return True
    else:
        return False


def add_expenses(userexpense , category , amount):
    category_exist = False
    for reason in userexpense.keys():
        if reason.lower() == category :
            category_exist = True
    money = 0
    if category_exist:
        money += userexpense[category.capitalize()]
    userexpense.update({category.capitalize() : amount+money})


def check_reciever(recievcer_account_number , accounts):
    reciever_exists = False
    if recievcer_account_number in accounts.keys():
        reciever_exists = True
    return reciever_exists


def update_riciever_file(personal_number, users,transactions):
    update_data(users, "./data/users.json")
    update_data(transactions, f"./data/{personal_number}_transactions.json")
    update_data(users, "./data/users.json")
    update_data(transactions, f"./data/{personal_number}_transactions.json")


def get_reciever_personal_number(reciever  , accounts):
    for account in accounts.keys():
        if reciever == account:
            return accounts[account]
        