# Define the geography
N_CITIES = 1


# =============================================================================
# Define the product type and production chain

N_GOODS = 3

PRODUCT_NAMES = ["WATER", "WHEAT", "BREAD"]

WATER = 0
WHEAT = 1
BREAD = 2

INGREDIENTS = [[0 for i in range(N_GOODS)] for j in range(N_GOODS)]
INGREDIENTS[WHEAT][WATER] = 1
INGREDIENTS[BREAD][WHEAT] = 1

PRODUCTIVITIES = [1 for i in range(N_GOODS)]

# Hard code of the productivity
PRODUCTIVITIES[WATER] = 10
PRODUCTIVITIES[WHEAT] = 6
PRODUCTIVITIES[BREAD] = 2

# =============================================================================
# For the labour section
INIT_CITIZENS = 230

INIT_SALARY = 100

INIT_FIRMS = [0 for i in range(N_GOODS)]

# Hard code for testing
INIT_FIRMS[WATER] = 29
INIT_FIRMS[WHEAT] = 51
INIT_FIRMS[BREAD] = 149

# =============================================================================
# For the market section

INIT_PRICES = [INIT_SALARY / PRODUCTIVITIES[i] for i in range(N_GOODS)]

# Calculate the base prices without markup
for i in range(N_GOODS):

    # FOr each good, loop through the ingredient 
    for j in range(N_GOODS):
        INIT_PRICES[i] += INGREDIENTS[i][j] * INIT_PRICES[j]

# Define how much the public budget spends
BUDGET_RATIO = [0 for i in range(N_GOODS)]

# Hard code for initial model
BUDGET_RATIO[BREAD] = 1

# Calculate base markup for city
total_budget = 0
for i in range(N_GOODS):
    if BUDGET_RATIO[i] > 0:
        total_budget += INIT_FIRMS[i] * PRODUCTIVITIES[i] * INIT_PRICES[i]

BASE_MARKUP = (total_budget / INIT_CITIZENS / INIT_SALARY - 1) * 2

# =============================================================================
# Define the city

INIT_CITY_CASH = INIT_CITIZENS * INIT_SALARY * 21

# =============================================================================
# Define the firm

INIT_EMPLOYEES = 1

INIT_FIRM_CASH = INIT_SALARY * INIT_EMPLOYEES * 21

# ===============================================================================
# Output for debug

print(" =================== Report parameter ========================")
print("Product network:")
for i in range(N_GOODS):
    print("Material: {} Base cost:{} Productivity:{} Ingredient:{}".format(
        PRODUCT_NAMES[i], INIT_PRICES[i], PRODUCTIVITIES[i], INGREDIENTS[i]
    ))
print("\nInitial markup: {}\n".format(BASE_MARKUP))
