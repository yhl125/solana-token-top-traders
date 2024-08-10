import json
import time
import requests
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=5, 
    backoff_factor=1, 
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

allData = {}
allAddresses = set()
addressFrequency = defaultdict(int)
totalTraders = 0

def fetch_top_traders(contract_address):
    url = f"https://gmgn.ai/defi/quotation/v1/tokens/top_traders/sol/{contract_address}?orderby=profit&direction=desc"
    try:
        response = session.get(url)
        return response.json().get('data', [])
    except requests.RequestException as e:
        print(f"Error fetching data for {contract_address}: {e}")
        return []

with open('tokens.txt', 'r') as fp:
    contractAddresses = fp.read().splitlines()
    print(f"[✅] Loaded {len(contractAddresses)} contract addresses")

try:
    threads = int(input("[❓] Threads: "))
except Exception:
    threads = 15

print(f"[🤖] Set threads to {threads}")

startTime = time.time()

with ThreadPoolExecutor(max_workers=threads) as executor:
    futures = {executor.submit(fetch_top_traders, contractAddress): contractAddress for contractAddress in contractAddresses}
    
    for future in as_completed(futures):
        contractAddress = futures[future]
        response = future.result()
        
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

endTime = time.time()
totalTime = endTime - startTime

repeatedAddresses = [address for address, count in addressFrequency.items() if count > 1]

with open('top_trader_addresses.txt', 'w') as av:
    for address in allAddresses:
        av.write(f"{address}\n")

with open('repeated_addresses.txt', 'w') as ra:
    for address in repeatedAddresses:
        ra.write(f"{address}\n")

with open('top_traders.json', 'w') as fp:
    json.dump(allData, fp, indent=4)

requestsSec = len(contractAddresses) / totalTime
print(f"[✅] Dumped {totalTraders} top traders for {len(contractAddresses)} tokens..")
print(f"[✅] Saved {len(allAddresses)} unique top trader addresses to top_trader_addresses.txt")
print(f"[✅] Saved {len(repeatedAddresses)} repeated addresses to repeated_addresses.txt")
print(f"[✅] Requests/Sec: {requestsSec:.2f} | Time Taken: {totalTime:.2f}s")
