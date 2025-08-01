new_url = 'https://www.optionsprofitcalculator.com/ajax/getOptions?stock={}&reqId=1'



import asyncio
import aiohttp
import json
import numpy as np

def OpTable(x):
    hold = ''
    for i in x:
        hold += json.dumps(i) + "\n"
    return hold

class OptionsData:

    def __init__(self, price=501.20, ticker='SPY'):
        self.ticker = ticker
        self.stock_price = price
        self.call_strikes = []
        self.put_strikes = []
        self.call_prices = []
        self.put_prices = []

    def fetcher(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.fetch_data())

    async def fetch_data(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(new_url.format(self.ticker)) as response:
                r = await response.text()
                r = json.loads(r)
                date = list(r['options'].keys())[0]
                call = r['options'][date]['c']
                put = r['options'][date]['p']
                for K, items in call.items():
                    self.call_strikes.append(float(K))
                    self.call_prices.append(float(items['l']))
                for K, items in put.items():
                    self.put_strikes.append(float(K))
                    self.put_prices.append(float(items['l']))
                


import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Options(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.wm_title(self, 'Options Payoff Diagram')
        self.geometry('1000x750')

        self.selected_call_strike = 0
        self.selected_call_price = 0

        self.selected_put_strike = 0
        self.selected_put_price = 0

        self.OPTIONS = []
        self.STOCKPRICE = []
        self.PAYOFF = []


        ctrl_frame = tk.Frame(self)
        ctrl_frame.pack(side=tk.TOP)

        ctrl_frame2 = tk.Frame(self)
        ctrl_frame2.pack(side=tk.TOP)

        graph_frame = tk.Frame(self)
        graph_frame.pack(side=tk.TOP)
        
        
        self.controlFrame(ctrl_frame, ctrl_frame2)
        self.graphFrame(graph_frame)

    def graphFrame(self, frame):
        fig = Figure(figsize=(8, 4))
        self.plot = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP)



    def controlFrame(self, frame, frame2):
        def fetch_data():
            ticker = self.ticker.get()
            self.options_data = OptionsData(ticker=ticker)
            self.options_data.fetcher()
            self.select_call_strikes.configure(values=self.options_data.call_strikes)
            self.select_put_strikes.configure(values=self.options_data.put_strikes)
            self.displayPrice.configure(text=f'Stock Price: {self.options_data.stock_price}')
            
        def on_call_select(evt):
            strike = float(self.select_call_strikes.get())
            i = self.options_data.call_strikes.index(strike)
            self.selected_call_strike = self.options_data.call_strikes[i]
            self.selected_call_price = self.options_data.call_prices[i]

        def on_put_select(evt):
            strike = float(self.select_put_strikes.get())
            i = self.options_data.put_strikes.index(strike)
            self.selected_put_strike = self.options_data.put_strikes[i]
            self.selected_put_price = self.options_data.put_prices[i]

        def Clear():
            self.OPTIONS = []
            self.STOCKPRICE = []
            self.PAYOFF = []
            self.selected_options.configure(text='waiting...')
            self.plot.cla()
            self.canvas.draw()

        def BuyCall():
            self.OPTIONS.append({'side':'buy','price':float(self.selected_call_price),
                                 'strike':float(self.selected_call_strike),'optype':'call'})

            self.selected_options.configure(text=OpTable(self.OPTIONS))

        def SellCall():
            self.OPTIONS.append({'side':'sell','price':float(self.selected_call_price),
                                 'strike':float(self.selected_call_strike),'optype':'call'})

            self.selected_options.configure(text=OpTable(self.OPTIONS))

        def BuyPut():
            self.OPTIONS.append({'side':'buy','price':float(self.selected_put_price),
                                 'strike':float(self.selected_put_strike),'optype':'put'})
            self.selected_options.configure(text=OpTable(self.OPTIONS))

        def SellPut():
            self.OPTIONS.append({'side':'sell','price':float(self.selected_put_price),
                                 'strike':float(self.selected_put_strike),'optype':'put'})
        
            self.selected_options.configure(text=OpTable(self.OPTIONS))

        def ComputePayoffs():
            stockPrice = self.options_data.stock_price
            dS = int(stockPrice*0.5)
            lower = np.max([stockPrice - dS, 0])
            upper = stockPrice + dS
            A = np.arange(lower, upper+1, 1).tolist()
            TABLE = []
            for option in self.OPTIONS:
                if option['side'] == 'buy':
                    if option['optype'] == 'call':
                        TABLE.append([np.max([price - option['strike'], 0]) for price in A])
                        TABLE.append([-option['price'] for price in A])
                    if option['optype'] == 'put':
                        TABLE.append([np.max([option['strike'] - price, 0]) for price in A])
                        TABLE.append([-option['price'] for price in A])
                if option['side'] == 'sell':
                    if option['optype'] == 'call':
                        TABLE.append([-np.max([price - option['strike'], 0]) for price in A])
                        TABLE.append([option['price'] for price in A])
                    if option['optype'] == 'put':
                        TABLE.append([-np.max([option['strike'] - price, 0]) for price in A])
                        TABLE.append([option['price'] for price in A])
            
            TABLE = np.array(TABLE).T.tolist()
            self.PAYOFF = [np.sum([float(j) for j in i]) for i in TABLE]

            self.plot.cla()
            Z = np.zeros(len(A))
            self.plot.plot(A, Z, color='limegreen')
            self.plot.plot(A, self.PAYOFF, color='red')
            self.canvas.draw()

            
        tk.Label(frame, text='\t').grid(row=1, column=1)
        self.displayPrice = tk.Label(frame, text='')
        self.displayPrice.grid(row=1, column=2)
        tk.Label(frame, text='Ticker').grid(row=2, column=1)
        tk.Label(frame, text='Call Strike').grid(row=2, column=2)
        tk.Label(frame, text='Put Strike').grid(row=2, column=3)
        self.ticker = ttk.Entry(frame, justify='center', width=10)
        self.ticker.grid(row=3, column=1)
        tk.Button(frame, text='Fetch', command=lambda: fetch_data()).grid(row=3, column=4)

        callstrike = tk.StringVar()
        self.select_call_strikes = ttk.Combobox(frame, width=10, values=[], textvariable=callstrike)
        self.select_call_strikes.grid(row=3, column=2)

        putstrike = tk.StringVar()
        self.select_put_strikes = ttk.Combobox(frame, width=10, values=[], textvariable=putstrike)
        self.select_put_strikes.grid(row=3, column=3)

        tk.Label(frame,text='\t').grid(row=4, column=1)
        tk.Button(frame, text='BuyCall', command=lambda: BuyCall()).grid(row=5, column=1)
        tk.Button(frame, text='SellCall', command=lambda: SellCall()).grid(row=6, column=1)
        tk.Button(frame, text='BuyPut', command=lambda: BuyPut()).grid(row=5, column=2)
        tk.Button(frame, text='SellPut', command=lambda: SellPut()).grid(row=6, column=2)
        tk.Button(frame, text='Clear', command=lambda: Clear()).grid(row=5, column=3)
        tk.Button(frame, text='Compute',command=lambda: ComputePayoffs()).grid(row=6, column=3)

        self.selected_options = tk.Label(frame2, text='waiting...')
        self.selected_options.grid(row=7, column=1)

        self.select_call_strikes.bind("<<ComboboxSelected>>", on_call_select)
        self.select_put_strikes.bind("<<ComboboxSelected>>", on_put_select)
        


Options().mainloop()