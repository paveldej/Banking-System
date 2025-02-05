
from tools import *
from login_register import check_personal_number
from stock_api import *
import PySimpleGUI as sg

def main(personal_number):
    format = [[sg.Button("view stocks")] ,
              [sg.Button("buy stocks")],
              [sg.Button("sell stocks")],
              [sg.Button("send stocks")],
              [sg.Button("back")]]
    window = sg.Window("Stocks menu" , format)
    event, values = window.read()
    while event != "back" and event != sg.WIN_CLOSED:
        match event :
            case "view stocks":
                view_stocks(personal_number)
            case "buy stocks":
                buy_stocks(personal_number)
            case "sell stocks":
                sell_stocks(personal_number)
            case "send stocks" :
                send_stocks(personal_number)
        event, values = window.read()
    window.close()


def buy_stocks(personal_number):
    layout = [[sg.Text('Buy Stocks', font=(48), expand_x=True, justification='center')],
            [sg.Text('Stock Name: ', font=(32)),sg.Sizer(30), sg.Input(font=(32), s=30, key="stock_name")],
            [sg.Text('Amount ', font=(32)),sg.Sizer(30), sg.Input(font=(32), s=30, key="purchase_amount")],
            [sg.Button('Confirm', font=(32)), sg.Button('Back', font=(32))]]
    window = sg.Window('Login', layout)

    finished = False
    while not finished:
        try:
            event, values = window.read()
            if event == "Confirm":
                stock_name = values["stock_name"]
                if find_name(stock_name) == None:
                        raise Exception
                if not finished:
                    stock_name = get_name(stock_name)
                    stock_price = float(get_price(stock_name))
                    if stock_name == None or stock_price == None:
                        raise Exception
                    users = open_users()
                    balance = users[personal_number]["balance"]
                    purchase_amount = int(values["purchase_amount"])
                    while purchase_amount < 1 or purchase_amount * stock_price > balance:
                        error_layout = [[sg.Text("Not enough balance, or invalid amount entered. Please try again."), sg.Button("OK")]]
                        error_window = sg.Window("error",error_layout)
                        event, values = error_window.read()
                        error_window.close()
                        event,values = window.read()
                        purchase_amount = int(values["purchase_amount"])
                    
                    if event == "Confirm":
                        purchase_amount = int(values["purchase_amount"])
                        balance = users[personal_number]["balance"]
                        total_price = purchase_amount * stock_price
                        prompt = f"Are you sure you wish to purchase {purchase_amount} {stock_name} for a total of {total_price} SEK?"
                        if confirm_action(prompt):
                                update_balance(personal_number, -total_price)
                                updateStocks(personal_number, stock_name, purchase_amount)
                                finished = True
                                window.close()
                    else:
                        finished = True
                        window.close()
            else:
                finished = True
                window.close()

        except Exception:
            error_layout = [[sg.Text('The stock market is currently offline or You have entered an invalid value'), sg.Button("OK")]]
            error_window = sg.Window("error",error_layout)
            event, values = error_window.read()
            error_window.close()
        

    

def updateStocks(personal_number, stock_name, amount):
    stocks = read_data("./data/stocks.json")
    if not stocks.get(personal_number):     #if the user does not hava a stocks dictionary, make it for them
        stocks[personal_number] = {}
    if not stocks[personal_number].get(stock_name):       #if the user does not have the stock already, make it for them
        stocks[personal_number][stock_name] = amount
    else:
        stocks[personal_number][stock_name] += amount       #if the user already has the stock, add it to the old amount
    if not update_data(stocks,"./data/stocks.json"):
        print("An error occured, please try again. ")


def sell_stocks(personal_number):
    stocks = read_data("data/stocks.json")
    user_stocks = stocks.get(personal_number , None)
    if user_stocks is None:
        error_layout = [[sg.Text("You don't have any stocks owned"), sg.Button("OK")]]
        error_window = sg.Window("error",error_layout)
        event, values = error_window.read()
        error_window.close()
    else: 
        stocks_list = []
        holding_shares = 0
        for stock , shares in user_stocks.items():
            stocks_list.append(stock)

        #display the window and get data
        layout = [[sg.Text('Sell Stocks', font=(48), expand_x=True, justification='center')],
            [sg.Text('Stocks: ', font=(32)),sg.Sizer(30), sg.Combo(stocks_list, default_value=stocks_list[0], key="stock_name")],
            [sg.Text('Amount ', font=(32)),sg.Sizer(30), sg.Input(font=(32), s=30, key="purchase_amount")],
            [sg.Button('Confirm', font=(32)), sg.Button('Back', font=(32))]]
        window = sg.Window('Login', layout)

        program_running = True
        while program_running:
            #save stocks in a list
            event, values = window.read()
            if event == "Confirm":  
                try:
                    choosen_stock = values["stock_name"]
                    holding_shares = user_stocks[choosen_stock]
                    amount = int(values["purchase_amount"])

                    #validate the input
                    while amount > holding_shares:
                        error_layout = [[sg.Text("You don't have that many shares"), sg.Button("OK")]]
                        error_window = sg.Window("error",error_layout)
                        event, values = error_window.read()
                        error_window.close()
                        event,values = window.read() 
                        if event == "Confirm":
                            amount = int(values["purchase_amount"])
                            choosen_stock = values["stock_name"]
                        else:
                            window.close()
                            return None

                    #check the api
                    price = get_price(choosen_stock)
                    if price is None:
                        error_layout = [[sg.Text('The stock market is currently offline'), sg.Button("OK")]]
                        error_window = sg.Window("error",error_layout)
                        event, values = error_window.read()
                        error_window.close()
                        window.close()
                        program_running = False
                    else:
                        price = float(price)
                        prompt = f"you are about to sell {amount} of the total {holding_shares} you have, with the price of {price * amount} , are you sure?"
                        
                        if confirm_action(prompt):
                            if holding_shares == amount:
                                del stocks[personal_number][choosen_stock]
                            else:
                                stocks[personal_number][choosen_stock] = holding_shares - amount
                            update_data(stocks,"data/stocks.json")
                            update_balance(personal_number, price * amount)
                            correct_input = True
                            program_running = False
                            window.close()
                            return

                except Exception:
                    sg.popup_error("You have entered an invalid value.")


            else:
                program_running = False
        window.close()
        

def send_stocks(personal_number):
    stocks = read_data("data/stocks.json")
    customer_stocks = stocks.get(personal_number)
    if customer_stocks is None :
        sg.popup("you have no stocks.")
        return
    else:
        names = []
        for stock_names in customer_stocks.keys():
            names.append(stock_names)
        running = True
        while running:
            format = [[sg.Text("Stocks : ")],[sg.Combo(names)],
                    [sg.Text("Amount of shares : ")],[sg.Input()],
                    [sg.Text("Reciever's personal number : ")],[sg.Input()],
                    [sg.Button('ok'), sg.Button('cancel')]]
            window = sg.Window("sending stocks" , format)
            event, values = window.read()
            
            
            match event:
                case "cancel" :
                    window.close()
                    running = False
                case sg.WIN_CLOSED:
                    window.close()
                    running = False
                case "ok":
                    choosen_stock = values[0]
                    stock = None
                    amount_to_send = values[1]
                    receiver_personal_number = values[2]
                    window.close()
                    running = False
                    update = True
                    
                    if not check_personal_number(receiver_personal_number):
                        if sg.popup_yes_no("Invalid format of personal number,do you want to try again") == "Yes" :
                            update = False
                            running = True
                        else: running = False
                    
                    try:
                        check_amount = int(amount_to_send)
                    except : 
                        if sg.popup_yes_no("Invalid amount,do you want to try again") == "Yes" :
                            update = False
                            running = True
                        else: running = False
                    if choosen_stock == "":
                        if sg.popup_yes_no("you did not choose a stock , do you want to try again") == "Yes" :
                            update = False
                            running = True
                        else: running = False
                
                        

                    if stocks[personal_number][choosen_stock] < check_amount :
                        update = False
                        if sg.popup_yes_no("you dont have enough shares , do you want to try again") == "Yes" :
                            running = True
                        else :
                            running = False

                    
                            
                    if update:  
                        if sg.popup_yes_no("Are you sure you want to complete transaction") == 'Yes': 
                            
                            if stocks.get(receiver_personal_number) is None:
                                stocks[receiver_personal_number] = {choosen_stock : int(amount_to_send)}
                                
                            elif stocks[receiver_personal_number].get(choosen_stock) is None:
                                stocks[receiver_personal_number][choosen_stock] = int(amount_to_send)
                                
                            else:
                                owned = int(stocks[receiver_personal_number][choosen_stock])
                                amount = owned + int(amount_to_send)
                                


                        if stocks[personal_number][choosen_stock] == int(amount_to_send):
                            del stocks[personal_number][choosen_stock]
                        else:    
                            stocks[personal_number][choosen_stock] -= int(amount_to_send)
                        
                        update_data(stocks, "data/stocks.json")
                        sg.popup("Transaction has been completed.")
            

            
                
        
        

       
            
                

    
def get_view_stocks_window(customer_stocks):
    layout = [[sg.Text("Your owned stocks")],
               [sg.Table(values = list([name,amount] for name,amount in customer_stocks.items()), headings = ["Stock name", "Amount"], key = "stocks")],
               [sg.Button("Back")]]
    return sg.Window("Bank", layout)    

    
def view_stocks(personal_number):
    customer_stocks = None
    try:
        customer_stocks = read_data("./data/stocks.json")[personal_number]
    except KeyError:
        sg.popup_no_border("Your stocks haven't been found.")
        return
    
    window = get_view_stocks_window(customer_stocks)
    is_running = True
    while is_running:
        event, values = window.read()
        if event == "Back" or event == sg.WIN_CLOSED:
            is_running = False
    
    window.close()