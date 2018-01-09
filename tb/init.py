import pandas as pd
import matplotlib.pyplot as plt
from temp.code_snippets import Test

balance = 4000
data = pd.DataFrame()
buy = pd.DataFrame (columns=['value', 'amount'])
sell = pd.DataFrame (columns=['value', 'amount'])
for tick in list(Test().listen()):
    data = data.append (tick)
    if data.shape[0] > 1:
        current_diff = data.iloc[-2:]['close'].diff().iloc[-1]
        data.iloc[-1, 1] = current_diff

        if current_diff > 0:
            buy = buy.append (pd.Series({'amount': tick.at['close'] * 0.01, 'value': 0.01}),ignore_index=True)
        else:
            sell = sell.append (pd.Series({'amount': tick.at['close'] * 0.01, 'value': 0.01}),ignore_index=True)

#data['close'].plot(figsize=(12,8))
#data['diff'].plot(figsize=(12,8))
#plt.show()

print (buy['value'].sum())
print (sell['value'].sum())

print (buy['amount'].sum())
print (sell['amount'].sum())

print (sell['amount'].sum() - buy['amount'].sum())

