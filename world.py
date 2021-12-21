"""
The World class. It contains all the essential classes
in the same platform including City, Firms and Market

Also see readme.md on Github for its logical design
Written by Shing Chi Leung in Dec 2021

"""

from mycalendar import Calendar
from param import BREAD, N_CITIES, N_GOODS, WATER, WHEAT
from city import City
from good_market import GoodMarket
from forex_market import ForexMarket

class World():

    def __init__(self):

        self.cities = [City(i) for i in range(N_CITIES)]

        self.goodMarket = GoodMarket()
        self.forexMarket = ForexMarket()

        self.calendar = Calendar()

    def evolve(self):

        '''
        evolve one day in the world, which includes all the activities
        of all agents in a cycle

        return None
        '''

        global_ask_order = [[0 for i in range(N_GOODS)] for j in range(N_CITIES)]
        global_bid_order = [[0 for i in range(N_GOODS)] for j in range(N_CITIES)]

        for city in self.cities:
            city.firms_decide_budget(self.goodMarket.prices, self.goodMarket.trends)

        for city in self.cities:
            city.firms_make_products()

        for city in self.cities:
            ask_order = city.firms_get_ask_orders()

            for i in range(N_CITIES):
                for j in range(N_GOODS):
                    global_ask_order[i][j] += ask_order[i][j]

        for city in self.cities:
            bid_order = city.firms_get_bid_orders(self.goodMarket.prices, self.forexMarket.prices)

            for i in range(N_CITIES):
                for j in range(N_GOODS):
                    global_bid_order[i][j] += bid_order[i][j]

        for city in self.cities:
            order = city.decide_purchase(self.goodMarket.prices)

            for k, v in order.items():
                global_ask_order[v["city"]][k] += v["amount"]

        self.goodMarket.update_ask_transactions(global_ask_order)
        self.goodMarket.update_bid_transactions(global_bid_order)
        ask_ratios, bid_ratios = self.goodMarket.update_price()

        for city in self.cities:
            city.process_transactions(ask_ratios, bid_ratios, self.goodMarket.prices)

        # decide forex transactions

        # decide investment

        # decide employment 
        for city in self.cities:
            city.firms_decide_employ()

        # city logistics

        # miscellaneous
        for city in self.cities:
            city.advance_day()

        self.goodMarket.advance_day()
        self.forexMarket.advance_day()
        self.calendar.advance_day()

    def output_price(self, f_price_hist):
        f_price_hist.write("{},{},{},{},{},{}\n".format(
            self.calendar.year, self.calendar.month, self.calendar.day,
            self.goodMarket.prices[0][WATER],self.goodMarket.prices[0][WHEAT],self.goodMarket.prices[0][BREAD]
        ))


def main():

    f_price_hist = open("price_hist.csv", "w")
    f_price_hist.write("Y,M,D,WATER,WHEAT,BREAD\n")

    world = World()
    for i in range(100):
        world.evolve()

        world.output_price(f_price_hist)

    for firm in world.cities[0].firms:
        print("Firm {} Employees:{} cash:{} salary:{} purchase:{} employ:{} budget:{}".format(
            firm.firm_id, firm.employees, firm.cash[0], firm.salary_budget[0], 
            firm.purchase_budget[0], firm.employ_budget[0], firm.invest_budget[0]
        ))

    f_price_hist.close()

if __name__=="__main__":
    main()
