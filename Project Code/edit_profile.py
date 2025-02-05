import re
from tools import *
import PySimpleGUI as sg


def edit_password(users , personal_number):
    correct_password = False
    layout = [[sg.Text("Old Password"), sg.InputText()],
                  [sg.Text("New Password"), sg.InputText()],
                  [sg.Text("Confirm Password"), sg.InputText()],
                  [sg.Button("Back")],  
                  [sg.Button("OK")]  
                 ]
    window = sg.Window("Edit Password", layout)
    while not correct_password:
        option, values = window.read()
        
        if option == "Back" or option == sg.WIN_CLOSED:
            window.close()
            correct_password = True
        
        if option == "OK":
            old_password = values[0]
            new_password = values[1]
            confirmation = values[2]

            if old_password != users[personal_number]["password"]:
                sg.popup_no_border("Incorrect Password! Please try again.")
                
            elif new_password != confirmation:
                sg.popup_no_border("Passwords do not match. Please try again.")

            elif strong_password(new_password):
                if sg.popup_ok_cancel(f"Confirm Password Change?") == 'OK':
                    users[personal_number]["password"] = new_password  # Update user's password
                    update_users(users)  # Save the changes to the file
                    window.close()
                    sg.popup_no_border("Password changed successfully.")
                    correct_password = True
            
            else:
                sg.popup_no_border("Password must have at least 8 characters, including a lowercase letter, "
                    "an uppercase letter, a number, and a symbol.")
    window.close()


def edit_information (pr):
    correct_option = False
    info = open_users()
    while not correct_option:
        layout = [[sg.Text("what do you want to change?")],
                  [sg.Button("Edit Income")],        
                  [sg.Button("Edit Name")],        
                  [sg.Button("Edit Password")],        
                  [sg.Button("Back")]]
        window = sg.Window("Edit Profile Menu", layout)
        option, values = window.read()
        match option:
            case "Edit Income": 
                window.close()
                edit_income(info , pr)
            case "Edit Name": 
                window.close()
                edit_name(info ,pr)
            case "Edit Password": 
                window.close()
                edit_password(info , pr)
            case "Back": 
                window.close()
                correct_option = True
            case sg.WIN_CLOSED: 
                window.close()
                correct_option = True
    window.close()


def edit_name(users, personal_number):
    window = create_edit_name_window()
    name_pattern = r"^[A-Z][a-z]+ [A-Z][a-z]+$" 
    event, values = window.read()
    while event != sg.WIN_CLOSED and event != 'Cancel':

        new_name = values[0]
        if event == 'Ok':
            if new_name == '':
                sg.popup_no_border("Name cannot be empty!")
            elif not re.match(name_pattern,new_name):
                sg.popup_no_border("Name must consist of first name and last name, starting from capital letter!")
                
            
            elif sg.popup_ok_cancel("Are you sure you want to change name?") == 'OK':
                users[personal_number]["name"] = new_name  # Update the user's name
                update_users(users)  # Persist the changes
                sg.popup_no_border("Name has been changed.")
                break
            
        event, values = window.read()
        
    window.close()
            
            
def create_edit_name_window():
    loyout = [[sg.Text("Enter new name:"),sg.InputText()],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    return sg.Window("MyBank", loyout)

def edit_income(users, personal_number):
    window = create_edit_income_window()
    finished = False
    while not finished:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED or event == 'Cancel':
            window.close()
            finished = True
        
        elif event == 'Ok':
            new_income = values[0]
            current_income = users[personal_number]["income"]
            if new_income == '':
                sg.popup_no_border("Income cannot be empty!")
                
            elif not new_income.isdigit():
                sg.popup_no_border("Please enter a valid numeric value for income.")
                
            elif int(new_income) < 0:
                sg.popup_no_border("Income should consist only of positive numbers!")
                
            elif int(new_income) == int(current_income):
                sg.popup_no_border("The new income is the same as the current one. No changes were made.")
                
            elif sg.popup_ok_cancel("Are you sure you want to change income?") == 'OK':
                users[personal_number]["income"] = new_income  # Update the user's name
                update_users(users)  # Changes
                window.close()
                finished = True
                sg.popup_no_border("Income has been changed.")
                


def create_edit_income_window():
    loyout = [[sg.Text("Enter new income:"), sg.InputText()],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    return sg.Window("MyBank", loyout)

