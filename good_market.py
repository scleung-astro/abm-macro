"""
The Market class. It collects all the ask-bid orders 
from workers and firms, update the price and allocate the 
distrbution of products. 

Also see readme.md on Github for its logical design
Written by Shing Chi Leung in Dec 2021

"""

from mycalendar import Calendar
from param import INGREDIENTS, INIT_PRICES, INIT_SALARY, N_CITIES, N_GOODS, PRODUCTIVITIES

import numpy as np
from math import exp
from random import SystemRandom

class GoodMarket():


    def __init__(self):

        self.prices = [[INIT_PRICES[i] for i in range(N_GOODS)] for j in range(N_CITIES)]
        self.prices_ema9 = [[INIT_PRICES[i] for i in range(N_GOODS)] for j in range(N_CITIES)]
        self.prices_ema21 = [[INIT_PRICES[i] for i in range(N_GOODS)] for j in range(N_CITIES)]

        self.ask = [[0 for i in range(N_GOODS)] for j in range(N_CITIES)]
        self.bid = [[0 for i in range(N_GOODS)] for j in range(N_CITIES)]

        self.trends = [[0 for i in range(N_GOODS)] for j in range(N_CITIES)]

        # compute how much fraction can be bought, sold
        self.ask_ratios = [[0 for i in range(N_GOODS)] for j in range(N_CITIES)]
        self.bid_ratios = [[0 for i in range(N_GOODS)] for j in range(N_CITIES)]

        self.ref_salary = [INIT_SALARY for i in range(N_CITIES)]
        self.ref_productivity = [PRODUCTIVITIES[i] for i in range(N_GOODS)]

        # ranking of products
        self.ranks = [[0 for i in range(N_GOODS)] for j in range(N_CITIES)]

        # internal calendar
        self.calendar = Calendar()

    def update_ask_transactions(self, transactions):

        '''
        collect and record all ask orders

        transaction : list => a tuple contains
            1. city_id of the firm
            2. firm_id of the firm
            3. city_id where the product is sold
            4. the product (id) to be sold
            5. amount

        return None
        '''

        # transaction contain 
        # [0-2] self.city_id, self.firm_id, self.city_id
        # [3-4] good_index, amount

        for i in range(N_CITIES):
            for j in range(N_GOODS):
                self.ask[i][j] = transactions[i][j]

    def update_bid_transactions(self, transactions):

        '''
        collect and record all bid orders

        transaction : list => a tuple contains
            1. city_id of the firm
            2. firm_id of the firm
            3. city_id where the product is sold
            4. the product (id) to be sold
            5. amount

        return None
        '''

        # transaction contain 
        # [0-2] self.city_id, self.firm_id, self.city_id
        # [3-4] good_index, amount

        for i in range(N_CITIES):
            for j in range(N_GOODS):
                self.bid[i][j] = transactions[i][j]


    def update_price(self):

        '''
        update the product prices based on non-equilibrium pricing
        based on the demand and supply of that round    

        return 
            self.ask_ratios: list => the fraction to be bought 
            self.bid_ratios: list => the fraction to be sold
        '''

        for i in range(N_CITIES):
            for j in range(N_GOODS):

                self.prices[i][j] *= exp(0.05 * (self.ask[i][j] - self.bid[i][j]) / (self.ask[i][j] + self.bid[i][j] + 1))
                #self.prices[i][j] = round(self.prices[i][j], 2)

                if self.ask[i][j] > self.bid[i][j]:
                    self.ask_ratios[i][j] = self.bid[i][j] / self.ask[i][j]
                    self.bid_ratios[i][j] = 1
                elif self.ask[i][j] < self.bid[i][j]:
                    self.ask_ratios[i][j] = 1
                    self.bid_ratios[i][j] = self.ask[i][j] / self.bid[i][j]
                else:
                    self.ask_ratios[i][j] = 1
                    self.bid_ratios[i][j] = 1

                self.prices_ema9[i][j] = 0.2 * self.prices[i][j] + 0.8 * self.prices_ema9[i][j]
                self.prices_ema21[i][j] = 0.099 * self.prices[i][j] + 0.901 * self.prices_ema21[i][j]

                if self.prices_ema9[i][j] > self.prices_ema21[i][j]:
                    self.trends[i][j] = 1
                elif self.prices_ema9[i][j] > self.prices_ema21[i][j]:
                    self.trends[i][j] = -1

        print("Updated price:{} ask:{} bid{}".format(self.prices, self.ask, self.bid))

        return self.ask_ratios, self.bid_ratios

    def rank_goods(self):

        '''
        order the product according to their profitability
        i.e. how much profit for selling one item

        return None
        '''

        # compute the market mark up
        costs = [[self.ref_salary[j] / self.ref_productivity[i] for i in range(N_GOODS)] for j in range(N_CITIES)]

        for i in range(N_CITIES):
            for j1 in range(N_GOODS):
                for j2 in range(N_GOODS):
                    costs[i][j1] += costs[i][j2] * INGREDIENTS[j1][j2]

        markup = [[self.price[i][j] / costs[i][j] for j in range(N_GOODS)] for i in range(N_CITIES)]
        
        for i in range(N_CITIES):
            ranks = np.argsort(np.array(self.costs[i]))[::-1]
            for j in range(N_GOODS):
                self.rank_goods[i][j] = ranks[j]

    def advance_day(self):

        '''
        advance to the next day
        
        return None
        '''

        self.calendar.advance_day()