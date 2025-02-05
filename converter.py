from tools import *
import PySimpleGUI as sg
import requests

def check_the_currency(currency_code):
    """Validate and return currency description."""
    currency_map = read_data(".\\data\\currency.json")
    return currency_map.get(currency_code.upper(), None)

def convert_currency(amount, from_currency, to_currency):
    """Fetch data and convert currency."""
    response = requests.get(
        f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
    )
    if response.status_code == 200:
        return round(response.json()["rates"].get(to_currency.upper(), 0), 2)
    return None

def main():
    """Create a PySimpleGUI currency converter app."""
    currency_map = read_data(".\\data\\currency.json")

    currency_data = [
        (code, desc) for code, desc in currency_map.items()
    ]

    layout = [
        [sg.Text("Currency Converter", font=("Helvetica", 16), justification="center",expand_x=True)],
        [sg.Column([[sg.Text(f"{code}: {desc}", font=("Helvetica", 12))] for code, desc in currency_data],scrollable=True,vertical_scroll_only=True,justification='center'),
        ],

        [
        sg.HorizontalSeparator()],
        [sg.Text("From Currency"), sg.InputText(key="-FROM-")],
        [sg.Text("To Currency"), sg.InputText(key="-TO-")],
        [sg.Text("Amount"), sg.InputText(key="-AMOUNT-")],
        [sg.Button("Convert", key="-CONVERT-"), sg.Button("Exit", key="-EXIT-")],
        [sg.Text("", key="-RESULT-")]
    ]

    converter_window = sg.Window("Currency Converter", layout,size=(400, 650))


    choice = ""
    while choice != "exit":
        event, values = converter_window.read()
        if event == sg.WINDOW_CLOSED:
            converter_window.close()
            choice = "exit"

        if event == "-EXIT-":
            user_choice = sg.popup_yes_no("You really want to close this page?")
            if user_choice == "Yes":
                converter_window.close()
                choice = "exit"
            else:
                continue

        if event == "-CONVERT-":
            from_currency = values["-FROM-"].strip().upper()
            to_currency = values["-TO-"].strip().upper()
            try:
                amount = float(values["-AMOUNT-"].strip())
            except ValueError:
                sg.popup("Please enter a valid amount.", text_color="red",font=("Helvetica", 12, "bold"))
                continue

            if check_the_currency(from_currency) is None:
                sg.popup("Invalid 'From' currency code.", text_color="red",font=("Helvetica", 12, "bold"))
                continue

            if check_the_currency(to_currency) is None:
                sg.popup("Invalid 'To' currency code.", text_color="red",font=("Helvetica", 12, "bold"))
                continue

            if from_currency == to_currency:
                sg.popup("Cannot convert currency to itself.", text_color="red",font=("Helvetica", 12, "bold"))
                continue

            result = convert_currency(amount, from_currency, to_currency)
            if result is not None:
                sg.popup(f"{amount} {from_currency} = {result} {to_currency}", text_color="#7cfc00",font=("Helvetica", 12, "bold"))
            else:
                sg.popup("Conversion failed. Try again.", text_color="red",font=("Helvetica", 12, "bold"))

    converter_window.close()