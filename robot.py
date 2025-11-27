from QuikPy import QuikPy # для взаимодействия с Quik
import pandas as pd # для удобной работы с таблицами
import time # для установки задержки в работе программы
import warnings # для заглушения предупреждений в коде
import itertools # для генерации ID транзакций
warnings.simplefilter("ignore") # КОСТЫЛЬ, УБРАТЬ!!!

qp_provider = QuikPy() # устанавливаем соединение с Quik

class_code = "QJSIM"
sec_code = "SBER"
trans_id_buy = itertools.count(start=2, step=2) # начинаем генерировать ID транзакций для заявок на покупку, начинаем с 2 и идём по чётным числам
trans_id_sell = itertools.count(start=3, step=2) # аналогично для продажи - с 3 и по нечётным числам
trans_id_remove = 1 # единицу резервируем под ID для посылки отмены заявки
order_num_buy = 0 # задаём номер заявки на покупку - он заполняется в _on_trans_reply
order_num_sell = 0 # аналогично с заявкой на продажу


def read_grid(sec_code) -> pd.DataFrame:
    """ Функция, считывающая сетку 'цена-позиция' """
    grid = pd.read_excel(io="Price_contracts_grid.xlsx", sheet_name = sec_code, header=0)
    grid["Quantity_delta_sell"] = grid["Quantity"] - grid["Quantity"].shift(-1).fillna(grid.tail(1)["Quantity"] + 1) # в колонке хранится разница между позициями для соответствующих цен - она же кол-во в заявке
    grid["Quantity_delta_buy"] = grid["Quantity"] - grid["Quantity"].shift(1).fillna(grid.head(1)["Quantity"] - 1) # аналогично
    return grid



def _on_trans_reply(data) -> None: 
    """ Обработчик события 'отправлена новая заявка' """
    global order_num_buy # создаём глобальную переменную с номером заявки, если она была на покупку
    global order_num_sell # аналогично, если она была на продажу
    if int(data["data"]["trans_id"] % 2) == 0: # если заявка была на покупку
        order_num_buy = int(data["data"]["order_num"]) # записываем номер заявки на покупку в переменную
    else:
        order_num_sell = int(data["data"]["order_num"]) # аналогично для заявки на продажу

def _on_trade(data) -> None:
    """ Обработчик события 'получена новая сделка (наша)' """
    grid = read_grid(sec_code=sec_code)
    new_trades_df = load_trades() # загружаем новые сделки
    
    latest_trade = new_trades_df.tail(1) # получаем информацию о последней сделке
    grid_position_latest_price = grid[grid["Price"] < float(latest_trade["Price"])].head(1).index[0] # получаем номер строки, соответствующей цене последней сделки
    type_latest_trade = latest_trade["Trade_Type"].to_list()[0] # получаем тип ("Buy"/"Sell" последней сделки)
    
    if type_latest_trade == "Buy":
        
        price_for_buy_order = round(grid.loc[grid_position_latest_price + 1, "Price"], 2) # задаём цену для заявки на покупку (следующая строка schedule'a)
        price_for_sell_order = round(grid.loc[grid_position_latest_price - 1, "Price"], 2) # задаём цену для заявки на продажу (предыдущая строка schedule'a)
        
        quantity_for_buy_order = grid.loc[grid_position_latest_price + 1, "Quantity_delta_buy"] # задаём количество для заявки на покупку (следующая строка schedule'a)
        quantity_for_sell_order = -grid.loc[grid_position_latest_price - 1, "Quantity_delta_sell"] # задаём количество для заявки на продажу (предыдущая строка schedule'a)
        
        global order_num_sell
        remove_sell_order(order_num=order_num_sell) # снимаем оставшуюся заявку на продажу

        place_buy_order(price=price_for_buy_order, quantity=quantity_for_buy_order, order_type="L")
        place_sell_order(price=price_for_sell_order, quantity=quantity_for_sell_order, order_type="L")
    
    else:
        
        price_for_buy_order = round(grid.loc[grid_position_latest_price + 1, "Price"], 2) # задаём цену для заявки на покупку (следующая строка schedule'a)
        price_for_sell_order = round(grid.loc[grid_position_latest_price - 1, "Price"], 2) # задаём цену для заявки на продажу (предыдущая строка schedule'a)
        
        quantity_for_buy_order = grid.loc[grid_position_latest_price + 1, "Quantity_delta_buy"] # задаём количество для заявки на покупку (следующая строка schedule'a)
        quantity_for_sell_order = -grid.loc[grid_position_latest_price - 1, "Quantity_delta_sell"] # задаём количество для заявки на продажу (предыдущая строка schedule'a)
        
        global order_num_buy
        remove_buy_order(order_num=order_num_buy) # снимаем оставшуюся заявку на покупку
        
        place_buy_order(price=price_for_buy_order, quantity=quantity_for_buy_order, order_type="L")
        place_sell_order(price=price_for_sell_order, quantity=quantity_for_sell_order, order_type="L")

       
    

def place_buy_order(quantity, order_type, price=0) -> None:
    transaction = {
        "TRANS_ID" : str(next(trans_id_buy)), # задаём номер сделки как предыдущий номер сделки (покупки) + 2 => будет чётным
        "CLIENT_CODE" : "10651",
        "ACCOUNT" : "NL0011100043",
        'ACTION' : 'NEW_ORDER',
        'CLASSCODE' : class_code,
        'SECCODE' : sec_code,
        'OPERATION' : 'B',
        'PRICE' : str(price),
        'QUANTITY' : str(int(quantity)),
        'TYPE' : order_type}
    qp_provider.send_transaction(transaction=transaction)
    
def place_sell_order(quantity, order_type, price=0) -> None:
    transaction = {
        "TRANS_ID" : str(next(trans_id_sell)), # задаём номер сделки как предыдущий номер сделки (продажи) + 2 => будет нечётным
        "CLIENT_CODE" : "10651",
        "ACCOUNT" : "NL0011100043",
        'ACTION' : 'NEW_ORDER',
        'CLASSCODE' : class_code,
        'SECCODE' : sec_code,
        'OPERATION' : 'S',
        'PRICE' : str(price),
        'QUANTITY' : str(int(quantity)),
        'TYPE' : order_type}
    qp_provider.send_transaction(transaction=transaction)
    
def remove_buy_order(order_num) -> None:
    transaction = {
        'TRANS_ID': str(trans_id_remove), # trans_id_remove=1
        'ACTION': 'KILL_ORDER',
        'CLASSCODE': class_code,
        'SECCODE': sec_code,
        'ORDER_KEY': str(order_num)}
    qp_provider.send_transaction(transaction=transaction)
    
def remove_sell_order(order_num) -> None:
    transaction = {
        'TRANS_ID': str(trans_id_remove), # trans_id_remove=1
        'ACTION': 'KILL_ORDER',
        'CLASSCODE': class_code,
        'SECCODE': sec_code,
        'ORDER_KEY': str(order_num)}
    qp_provider.send_transaction(transaction=transaction)


def init() -> None:
    """ Функция запускается в начале работы алгоритма и автоматически выставляет рыночный ордер на покупку/продажу такого количества контрактов, которое выровняет нас по schedule"""
    grid = read_grid(sec_code=sec_code)
    
    last_trade_before_init = qp_provider.get_trade(class_code=class_code, sec_code=sec_code)["data"][-1] # получаем данные о последней сделке на рынке
    last_price_before_init = last_trade_before_init["price"] # получаем из них цену последней сделки
    
    grid_position_last_price_before_init = int(grid[grid["Price"] < float(last_price_before_init)].head(1).index[0]) # находим номер строки schedule, соответствующей этой цене
    wanted_instrument_position = grid.loc[grid_position_last_price_before_init, "Quantity"] # записываем из этой строки количество контрактов, которое должно быть для этой цены
    
    curr_instrument_position = qp_provider.get_depo_limits(sec_code=sec_code)["data"][-1]["currentbal"] # получаем текущую позицию по инструменту
        
    init_order_quantity = wanted_instrument_position - curr_instrument_position # рассчитываем, сколько контрактов нужно купить/продать
    if init_order_quantity > 0:
        place_buy_order(quantity=init_order_quantity, order_type="M")
    elif init_order_quantity < 0:
        place_sell_order(quantity=-init_order_quantity, order_type="M")

def load_orders() -> pd.DataFrame:
    """ Функция загружает наши заявки """
    curr_orders = qp_provider.get_all_orders()["data"] # получаем все заявки
    new_orders_df = pd.DataFrame(columns=["Order_ID", "Security_Code", "Order_Type", "Placement_Date_Time", "Expiry_Date", "Price"]) # создаём датафрейм, в который запишем новые заявки
    for curr_order in curr_orders: # для каждой загруженной заявки
        if curr_order["balance"] != 0.0 and format(curr_order["flags"], "#010b")[2:][-2] != "1": # если заявка не исполнена и не снята
            # записываем информацию о заявке
            curr_order_row = pd.DataFrame({"Order_ID" : int(curr_order["ordernum"]), # уникальный номер заявки
                                           "Security_Code" : curr_order["seccode"], # код инструмента
                                           "Order_Type" : "Buy" if format(curr_order["flags"], "#010b")[2:][-3] == "0" else "Sell", # тип заявки (либо "Buy", либо "Sell")
                                           "Placement_Date_Time" : f"{curr_order["datetime"]["day"]}.{curr_order["datetime"]["month"]}.{curr_order["datetime"]["year"]} {curr_order["datetime"]["hour"]}:{curr_order["datetime"]["min"]}:{curr_order["datetime"]["sec"]}", # дата и время выставления заявки
                                           "Expiry_Date" : curr_order["expiry"], # дата и время экспирации заявки (-1, если не применимо)
                                           "Price" : curr_order["value"] / curr_order["qty"]}, index=[0]) # цена в заявке
            
            with warnings.catch_warnings(category=FutureWarning): # КОСТЫЛЬ, УБРАТЬ!!!
                warnings.simplefilter(action="ignore")
                
                new_orders_df = pd.concat([new_orders_df, curr_order_row], axis=0, ignore_index=True) # записываем заявку в датафрейм
    return new_orders_df

def load_trades() -> pd.DataFrame:
    """ Функция загружает наши сделки """
    curr_trades = qp_provider.get_all_trades()["data"] # получаем все НАШИ сделки
    new_trades_df = pd.DataFrame(columns=["Trade_ID", "Order_ID", "Security_Code", "Trade_Type", "Execution_Date_Time", "Price"]) # создаём датафрейм, в который запишем новые сделки
    for curr_trade in curr_trades: # для каждой загруженной сделки
        # записываем информаци о сделке
        curr_trade_row = pd.DataFrame({"Trade_ID" : curr_trade["trade_num"], # уникальный номер сделки
                                       "Order_ID" : curr_trade["ordernum"], # номер заявки, по которой прошла сделка
                                       "Security_Code" : curr_trade["seccode"], # код инструмента
                                       "Trade_Type" : "Buy" if format(curr_trade["flags"], "#010b")[2:][-3] == "0" else "Sell", # тип сделки (либо "Buy", либо "Sell")
                                       "Execution_Date_Time" : f"{curr_trade["datetime"]["day"]}.{curr_trade["datetime"]["month"]}.{curr_trade["datetime"]["year"]} {curr_trade["datetime"]["hour"]}:{curr_trade["datetime"]["min"]}:{curr_trade["datetime"]["sec"]}", # дата и время исполнения сделки
                                       "Price" : curr_trade["price"]}, index=[0]) # цена исполнения сделки
        
        with warnings.catch_warnings(category=FutureWarning): # КОСТЫЛЬ, УБРАТЬ!!!
            warnings.simplefilter(action="ignore")
            
            new_trades_df = pd.concat([new_trades_df, curr_trade_row], axis=0, ignore_index=True) # записываем сделку в датафрейм
    return new_trades_df



qp_provider.on_trade.subscribe(_on_trade) # подписываемся на новые сделки
qp_provider.on_trans_reply.subscribe(_on_trans_reply) # подписываемся на результат отправки заявки

init()

while True: # бесконечный цикл
    time.sleep(0.1) # задержка на 0.1 секунду между любыми операциями

# сделать в Excel таблицу инструментов    
# сделать проверку спрэда при инициализации (lster)

# нужно вытаскивать цену в заявке, по которой прошла последняя наша сделка по инструменту, 
# и проверять на соответствие количества контрактов
# если правильно:
#    начинаю по schedule без "выравниваний"
# если нет:
#    quit() и сообщение в Quik

# в schedule будет остановка
# что делать, если поис к schedule не нашёл нужного уровня?