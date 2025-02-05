import random
from datetime import datetime
import PySimpleGUI as sg
from tools import *
    
def view_my_cards(personal_number:str):
    user_info = open_users()
    cards = user_info[personal_number]["cards"]
    if not cards:
        sg.popup("You don't have any cards yet.")
    
    else:
        is_finished = False
        while not is_finished:
            layout=[[sg.Push(), sg.Text("My cards", font="helvetica", key="HEADER"), sg.Push()]]
            for card in cards:
                current_card = [sg.Button(f"{card['card_number']}", size=30, button_color=("white", "blue"), key=f"{card['card_number']}")]
                layout.append(current_card)
            
            layout.append([sg.Button("Back", key="EXIT", size=20), sg.Push()])

            window = sg.Window("My cards",layout, grab_anywhere=False)
            event, values = window.read()
            
            if event == sg.WIN_CLOSED or event == "EXIT":
                window.close()
                is_finished = True

            elif event != "":
                button_clicked = window[event].key
                for card in cards:
                    if card["card_number"] == button_clicked: 
                        window.close()
                        show_card(card, personal_number)



def change_card_status_to(personal_number:str, card_number:str, status:bool):
    users = open_users()
    current_user = users[personal_number]
    for card in current_user["cards"]:
        if card["card_number"] == card_number:
            card["is_active"] = status
            update_data(users, "./data/users.json")



def show_card(card:dict, personal_number:str):
    status = card["is_active"]
    is_finished = False
    while not is_finished:
        layout=[[sg.Push(), sg.Text(card["card_number"],font="helvetica", size=24), sg.Push()],
                [sg.Text(f"CVV:{card['cvv']}"), sg.Push()],
                [sg.Text(f"{card['expiration_date'][2:7]}:"), sg.Push()],
                [sg.Push(), sg.Checkbox("Active", default=status, key="ENABLE_DISABLE")],
                [sg.Push(), sg.Button(f"Change PIN", key="PIN_CHANGE", size=15)],
                [sg.Button("Save changes", key="SUBMIT", size=15, expand_x=True), sg.Push()],
                [sg.Button("Back", key="BACK", size=15, expand_x=True), sg.Push()]]
        window = sg.Window(f"Card {card['card_number']}", layout, grab_anywhere=False)
        event, values = window.read()
        
        match event:
            case sg.WIN_CLOSED:
                window.close()
                is_finished = True
            
            case "BACK":
                window.close()
                is_finished = True
            
            case "PIN_CHANGE":
                window.close()
                change_pin_gui(personal_number,card["card_number"], card["pin"])

            case "SUBMIT":
                if values["ENABLE_DISABLE"]:
                    change_card_status_to(personal_number, card["card_number"], status=True )
                    window.close()
                    sg.popup("Card activated successfully.")
                    #I unfortunately could not use the change_status function
                else:
                    change_card_status_to(personal_number, card["card_number"], status=False )
                    window.close()
                    sg.Popup("Card frozen successfully.")
                is_finished = True



def main(personal_number):
    is_finished = False
    while not is_finished:
        layout = [[sg.Push(), sg.Text('Cards', font=('Helvetica', 14, 'bold'), key='HEADER'), sg.Push()],
            [sg.VPush()],
            [sg.Push(), sg.Button('Order card', key='ORDER_CARD', size=25), sg.Push()],
            [sg.Push(), sg.Button('My cards', key='MY_CARDS', size=25), sg.Push()],
            [sg.Push(), sg.Button('Back', key='EXIT', size=25), sg.Push()],
            [sg.VPush()]]
        window = sg.Window("Cards", layout)
        event, values = window.read()
        match event:
            case sg.WIN_CLOSED:
                window.close()
                is_finished = True
            
            case 'EXIT':
                window.close()
                is_finished = True
            
            case 'ORDER_CARD':
                window.close()
                generate_card(personal_number)
            
            case 'MY_CARDS':
                window.close()
                view_my_cards(personal_number)
            


def generate_card(personal_number: str) -> None:
    order_complete = False
    layout = [[sg.Text("PIN"), sg.InputText()],
                  [sg.Button("Back")],  
                  [sg.Button("OK")]  
             ]
    window = sg.Window("Order Card", layout)
    
    while not order_complete:
        try:
            option, values = window.read()

            if option == "Back" or option == sg.WIN_CLOSED:
                window.close()
                order_complete = True

            if option == "OK":
                pin = values[0]
                if len(pin) != 4:
                    sg.popup_no_border("Please enter a 4 digit PIN number.")
                
                elif not pin.isdigit():
                    sg.popup_no_border("PIN must only consist of digits.")
                
                elif sg.popup_ok_cancel(f"Confirm Card Order?") == 'OK':
                    card_info = {
                        'card_number': generate_card_number(),
                        'cvv': generate_digit_sequence(3),
                        'pin': pin,
                        'expiration_date': f"{datetime.today().year + 5}/{datetime.today().month}/01",
                        'is_active': False
                    }
                    if save_card_info(card_info, personal_number):
                        window.close()
                        sg.popup_no_border("Card was added successfully. In order to use this card, you need to activate it.")
                        order_complete = True

                    else:
                        sg.popup_no_border("Error occurred, please try again.")
        
        except ValueError:
            sg.popup_no_border("Invalid PIN entered. Please try again.")
        except json.JSONDecodeError:
            sg.popup_no_border("There is something wrong with the JSON.")
        except FileNotFoundError:
            sg.popup_no_border("File not found.")


def generate_card_number() -> str:
    cards = read_data(".\\data\\cards.json")
    card_number = generate_digit_sequence(16)
    while card_number in cards.keys():
        card_number = generate_digit_sequence(16)
    return card_number


def generate_digit_sequence(length:int) -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

    
    
def save_card_info(card_info:dict,personal_number:dict) -> bool:
    cards = read_data(".\\data\\cards.json")
    users = read_data(".\\data\\users.json")
    """Add card to users and cards data"""
    cards[card_info['card_number']] = personal_number
    if not update_data(cards,".\\data\\cards.json"):
        return False

    users[personal_number]['cards'].append(card_info)
    if not update_data(users,".\\data\\users.json"):
        return False
    
    return True    
    

def change_pin_gui(personal_number, card_number, current_pin):
    users = open_users()
    layout = [
        [sg.Text("Enter your old pin code: "), sg.InputText(key='-INPUT old_pin-')],
        [sg.Text("Please choose your new 4 digit pin-code: "), sg.InputText(key='-INPUT new_pin-')],
        [sg.Button('Back'), sg.Button('Confirm')]         
    ]
    window = sg.Window('Change Pin', layout)
    is_finished = False
    while not is_finished:
        event, value = window.read()
        
        match event:
            case sg.WIN_CLOSED:
                window.close()
                is_finished = True
            
            case "Back":
                window.close()
                is_finished = True

            case 'Confirm':
                new_pin_code = value['-INPUT new_pin-']
                old_pin_code = value['-INPUT old_pin-']

                if old_pin_code != current_pin:
                    sg.popup_no_border("Your old PIN code is incorrect. Please try again.")
                        
                elif re.fullmatch(r'^\d{4}$',new_pin_code) is None:
                    sg.popup_no_border("New PIN is invalid! It should consist of 4 digits.")

                elif old_pin_code == new_pin_code:
                    sg.popup_no_border("New PIN cannot be the same as the old PIN.")

                else:
                    if sg.popup_ok_cancel(f"Confirm Password Change?") == 'OK': 
                        for card in users[personal_number]["cards"]:
                            if card["card_number"] == card_number:
                                card["pin"] = new_pin_code
                        update_data(users,"data/users.json")
                        window.close()
                        sg.popup_no_border('Pin-code has been updated!')

        