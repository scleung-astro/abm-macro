"""
This file store the Shop class which represent an automaton agent which consumes
raw material, produces products and sells products. It interacts with the system
through the market and forex market. It also consumes research for its development
and can expand/diminish its size depending on its annual income. 

Written by Shing Chi Leung for the investigation of macroeconomics. 
"""

from param import *
from random import randint, choice, random, uniform

class Shop():

    '''
    set up a shop

    input:
    city_sid (the global city id where the firm locates)
    sid (the shop id to access the firm from the city)

    return:
    none
    '''
    def __init__(self,city_sid,sid):

        # the city where the firm locates
        self.city_sid = city_sid

        # its local ID for rapid access
        self.sid = sid

        # its role in the production chain
        self.shop = InitialOccupation[sid % InitialOccupationLen] # randint(0,NumType-1)

        # wage of each emplouee in the firm
        self.salary = InitialSalary

        # for testing how the distribution of different suppliers and availability of 
        # international supplier to the local product chain
        self.switchJob = choice([True, False])
        self.localSales = choice([True, False])

        # initial usable cash 
        self.cash = [0 for i in range(NumCity)]
        self.cash[self.city_sid] = int(ReserveBudget[self.shop]/2)

        # inventory for all production
        self.warehouse = [0 for i in range(NumType)]
        
        # period for one operation decision 
        self.interval = choice([3,5,7,11,13,17])
        self.interval_day = randint(0, self.interval-1)

        # shop employees
        self.staff = 1

        # production rate per employee
        self.production_rate = Productivity[self.shop] #randint(5,10)

        # total production (production rate * employee * factor)
        self.production = 0
        
        # accounting purpose
        # average cost, minimum profit of the product
        self.avg_cost = [1 for i in range(NumType)]
        self.profit_margin = uniform(0.02,0.05)

        # minimum cash per employee before investment 
        self.reserveBudget = ReserveBudget[self.shop]

        # bankrupt flag to signal the firm making loss
        self.bankrupt = False
        self.bankruptCount = 0

        # account purpose, number of good on market
        self.goodsOnSale = 0

        # investment extension       
        # extra cash are 
        self.investmentCash = [0 for i in range(NumCity)] 
        self.researchCash = [0 for i in range(NumCity)]
        self.expandCash = [0 for i in range(NumCity)]

        # for extension with financial investment 
        self.investor = 0

        # research extension
        # bonus due to consumption of research 
        self.production_boost = 1
        self.researchType = ResearchType[self.shop]

        # give the shop-specific production ingredient
        self.ingredients = []
        for i in range(NumType):
            if Ingredients[self.shop][i] != 0:
                self.ingredients.append([i,Ingredients[self.shop][i]])
                self.warehouse[i] = randint(20,30) * self.production_rate

        # also fill the initial warehouse with some ingredient to start
        self.warehouse[self.shop] = randint(20,30) * self.production_rate

    '''
    shop check its available budget and decides whether or not to employ a new staff

    input: 
    none

    returns:
    newMember (number of new staff)   
    payment (cost to pay to the city for employing the staff)
    '''
    def DecideExpansion(self):

        payment = 0
        newMember = 0

        if self.expandCash[self.city_sid] > self.staff * UpgradeCost:

            newMember = 1
            payment = UpgradeCost * self.staff

            self.staff += newMember
            self.production_rate += newMember * Productivity[self.shop]
            self.expandCash[self.city_sid] -= payment
        
        return newMember, payment


    '''
    shop checks its investment account and decides if hire a new investor

    input:
    none

    return:
    newMember (number of new investor to be hired/fired)
    '''
    def DecideHireInvestor(self):

        newMember = 0

        if self.investmentCash[self.city_sid] > 2500000 * (self.investor + 1) :
            newMember = 1
            self.investor += newMember

        elif self.investmentCash[self.city_sid] < 2500000 * self.investor and self.investor >= 1:
            newMember = -1
            self.investor += newMember
            
        return newMember
        
    '''
    shop checks if its cash is negative and decides whether to downgrade

    input: 
    none

    returns:
    newMember (number of staffs removed)
    payment (subsidy receive from city)
    '''
    def DecideDowngrade(self):

        payment = 0
        newMember = 0

        if self.cash[self.city_sid] < 0:
            
            if self.staff > 1:
                newMember = -1
                payment = -UpgradeCost

                self.staff += newMember
                self.production_rate += newMember * Productivity[self.shop]
                self.cash[self.city_sid] -= payment
            else:
                self.bankrupt = True

        else:
            self.bankrupt = False
            self.bankruptCount = 0
        
        return newMember, payment

    '''
    shop decides how much to produce depends on its staff, number of day before the next decision
    and its research bonus

    returns:
    none
    '''
    def DecideProduction(self):
        if self.cash[self.city_sid] > 0:
            self.production = int(self.production_rate * self.interval * self.production_boost)
            for ingredient in self.ingredients:
                self.production = int(min(self.warehouse[ingredient[0]] / ingredient[1], self.production))
        else:
            self.production = 0

    ''' 
    shop decides to purchase raw material for its production depending on its recipe for production
    from the market

    input:
    priceSnap: (a matrix storing all product price in each market and its volume)

    returns:
    ask_order: (a tuple of <city_sid, shop_sid, ingreident_id, price, amount>)
    '''
    def DecidePurchase(self, priceSnap):

        # this phase only local purchase available
        ask_order = []
        if self.ingredients != [] and self.cash[self.city_sid] > 0:
            for ingredient in self.ingredients:
                ask_order.append((self.city_sid, self.sid, self.city_sid, ingredient[0], None, 
                    int(ingredient[1] * self.production_rate * self.interval * self.production_boost)))


        # experimental treatment for setting gold as a storage asset    
        '''
        if self.shop != GOLD:
            useableCash = max(self.cash[self.city_sid] - 150000 * self.production_rate, 0) / 5
            if useableCash > 0:
                buyGoldAmt = int(useableCash / priceSnap[self.city_sid][GOLD][0])
                ask_order.append((self.city_sid, self.sid, self.city_sid, GOLD, None, buyGoldAmt))
        else:
            useableCash = max(self.cash[self.city_sid] - 150000 * self.production_rate, 0) / 5
            if useableCash > 0:
                buyGoldAmt = int(useableCash / priceSnap[self.city_sid][PIE][0])
                ask_order.append((self.city_sid, self.sid, self.city_sid, PIE, None, buyGoldAmt))
        '''
        

        if ask_order != []:
            return ask_order
        else:
            return None

    '''
    shop decides whether and how much research it will purchase from the market

    input: 
    priceSnap (a metrix storing all product price in each market and its volume)

    returns:
    ask_order (a tuple of <city_sid, shop_sid, ingreident_id, price, amount>)
    '''
    def DecidePurchaseResearch(self, priceSnap):
        
        # this phase only local purchase available
        ask_order = []
        if self.researchCash[self.city_sid] > 0:
            price = priceSnap[self.city_sid][self.researchType][0]
            volume = int(self.researchCash[self.city_sid] / price)
            ask_order.append((self.city_sid, self.sid, self.city_sid, self.researchType, None, volume))

        if ask_order != []:
            return ask_order
        else:
            return None

    '''
    shop allocates its budget from its usable cash
    it first keep the minimal amount of useable cash, then distribute the surplus cash to
    1. research account, 2. construction account

    input:
    none

    return:
    none
    '''
    def DecideBudget(self):

        # Research company does not buy research
        if self.researchType != None:
            researchRatio = min(self.goodsOnSale / self.production_rate / 20, 1)
        else:
            researchRatio = 0

        useableCash = int(max(self.cash[self.city_sid] - self.staff * self.reserveBudget, 0))
        self.cash[self.city_sid] -= useableCash
        self.researchCash[self.city_sid] += int(useableCash * researchRatio)
        self.expandCash[self.city_sid] += useableCash - int(useableCash * researchRatio)

    '''
    shop decides how much budget to be allocated to investment account

    input:
    none

    return:
    none
    '''
    def DecideInvestment(self):
        investmentCash = 0
        saving_threshold = self.staff * self.reserveBudget

        if self.cash[self.city_sid] > saving_threshold:
            if self.investmentCash[self.city_sid] < saving_threshold:
                investmentCash = int(max(self.cash[self.city_sid] - saving_threshold, 0) * 0.25)
        elif self.cash[self.city_sid] < 0:
            investmentCash = -max(min(self.investmentCash[self.city_sid], -self.city_sid), 0)
        
        self.cash[self.city_sid] -= investmentCash
        self.investmentCash[self.city_sid] += investmentCash
        
    '''
    shop allocates budgets for income tax payment

    input:
    none

    return:
    none
    '''
    def DecideTaxPayment(self):
        tax = int(max(self.cash[self.city_sid] - self.staff * self.reserveBudget, 0) * 0.2)
        self.cash[self.city_sid] -= tax
        return (self.city_sid, tax)

    '''
    shop allocates budgets for investment 
    the current principle is to buy low and sell high, and maintain a fixed amount of fraction
    for each of the currency

    input: 
    forexSnap (a matrix storing all currency pair rate and its volume)

    return:
    forex_order (city_id, shop_id, market_id, currency_id, price, volume)
    '''
    def DecideInvestmentTrade(self, forexSnap):
        forexOrder = []

        if self.investor > 0:

            investmentAsset = 0
            for i in range(NumCity):
                investmentAsset += self.investmentCash[i] * forexSnap[self.city_sid][i][0] / 1000

            expected_trade = [(investmentAsset / 3 * 1000 / forexSnap[self.city_sid][i][0]) - self.investmentCash[i] for i in range(NumCity)]
            for i in range(NumCity):
                if i == self.city_sid: continue

                # sell forex i and buy own currency
                if expected_trade[i] < -100:
                    price = forexSnap[self.city_sid][i][0]
                    volume = min(int(-expected_trade[i]), 10000 * self.investor)
                    if self.investmentCash[i] > volume: 
                        forexOrder.append([self.city_sid, self.sid, self.city_sid, i, price, volume])
                        self.investmentCash[i] -= volume

                # buy forex i and sell own currency
                elif expected_trade[i] > 100:
                    price = forexSnap[self.city_sid][i][0]
                    volume = min(int(expected_trade[i] * price / 1000), 10000 * self.investor)
                    if self.investmentCash[self.city_sid] > volume: 
                        forexOrder.append([self.city_sid, self.sid, i, self.city_sid, price, volume])
                        self.investmentCash[self.city_sid] -= volume
    
        if forexOrder == []:
            return None
        else:
            return forexOrder
    
    '''
    shop consumes its raw material and produces items

    input:
    none

    return:
    none
    '''
    def MakeProduct(self):
        
        # no production occurs if cash < 0
        if self.production > 0:

            # update the total cost of production
            total_cost = self.salary * self.staff * self.interval   
            for ingredient in self.ingredients:
                self.warehouse[ingredient[0]] -= ingredient[1] * self.production
                total_cost += ingredient[1] * self.production * self.avg_cost[ingredient[0]]

            # update the average cost of unsold items
            self.avg_cost[self.shop] = (self.avg_cost[self.shop] * self.warehouse[self.shop] + total_cost) / \
                (self.warehouse[self.shop] + self.production)
            self.warehouse[self.shop] += self.production

            # pay employees wage for the production
            total_salary = self.salary * self.staff * self.interval
            self.cash[self.city_sid] -=  total_salary

        else:

            total_salary = 0

        #if (self.sid==7 and self.city_sid==0): print(total_cost, self.cash, self.production)

        return (self.city_sid, total_salary)

    '''
    shop receives cash from market after selling its product to its useable cash account

    input:
    payment (a tuple of <currency, amount>)

    return: 
    none
    '''
    def ReceiveCash(self, payment):
        self.cash[payment[0]] += payment[1]

    '''
    reduce the number of product selling on market when receiving the receipt from market

    input: 
    payment (a tuple containing <product, amount>)

    return:
    none
    '''
    def RemoveGoodsOnSale(self, payment):
        self.goodsOnSale -= payment[1]
        
    '''
    shop receives investmetn payment from forex market to its investment account

    input:
    payment (a tuple of <currency, amount>)

    return: 
    none
    '''
    def ReceiveInvestmentCash(self, payment):
        self.investmentCash[payment[0]] += payment[1]

    '''
    shop pays cash for purchasing items in the market using the usable cash

    input:
    payment (a tuple of <currency, amount>)

    return: 
    none
    '''
    def PayCash(self, payment):
        self.cash[payment[0]] -= payment[1]

    '''
    shop pays cash for purchasing research from the market using the research budget

    input:
    payment (a tuple of <currency, amount>)

    return: 
    none
    '''
    def PayResearchCash(self, payment):
        self.researchCash[payment[0]] -= payment[1]
    
    '''
    shop receive cash to its research account

    input:
    payment (a tuple of <currency1, amount to be sold, currency2, amount to be bought>)

    return: 
    none
    '''
    def ReceiveResearchCash(self, payment):
        self.researchCash[payment[0]] += payment[1]

    '''
    shop receive product after its purchase

    input:
    delivery (a tuple of <product_type, amount>)
    payment (a tuple of <currency, amount>)

    return: 
    none
    '''
    def ReceiveProduct(self, delivery, payment):

        # update the average cost of the goods according to the payment
        if delivery[1] > 0:
            self.avg_cost[delivery[0]] = (self.avg_cost[delivery[0]] * self.warehouse[delivery[0]] + payment[1]) / \
                (self.warehouse[delivery[0]] + delivery[1])

        # update inventory and pays for the product
        self.warehouse[delivery[0]] += delivery[1]
        self.cash[payment[0]] -= payment[1]

    '''
    shop receive research and pays from its investment account

    input:
    delivery (a tuple of <product, amount>)
    payment (a tuple of <currency1, amount to be sold, currency2, amount to be bought>)

    return: 
    none
    '''
    def ReceiveResearch(self, delivery, payment):
        if delivery[1] > 0:
            self.avg_cost[delivery[0]] = (self.avg_cost[delivery[0]] * self.warehouse[delivery[0]] + payment[1]) / \
                (self.warehouse[delivery[0]] + delivery[1])
        self.warehouse[delivery[0]] += delivery[1]
        self.researchCash[payment[0]] -= payment[1]
        
    '''
    !!! OBSOLETE !!!
    shop switches its production type according to the current market status

    input:
    costSnap (a matrix of the basic cost of all products)
    priceSnap (a matrix containing the prices of all products in all markets)
    forexSnap (a matrix containing the exchange rates of all forex pairs)

    return: 
    none
    '''
    def DecideJob(self, costSnap, priceSnap, forexSnap):

        # this version considers only local market
        if self.switchJob == True:
            max_rate = 0
            max_job = self.shop
            for i in range(NumType):
                rate = (priceSnap[self.city_sid][i][0] - costSnap[self.city_sid][i]) / costSnap[self.city_sid][i]
                if  rate > max_rate:
                    max_job = i
                    max_rate = rate
            
            self.shop = max_job

    '''
    shop decides how many product and where it will sell the products by comparing
    the prices in different market

    input:
    priceSnap (a matrix containing prices of all products in all market)
    forexSnap (a matrix containing exchange rates of all currency pairs)

    return: 
    self.city_sid, self.sid, iCity, self.shop, salesPrice, salesVolume
    '''
    def DecideSales(self, priceSnap, forexSnap):
        
        salesPrice = 0
        salesVolume = 0

        # in this phase only local sales
        iCity = self.city_sid
        maxPrice = priceSnap[iCity][self.shop][0]
        
        if self.localSales == False:
            for i in range(NumCity):
                localPrice = priceSnap[i][self.shop][0] / forexSnap[i][self.city_sid][0] * 1000
                #print(self.city_sid, self.sid, i, localPrice, maxPrice, forexSnap[self.city_sid][i][0])
                if localPrice > maxPrice:
                    maxPrice = localPrice
                    iCity = i
            #print("Decides to sell at city: ", self.city_sid, iCity)

        # based on chosen city, decide the price
        #price = priceSnap[iCity][self.shop][0]
        #volume = priceSnap[iCity][self.shop][1]

        #if price > self.avg_cost[self.shop]:       
        #    if volume > self.production:
        #        salesPrice = price - 1
        #    else:
        #        salesPrice = price
        
        #    salesVolume = min(self.production, self.warehouse[self.shop])

        #    if salesVolume > 0:
        #        self.warehouse[self.shop] -= salesVolume
        #        salesOrder =  (self.city_sid, self.sid, iCity, self.shop, salesPrice, salesVolume)
        #        return salesOrder
        #    else:
        #        return None
        #else:
        #    return None

        salesPrice = int(self.avg_cost[self.shop] * (1 + self.profit_margin)) + 1
        salesVolume = min(self.production, self.warehouse[self.shop])

        if salesVolume > 0:
            self.warehouse[self.shop] -= salesVolume
            salesOrder =  [self.city_sid, self.sid, iCity, self.shop, salesPrice, salesVolume]
            self.goodsOnSale += salesVolume
            return salesOrder
        else:
            return None

    '''
    shop decides how much foreign currency to be sold

    input:
    forexSnap (a matric storing exchange rate of all currency pairs and its volume)

    return: 
    none
    '''
    def DecideForex(self, forexSnap):
        forexOrder = []
        for i in range(NumCity):
            if i == self.city_sid: continue
            if self.cash[i] > 1000:

                price = forexSnap[self.city_sid][i][0]
                volume = forexSnap[self.city_sid][i][1]

                #if price > self.avg_cost[self.shop]:       
                #    if volume > self.production:
                #        salesPrice = price - 1
                #else:
                #    salesPrice = price
                salesPrice = price

                salesVolume = self.cash[i]
                forexOrder.append([self.city_sid, self.sid, self.city_sid, i, salesPrice, salesVolume])

                self.cash[i] -= salesVolume
               
        if forexOrder == []:
            return None
        else:
            return forexOrder

    '''
    shop increases its number of day of bankrupt after it declares bankrupt

    input:
    none

    return: 
    none
    '''
    def UpdateBankrupCount(self):
        if self.bankrupt == True:
            self.bankruptCount += 1
        else:
            self.bankruptCount = 0
    
    '''
    shop defaults and resets its debt to zero, and reset its initial useable cash

    input:
    none

    return: 
    city_sid (city id where the default takes place)
    subsidy (amount of money taken from city for the default)
    '''
    def Reset(self):

        #print("Shop {} resets: cash {}, bankruptCnt {}".format(self.sid, self.cash[self.city_sid], self.bankruptCount))

        # reset finance
        subsidy = InitialCash - self.cash[self.city_sid]
        self.cash[self.city_sid] += subsidy

        # reset bankrupt flag
        self.bankrupt = False
        self.bankruptCount = 0

        # reset warehouse?

        return (self.city_sid, subsidy)

    '''
    shop pays forex for exchange from foreign currency to local currency from its 
    useable cash account

    input:
    payment (a tuple of <currency1, amount to be sold, currency2, amount to be bought>)

    return: 
    none
    '''
    def PayForex(self, payment):
        self.cash[payment[0]] -= payment[1]
        self.cash[payment[2]] += payment[3]

    '''
    shop pays forex for exchange from foreign currency to local currency from its 
    investment account

    input:
    payment (a tuple of <currency1, amount to be sold, currency2, amount to be bought>)

    return: 
    none
    '''
    def PayInvestmentForex(self, payment):
        self.investmentCash[payment[0]] -= payment[1]
        self.investmentCash[payment[2]] += payment[3]

    '''
    shop pays its investor wages from its investment account

    input:
    none

    return: 
    none
    '''
    def PayInvestor(self):
        payment = self.investor * self.salary
        self.investmentCash[self.city_sid] -= payment
        return (self.city_sid, payment)

    '''
    shop updates its research bonus acording to the city decision

    input:
    bonus (factor for increasing its production)

    return: 
    none
    '''
    def UpdateResearchBonus(self, bonus):
        self.warehouse[self.researchType] = 0
        self.production_boost = bonus

    '''
    display properties of the shop for debug purpose

    input:
    none

    return: 
    none
    '''
    def ShowShop(self):
        print("Shop City: {}, ID: {}, Type: {} Interval".format(self.city_sid, self.sid, self.shop, self.interval))
        print("Cash: {}, avg_cost: {}".format(self.cash, self.avg_cost))
        print("Warehouse: {} Ingredient: {} Production: {}".format(self.warehouse, self.ingredients, self.production))

def main():

    shop = Shop(0,0)
    shop.DecideProduction()
    ask_order = shop.DecidePurchase()
    print(ask_order)

    print(shop.ShowShop())

    print("Pay cash")
    shop.PayCash((1,100))
    print(shop.ShowShop())
    
    print("Receive product Type 0 amount 10, pay Cash 0 amount 2000...")
    shop.ReceiveProduct((0,10),(0,2000))
    print(shop.ShowShop())

    print("Make product...")
    shop.MakeProduct()
    shop.ShowShop()

    print("Decide sales order")
    salesOrder = shop.DecideSales([[[100,10],[90,9],[80,8],[70,7]]],[[[10,1],[11,2],[12,3],[13,4]]])
    print(salesOrder)
    shop.ShowShop()

if __name__=="__main__":
    main()
                     
