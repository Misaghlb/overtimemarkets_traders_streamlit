import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title='Overtime Markets Dashboard', layout='wide', page_icon=':dollar:')
st.title("Overtime Markets - Profitable Traders")


def clean_data(data_raw):
    for item in data_raw:
        tag = int(item['tags'][0])
        sport_name = ''
        if tag in (9001, 9002): sport_name = 'Football'
        if tag == 9003: sport_name = 'Baseball'
        if tag in (9004, 9005, 9008): sport_name = 'Basketball'
        if tag in (9006,): sport_name = 'Hockey'
        if tag in (9010, 9011, 9012, 9013, 9014, 9015, 9016): sport_name = 'Soccer'
        if tag in (9007,): sport_name = 'UFC'
        item['sport'] = sport_name
    return data_raw


@st.cache(ttl=24 * 60 * 60)
def fetch_names_data():
    payload = {
        "query": """{
              sportMarkets(first: 1000) {
                address
                homeTeam
                awayTeam
                tags
              }
            }""",
    }
    res = requests.post(url='https://api.thegraph.com/subgraphs/name/thales-markets/thales-markets-v2',
                        json=payload).json()['data']['sportMarkets']

    return clean_data(res)


data = fetch_names_data()


@st.cache(ttl=24 * 60 * 60)
def fetch_data(url: str):
    res = requests.get(url=url).json()

    for item in res:
        item['GAME_ADDRESS'] = item['GAME_ADDRESS']
        item['TAMOUNT'] = float(item['VOL'])
        item['WALLET'] = item['WALLET']

        for jj in data:
            if item['GAME_ADDRESS'] == jj['address']:
                item['sport'] = jj['sport']
                item['game_name'] = f"{jj['homeTeam']} VS {jj['awayTeam']}"
                # break

    return pd.DataFrame(
        res,
        columns=["GAME_ADDRESS", "TAMOUNT", "WALLET", "sport", "game_name"])


c1, c2 = st.columns(2)

c1.markdown("""
Overtime Market is built on top of Thales, which allows users bet on sport games like Football, baseball, Soccer and UFC.
### How it works?
for example there is match tomorrow, i can bet on Team A or B Winning or Draw. for betting i have to Buy the Token which is issued for that match. then after the match if i win, my tokens will worth exactly one dollar,
for example i bought each token for \$0.4, and now they worth \$1, great profit. but if i lose, they worth zero.


### You Will Read:
1. Top 10 most profitable wallets by each Sport
2. The Top 5 most profitable traders gain in dollar by sport and game 
""")

c2.markdown("""### Method:
I use the Flipside data to get the Overtime markets transactions and volume, and because the sport and for game labels i used thegraph.com api. \n
calculate the profit:
- we calculate the total profit that wallet gained after winning the bet,  
- total USD each wallet paid on bets
- total sold bets (users can sell their bought positions with a lower price)
- **formula: profit = (gained_from_bets + sold_bets) - paid_to_buy**
In this dashboard we will look at the most profitable traders by game and sport over last 2 weeks.""")

st.markdown("---")
st.write('')
st.write('')
st.markdown("# Top Wallets per Sport")

chart_data = fetch_data(
    'https://node-api.flipsidecrypto.com/api/v2/queries/84089b2a-ad97-469b-9203-38f96f64aa04/data/latest')

c1, c2 = st.columns(2)

soccer_data = chart_data[chart_data['sport'] == 'Soccer']
soccer_tops = soccer_data.groupby(["WALLET"], as_index=False).sum().sort_values('TAMOUNT', ascending=False).head(10)

fig = px.bar(soccer_tops, x='WALLET', y='TAMOUNT', color='WALLET', title="Top 10 Wallets by Soccer Sport",
             color_discrete_sequence=px.colors.qualitative.Safe)
fig.update_traces(hovertemplate=None)
fig.update_layout(hovermode="x")
fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
fig.update_layout(xaxis={'visible': False, 'showticklabels': False})
c1.plotly_chart(fig, use_container_width=True)

Baseball_data = chart_data[chart_data['sport'] == 'Baseball']
Baseball_tops = Baseball_data.groupby(["WALLET"], as_index=False).sum().sort_values('TAMOUNT', ascending=False).head(10)

fig = px.bar(Baseball_tops, x='WALLET', y='TAMOUNT', color='WALLET', title="Top 10 Wallets by Baseball Sport",
             color_discrete_sequence=px.colors.qualitative.Safe)
fig.update_traces(hovertemplate=None)
fig.update_layout(hovermode="x")
fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
fig.update_layout(xaxis={'visible': False, 'showticklabels': False})
c2.plotly_chart(fig, use_container_width=True)

ufc_data = chart_data[chart_data['sport'] == 'UFC']
ufc_tops = ufc_data.groupby(["WALLET"], as_index=False).sum().sort_values('TAMOUNT', ascending=False).head(10)

fig = px.bar(ufc_tops, x='WALLET', y='TAMOUNT', color='WALLET', title="Top 10 Wallets by UFC Sport",
             color_discrete_sequence=px.colors.qualitative.Bold)
fig.update_traces(hovertemplate=None)
fig.update_layout(hovermode="x")
fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
fig.update_layout(xaxis={'visible': False, 'showticklabels': False})
c1.plotly_chart(fig, use_container_width=True)

football_data = chart_data[chart_data['sport'] == 'Football']
football_tops = football_data.groupby(["WALLET"], as_index=False).sum().sort_values('TAMOUNT', ascending=False).head(10)

fig = px.bar(football_tops, x='WALLET', y='TAMOUNT', color='WALLET', title="Top 10 Wallets by Football Sport",
             color_discrete_sequence=px.colors.qualitative.Bold)
fig.update_traces(hovertemplate=None)
fig.update_layout(hovermode="x")
fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
fig.update_layout(xaxis={'visible': False, 'showticklabels': False})
c2.plotly_chart(fig, use_container_width=True)

st.markdown("""
these charts show the wallets that gained most profit from each Sport. \n
1. Top Wallet among these is the 0xe...a11 in Baseball Sport bets with total profit of 9.7K dollars.
2. Football and UFC wallets gained lowest profit, UFC top wallet could earn 1.2K dollars
3. on Football sport, the difference profit between first top wallet with next ones is too high, the first wallet has 5K dollars, but the second one is 10X lower, and the number of succesfull wallets is too low compare to the other sports.
4. total profit gained by all top 10 wallets for Baseball is more than the other sports
""")
st.markdown("---")

st.write('')
st.write('')
st.write('')
c1, c2 = st.columns(2)

# top 5 wallets among all sports
top_5_wallets = chart_data.groupby(["WALLET"], as_index=False).sum().sort_values('TAMOUNT', ascending=False).head(5)
cc = chart_data[chart_data.WALLET.isin(top_5_wallets['WALLET'])]

top_wallets_by_sport = cc.groupby(["WALLET", "sport"], as_index=False).sum()
fig = px.bar(top_wallets_by_sport, x='WALLET', y='TAMOUNT', color='sport', title="Top Five Wallets Profit by Sport",
             color_discrete_sequence=px.colors.qualitative.G10)
fig.update_traces(hovertemplate=None)
fig.update_layout(hovermode="x")
fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
fig.update_layout(xaxis={'visible': False, 'showticklabels': False})
c1.plotly_chart(fig, use_container_width=True)

top_wallets_by_game = cc.groupby(["WALLET", "game_name"], as_index=False).sum()
fig = px.bar(top_wallets_by_game, x='WALLET', y='TAMOUNT', color='game_name', title="Top Five Wallets Profit by Games",
             color_discrete_sequence=px.colors.qualitative.G10)
fig.update_traces(hovertemplate=None)
fig.update_layout(hovermode="x", hoverlabel=dict(namelength=-1))
fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
fig.update_layout(xaxis={'visible': False, 'showticklabels': False})
c2.plotly_chart(fig, use_container_width=True)

st.markdown("""
these charts show the Top 5  profitable wallets which could gain the most profit in all sports and games. \n
1. the left chart shows that out of 5 top wallets, 3 of them are from Baseball, so baseball wallets gained more profit as we saw above.
2. UFC wallets could get into top 5 wallets.
3. the right chart show that these top wallets, gained profit from which games. 3 wallets only gained their profit from one game. and one of them only two game. only one wallet could earm profits from diffrent games.
4. Top wallet, gained 9.7K dollars from Boston Red Sox vs NY Yankees
""")

st.markdown("---")
st.markdown("""
## Conclusion:
1. total profit gained by all top 10 wallets for Baseball is more than the other sports
2. Football and UFC wallets gained lowest profit, and were less successful
3. out of 5 top wallets, 3 of them are from Baseball, so baseball wallets gained more profit as we saw above
4. among top 5 wallets, 4 wallets gained their profit from only 1-2 games
""")

st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.markdown("---")
st.markdown("##### Contact:\n"
            "- developed by Misagh lotfi \n"
            "- https://twitter.com/misaghlb \n"
            )

st.markdown("##### Sources:\n"
            "- graph data: https://thegraph.com/hosted-service/subgraph/thales-markets/thales-markets-v2 \n"
            "- flipside data: https://app.flipsidecrypto.com/velocity/queries/84089b2a-ad97-469b-9203-38f96f64aa04  \n"
            "- code: https://github.com/Misaghlb/overtimemarkets_traders_streamlit \n"
            )
