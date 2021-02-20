import pandas as pd
import json

data = json.load(open('mf_div_data.json'))
s = pd.DataFrame()
for amc, scheme_d in data.items():
    for scheme_n, div_data in scheme_d.items():
        div_df = pd.DataFrame(div_data, columns=['Date', 'Dividend_%', 'Bonus'])
        div_df['Date'] = pd.to_datetime(div_df['Date'], format='%d/%m/%Y')
        div_df = div_df.set_index('Date')
        div_df = div_df.sort_index(ascending=False).drop_duplicates()
        div_df = div_df.loc[div_df.index > '2020']
        print(scheme_n, len(div_df))
        s = pd.concat([s, pd.DataFrame((scheme_n, len(div_df), div_df['Dividend_%'].astype('float64').mean())).T])
s = s.sort_values([1, 2], ascending=False)
print(s)
