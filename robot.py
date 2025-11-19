from QuikPy import QuikPy
import pandas as pd
from tabulate import tabulate

qp_provider = QuikPy()

class_code = "QJSIM"
sec_code = "SBER"

grid = pd.read_excel(io="Price_contracts_grid.xlsx", sheet_name = sec_code, header=0)
grid["Quantity_delta_sell"] = grid["Quantity"] - grid["Quantity"].shift(-1).fillna(grid.tail(1)["Quantity"] + 1)
grid["Quantity_delta_buy"] = grid["Quantity"] - grid["Quantity"].shift(1).fillna(grid.head(1)["Quantity"] -1)

def on_order(data):
    """Creation of new order/change of existing order handler"""
    print('OnOrder')
    print(data['data'])

def on_trade(data):
    """ ??? """
    print('OnTrade')
    print(data['data'])
       
    

def place_buy_order(price, quantity):
    transaction = {
        'ACTION': 'NEW_ORDER',
        'CLASSCODE': class_code,
        'SECCODE': sec_code,
        'OPERATION': 'B',
        'PRICE': str(price),
        'QUANTITY': str(quantity),
        'TYPE': 'L'}
    qp_provider.send_transaction(transaction=transaction)
    
def place_sell_order(price, quantity):
    transaction = {
        'ACTION': 'NEW_ORDER',
        'CLASSCODE': class_code,
        'SECCODE': sec_code,
        'OPERATION': 'S',
        'PRICE': str(price),
        'QUANTITY': str(quantity),
        'TYPE': 'L'}
    qp_provider.send_transaction(transaction=transaction)
    


orders_df = pd.DataFrame(columns=["Order_ID", "Security_Code", "Order_Type", "Placement_Date_Time", "Price"])
curr_orders = qp_provider.get_all_orders()["data"]
for curr_order in curr_orders:
    if curr_order["balance"] != 0.0 and bin(curr_order["flags"])[2:][-2] != "1":
        curr_order_row = pd.DataFrame({"Order_ID" : int(curr_order["ordernum"]), 
                                       "Security_Code" : curr_order["seccode"],
                                       "Order_Type" : "Buy" if bin(curr_order["flags"])[2:][-3] == "0" else "Sell",
                                       "Placement_Date_Time" : f"{curr_order["datetime"]["day"]}.{curr_order["datetime"]["month"]}.{curr_order["datetime"]["year"]} {curr_order["datetime"]["hour"]}:{curr_order["datetime"]["min"]}:{curr_order["datetime"]["sec"]}",
                                       "Price" : int(curr_order["value"])}, index=[0])
        if curr_order["ordernum"] not in orders_df["Order_ID"]:
            orders_df = pd.concat([orders_df, curr_order_row], axis=0)
            
trades_df = pd.DataFrame(columns=["Trade_ID", "Security_Code", "Trade_Type", "Execution_Date_Type", "Price"])
curr_trades = qp_provider.get_all_trades()["data"]
#for curr_trade in curr_trades:
    

#print(tabulate(orders_df, headers="keys", tablefmt="psql"))
qp_provider.close_connection_and_thread()