import asyncio,json,time,aiohttp,websockets
REST="https://api.binance.com"; WS="wss://stream.binance.com:9443/stream"
async def exchange_info():
    async with aiohttp.ClientSession() as s:
        async with s.get(REST+"/api/v3/exchangeInfo",timeout=20) as r:
            r.raise_for_status(); return await r.json()
async def book_tickers():
    async with aiohttp.ClientSession() as s:
        async with s.get(REST+"/api/v3/ticker/bookTicker",timeout=20) as r:
            r.raise_for_status(); return await r.json()
async def stream(symbols,q):
    for i in range(0,len(symbols),150):
        asyncio.create_task(_stream(symbols[i:i+150],q))
    while True: await asyncio.sleep(3600)
async def _stream(symbols,q):
    url=WS+"?streams="+"/".join(s.lower()+"@bookTicker" for s in symbols)
    while True:
        try:
            async with websockets.connect(url,ping_interval=20,ping_timeout=20) as ws:
                async for raw in ws:
                    d=json.loads(raw).get("data",{})
                    if d.get("s"): await q.put({"symbol":d["s"],"bid":float(d["b"]),"ask":float(d["a"]),"bid_qty":float(d["B"]),"ask_qty":float(d["A"]),"ts":int(time.time()*1000)})
        except Exception as e:
            print("WS reconnect:",e,flush=True); await asyncio.sleep(3)
