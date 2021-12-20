import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

df = pd.read_csv("price_hist.csv")

def form_date(y,m,d):
    return dt.date(year=2000+int(y), month=int(m), day=int(d))

# add the date column
df["date"] = df.apply(lambda row: form_date(row["Y"], row["M"], row["D"]), axis=1)
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

# set up the figure
fig, ax = plt.subplots(ncols=2, nrows=2)

ax[0,0].plot(df["date"], df["WATER"])

ax[0,1].plot(df["date"], df["WHEAT"])
ax[1,0].plot(df["date"], df["BREAD"])

xticks = ax[0,0].get_xticks()
#ax[0,0].set_xticks()
plt.show()