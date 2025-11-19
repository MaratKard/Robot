from QuikPy import QuikPy  # Работа с QUIK из Python через LUA скрипты QuikSharp
import time 

lot = int(input('Введите лотаж позиции'))
grid = int(input('Суммарное количество лимитных ордеров:'))
gridrange = float(input('Какой ход цены для грид-бота?')) // 2
local_stop = -(int(input('Какой убыток за 1 цикл вы готовы понести?')) )
grid_stop = -(int(input('Какой убыток грид-бота вообщем вы готовы понести?')) )
quantity = int(input('Количество акций в лотах на одну линию сетки'))

unrealized_pnl = 0
avg_price = 0
position = 0
result = 0
class_code = "QJSIM"  # Код площадки
sec_code = "AFLT"  # Код тикера
trans_id = 12358  # Номер транзакции
diff = gridrange * 2 / grid # Ход цены для лимитки
flag = True



def on_trans_reply(data):
    """Обработчик события ответа на транзакцию пользователя"""
    print('OnTransReply')
    print(data['data'])  # Печатаем полученные данные


def on_order(data):
    """Обработчик события получения новой / изменения существующей заявки"""
    print('OnOrder')
    print(data['data'])  # Печатаем полученные данные


def on_trade(data):
    """Обработчик события получения новой / изменения существующей сделки
    Не вызывается при закрытии сделки
    """
    print('OnTrade')
    print(data['data'])  # Печатаем полученные данные


def on_futures_client_holding(data):
    """Обработчик события изменения позиции по срочному рынку"""
    print('OnFuturesClientHolding')
    print(data['data'])  # Печатаем полученные данные


def on_depo_limit(data):
    """Обработчик события изменения позиции по инструментам"""
    print('OnDepoLimit')
    print(data['data'])  # Печатаем полученные данные


def on_depo_limit_delete(data):
    """Обработчик события удаления позиции по инструментам"""
    print('OnDepoLimitDelete')
    print(data['data'])  # Печатаем полученные данные
    

def buy():
    transaction = {
        'ACTION': 'NEW_ORDER',
        'CLASSCODE': class_code,
        'SECCODE': sec_code,
        'OPERATION': 'B',
        'PRICE': str(0),  # рыночная заявка
        'QUANTITY': str(quantity),
        'TYPE': 'M'}
    qp_provider.SendTransaction(transaction)

def sell():
    transaction = {
        'ACTION': 'NEW_ORDER',
        'CLASSCODE': class_code,
        'SECCODE': sec_code,
        'OPERATION': 'S',
        'PRICE': str(0),  # рыночная заявка
        'QUANTITY': str(quantity),
        'TYPE': 'M'}
    qp_provider.SendTransaction(transaction)
    
    
while gridprofit < grid_take and grid_stop < gridprofit:
    
    qp_provider = QuikPy()  # Подключение к локальному запущенному терминалу QUIK
    qp_provider.OnTransReply = on_trans_reply  # Ответ на транзакцию пользователя. Если транзакция выполняется из QUIK, то не вызывается
    qp_provider.OnOrder = on_order  # Получение новой / изменение существующей заявки
    qp_provider.OnTrade = on_trade  # Получение новой / изменение существующей сделки
    qp_provider.OnFuturesClientHolding = on_futures_client_holding  # Изменение позиции по срочному рынку
    qp_provider.OnDepoLimit = on_depo_limit  # Изменение позиции по инструментам
    qp_provider.OnDepoLimitDelete = on_depo_limit_delete  # Удаление позиции по инструментам
    
    
    price = round(float(qp_provider.GetParamEx(class_code, sec_code, 'LAST')['data']['param_value']), 1)
    quantity = 3  # Кол-во в лотах
    

    lastdealprice =  round(float(qp_provider.GetParamEx(class_code, sec_code, 'LAST')['data']['param_value']), 1)

    print(price)
    a = []
    for x in range(grid//-2, grid//2 + 1):
        a.append (round(lastdealprice + diff*x, 1))
    index = len(a) // 2
    
    print(a)

    print("\n Grid net prices: " + str(a) + '\nDifference between trade levels is: ' + str(diff) )
    while total_pnl < local_take and total_pnl > local_stop:    
        lastPrice = round(float(qp_provider.GetParamEx(class_code, sec_code, 'LAST')['data']['param_value']), 1)
        if lastPrice in a and lastPrice > lastdealprice:
            for i in range(len(a)):
                if lastPrice % 0.1 == a[i] %0.1 and index != i:
                    index = i
                    # Продажа
                    
                    sell()
                    print(f'sell @ {lastPrice}')
                    pnl = (lastPrice - avg_price) * quantity * lot
                    realized_pnl += pnl
                    position -= quantity 
                    print(f'Реализованный PnL: {realized_pnl:.2f}')
                    if position != 0:
                        avg_price = (avg_price * position + lastPrice * quantity) / (position)
                    else:
                        avg_price = 0
                    lastdealprice = lastPrice
                    time.sleep(5)

        if lastPrice in a and lastPrice < lastdealprice:
            for i in range(len(a)):
                if lastPrice % 0.1 == a[i] %0.1 and index != i:
                    index = i
                    # Покупка
                    buy()
                    print(f'buy @ {lastPrice}')
                    position += quantity
                    if position != 0:
                        avg_price = (avg_price * position + lastPrice * quantity) / (position)
                    else:
                        avg_price = 0
                    print(f'Средняя цена: {avg_price:.2f}')
                    lastdealprice = lastPrice
                    time.sleep(5)

        # Подсчет нереализованного PnL
        unrealized_pnl = (lastPrice - avg_price) * position if position != 0 else 0.0
        total_pnl = realized_pnl + unrealized_pnl

        print(f'Позиция: {position}, Реализ. PnL: {realized_pnl:.2f}, Нереализ. PnL: {unrealized_pnl:.2f}, Всего: {total_pnl:.2f}')

        time.sleep(1)  # Чтобы не перегружать QUIK запросами

if position > 0 and (total_pnl <= local_stop or total_pnl >= local_take):
    for i in range(position):
        sell()
elif position < 0 and (total_pnl <= local_stop or total_pnl >= local_stop):
    for i in range(position):
        buy()
print('result' + str(total_pnl))


gridprofit += total_pnl