import backtrader as bt
from backtrader import Order
from ccxtbt import CCXTStore
import datetime
from collections import defaultdict

apikey = 'oCBlz-7K5Lfq54qH7tQP5DR5watyr3KxFzjfgKr2'
secret = 'D2LRSGLAj45b-YEJI_IPXgLJ_ddJQdzpJXur6Dzd'

# apikey = '1ZkwpIpPpKd7ydZGNW_t8MVkkvaIGBUZ0Q9h4GTP'
# secret = 'lAwxrvkmOolTbImV0Wv9WfmcoQVTs6rB7Phero1p'

# broker_mapping = {
#     'order_types': {
#         bt.Order.Market: 'market',
#         bt.Order.Limit: 'limit',
#         bt.Order.Stop: 'stop_loss', #stop-loss for kraken, stop for bitmex
#         bt.Order.StopLimit: 'STOP_LOSS_LIMIT'
#     },
#     'mappings':{
#         'closed_order':{
#             'key': 'status',
#             'value':'closed'
#         },
#         'canceled_order':{
#             'key': 'result',
#             'value':1}
#     }
# }

# config = {'apiKey': apikey,
#           'secret': secret,
#           'enableRateLimit': True,
#           'rateLimit': 3000
#         }

# cerebro = bt.Cerebro(quicknotify=True)
# # cerebro.addstrategy(TestStrategy)
# store = CCXTStore(exchange='ftx', currency=f'USDT', retries=5, debug=False,
#                         config=config)
# positions = store.getposition()
# print(positions)                       
# broker = store.getbroker(broker_mapping=config)
# cerebro.setbroker(broker)

import ccxt
exchange = ccxt.ftx({
    'apiKey': apikey,
    'secret': secret,
})

poss = exchange.fetch_positions()
# print(poss)
balance = exchange.fetch_balance()
print(f"balance : {balance}")

for pos in poss :
    print(pos['info']['future'])
    print(float(*pos['info']['size']))