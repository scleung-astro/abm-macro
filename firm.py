from mycalendar import Calendar
from param import INGREDIENTS, INIT_EMPLOYEES, INIT_FIRM_CASH, INIT_SALARY, N_CITIES, N_GOODS, PRODUCTIVITIES
from random import randint, uniform, random

class Firm():

    def __init__(self, city_id, firm_id, product):

        self.city_id = city_id
        self.firm_id = firm_id
        self.product = product

        self.risk_beta = uniform(0,2)

        self.cash = [0 for i in range(N_CITIES)]    

        self.salary_budget = [0 for i in range(N_CITIES)]
        self.purchase_budget = [0 for i in range(N_CITIES)]
        self.employ_budget = [0 for i in range(N_CITIES)]
        self.invest_budget = [0 for i in range(N_CITIES)]
        self.debt = [0 for i in range(N_CITIES)]

        # initial cash
        self.salary_budget[city_id] = INIT_FIRM_CASH


        self.employees = INIT_EMPLOYEES
        self.salary = INIT_SALARY

        self.productivity = PRODUCTIVITIES[self.product]

        self.ask_orders = {}
        self.bid_orders = {}

        self.ingredients = []
        for i in range(N_GOODS):
            if INGREDIENTS[self.product][i] > 0:
                self.ingredients.append((i, INGREDIENTS[self.product][i]))
                self.ask_orders[i] = {}
        
        self.bid_orders[self.product] = {}

        self.inventory = [0 for i in range(N_GOODS)]
        for ingredient in self.ingredients:
            self.inventory[ingredient[0]] = self.employees * self.productivity * ingredient[1]

        
        self.change_prod = False
        self.only_domestic_sales = True

        self.calendar = Calendar()



        self.employ_date = randint(1,20)

    def allocate_budget(self, prices, trends):

        x = max(self.employees * self.salary - self.salary_budget[self.city_id], 0)
        #x = round(x, 2)

        self.cash[self.city_id] -= x
        self.salary_budget[self.city_id] += x

        x = 0
        for ingredient in self.ingredients:
            x = self.employees * self.productivity * prices[self.city_id][ingredient[0]]
        #x = round(x, 2)

        self.cash[self.city_id] -= x
        self.purchase_budget[self.city_id] += x

        if self.cash[self.city_id] < 0 or (self.cash[self.city_id] >= 0 and trends[self.city_id][self.product] > 0):
            x = self.cash[self.city_id]
            self.cash[self.city_id] -= x
            self.employ_budget[self.city_id] += x
        else:
            x = self.cash[self.city_id]
            self.cash[self.city_id] -= x
            self.invest_budget[self.city_id] += x

        #print("City{}-Firm{} allocate_budget: cash:{} salary:{} purchase:{} employ:{} invest:{}".format(
        #    self.city_id, self.firm_id, self.cash[self.city_id], self.salary_budget[self.city_id],
        #    self.purchase_budget[self.city_id], self.employ_budget[self.city_id], self.invest_budget[self.city_id]
        #))

    def decide_prod_ask_order(self):

        for ingredient in self.ingredients:
            self.ask_orders[ingredient[0]]["city"] = self.city_id
            self.ask_orders[ingredient[0]]["amount"] = ingredient[1] * self.employees * self.productivity

        #print("City{}-Firm{} ask_order: {}".format(
        #    self.city_id, self.firm_id, self.ask_orders
        #))

        return self.ask_orders

    def decide_prod_bid_order(self, prices, rates):

        # decide which city to sell the product
        if self.only_domestic_sales:
            city_id = self.city_id

        self.bid_orders[self.product]["city"] = city_id
        self.bid_orders[self.product]["amount"] = self.inventory[self.product]

        #print("City{}-Firm{} bid_order: {}".format(
        #    self.city_id, self.firm_id, self.bid_orders
        #))

        return self.bid_orders

    def process_transactions(self, ask_ratios, bid_ratios, prices):
        
        for k, v in self.ask_orders.items():

            amt = v["amount"] * ask_ratios[v["city"]][k] * prices[v["city"]][k]
            #amt = round(amt, 2)

            self.inventory[k] += ask_ratios[v["city"]][k] * v["amount"]
            self.purchase_budget[v["city"]] -= amt

        for k, v in self.bid_orders.items():

            amt = v["amount"] * bid_ratios[v["city"]][k] * prices[v["city"]][k]
            #amt = round(amt, 2)

            self.inventory[k] -= ask_ratios[v["city"]][k] * v["amount"]
            self.cash[v["city"]] += amt

        #print("City{}-Firm{} cash:{} inventory:{} Ask:{} Bid:{}".format(
        #    self.city_id, self.firm_id, self.cash[self.city_id], self.inventory, self.ask_orders, self.bid_orders
        #))


    def make_product(self):


        x = self.employees * self.productivity
        for ingredient in self.ingredients:
            x = min(x, self.inventory[ingredient[0]] / ingredient[1])

        for ingredient in self.ingredients:
            self.inventory[ingredient[0]] -= ingredient[1] * x
        self.inventory[self.product] += x

        salary = self.employees * self.salary
        #salary = round(salary, 2)

        self.salary_budget[self.city_id] -= salary
        return (self.city_id, salary)


    def decide_employ(self):

        employment = None

        x = self.employees * self.salary * 21
        y = x / (1 + self.risk_beta)

        if self.employ_budget[self.city_id] > y:
            debt = y * self.risk_beta

            self.debt[self.city_id] += debt
            self.employ_budget[self.city_id] -= y

            self.employees += 1

            employment = (self.city_id, self.firm_id, self.city_id, x, debt, 1)

        elif self.employees > 1 and self.employ_budget[self.city_id] < -(self.employees-1) * y:

            unemployed = 1
            payable = (self.employees-1) * x

            for i in range(self.employees-1,1,-1):
                if payable > -self.employ_budget[self.city_id]:
                    break

                unemployed += 1
                payable += (i-1)*x

            self.employees -= unemployed

            debt_reduction = payable * self.risk_beta / (1 + self.risk_beta)
            self.debt[self.city_id] -= debt_reduction
            self.employ_budget[self.city_id] += payable / (1 + self.risk_beta)

            employment = (self.city_id, self.firm_id, self.city_id, -payable, -debt_reduction, -unemployed)

        #if employment:
        #    print("City{}-Firm{} employ:{} employment:{}".format(
        #        self.city_id, self.firm_id, self.employ_budget[self.city_id], employment
        #    ))
    
        return employment

    def change_production(self, rank_goods):

        if self.change_prod and self.employees == 1:

            cum_prod = 0.5
            switched_job = False

            for i in range(N_GOODS):
                x = random()
                if x < 0.5:

                    job = i
                    self.product = rank_goods[self.city_id][job]
                    switched_job = True
                    break

            if switched_job:

                self.ask_orders.clear()
                self.bid_orders.clear()

                for i in range(self.ingredients):
                    self.ingredients.pop()

                for i in range(N_GOODS):
                    if INGREDIENTS[self.product] > 0:
                        self.ingredients.append((i, INGREDIENTS[self.product]))
                        self.ask_orders[i] = {}

                self.bid_orders[job] = {}

    def advance_day(self):

        

        self.calendar.advance_day()