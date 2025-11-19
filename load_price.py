from QuikPy import QuikPy # для работы с Quik через Python
import pandas as pd
import time # для создания задержки в коде 
import warnings # для заглушения предупреждений

warnings.simplefilter("ignore") # заглушаем предупреждения

class_code_our = "QJSIM" # код класса секьюрити (взял из Quik)
sec_code_our = "AFLT" # код секьюрити

qp = QuikPy() # создаём объект, взаимодействующий с Quik

trades = pd.DataFrame(columns=["Ticker", "Price"]) # создаём датафрейм, который будем наполнять сделками
trades.loc[0] = [sec_code_our, 0] # создаём первую строчку с нулями - иначе при первом сравнении будет ошибка

for i in range(5):
    print("Получены данные о последней сделке")
    
    # получаем цену сделки
    latest_trade_price = qp.get_trade(class_code=class_code_our, sec_code=sec_code_our)["data"][-1]["price"]

    # если цена в датафрейме отличается от полученых данных
    if trades.loc[0].to_list()[-1] != latest_trade_price:
        
        # обновляем цену согласно полученым данным
        trades.loc[0, "Price"] = latest_trade_price
        
        print("Произошли новые сделки. Цена обновлена")
        print("---")
    else:
        print("Новых сделок не было")
        print("---")
    time.sleep(.1) # задержка в 0.5 секунды после загрузки данных

print(trades)
qp.close_connection_and_thread() # окончание работы python-скрипта