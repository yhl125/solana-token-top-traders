from bs4 import BeautifulSoup
import tls_client
import json
import re

allData: dict = {}

totalTraders = 0

session = tls_client.Session(client_identifier="chrome_105")

with open('tokens.txt', 'r') as fp:
    contractAddresses = fp.read().splitlines()
    print(f"[-] Dumping data..")

for contractAddress in contractAddresses:
        grabTopTradersURL = f"https://gmgn.ai/defi/quotation/v1/tokens/top_traders/sol/{contractAddress}?orderby=profit&direction=desc"

        response = session.get(grabTopTradersURL).json()['data']

        allData[contractAddress] = {}

        totalTraders = totalTraders + len(response)

        allData[contractAddress] = {}

        for topTrader in response:
              address = topTrader['address']
              boughtUsd = f"${topTrader['total_cost']:,.2f}"
              totalProfit = f"${topTrader['realized_profit']:,.2f}"
              unrealizedProfit = f"${topTrader['unrealized_profit']:,.2f}"
              multiplier = f"{topTrader['profit_change']:.2f}x" if topTrader['profit_change'] is not None else "?"
              buys = f"{topTrader['buy_tx_count_cur']}"
              sells = f"{topTrader['sell_tx_count_cur']}"

              allData[contractAddress][address] = {
                    "boughtUsd": boughtUsd,
                    "totalProfit": totalProfit,
                    "unrealizedProfit": unrealizedProfit,
                    "multiplier": multiplier,
                    "buys": buys,
                    "sells": sells
                }

with open('top_traders.json', 'w') as fp:
    json.dump(allData, fp, indent=4)
    print(f"[✅] Dumped {totalTraders} top traders for {len(contractAddresses)} tokens..")
