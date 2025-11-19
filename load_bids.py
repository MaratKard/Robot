from QuikPy import QuikPy
import pandas as pd

qp = QuikPy()
bids = qp.get_all_orders()
print(bids)
qp.close_connection_and_thread()