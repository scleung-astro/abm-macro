from mycalendar import Calendar
from firm import Firm
from param import BASE_MARKUP, BUDGET_RATIO, INIT_CITIZENS, INIT_CITY_CASH, INIT_FIRMS, INIT_SALARY, N_CITIES, N_GOODS
from random import random

class City():

    def __init__(self, city_id):

        self.city_id = city_id

        self.citizens = INIT_CITIZENS
        self.employed = INIT_CITIZENS

        # instantiate and populate the firms
        idx = 0
        self.firms = []
        for i in range(N_GOODS):
            for j in range(INIT_FIRMS[i]):
                self.firms.append(Firm(self.city_id, idx, i))
                idx += 1

        self.cash = [0 for i in range(N_CITIES)]
        self.cash[self.city_id] = INIT_CITY_CASH

        self.liability = [0 for i in range(N_CITIES)]

        self.markup = BASE_MARKUP
        self.ref_salary = INIT_SALARY

        self.budget = 0

        self.budget_ratio = [BUDGET_RATIO[i] for i in range(N_GOODS)]

        self.reserve = [0 for i in range(N_CITIES)]
        self.debt = [0 for i in range(N_CITIES)]
        
        self.ask_order = {}
        for i in range(N_GOODS):
            if BUDGET_RATIO[i] > 0:
                self.ask_order[i] = {}


        # internal calendar
        self.calendar = Calendar()


    def firms_get_ask_orders(self):

        firms_ask = [[0 for i in range(N_GOODS)] for j in range(N_CITIES)]

        for firm in self.firms:
            firm_orders = firm.decide_prod_ask_order()
            for k, v in firm_orders.items():
                firms_ask[v["city"]][k] += v["amount"]

        return firms_ask

    def firms_get_bid_orders(self, prices, rates):

        firms_bid = [[0 for i in range(N_GOODS)] for j in range(N_CITIES)]
    
        for firm in self.firms:
            firm_orders = firm.decide_prod_bid_order(prices, rates)
            for k, v in firm_orders.items():
                firms_bid[v["city"]][k] += v["amount"]

        return firms_bid

    def firms_make_products(self):

        for firm in self.firms:
            salary = firm.make_product()
            self.cash[salary[0]] += salary[1]

    def firms_decide_budget(self, prices, trends):

        for firm in self.firms:
            firm.allocate_budget(prices, trends)

    def decide_purchase(self, prices : list):

        # first print the money
        budget = self.ref_salary * self.citizens
        new_money = budget * self.markup
        #new_money = round(new_money, 2)
        
        self.liability[self.city_id] += new_money
        self.cash[self.city_id] += new_money
        budget += new_money

        if self.cash[self.city_id] > 0:
            for i in range(N_GOODS):
                if self.budget_ratio[i] > 0:
                    x = int(budget * self.budget_ratio[i] / prices[self.city_id][i])
                    self.ask_order[i]["city"] = self.city_id
                    self.ask_order[i]["amount"] = x

        print("City:{} Ask order:{} New money:{}".format(self.city_id, self.ask_order, new_money))
        return self.ask_order

    def process_transactions(self, ask_ratios, bid_ratios, prices):

        for firm in self.firms:
            firm.process_transactions(ask_ratios, bid_ratios, prices)

        for k, v in self.ask_order.items():

            amt = v["amount"] * ask_ratios[v["city"]][k] * prices[v["city"]][k]
            #amt = round(amt, 2)

            self.cash[v["city"]] -= amt

        


    def population_growth(self):

        annual_salary = 252 * self.ref_salary 
        self.citizens += self.reserve / annual_salary

    def firms_decide_employ(self):

        for firm in self.firms:

            if firm.employ_date == self.calendar.day:

                employment = firm.decide_employ()

                if employment:
                    self.reserve[self.city_id] += employment[3]
                    self.debt[self.city_id] += employment[4]
                    self.employed += employment[5]

    def grow_new_firm(self, rank_goods : list):

        n_new_firms = int(len(self.firms) * 0.01)

        for i in range(n_new_firms):
            
            found_job = False
            for j in range(N_GOODS):
                x = random()
                if x < 0.5:
                    self.product = rank_goods[self.city_id][j]
                    job = j
                    found_job = True
                    break

                if not found_job:
                    job = rank_goods[self.city_id][-1]

            self.firms.append(Firm(self.city_id, len(self.firms), job))

    def advance_day(self):

        self.calendar.advance_day()

        for firm in self.firms:
            firm.advance_day()