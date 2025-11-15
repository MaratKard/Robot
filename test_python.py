from QuikPy import QuikPy
import pandas as pd

class_code_our = "TQOB"
sec_code_our = "SU26238RMFS4"

qp_provider = QuikPy()
money = qp_provider.get_money(client_code="S04X06L", firm_id="MC0002500000", tag="EQTV", curr_code="SUR")["data"]["money_limit_available    "]
print(money)
qp_provider.close_connection_and_thread()