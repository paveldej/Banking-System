#THIS IS THE MAIN PROGRAM

import PySimpleGUI as sg
from edit_profile import edit_information
from account_overview import main as customer_account_overview
from cards import main as organise_cards
from login_register import main_menu as customer_login_register
from transfers import main as make_transfers
from loans import main as loans
from savings import main as savings
from tools import sync


def main():
    sync()
    personal_number = 0
    while personal_number!= None:
        personal_number, name = customer_login_register()
        
        if personal_number != None:
            is_button_clicked = False
            while not is_button_clicked:
                window = create_main_window()
                event, values = window.read()
                match event:
                    case sg.WIN_CLOSED:
                        window.close()
                        sg.popup_no_border("See you next time!")
                        is_button_clicked = True
                    case 'Log out':
                        window.close()
                        sg.popup_no_border("See you next time!")
                        is_button_clicked = True
                    case 'Edit Information':
                        window.close()
                        edit_information(personal_number)
                        is_button_clicked = True
                    case 'Account Overview':
                        window.close()
                        customer_account_overview(personal_number, name)
                    case 'Transfers':
                        window.close()
                        make_transfers(personal_number)
                    case 'Cards':
                        window.close()
                        organise_cards(personal_number)
                    case 'Loans':
                        window.close()
                        loans(personal_number)
                    case 'Savings':
                        window.close()
                        savings(personal_number)
        
    
        
                
def create_main_window():
    button_size = (13,2)
    layout = [[sg.Button('Log out',)],
              [sg.Button('Edit Information',size=button_size)],
              [sg.Button('Account Overview',size=button_size)],
              [sg.Button('Transfers',size=button_size)],
              [sg.Button('Cards',size=button_size)],
              [sg.Button('Loans',size=button_size)],
              [sg.Button("Savings",size=button_size)]]
    return sg.Window("MyBank", layout)
    
    
        
            
if __name__ == "__main__":
    main()

    
