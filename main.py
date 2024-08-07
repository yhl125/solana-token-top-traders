import requests
import json
from collections import defaultdict

allData = {}
allAddresses = set()
addressFrequency = defaultdict(int)
totalTraders = 0

def fetch_top_traders(contract_address):
    url = f"https://gmgn.ai/defi/quotation/v1/tokens/top_traders/sol/{contract_address}?orderby=profit&direction=desc"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json().get('data', [])
    except requests.RequestException as e:
        print(f"Error fetching data for {contract_address}: {e}")
        return []

with open('tokens.txt', 'r') as fp:
    contractAddresses = fp.read().splitlines()
    print(f"[-] Dumping data..")

for contractAddress in contractAddresses:
    response = fetch_top_traders(contractAddress)
    
    allData[contractAddress] = {}
    totalTraders += len(response)
    
    for topTrader in response:
        address = topTrader['address']
        addressFrequency[address] += 1 
        allAddresses.add(address)
        
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

repeatedAddresses = [address for address, count in addressFrequency.items() if count > 1]

with open('top_trader_addresses.txt', 'w') as av:
    for address in allAddresses:
        av.write(f"{address}\n")

with open('repeated_addresses.txt', 'w') as ra:
    for address in repeatedAddresses:
        ra.write(f"{address}\n")

with open('top_traders.json', 'w') as fp:
    json.dump(allData, fp, indent=4)

print(f"[✅] Dumped {totalTraders} top traders for {len(contractAddresses)} tokens..")
print(f"[✅] Saved {len(allAddresses)} unique top trader addresses to top_trader_addresses.txt")
print(f"[✅] Saved {len(repeatedAddresses)} repeated addresses to repeated_addresses.txt")
