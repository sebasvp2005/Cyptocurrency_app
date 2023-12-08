import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
import matplotlib.pyplot as plt


st.set_page_config(layout='wide')
st.title("Coin Market")
st.markdown("""
This app retrieves information of **CoinMarketCap**
            
You can select your favorite cryptocurrencies in the left sidebar and the information will displayed""")

about = st.expander('About')
about.markdown("""
Libraries: pandas, beautifulSoup , json, matplotlib, request, time
               
Data source: CoinMarketCap (https://coinmarketcap.com/)
               
""")

## sidebar
sidebar = st.sidebar

sidebar.header('Options')


# scraping information
@st.cache_data
def load_data():
  url = 'https://coinmarketcap.com'
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')
  data =soup.find('script', id='__NEXT_DATA__', type='application/json')
  coins_data_raw = json.loads(data.contents[0])
  #fixing error while scraping information
  fixed_data = json.loads(coins_data_raw['props']['initialState'])
  coins_info = fixed_data['cryptocurrency']['listingLatest']['data']
  colums = coins_info[0]['keysArr']

  new_data = { colums[i]: [ coins_info[j][i] for j in range(1, len(coins_info))] for i in range(len(colums))}

  df = pd.DataFrame(columns=['coin_name', 'coin_symbol', 'market_cap', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d', 'price', 'volume_24h'])
  df['coin_name'] = new_data['slug']
  df['coin_symbol'] = new_data['symbol']
  df['market_cap'] = new_data['quote.USD.selfReportedMarketCap']
  df['price'] = new_data['quote.USD.price']
  df['percent_change_1h'] = new_data['quote.USD.percentChange1h']
  df['percent_change_24h'] = new_data['quote.USD.percentChange24h']
  df['percent_change_7d'] = new_data['quote.USD.percentChange7d']
  df['volume_24h'] = new_data['quote.USD.volume24h']
  return df

df = load_data()

#cryptocurrency selection
coins = df['coin_name']
coins_selected = sidebar.multiselect('Currency', coins, coins)

df_selected_coins = df[(df['coin_name']).isin(coins_selected)]

#number of coins to display

num_coins = sidebar.slider('Number of coins to display', 1, 100, 100)
df_coins_to_display = df_selected_coins[:num_coins]

#time_range

time_range_selection = sidebar.selectbox('Time range', ['7d', '24h', '1h'])
time_convertion = {'7d': 'percent_change_7d', '24h': 'percent_change_24h', '1h' :'percent_change_1h' }

time_range = time_convertion[time_range_selection]



#sorted_values

sort_selection = sidebar.checkbox('Sorted values')
values_sorted = sort_selection

#page division
main,  space , right_column = st.columns((10,1, 5))

#main content

#display values
main.subheader('Information of coins selected')

main.dataframe(df_coins_to_display)

#display prices
main.subheader('Table of Price change %')
df_change = df_coins_to_display[['coin_symbol','percent_change_1h','percent_change_24h', 'percent_change_7d']]
df_change = df_change.set_index('coin_symbol')

main.dataframe(df_change)


#right division


right_column.subheader('Price change %')


if values_sorted:
  df_change = df_change.sort_values(time_range)
plt.figure(figsize=(5,20))
if df_change[time_range].size!=0:
  df_change[time_range].plot(kind = 'barh', color = (df_change[time_range]>0).map({True: 'g', False: 'r'}))

right_column.pyplot(plt)


















