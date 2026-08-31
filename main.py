import asyncio,json,os,time
from pathlib import Path
from binance import exchange_info,book_tickers,stream
from arbitrage import routes,evaluate
START=float(os.getenv("STARTING_AMOUNT","100")); FEE=float(os.getenv("FEE_RATE","0.001"))
MINP=float(os.getenv("MIN_NET_PROFIT_PERCENT","0.05")); MINU=float(os.getenv("MIN_NET_PROFIT_USDT","0.01"))
OUT=Path("data/signals.json")
async def main():
    info=await exchange_info()
    symbols=[x["symbol"] for x in info["symbols"] if x.get("status")=="TRADING" and x.get("isSpotTradingAllowed",True)]
    rs=routes(symbols); books={}
    for x in await book_tickers():
        try: books[x["symbol"]]={"bid":float(x["bidPrice"]),"ask":float(x["askPrice"]),"bid_qty":float(x["bidQty"]),"ask_qty":float(x["askQty"])}
        except: pass
    needed=set()
    for a,c,b in rs:
        for s in (a+c,c+a,c+b,b+c,b+a,a+b):
            if s in symbols: needed.add(s)
    print(f"Active symbols: {len(symbols)} | Routes: {len(rs)} | Live books: {len(needed)}",flush=True)
    q=asyncio.Queue(); asyncio.create_task(stream(sorted(needed),q)); last={}
    while True:
        x=await q.get(); books[x["symbol"]]=x
        for r in rs:
            if not any(s==x["symbol"] for s in (r[0]+r[1],r[1]+r[0],r[1]+r[2],r[2]+r[1],r[2]+r[0],r[0]+r[2])): continue
            v=evaluate(r,books,START,FEE)
            if v and v["net_profit"]>=MINU and v["net_profit_percent"]>=MINP:
                k=">".join(v["route"]); now=time.time()
                if now-last.get(k,0)<.5: continue
                last[k]=now; sig={"timestamp":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"status":"LIVE","type":"TRIANGULAR_ARBITRAGE","fee_rate_per_leg":FEE,**v}
                print(json.dumps(sig,separators=(",",":")),flush=True)
                try:data=json.loads(OUT.read_text())
                except:data=[]
                data.append(sig); OUT.write_text(json.dumps(data[-500:],indent=2))
if __name__=="__main__": asyncio.run(main())
