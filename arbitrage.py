from itertools import permutations
QUOTES=["USDT","USDC","FDUSD","BTC","ETH","BNB"]
def routes(symbols):
    S=set(symbols); out=set()
    for coin in {s[:-len(q)] for s in S for q in QUOTES if s.endswith(q) and len(s)>len(q)}:
        qs=[q for q in QUOTES if coin+q in S]
        for a,b in permutations(qs,2):
            if b+a in S: out.add((a,coin,b))
    return sorted(out)
def leg(amount,a,b,books):
    if a+b in books:
        x=books[a+b]; return amount*x["bid"],a+b,"SELL",x["bid_qty"]
    if b+a in books and books[b+a]["ask"]>0:
        x=books[b+a]; return amount/x["ask"],b+a,"BUY",x["ask_qty"]
def evaluate(r,books,start,fee):
    a,c,b=r; legs=[]; amount=start
    for x,y in ((a,c),(c,b),(b,a)):
        z=leg(amount,x,y,books)
        if not z:return
        amount,s,side,liq=z; amount*=1-fee
        legs.append({"symbol":s,"side":side,"liquidity":liq})
    p=amount-start
    return {"route":[a,c,b,a],"start_amount":start,"final_amount":amount,"net_profit":p,"net_profit_percent":p/start*100,"legs":legs}
