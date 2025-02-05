import PySimpleGUI as sg
from tools import *


def main(personal_number, name):
    user_info = read_data("./data/users.json")[personal_number]
    expenses_info = read_data(f"./data/{personal_number}_expenses.json")
    transactions_info = read_data(f"./data/{personal_number}_transactions.json")

    if not user_info or not expenses_info or not transactions_info:
        sg.popup_no_border("User info not found.", title="My Bank", auto_close=True, auto_close_duration=3)
    
    else: 
        transactions_in = []
        for transaction in list(transactions_info["in"].values())[:-4:-1]:
            transactions_in.append([attrib for attrib in transaction.values()])
        
        transactions_out = []
        for transaction in list(transactions_info["out"].values())[:-4:-1]:
            transactions_out.append([attrib for attrib in transaction.values()])
        
        top_expense = max(list(expenses_info.values()))
       
        is_button_pressed = False
        while not is_button_pressed:
            window = get_main_window(transactions_in, transactions_out, top_expense, user_info)
            event, values = window.read()
            
            match event:
                case sg.WIN_CLOSED:
                    window.close()
                    is_button_pressed = True
                
                case "Back":
                    window.close()
                    is_button_pressed = True

                case "View All Transactions":
                    window.close()
                    view_all_transactions(transactions_info)
        
                case "View All Expenses":
                    window.close()
                    view_all_expenses(expenses_info)



def get_main_window(transactions_info_in, transactions_info_out, top_expense, users_info):
    layout = [[sg.Text(f"Balance: {users_info['balance']} SEK")],
              [sg.Text(f"Income: {users_info['income']} SEK")],
              [sg.Text("Incoming transactions:")],
              [sg.Table(values=transactions_info_in, headings=['Sender', 'Amount', 'Category'], max_col_width=25, auto_size_columns=True, justification='center', num_rows=10, alternating_row_color='lightblue', key='-TABLE1-')],
              [sg.Text("Outgoing transactions:")],
              [sg.Table(values=transactions_info_out, headings=['Receiver', 'Amount', 'Category'], max_col_width=25, auto_size_columns=True, justification='center', num_rows=10, alternating_row_color='lightblue', key='-TABLE2-')],
              [sg.Button("View All Transactions")],
              [sg.Text("Expenses:")],
              [sg.Text(f"Top Expense: {top_expense}"), sg.Button("View All Expenses")],
              [sg.Button("Back")]]
    return sg.Window("My Bank", layout, finalize=True)




def view_all_transactions(transactions_info):
    transactions_in = []
    for transaction in list(transactions_info["in"].values())[::-1]:
        transactions_in.append([attrib for attrib in transaction.values()])

    transactions_out = []
    for transaction in list(transactions_info["out"].values())[::-1]:
        transactions_out.append([attrib for attrib in transaction.values()]) 

    layout = [
        [sg.Text("All Transactions\n")],
        [sg.Text("Incoming transactions")],
        [sg.Table(values=transactions_in, headings=['Sender', 'Amount', 'Category'], max_col_width=25, auto_size_columns=True, justification='center', num_rows=10, alternating_row_color='lightblue', key='-TABLE1-')],
        [sg.Text("\nOutgoing transactions")],
        [sg.Table(values=transactions_out, headings=['Receiver', 'Amount', 'Category'], max_col_width=25, auto_size_columns=True, justification='center', num_rows=10, alternating_row_color='lightblue', key='-TABLE2-')],
        [sg.Button('Back')]         
    ]
    
    window = sg.Window('My Bank', layout)
    is_button_pressed = False
    while not is_button_pressed:
        event, value = window.read()
        match event:
            case sg.WIN_CLOSED:
                window.close()
                is_button_pressed = True
            
            case "Back":
                window.close()
                is_button_pressed = True


def view_all_expenses(expenses_info):
    expenses = [[category, expense] for category, expense in expenses_info.items()][::-1]
    layout = [
        [sg.Text("All Expenses\n")],
        [sg.Table(values=expenses, headings=['Category', 'Amount'], max_col_width=25, auto_size_columns=True, justification='center', num_rows=10, alternating_row_color='lightblue', key='-TABLE1-')],
        [sg.Button('Back')]         
    ]
    
    window = sg.Window('My Bank', layout)
    is_button_pressed = False
    while not is_button_pressed:
        event, value = window.read()
        match event:
            case sg.WIN_CLOSED:
                window.close()
                is_button_pressed = True
            
            case "Back":
                window.close()
                is_button_pressed = True

