from QuikPy import QuikPy
import pandas as pd
import time
import warnings
import itertools

qp_provider = QuikPy()

class_code = "QJSIM"
sec_code = "SBER"
trans_id = itertools.count(1)

def read_grid(sec_code) -> pd.DataFrame:
    grid = pd.read_excel(io="Price_contracts_grid.xlsx", sheet_name = sec_code, header=0)
    grid["Quantity_delta_sell"] = grid["Quantity"] - grid["Quantity"].shift(-1).fillna(grid.tail(1)["Quantity"] + 1)
    grid["Quantity_delta_buy"] = grid["Quantity"] - grid["Quantity"].shift(1).fillna(grid.head(1)["Quantity"] - 1)
    return grid



def _on_order(data):
    """Creation of new order/change of existing order handler"""
    #new_orders_df = load_orders()
    #print(tabulate(new_orders_df, headers="keys", tablefmt="psql"))

def _on_trade(data):
    """ Execution of a new trade handler """
    grid = read_grid(sec_code=sec_code)
    new_trades_df = load_trades()
    
    latest_trade = new_trades_df.tail(1)
    print(f"Цена последней сделки: {float(latest_trade["Price"])}")
    grid_position_latest_price = grid[grid["Price"] < float(latest_trade["Price"])].head(1).index[0]
    type_latest_trade = latest_trade["Trade_Type"].to_list()[0]
    print(f"Тип последней сделки: {type_latest_trade}")
    
    if type_latest_trade == "Buy":
        
        price_for_buy_order = grid.loc[grid_position_latest_price, "Price"]
        price_for_sell_order = grid.loc[grid_position_latest_price - 1, "Price"]
        
        quantity_for_buy_order = grid.loc[grid_position_latest_price, "Quantity_delta_buy"]
        quantity_for_sell_order = -grid.loc[grid_position_latest_price - 1, "Quantity_delta_sell"]     
        
        if float(latest_trade["Price"]) < price_for_buy_order or float(latest_trade["Price"]) > price_for_sell_order:
            price_for_buy_order = qp_provider.price_to_quik_price(class_code="QJSIM", sec_code="SBER", price=price_for_buy_order)
            price_for_sell_order = qp_provider.price_to_quik_price(class_code="QJSIM", sec_code="SBER", price=price_for_sell_order)
            place_buy_order(price=price_for_buy_order, quantity=quantity_for_buy_order)
            place_sell_order(price=price_for_sell_order, quantity=quantity_for_sell_order)
    
    else:
        
        price_for_buy_order = grid.loc[grid_position_latest_price, "Price"]
        price_for_buy_order = qp_provider.price_to_quik_price(class_code="QJSIM", sec_code="SBER", price=price_for_buy_order)
        price_for_sell_order = grid.loc[grid_position_latest_price - 1, "Price"]
        price_for_sell_order = qp_provider.price_to_quik_price(class_code="QJSIM", sec_code="SBER", price=price_for_sell_order)
        
        quantity_for_buy_order = grid.loc[grid_position_latest_price, "Quantity_delta_buy"]
        quantity_for_sell_order = -grid.loc[grid_position_latest_price - 1, "Quantity_delta_sell"]     
        
        if float(latest_trade["Price"]) < price_for_buy_order or float(latest_trade["Price"]) > price_for_sell_order:
            price_for_buy_order = qp_provider.price_to_quik_price(class_code="QJSIM", sec_code="SBER", price=price_for_buy_order)
            price_for_sell_order = qp_provider.price_to_quik_price(class_code="QJSIM", sec_code="SBER", price=price_for_sell_order)
            place_buy_order(price=price_for_buy_order, quantity=quantity_for_buy_order)
            place_sell_order(price=price_for_sell_order, quantity=quantity_for_sell_order)

       
    

def place_buy_order(price, quantity) -> None:
    transaction = {
        "TRANS_ID" : str(next(trans_id)),
        "CLIENT_CODE" : "10651",
        "ACCOUNT" : "NL0011100043",
        'ACTION' : 'NEW_ORDER',
        'CLASSCODE' : "QJSIM",
        'SECCODE' : "SBER",
        'OPERATION' : 'B',
        'PRICE' : str(price),
        'QUANTITY' : str(int(quantity)),
        'TYPE' : 'L'}
    print(qp_provider.send_transaction(transaction=transaction))
    
def place_sell_order(price, quantity) -> None:
    transaction = {
        "TRANS_ID" : str(next(trans_id)),
        "CLIENT_CODE" : "10651",
        "ACCOUNT" : "NL0011100043",
        'ACTION' : 'NEW_ORDER',
        'CLASSCODE' : "QJSIM",
        'SECCODE' : "SBER",
        'OPERATION' : 'S',
        'PRICE' : str(price),
        'QUANTITY' : str(int(quantity)),
        'TYPE' : 'L'}
    print(qp_provider.send_transaction(transaction=transaction))



def load_orders() -> pd.DataFrame:
    curr_orders = qp_provider.get_all_orders()["data"]
    new_orders_df = pd.DataFrame(columns=["Order_ID", "Security_Code", "Order_Type", "Placement_Date_Time", "Expiry_Date", "Price"])
    for curr_order in curr_orders:
        if curr_order["balance"] != 0.0 and format(curr_order["flags"], "#010b")[2:][-2] != "1":
            curr_order_row = pd.DataFrame({"Order_ID" : int(curr_order["ordernum"]), 
                                           "Security_Code" : curr_order["seccode"],
                                           "Order_Type" : "Buy" if format(curr_order["flags"], "#010b")[2:][-3] == "0" else "Sell",
                                           "Placement_Date_Time" : f"{curr_order["datetime"]["day"]}.{curr_order["datetime"]["month"]}.{curr_order["datetime"]["year"]} {curr_order["datetime"]["hour"]}:{curr_order["datetime"]["min"]}:{curr_order["datetime"]["sec"]}",
                                           "Expiry_Date" : curr_order["expiry"],
                                           "Price" : curr_order["value"] / curr_order["qty"]}, index=[0])
            with warnings.catch_warnings(category=FutureWarning):
                warnings.simplefilter(action="ignore")
                new_orders_df = pd.concat([new_orders_df, curr_order_row], axis=0, ignore_index=True)
    return new_orders_df

def load_trades() -> pd.DataFrame:
    curr_trades = qp_provider.get_all_trades()["data"]
    new_trades_df = pd.DataFrame(columns=["Trade_ID", "Order_ID", "Security_Code", "Trade_Type", "Execution_Date_Time", "Price"])
    for curr_trade in curr_trades:
        curr_trade_row = pd.DataFrame({"Trade_ID" : curr_trade["trade_num"],
                                       "Order_ID" : curr_trade["ordernum"],
                                       "Security_Code" : curr_trade["seccode"],
                                       "Trade_Type" : "Buy" if format(curr_trade["flags"], "#010b")[2:][-3] == "0" else "Sell",
                                       "Execution_Date_Time" : f"{curr_trade["datetime"]["day"]}.{curr_trade["datetime"]["month"]}.{curr_trade["datetime"]["year"]} {curr_trade["datetime"]["hour"]}:{curr_trade["datetime"]["min"]}:{curr_trade["datetime"]["sec"]}",
                                       "Price" : curr_trade["price"]}, index=[0])
        with warnings.catch_warnings(category=FutureWarning):
            warnings.simplefilter(action="ignore")
            new_trades_df = pd.concat([new_trades_df, curr_trade_row], axis=0, ignore_index=True)
    return new_trades_df



qp_provider.on_order.subscribe(_on_order)
qp_provider.on_trade.subscribe(_on_trade)

for i in range(1000000):
    time.sleep(0.01)

qp_provider.close_connection_and_thread()