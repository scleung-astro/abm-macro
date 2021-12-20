# abm-macro
Agent based modeling of macroeconomics

This code contains the backbone for running the ABM models of a simulated 
world with market exchange. Further components available for collaborations. 
The simulation assumes three components:

1. **Firms**: They are the production power of the simulation. They can hire 
staffs, make product, buy ingredient from the market and sell their product. 
They can choose to use the profit to expand their companies or use it for 
investment. 

2. **City**: The city contains two roles. One is the role of the state, that
it controls how much "cash" is flowing in the society by deciding the amount
of purchase through its liability. It is also responsible for collecting. 
The second role is the workers. Firm employ the workers for their production. 
The workers receive the payment and spend it in daily household items, which 
are also coming from the firms. In this simulation, the workers are assumed to 
have the same salary.  

3. **Market**: The centralized place for trading. All firms and workers can 
buy what they need from the market. The trade is done in the implicit way. 
The market records first how much demand and supply occurs at that day. 
Then update the price. And the firms and workers pay for the trade using the 
updated price. This guarantees that if there are some unusual demand or 
supply from the users, the user will have to pay a premium for changing the 
market. 

4. **World**: In a more generalized context, we can consider trade not only
inside a city with the market, but also among cities. In that case, we need
to generalize the market structure that it can accept trade from different 
cities inside the simulation. This allows firms sell their product in other 
cities other their theirs. For inter-city trade, we can also introduce the 
concept of Forex that for profit or expense done in other cities, the firms
need to exchange for the local cash. This generates the forex market which 
can be further established. 

In this simulation, the price is assumed to follow the non-equilibrium 
pricing scheme, where the price changes according to the local demand 
and supply of that day. It is possible that this may over-estimate the 
price variation for some items. However, to make sure the code can finish
one simulation within an hour. I choose this simplified scheme instead of 
the more complicated but realistic market book scheme. 

## To be done

Some of the components are implemented in the previous (but not so stable)
version and after checking that the system is stable against different 
setting, I will put them back in this version. 

1. A tax system with public welfare: In the current version the city has 
almost no role in the society except printing money. In fact, a more realistic
system should also consider the macro-economics, how willing the workers are 
spending money, and this will lead to consideration of how "good" the society
is, for example, education, health care and so on. 

2. An investment tool: Since this version contains the backbone of the code, 
it still needs a good investment channel to remove excess cash in the market. 
The investment can also generate secondary employment which also affects the 
global employment rate. The investment tool can be viewed as also the indicator
to the sentiment of different cities. 

3. A more generalized product chain: In this version the minimal product chain
(only 3: Water, wheat and bread) is included to make sure the firms and
workers can trade successfully. To create a more complex system where 
more non-linear relation appears among firms, we can include a more 
genearlized product chain. 

Enjoy simulation! 😃
