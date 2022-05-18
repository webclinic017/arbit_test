import backtrader as bt
from backtrader import Order
from ccxtbt import CCXTStore
import datetime
from collections import defaultdict

class TestStrategy(bt.Strategy):

    params = dict(
        threshold = 0.5,
        result = defaultdict(lambda : []),
    )

    def next(self):

        today_date = self.datetime.date()
        gap = datetime.datetime.strptime("2022-09-25", "%Y-%m-%d").date() - today_date

        if self.live_data:

            cash, value = self.broker.get_balance()

            rank_list = []
            premiums= dict()
            poss = dict()

            for i, d in enumerate(self.datas):
                poss[d._name] = 0

                if i % 2 != 0 : 
                    dt, dn = self.datetime.date(), d._name
                    premium = (self.datas[i].close[0] / self.datas[i-1].close[0] - 1) * (365/ gap.days)
                    rank_list.append([premium,i])
                    premiums[d._name] = premium 

                    print('DATE   : {}'.format(dt))
                    print('ASSET  : {}'.format(dn))
                    print('PREMIUM  : {}'.format(premium))

            rank_list.sort()

            spot_to_trade = self.p.threshold * cash / self.datas[rank_list[-1][-1]-1].close[0]
            future_to_trade = self.p.threshold * cash / self.datas[rank_list[-1][-1]].close[0]

            positions = self.broker.getposition()

            for pos in positions :
                poss[pos['info']['future']] = pos['info']['size']

            cash, value = self.broker.get_wallet_balance('BTC')
            poss[self.datas[rank_list[-1][-1]-1]._name] = cash

            print(poss[self.datas[rank_list[-1][-1]-1]._name])
            if poss[self.datas[rank_list[-1][-1]-1]._name] == 0 :
                self.order = self.buy(data = self.datas[rank_list[-1][-1]-1], size = spot_to_trade,exectype=Order.Market)
                self.order = self.sell(data = self.datas[rank_list[-1][-1]], size = future_to_trade,exectype=Order.Market)

            for pos in positions :
                if (poss[pos['info']['future']] != 0) & (premiums[pos['info']['future']] <= 0) :
                    try :
                        self.order = self.sell(data = self.datas[rank_list[-1][-1]-1],exectype=Order.Market)
                        self.order = self.create_order(self.datas[rank_list[-1][-1]], type='Market', side='sell',amount=pos['info']['size'] ,params={'reduce_only': true})
                    except :
                        pass

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.datetime.now()
        msg= 'Data Status: {}, Order Status: {}'.format(data._getstatusname(status), status)
        print(dt,dn,msg)
        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
        else:
            self.live_data = False

def get_ftx():
    apikey = 'oCBlz-7K5Lfq54qH7tQP5DR5watyr3KxFzjfgKr2'
    secret = 'D2LRSGLAj45b-YEJI_IPXgLJ_ddJQdzpJXur6Dzd'

    broker_mapping = {
        'order_types': {
            bt.Order.Market: 'market',
            bt.Order.Limit: 'limit',
            bt.Order.Stop: 'stop_loss', #stop-loss for kraken, stop for bitmex
            bt.Order.StopLimit: 'STOP_LOSS_LIMIT'
        },
        'mappings':{
            'closed_order':{
                'key': 'status',
                'value':'closed'
            },
            'canceled_order':{
                'key': 'result',
                'value':1}
        }
    }

    config = {'apiKey': apikey,
            'secret': secret,
            'enableRateLimit': True,
            'rateLimit': 3000
            }

    future_list = ['BTC',
    # 'ETH','BNB','SOL','LTC','DOT','XRP','LINK','AVAX','DOGE','SUSHI','BAL','BCH','TRX','CHZ','AAVE','UNI','SXP','COMP','XAUT'
    ]
    return future_list,config

def main() :

    future_list,config = get_ftx()

    cerebro = bt.Cerebro(quicknotify=True)
    cerebro.addstrategy(TestStrategy)
    store = CCXTStore(exchange='ftx', currency=f'USDT', retries=5, debug=False,
                            config=config)
    broker = store.getbroker(broker_mapping=config)
    cerebro.setbroker(broker)

    for i in future_list :

        spot   = store.getdata(
                                dataname=f'{i}/USDT', name=f'{i}/USDT', timeframe=bt.TimeFrame.Minutes,
                                # fromdate=datetime.datetime.utcnow()-datetime.timedelta(hours=600),
                                 fromdate=datetime.datetime.utcnow()-datetime.timedelta(hours=24),
                                compression=5, ohlcv_limit=1505, drop_newest=True)
        cerebro.adddata(spot)
        
        future = store.getdata(
                                dataname=f'{i}-0930', name=f'{i}-0930', timeframe=bt.TimeFrame.Minutes,
                                fromdate=datetime.datetime.utcnow()-datetime.timedelta(hours=24),
                                # fromdate=datetime.datetime.utcnow()-datetime.timedelta(hours=1505),
                                compression=5, ohlcv_limit=1505, drop_newest=True,params={'type': 'future'})

        cerebro.adddata(future)

    initial_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % initial_value)
    result = cerebro.run()

    final_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % final_value)

if __name__ == "__main__":
    main()