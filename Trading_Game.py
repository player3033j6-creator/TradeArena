"""
╔══════════════════════════════════════════════════════════════════════╗
║   TRADEARENA  ──  Multiplayer Historical Trading Simulator           ║
║   • Admin creates rooms with a 6-char code                           ║
║   • 10-minute game on 2025–2026 real market data                     ║
║   • 10 companies randomly picked from 100+ each game                 ║
║   • Cash: $50,000 injected every 2 minutes (5× total)                ║
║   • Premium terminal UI with live charts & leaderboard               ║
╚══════════════════════════════════════════════════════════════════════╝

Install: pip install streamlit pandas numpy plotly yfinance
Run:     streamlit run trading_simulator.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json, os, hashlib, time, random, string, tempfile

try:
    import yfinance as yf
    YF = True
except ImportError:
    YF = False

st.set_page_config(page_title="TradeArena", layout="wide",
                   initial_sidebar_state="expanded", page_icon="⚡")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=Chakra+Petch:wght@300;400;500;600;700&display=swap');

:root {
  --bg:#060a0f; --bg2:#0c1219; --bg3:#111820;
  --border:#1e2d3d; --border2:#243447;
  --accent:#00d4ff; --green:#00e676; --red:#ff3d57;
  --gold:#ffd740; --text:#e0eaf4; --text2:#7a9bb5; --text3:#3d5a73;
  --mono:'IBM Plex Mono',monospace; --display:'Chakra Petch',sans-serif;
}
html,body,[class*="css"]{font-family:var(--display)!important;background:var(--bg)!important;color:var(--text)!important;}
.stApp{background:var(--bg)!important;}
.stApp>header{background:transparent!important;}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] *{color:var(--text)!important;}
input,textarea,[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input{
  background:var(--bg3)!important;border-color:var(--border2)!important;
  color:var(--text)!important;font-family:var(--mono)!important;}
div[data-baseweb="select"] *{background:var(--bg3)!important;color:var(--text)!important;}
.stButton>button{background:transparent!important;border:1px solid var(--border2)!important;
  color:var(--text)!important;font-family:var(--display)!important;font-weight:600!important;
  letter-spacing:.05em!important;transition:all .2s!important;}
.stButton>button:hover{border-color:var(--accent)!important;color:var(--accent)!important;
  box-shadow:0 0 12px rgba(0,212,255,.15)!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#00d4ff18,#00d4ff08)!important;
  border-color:var(--accent)!important;color:var(--accent)!important;}
.stButton>button[kind="primary"]:hover{background:linear-gradient(135deg,#00d4ff30,#00d4ff15)!important;
  box-shadow:0 0 20px rgba(0,212,255,.25)!important;}
[data-testid="stTabs"] [role="tab"]{font-family:var(--display)!important;font-weight:600!important;
  letter-spacing:.04em!important;color:var(--text2)!important;}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{color:var(--accent)!important;
  border-bottom:2px solid var(--accent)!important;}
[data-testid="stMetric"]{background:var(--bg3)!important;border:1px solid var(--border)!important;
  border-radius:6px!important;padding:.6rem .8rem!important;}
[data-testid="stMetricLabel"]{color:var(--text2)!important;font-size:.7rem!important;letter-spacing:.08em!important;}
[data-testid="stMetricValue"]{font-family:var(--mono)!important;color:var(--text)!important;font-size:1.1rem!important;}
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:8px!important;overflow:hidden!important;}
.dvn-scroller{background:var(--bg2)!important;}
[data-testid="stProgress"]>div>div{background:var(--accent)!important;}
[data-testid="stProgress"]>div{background:var(--bg3)!important;}
[data-testid="stExpander"]{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:8px!important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:var(--bg2);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px;}
div.stForm{background:var(--bg2)!important;border:1px solid var(--border)!important;
  border-radius:10px!important;padding:1.2rem!important;}

.ta-logo{font-family:var(--display);font-weight:700;font-size:2.8rem;letter-spacing:.12em;
  background:linear-gradient(90deg,#00d4ff,#00e676 50%,#ffd740);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;text-transform:uppercase;}
.ta-tagline{font-family:var(--mono);font-size:.72rem;color:var(--text3);letter-spacing:.15em;text-transform:uppercase;}
.room-code{font-family:var(--mono)!important;font-size:2.4rem!important;font-weight:700!important;
  letter-spacing:.3em!important;color:var(--gold)!important;text-shadow:0 0 24px rgba(255,215,64,.35);}
.ticker-card{background:var(--bg2);border:1px solid var(--border);border-radius:8px;
  padding:.7rem .75rem;margin-bottom:.4rem;position:relative;overflow:hidden;}
.ticker-card.up::before,.ticker-card.down::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;}
.ticker-card.up::before{background:linear-gradient(90deg,var(--green),transparent);}
.ticker-card.down::before{background:linear-gradient(90deg,var(--red),transparent);}
.ticker-sym{font-family:var(--mono);font-weight:700;font-size:.92rem;color:var(--text);letter-spacing:.05em;}
.ticker-name{font-size:.62rem;color:var(--text3);margin:1px 0 3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.ticker-tag{font-size:.58rem;color:var(--text3);margin-bottom:3px;}
.ticker-price{font-family:var(--mono);font-size:1.1rem;font-weight:600;}
.ticker-chg{font-family:var(--mono);font-size:.7rem;}
.up{color:var(--green)!important;} .down{color:var(--red)!important;}
.cash-banner{background:linear-gradient(135deg,rgba(0,230,118,.07),rgba(0,212,255,.03));
  border:1px solid rgba(0,230,118,.25);border-radius:8px;padding:.6rem 1rem;
  font-family:var(--mono);font-size:.8rem;color:var(--green);font-weight:600;letter-spacing:.03em;}
.inject-flash{background:linear-gradient(135deg,rgba(0,230,118,.14),rgba(0,230,118,.04));
  border:1px solid var(--green);border-radius:8px;padding:.9rem 1.2rem;
  font-family:var(--display);font-size:1rem;color:var(--green);font-weight:700;
  text-align:center;letter-spacing:.08em;box-shadow:0 0 30px rgba(0,230,118,.12);}
.timer-block{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:1rem;text-align:center;}
.timer-digits{font-family:var(--mono);font-size:2.6rem;font-weight:700;letter-spacing:.12em;}
.timer-label{font-size:.6rem;color:var(--text3);letter-spacing:.18em;text-transform:uppercase;margin-top:.2rem;}
.lb-row{display:flex;align-items:center;justify-content:space-between;padding:.45rem .6rem;
  border-radius:6px;margin-bottom:.25rem;border:1px solid transparent;font-family:var(--mono);font-size:.82rem;}
.lb-row.me{border-color:var(--accent);background:rgba(0,212,255,.04);}
.stat-pill{display:inline-block;padding:.2rem .55rem;border-radius:4px;
  font-family:var(--mono);font-size:.67rem;font-weight:600;letter-spacing:.05em;}
.stat-pill.buy{background:rgba(0,230,118,.1);color:var(--green);border:1px solid rgba(0,230,118,.2);}
.stat-pill.sell{background:rgba(255,61,87,.1);color:var(--red);border:1px solid rgba(255,61,87,.2);}
.stat-pill.cash{background:rgba(0,212,255,.1);color:var(--accent);border:1px solid rgba(0,212,255,.2);}
.section-hdr{font-family:var(--mono);font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;
  color:var(--text3);border-bottom:1px solid var(--border);padding-bottom:.35rem;margin-bottom:.75rem;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
USERS_FILE              = "ta_users.json"
ROOMS_FILE              = "ta_rooms.json"
GAME_DURATION_SECS      = 600
TICKS_PER_GAME          = 390
TICK_REAL_SECS          = GAME_DURATION_SECS / TICKS_PER_GAME
STARTING_CASH           = 0.0
CASH_INJECTION          = 50_000.0
INJECTION_INTERVAL_SECS = 120
SYMBOLS_PER_GAME        = 10
DATA_START              = "2025-01-01"
DATA_END                = date.today().strftime("%Y-%m-%d")

# ─────────────────────────────────────────────────────────────────────────────
# MASTER STOCK POOL — 100+ companies
# ─────────────────────────────────────────────────────────────────────────────
ALL_STOCKS = {
    # ─ INDIA IT
    "INFY.NS":("Infosys","🇮🇳 IT"), "TCS.NS":("TCS","🇮🇳 IT"),
    "WIPRO.NS":("Wipro","🇮🇳 IT"), "HCLTECH.NS":("HCL Technologies","🇮🇳 IT"),
    "TECHM.NS":("Tech Mahindra","🇮🇳 IT"), "LTIM.NS":("LTIMindtree","🇮🇳 IT"),
    "MPHASIS.NS":("Mphasis","🇮🇳 IT"), "PERSISTENT.NS":("Persistent Systems","🇮🇳 IT"),
    "COFORGE.NS":("Coforge","🇮🇳 IT"), "KPITTECH.NS":("KPIT Technologies","🇮🇳 IT"),
    "TATAELXSI.NS":("Tata Elxsi","🇮🇳 IT"), "MASTEK.NS":("Mastek","🇮🇳 IT"),
    # ─ INDIA FINANCE
    "HDFCBANK.NS":("HDFC Bank","🇮🇳 Finance"), "ICICIBANK.NS":("ICICI Bank","🇮🇳 Finance"),
    "SBIN.NS":("State Bank of India","🇮🇳 Finance"), "KOTAKBANK.NS":("Kotak Mahindra","🇮🇳 Finance"),
    "AXISBANK.NS":("Axis Bank","🇮🇳 Finance"), "BAJFINANCE.NS":("Bajaj Finance","🇮🇳 Finance"),
    "BAJAJFINSV.NS":("Bajaj Finserv","🇮🇳 Finance"), "HDFCLIFE.NS":("HDFC Life","🇮🇳 Finance"),
    "ICICIGI.NS":("ICICI Lombard","🇮🇳 Finance"), "IDFCFIRSTB.NS":("IDFC First Bank","🇮🇳 Finance"),
    "INDUSINDBK.NS":("IndusInd Bank","🇮🇳 Finance"), "BANDHANBNK.NS":("Bandhan Bank","🇮🇳 Finance"),
    "MUTHOOTFIN.NS":("Muthoot Finance","🇮🇳 Finance"), "LICHSGFIN.NS":("LIC Housing","🇮🇳 Finance"),
    # ─ INDIA CONSUMER
    "TITAN.NS":("Titan Company","🇮🇳 Consumer"), "NYKAA.NS":("Nykaa","🇮🇳 Consumer"),
    "DMART.NS":("Avenue Supermarts","🇮🇳 Retail"), "TRENT.NS":("Trent","🇮🇳 Retail"),
    "ABFRL.NS":("Aditya Birla Fashion","🇮🇳 Retail"), "SHOPERSTOP.NS":("Shoppers Stop","🇮🇳 Retail"),
    # ─ INDIA FMCG
    "NESTLEIND.NS":("Nestle India","🇮🇳 FMCG"), "HINDUNILVR.NS":("Hindustan Unilever","🇮🇳 FMCG"),
    "ITC.NS":("ITC Limited","🇮🇳 FMCG"), "MARICO.NS":("Marico","🇮🇳 FMCG"),
    "DABUR.NS":("Dabur India","🇮🇳 FMCG"), "GODREJCP.NS":("Godrej Consumer","🇮🇳 FMCG"),
    "BRITANNIA.NS":("Britannia","🇮🇳 FMCG"), "COLPAL.NS":("Colgate-Palmolive IN","🇮🇳 FMCG"),
    "ZOMATO.NS":("Zomato","🇮🇳 Food Tech"), "SWIGGY.NS":("Swiggy","🇮🇳 Food Tech"),
    # ─ INDIA FINTECH
    "PAYTM.NS":("Paytm","🇮🇳 Fintech"), "POLICYBZR.NS":("PB Fintech","🇮🇳 Fintech"),
    "ANGELONE.NS":("Angel One","🇮🇳 Fintech"),
    # ─ INDIA AUTO
    "MARUTI.NS":("Maruti Suzuki","🇮🇳 Auto"), "TATAMOTORS.NS":("Tata Motors","🇮🇳 Auto"),
    "M&M.NS":("Mahindra & Mahindra","🇮🇳 Auto"), "EICHERMOT.NS":("Eicher Motors","🇮🇳 Auto"),
    "BAJAJ-AUTO.NS":("Bajaj Auto","🇮🇳 Auto"), "HEROMOTOCO.NS":("Hero MotoCorp","🇮🇳 Auto"),
    "TVSMOTOR.NS":("TVS Motor","🇮🇳 Auto"), "ASHOKLEY.NS":("Ashok Leyland","🇮🇳 Auto"),
    "MOTHERSON.NS":("Samvardhana Motherson","🇮🇳 Auto"),
    # ─ INDIA PHARMA
    "SUNPHARMA.NS":("Sun Pharma","🇮🇳 Pharma"), "DRREDDY.NS":("Dr Reddy's Labs","🇮🇳 Pharma"),
    "CIPLA.NS":("Cipla","🇮🇳 Pharma"), "DIVISLAB.NS":("Divi's Laboratories","🇮🇳 Pharma"),
    "APOLLOHOSP.NS":("Apollo Hospitals","🇮🇳 Healthcare"), "TORNTPHARM.NS":("Torrent Pharma","🇮🇳 Pharma"),
    "LUPIN.NS":("Lupin","🇮🇳 Pharma"), "BIOCON.NS":("Biocon","🇮🇳 Pharma"),
    "MAXHEALTH.NS":("Max Healthcare","🇮🇳 Healthcare"), "FORTIS.NS":("Fortis Healthcare","🇮🇳 Healthcare"),
    # ─ INDIA ENERGY
    "RELIANCE.NS":("Reliance Industries","🇮🇳 Energy"), "ONGC.NS":("ONGC","🇮🇳 Oil & Gas"),
    "ADANIGREEN.NS":("Adani Green Energy","🇮🇳 Energy"), "ADANIPORTS.NS":("Adani Ports","🇮🇳 Infra"),
    "ADANIENT.NS":("Adani Enterprises","🇮🇳 Conglomerate"), "NTPC.NS":("NTPC","🇮🇳 Power"),
    "POWERGRID.NS":("Power Grid Corp","🇮🇳 Power"), "IOC.NS":("Indian Oil","🇮🇳 Oil & Gas"),
    "BPCL.NS":("BPCL","🇮🇳 Oil & Gas"), "TATAPOWER.NS":("Tata Power","🇮🇳 Power"),
    # ─ INDIA METALS
    "TATASTEEL.NS":("Tata Steel","🇮🇳 Steel"), "JSWSTEEL.NS":("JSW Steel","🇮🇳 Steel"),
    "HINDALCO.NS":("Hindalco Industries","🇮🇳 Metals"), "VEDL.NS":("Vedanta","🇮🇳 Mining"),
    "COALINDIA.NS":("Coal India","🇮🇳 Mining"), "SAIL.NS":("Steel Authority","🇮🇳 Steel"),
    "NMDC.NS":("NMDC","🇮🇳 Mining"),
    # ─ INDIA TELECOM / REALTY / CEMENT
    "BHARTIARTL.NS":("Bharti Airtel","🇮🇳 Telecom"), "IDEA.NS":("Vodafone Idea","🇮🇳 Telecom"),
    "DLF.NS":("DLF Limited","🇮🇳 Real Estate"), "GODREJPROP.NS":("Godrej Properties","🇮🇳 Real Estate"),
    "PRESTIGE.NS":("Prestige Estates","🇮🇳 Real Estate"),
    "ULTRACEMCO.NS":("UltraTech Cement","🇮🇳 Cement"), "SHREECEM.NS":("Shree Cement","🇮🇳 Cement"),
    "ACC.NS":("ACC Limited","🇮🇳 Cement"), "AMBUJACEM.NS":("Ambuja Cements","🇮🇳 Cement"),
    # ─ US TECH
    "AAPL":("Apple","🇺🇸 Tech"), "MSFT":("Microsoft","🇺🇸 Tech"),
    "GOOGL":("Alphabet","🇺🇸 Tech"), "AMZN":("Amazon","🇺🇸 Tech"),
    "META":("Meta Platforms","🇺🇸 Tech"), "UBER":("Uber","🇺🇸 Tech"),
    "LYFT":("Lyft","🇺🇸 Tech"), "ORCL":("Oracle","🇺🇸 Tech"),
    "CRM":("Salesforce","🇺🇸 Tech"), "SNOW":("Snowflake","🇺🇸 Tech"),
    "DDOG":("Datadog","🇺🇸 Tech"), "PLTR":("Palantir","🇺🇸 AI/Data"),
    # ─ US SEMICON / EV
    "NVDA":("NVIDIA","🇺🇸 Semicon"), "AMD":("AMD","🇺🇸 Semicon"),
    "INTC":("Intel","🇺🇸 Semicon"), "QCOM":("Qualcomm","🇺🇸 Semicon"),
    "ARM":("Arm Holdings","🇺🇸 Semicon"), "TSLA":("Tesla","🇺🇸 EV"),
    # ─ US MEDIA / GAMING
    "NFLX":("Netflix","🇺🇸 Media"), "DIS":("Walt Disney","🇺🇸 Media"),
    "SPOT":("Spotify","🇺🇸 Media"), "RBLX":("Roblox","🇺🇸 Gaming"),
    "TTWO":("Take-Two Interactive","🇺🇸 Gaming"),
    # ─ US FINANCE
    "JPM":("JPMorgan Chase","🇺🇸 Finance"), "BAC":("Bank of America","🇺🇸 Finance"),
    "GS":("Goldman Sachs","🇺🇸 Finance"), "MS":("Morgan Stanley","🇺🇸 Finance"),
    "V":("Visa","🇺🇸 Finance"), "MA":("Mastercard","🇺🇸 Finance"),
    # ─ US FINTECH / CRYPTO
    "PYPL":("PayPal","🇺🇸 Fintech"), "SQ":("Block (Square)","🇺🇸 Fintech"),
    "COIN":("Coinbase","🇺🇸 Crypto"), "HOOD":("Robinhood","🇺🇸 Fintech"),
    # ─ US RETAIL / CONSUMER
    "WMT":("Walmart","🇺🇸 Retail"), "TGT":("Target","🇺🇸 Retail"),
    "COST":("Costco","🇺🇸 Retail"), "NKE":("Nike","🇺🇸 Consumer"),
    # ─ US PHARMA / ENERGY / AEROSPACE
    "LLY":("Eli Lilly","🇺🇸 Pharma"), "PFE":("Pfizer","🇺🇸 Pharma"),
    "MRNA":("Moderna","🇺🇸 Pharma"), "ABBV":("AbbVie","🇺🇸 Pharma"),
    "XOM":("ExxonMobil","🇺🇸 Energy"), "CVX":("Chevron","🇺🇸 Energy"),
    "BA":("Boeing","🇺🇸 Aerospace"), "RTX":("Raytheon","🇺🇸 Aerospace"),
    # ─ GLOBAL
    "TSM":("TSMC","🌏 Semicon"), "BABA":("Alibaba","🇨🇳 Tech"),
    "JD":("JD.com","🇨🇳 Tech"), "BIDU":("Baidu","🇨🇳 Tech"),
    "NIO":("NIO","🇨🇳 EV"), "XPEV":("XPeng","🇨🇳 EV"),
    "TM":("Toyota","🇯🇵 Auto"), "SONY":("Sony","🇯🇵 Tech"),
    "NVO":("Novo Nordisk","🇩🇰 Pharma"), "ASML":("ASML","🇳🇱 Semicon"),
    "SAP":("SAP SE","🇩🇪 Tech"), "SHOP":("Shopify","🇨🇦 Tech"),
    "RIO":("Rio Tinto","🇦🇺 Mining"), "BHP":("BHP Group","🇦🇺 Mining"),
    "SE":("Sea Limited","🌏 Tech"), "GRAB":("Grab Holdings","🌏 Tech"),
    "MELI":("MercadoLibre","🌎 Tech"), "NU":("Nubank","🌎 Fintech"),
    "VALE":("Vale S.A.","🌎 Mining"), "LVMH":("LVMH","🇫🇷 Luxury"),
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _load(path):
    if not os.path.exists(path): return {}
    for attempt in range(3):
        try:
            with open(path,"r") as f: content=f.read().strip()
            if not content: return {}
            return json.loads(content)
        except: 
            if attempt<2: time.sleep(0.05)
    return {}

def _save(path, data):
    dir_name=os.path.dirname(os.path.abspath(path))
    try:
        fd,tmp=tempfile.mkstemp(dir=dir_name,suffix=".tmp")
        try:
            with os.fdopen(fd,"w") as f: json.dump(data,f,default=str)
            os.replace(tmp,path)
        except:
            try: os.unlink(tmp)
            except: pass
            raise
    except:
        try:
            with open(path,"w") as f: json.dump(data,f,default=str)
        except: pass

def hp(pw): return hashlib.sha256(pw.encode()).hexdigest()
def dtick(sym): return sym.replace(".NS","")

def register(u,pw):
    users=_load(USERS_FILE)
    if u in users: return False,"Username taken."
    users[u]={"pw":hp(pw),"created":str(datetime.now())}
    _save(USERS_FILE,users); return True,"Account created!"

def login(u,pw):
    users=_load(USERS_FILE)
    if u not in users: return False,"User not found."
    if users[u]["pw"]!=hp(pw): return False,"Wrong password."
    return True,"OK"

def pick_game_symbols():
    india=[s for s,(_, t) in ALL_STOCKS.items() if "🇮🇳" in t]
    us_tech=[s for s,(_, t) in ALL_STOCKS.items()
             if any(x in t for x in ["🇺🇸 Tech","🇺🇸 Semicon","🇺🇸 EV","🇺🇸 AI","🇺🇸 Crypto","🇺🇸 Media","🇺🇸 Gaming"])]
    us_other=[s for s,(_, t) in ALL_STOCKS.items() if s not in us_tech and "🇺🇸" in t]
    glob=[s for s,(_, t) in ALL_STOCKS.items() if "🇺🇸" not in t and "🇮🇳" not in t]
    chosen=random.sample(india,min(4,len(india)))+random.sample(us_tech,min(3,len(us_tech)))+\
           random.sample(us_other,min(1,len(us_other)))+random.sample(glob,min(1,len(glob)))
    rem=[s for s in ALL_STOCKS if s not in chosen]
    needed=SYMBOLS_PER_GAME-len(chosen)
    if needed>0: chosen+=random.sample(rem,min(needed,len(rem)))
    random.shuffle(chosen)
    return {s:ALL_STOCKS[s] for s in chosen[:SYMBOLS_PER_GAME]}

@st.cache_data(ttl=1800,show_spinner=False)
def load_hist(sym):
    if not YF: return None
    try:
        df=yf.download(sym,start=DATA_START,end=DATA_END,progress=False,auto_adjust=True)
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        return df if not df.empty else None
    except: return None

def build_path(op,cp,hp_,lp,n=390):
    op=max(op,.01); cp=max(cp,.01); hp_=max(hp_,op); lp=max(min(lp,op),.01)
    vol=abs(hp_-lp)/op*0.25; prices=[op]
    for i in range(1,n):
        drift=(cp-prices[-1])/(n-i+1)*0.35
        shock=np.random.normal(0,vol*prices[-1]/np.sqrt(n))
        prices.append(round(min(max(prices[-1]+drift+shock,lp*.999),hp_*1.001),2))
    return prices

def sf(val,fb):
    try: v=float(val); return v if (np.isfinite(v) and v>0) else fb
    except: return fb

def pick_day(sym):
    df=load_hist(sym)
    if df is None or len(df)<3:
        b=random.uniform(50,3000)
        return "simulated",build_path(b,b*random.uniform(.97,1.03),b*1.04,b*.96)
    row=df.sample(1).iloc[0]
    ds=str(row.name.date()) if hasattr(row.name,"date") else str(row.name)
    op=sf(row.get("Open"),100.); cp=sf(row.get("Close"),op)
    hp_=sf(row.get("High"),op*1.02); lp=sf(row.get("Low"),op*.98)
    return ds,build_path(op,cp,hp_,lp)

def compute_inj_due(start):
    e=time.time()-start
    return min(int(e//INJECTION_INTERVAL_SECS)+1,int(GAME_DURATION_SECS//INJECTION_INTERVAL_SECS)+1)

def inject_cash(code,uname):
    rooms=_load(ROOMS_FILE); r=rooms.get(code)
    if not r or r["state"]!="running" or not r.get("start_epoch"): return 0
    p=r["players"].get(uname)
    if not p: return 0
    due=compute_inj_due(float(r["start_epoch"])); given=p.get("injections_given",0)
    new=due-given
    if new>0:
        amt=new*CASH_INJECTION; p["cash"]+=amt; p["injections_given"]=due
        r["trade_log"].append({"time":str(datetime.now()),"player":uname,"symbol":"—",
                               "action":"CASH_IN","qty":new,"price":CASH_INJECTION,"total":amt,"tick":r["current_tick"]})
        rooms[code]=r; _save(ROOMS_FILE,rooms)
    return new

def next_inj(start):
    e=time.time()-start
    return max(0.,((int(e//INJECTION_INTERVAL_SECS)+1)*INJECTION_INTERVAL_SECS)-e)

def gen_code():
    rooms=_load(ROOMS_FILE)
    for _ in range(200):
        c="".join(random.choices(string.ascii_uppercase+string.digits,k=6))
        if c not in rooms: return c
    return "".join(random.choices(string.ascii_uppercase,k=8))

def create_room(admin):
    code=gen_code(); gs=pick_game_symbols(); sl=list(gs.keys()); paths={}; dates={}
    pb=st.progress(0,text="⚡ Loading market data…")
    for i,sym in enumerate(sl):
        pb.progress((i+1)/len(sl),text=f"Fetching {dtick(sym)}…")
        ds,path=pick_day(sym); paths[sym]=path; dates[sym]=ds
    pb.empty()
    rooms=_load(ROOMS_FILE)
    rooms[code]={"admin":admin,"created":str(datetime.now()),"state":"waiting","start_epoch":None,
                 "players":{},"price_paths":paths,"day_dates":dates,"current_tick":0,"trade_log":[],
                 "game_symbols":{sym:list(info) for sym,info in gs.items()}}
    _save(ROOMS_FILE,rooms); return code

def get_room(code): return _load(ROOMS_FILE).get(code)

def join_room(code,uname):
    rooms=_load(ROOMS_FILE)
    if code not in rooms: return False,"Room not found."
    r=rooms[code]
    if r["state"]=="finished": return False,"Game already finished."
    if uname not in r["players"]:
        r["players"][uname]={"cash":0.,"portfolio":{},"injections_given":0}
        rooms[code]=r; _save(ROOMS_FILE,rooms)
    return True,"OK"

def advance_tick(code):
    rooms=_load(ROOMS_FILE); r=rooms.get(code)
    if r is None: return None
    if r["state"]=="running" and r["start_epoch"]:
        e=time.time()-float(r["start_epoch"]); nt=min(int(e/TICK_REAL_SECS),TICKS_PER_GAME-1)
        chg=False
        if nt!=r["current_tick"]: r["current_tick"]=nt; chg=True
        if nt>=TICKS_PER_GAME-1 and r["state"]!="finished": r["state"]="finished"; chg=True
        if chg: rooms[code]=r; _save(ROOMS_FILE,rooms)
    return r

def get_gs(room): return {sym:tuple(info) for sym,info in room.get("game_symbols",{}).items()}

def cur_prices(room):
    t=room["current_tick"]; gs=get_gs(room)
    return {sym:room["price_paths"][sym][min(t,len(room["price_paths"][sym])-1)] for sym in gs}

def pval(room,uname):
    p=room["players"].get(uname,{"cash":0,"portfolio":{}})
    pr=cur_prices(room)
    return p["cash"]+sum(pr.get(s,0)*q for s,q in p["portfolio"].items())

def lb(room):
    return sorted([{"Player":u,"Value":pval(room,u),
                    "CashIn":room["players"][u].get("injections_given",0)*CASH_INJECTION}
                   for u in room["players"]],key=lambda x:-x["Value"])

def do_trade(code,uname,sym,qty,action):
    rooms=_load(ROOMS_FILE); r=rooms.get(code)
    if not r: return False,"Room not found."
    if r["state"]!="running": return False,"Game not running."
    p=r["players"].get(uname)
    if not p: return False,"Not in room."
    pr=cur_prices(r); price=pr[sym]; total=price*qty
    if action=="BUY":
        if total>p["cash"]: return False,f"Need ${total:,.0f} · have ${p['cash']:,.0f}"
        p["cash"]-=total; p["portfolio"][sym]=p["portfolio"].get(sym,0)+qty
    else:
        owned=p["portfolio"].get(sym,0)
        if owned<qty: return False,f"Own {owned} shares only."
        p["cash"]+=total; p["portfolio"][sym]=owned-qty
        if p["portfolio"][sym]==0: del p["portfolio"][sym]
    r["trade_log"].append({"time":str(datetime.now()),"player":uname,"symbol":sym,
                           "action":action,"qty":qty,"price":price,"total":total,"tick":r["current_tick"]})
    rooms[code]=r; _save(ROOMS_FILE,rooms)
    return True,f"{'▲ Bought' if action=='BUY' else '▼ Sold'} {qty}× {dtick(sym)} @ ${price:.2f}"

CLAYOUT=dict(height=330,hovermode="x unified",plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
             xaxis=dict(gridcolor="rgba(30,45,61,.5)",color="#3d5a73",tickfont=dict(family="IBM Plex Mono",size=9)),
             yaxis=dict(gridcolor="rgba(30,45,61,.5)",color="#3d5a73",tickprefix="$",tickfont=dict(family="IBM Plex Mono",size=9)),
             margin=dict(l=0,r=0,t=28,b=0),font=dict(family="Chakra Petch"))

# ─────────────────────────────────────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────────────────────────────────────
def show_auth():
    st.markdown("""
    <div style='text-align:center;padding:4rem 0 1.5rem'>
      <div class='ta-logo'>⚡ TradeArena</div>
      <div class='ta-tagline' style='margin:.8rem 0 1rem'>Multiplayer · Real Market Data · 2025–2026</div>
      <div style='display:flex;gap:.8rem;justify-content:center;flex-wrap:wrap'>
        <span class='stat-pill buy'>100+ Companies</span>
        <span class='stat-pill cash'>Live Data</span>
        <span class='stat-pill sell'>10-Min Sessions</span>
      </div>
      <div style='font-family:var(--mono);font-size:.75rem;color:#1e6b4a;margin-top:.9rem'>
        💰 $50,000 every 2 min · $250k max · start from zero
      </div>
    </div>""",unsafe_allow_html=True)
    _,mid,_=st.columns([1,1.1,1])
    with mid:
        t1,t2=st.tabs(["  LOGIN  ","  REGISTER  "])
        with t1:
            with st.form("lf"):
                u=st.text_input("Username",placeholder="enter username")
                pw=st.text_input("Password",type="password",placeholder="••••••••")
                if st.form_submit_button("⚡  ENTER ARENA",use_container_width=True,type="primary"):
                    ok,msg=login(u,pw)
                    if ok: st.session_state.user=u; st.rerun()
                    else: st.error(msg)
        with t2:
            with st.form("rf"):
                u2=st.text_input("Username",placeholder="choose username")
                p1=st.text_input("Password",type="password",placeholder="••••••••")
                p2=st.text_input("Confirm",type="password",placeholder="••••••••")
                if st.form_submit_button("CREATE ACCOUNT",use_container_width=True,type="primary"):
                    if p1!=p2: st.error("Passwords don't match.")
                    elif not u2 or not p1: st.error("All fields required.")
                    else:
                        ok,msg=register(u2,p1)
                        st.success(msg) if ok else st.error(msg)

def show_lobby():
    user=st.session_state.user
    max_inj=int(GAME_DURATION_SECS//INJECTION_INTERVAL_SECS)+1
    st.markdown(f"""
    <div style='display:flex;align-items:center;justify-content:space-between;
                border-bottom:1px solid #1e2d3d;padding-bottom:1rem;margin-bottom:1.5rem'>
      <div><div class='ta-logo' style='font-size:1.9rem'>⚡ TradeArena</div>
           <div class='ta-tagline'>TRADING FLOOR · {DATA_START} → {DATA_END} · {len(ALL_STOCKS)} COMPANIES</div></div>
      <div style='text-align:right'>
        <div style='font-family:var(--mono);font-size:.65rem;color:#3d5a73'>LOGGED IN AS</div>
        <div style='font-family:var(--mono);font-weight:700;color:#00d4ff'>{user.upper()}</div>
      </div>
    </div>""",unsafe_allow_html=True)

    # Cash schedule cards
    cc=st.columns(max_inj)
    for i in range(max_inj):
        cc[i].markdown(
            f"<div style='background:#0c1219;border:1px solid #1e2d3d;border-radius:6px;padding:.5rem;text-align:center'>"
            f"<div style='font-family:var(--mono);font-size:.55rem;color:#3d5a73;letter-spacing:.1em'>T+{i*2}MIN</div>"
            f"<div style='font-family:var(--mono);font-size:.9rem;font-weight:700;color:#00e676'>$50K</div></div>",
            unsafe_allow_html=True)
    st.markdown("<div style='height:.6rem'></div>",unsafe_allow_html=True)

    ca,cb=st.columns(2)
    with ca:
        st.markdown("<div class='section-hdr'>CREATE ROOM</div>",unsafe_allow_html=True)
        st.markdown(f"<div style='font-family:var(--mono);font-size:.75rem;color:#3d5a73;margin-bottom:1rem;line-height:1.7'>"
                    f"{SYMBOLS_PER_GAME} stocks per game · ≥4 always Indian<br>{len(ALL_STOCKS)} companies across 🇮🇳 🇺🇸 🌏 🇨🇳 🇯🇵 🇩🇪 🇫🇷</div>",
                    unsafe_allow_html=True)
        if st.button("⚡  GENERATE ROOM",type="primary",use_container_width=True):
            code=create_room(user); join_room(code,user)
            st.session_state.room_code=code; st.session_state.is_admin=True; st.rerun()
    with cb:
        st.markdown("<div class='section-hdr'>JOIN ROOM</div>",unsafe_allow_html=True)
        with st.form("jf"):
            ci=st.text_input("Room Code",placeholder="ABC123").strip().upper()
            if st.form_submit_button("JOIN →",use_container_width=True,type="primary"):
                ok,msg=join_room(ci,user)
                if ok:
                    r=get_room(ci); st.session_state.room_code=ci
                    st.session_state.is_admin=(r or {}).get("admin")==user; st.rerun()
                else: st.error(msg)

    st.markdown("---")
    with st.expander(f"📊  FULL STOCK POOL  ·  {len(ALL_STOCKS)} companies"):
        tabs=st.tabs(["🇮🇳  India","🇺🇸  United States","🌏  Global"])
        regions=[{s:v for s,v in ALL_STOCKS.items() if "🇮🇳" in v[1]},
                 {s:v for s,v in ALL_STOCKS.items() if "🇺🇸" in v[1]},
                 {s:v for s,v in ALL_STOCKS.items() if "🇮🇳" not in v[1] and "🇺🇸" not in v[1]}]
        for tab,stocks in zip(tabs,regions):
            with tab:
                rows=[{"Ticker":dtick(s),"Company":v[0],"Sector":v[1]} for s,v in stocks.items()]
                st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True,height=280)
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("LOGOUT"):
        del st.session_state.user; st.rerun()

def show_game():
    code=st.session_state.room_code; user=st.session_state.user
    is_adm=st.session_state.get("is_admin",False)
    room=advance_tick(code)

    if room is None:
        st.error("⚠️ Room not found.")
        if st.button("← LOBBY",type="primary"): del st.session_state.room_code; st.session_state.pop("is_admin",None); st.rerun()
        return

    if user not in room["players"]:
        join_room(code,user); room=get_room(code)
        if room is None: st.error("Could not rejoin."); return

    new_inj=0
    if room["state"]=="running":
        new_inj=inject_cash(code,user)
        if new_inj>0: room=get_room(code)

    state=room["state"]; tick=room["current_tick"]
    gs=get_gs(room); sl=list(gs.keys()); prices=cur_prices(room)
    paths=room["price_paths"]; dates=room["day_dates"]
    players=room["players"]
    me=players.get(user,{"cash":0,"portfolio":{},"injections_given":0})
    elapsed=(time.time()-float(room["start_epoch"])) if room["start_epoch"] else 0
    remaining=max(0.,GAME_DURATION_SECS-elapsed)
    mkt_time=(datetime.now().replace(hour=9,minute=30,second=0,microsecond=0)+timedelta(minutes=tick)).strftime("%I:%M %p")
    sample_date=dates.get(sl[0],"?")
    MAX_INJ=int(GAME_DURATION_SECS//INJECTION_INTERVAL_SECS)+1
    inj_given=me.get("injections_given",0); inj_left=MAX_INJ-inj_given
    nxt_secs=next_inj(float(room["start_epoch"])) if room.get("start_epoch") else 0

    if new_inj>0: st.toast(f"💰 +${new_inj*CASH_INJECTION:,.0f} injected!",icon="💰")

    # SIDEBAR ─────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"<div style='border-bottom:1px solid #1e2d3d;padding-bottom:.6rem;margin-bottom:.7rem'>"
                    f"<div class='ta-logo' style='font-size:1rem'>⚡ TRADEARENA</div>"
                    f"<div style='font-family:var(--mono);font-size:.65rem;color:#3d5a73'>{user.upper()}</div></div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div style='font-family:var(--mono);font-size:.72rem;color:#7a9bb5;margin-bottom:.5rem'>"
                    f"ROOM &nbsp;<span style='color:#ffd740;font-size:.9rem;letter-spacing:.2em'>{code}</span></div>",
                    unsafe_allow_html=True)

        if state=="running":
            mins,secs=divmod(int(remaining),60)
            pct=remaining/GAME_DURATION_SECS
            tc="#00e676" if pct>.4 else ("#ffd740" if pct>.15 else "#ff3d57")
            st.markdown(f"<div class='timer-block' style='border-color:{tc}33'>"
                        f"<div class='timer-digits' style='color:{tc}'>{mins:02d}:{secs:02d}</div>"
                        f"<div class='timer-label'>remaining</div></div>",unsafe_allow_html=True)
            st.progress(remaining/GAME_DURATION_SECS)
            st.caption(f"📅 {sample_date}  ·  tick {tick}/390")
            st.markdown("<div class='section-hdr' style='margin-top:.7rem'>CASH INJECTIONS</div>",unsafe_allow_html=True)
            ic=st.columns(MAX_INJ)
            for i in range(MAX_INJ):
                with ic[i]:
                    recv=i<inj_given
                    c2="#00e676" if recv else "#1e2d3d"
                    st.markdown(f"<div style='height:4px;border-radius:2px;background:{c2};margin-bottom:2px'></div>"
                                f"<div style='font-family:var(--mono);font-size:.52rem;color:{'#00e676' if recv else '#3d5a73'};text-align:center'>$50k</div>",
                                unsafe_allow_html=True)
            if inj_left>0:
                ni_m,ni_s=divmod(int(nxt_secs),60)
                st.caption(f"⏳ next $50k in {ni_m:02d}:{ni_s:02d}")
            else: st.caption("✅ all received")

        elif state=="waiting":
            st.info("⏳ Waiting to start…")
            if is_adm:
                st.success(f"👥 {len(players)} player(s)")
                if st.button("▶️  START GAME",type="primary",use_container_width=True):
                    rooms=_load(ROOMS_FILE)
                    if code in rooms:
                        rooms[code]["state"]="running"; rooms[code]["start_epoch"]=time.time()
                        _save(ROOMS_FILE,rooms)
                    st.rerun()
        elif state=="finished": st.error("🏁 GAME OVER")

        st.markdown("<div class='section-hdr' style='margin-top:.7rem'>ACCOUNT</div>",unsafe_allow_html=True)
        p_val=pval(room,user); total_inj=inj_given*CASH_INJECTION; pnl_=p_val-total_inj
        c1,c2=st.columns(2)
        c1.metric("Value",f"${p_val/1000:.1f}k"); c2.metric("P&L",f"${pnl_/1000:+.1f}k")
        c1.metric("Cash",f"${me['cash']/1000:.1f}k"); c2.metric("Injected",f"${total_inj/1000:.0f}k")

        st.markdown("<div class='section-hdr' style='margin-top:.7rem'>STANDINGS</div>",unsafe_allow_html=True)
        medals=["🥇","🥈","🥉"]
        for i,row in enumerate(lb(room)):
            pnl_r=row["Value"]-row["CashIn"]
            clr="#00e676" if pnl_r>=0 else "#ff3d57"
            is_me=row["Player"]==user
            m=medals[i] if i<3 else f"{i+1}."
            st.markdown(f"<div class='lb-row {'me' if is_me else ''}'>"
                        f"<span>{m} <b style='color:var(--text)'>{row['Player'][:12]}</b></span>"
                        f"<span style='color:{clr};font-family:var(--mono);font-size:.75rem'>${row['Value']/1000:.1f}k</span>"
                        f"</div>",unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("← LEAVE",use_container_width=True):
            del st.session_state.room_code; st.session_state.is_admin=False; st.rerun()

    # HEADER ──────────────────────────────────────────────────────────────────
    h1,h2=st.columns([4,1])
    with h1:
        sc={"waiting":"#7a9bb5","running":"#00e676","finished":"#ff3d57"}.get(state,"#7a9bb5")
        sl_={"waiting":"⏸ WAITING","running":"● LIVE","finished":"■ FINISHED"}.get(state,"")
        st.markdown(f"<div style='display:flex;align-items:baseline;gap:1rem;margin-bottom:.15rem'>"
                    f"<span class='ta-logo' style='font-size:1.4rem'>⚡ TRADEARENA</span>"
                    f"<span style='font-family:var(--mono);font-size:.68rem;color:{sc};letter-spacing:.1em'>{sl_}</span>"
                    f"<span style='font-family:var(--mono);font-size:.72rem;color:#3d5a73'>{code}</span></div>"
                    f"<div style='font-family:var(--mono);font-size:.68rem;color:#3d5a73'>"
                    f"📅 {sample_date}  ·  ⏰ {mkt_time}  ·  👥 {len(players)}  ·  {DATA_START}→{DATA_END}</div>",
                    unsafe_allow_html=True)
    with h2:
        if state=="waiting":
            st.markdown(f"<div class='room-code'>{code}</div>",unsafe_allow_html=True)

    # INJECTION BANNER ────────────────────────────────────────────────────────
    if state=="running":
        if new_inj>0:
            st.markdown(f"<div class='inject-flash'>💰 +${new_inj*CASH_INJECTION:,.0f} CASH INJECTION  ·  {inj_given}/{MAX_INJ} RECEIVED</div>",
                        unsafe_allow_html=True)
        elif inj_left>0:
            ni_m,ni_s=divmod(int(nxt_secs),60)
            st.markdown(f"<div class='cash-banner'>💰 <b>${me['cash']:,.0f}</b> available  ·  "
                        f"Next +$50k in <b>{ni_m:02d}:{ni_s:02d}</b>  ·  "
                        f"{inj_given}/{MAX_INJ} received  ·  ${inj_left*CASH_INJECTION:,.0f} pending</div>",
                        unsafe_allow_html=True)

    # WAITING LOBBY ───────────────────────────────────────────────────────────
    if state=="waiting":
        st.markdown(f"""
        <div style='background:#0c1219;border:1px solid #1e2d3d;border-radius:10px;
                    padding:1.5rem;margin:1rem 0;text-align:center'>
          <div style='font-family:var(--mono);font-size:.68rem;color:#3d5a73;letter-spacing:.15em;margin-bottom:.4rem'>SHARE WITH FRIENDS</div>
          <div class='room-code'>{code}</div>
          <div style='font-family:var(--mono);font-size:.7rem;color:#3d5a73;margin-top:.4rem'>
            {len(players)} player(s) · {" · ".join(("👑 " if p==room["admin"] else "")+p for p in players)}
          </div>
        </div>""",unsafe_allow_html=True)
        inj_sched=" → ".join([f"t={i*2}m: $50k" for i in range(MAX_INJ)])
        st.markdown(f"<div style='font-family:var(--mono);font-size:.72rem;color:#1e6b4a;background:rgba(0,230,118,.04);"
                    f"border:1px solid rgba(0,230,118,.15);border-radius:6px;padding:.6rem 1rem;margin-bottom:1rem'>"
                    f"💰 {inj_sched} → TOTAL $250K</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='section-hdr'>THIS GAME'S {SYMBOLS_PER_GAME} STOCKS</div>",unsafe_allow_html=True)
        india_gs={s:v for s,v in gs.items() if "🇮🇳" in v[1]}
        other_gs={s:v for s,v in gs.items() if "🇮🇳" not in v[1]}
        def sgrid(syms):
            cols=st.columns(5)
            for i,(sym,(name,tag)) in enumerate(syms.items()):
                with cols[i%5]:
                    st.markdown(f"<div class='ticker-card'><div class='ticker-sym'>{dtick(sym)}</div>"
                                f"<div class='ticker-name'>{name}</div><div class='ticker-tag'>{tag}</div>"
                                f"<div style='font-family:var(--mono);font-size:.55rem;color:#1e6b4a'>📅 {dates.get(sym,'?')}</div></div>",
                                unsafe_allow_html=True)
        if india_gs: st.markdown("**🇮🇳 Indian**"); sgrid(india_gs)
        if other_gs: st.markdown("**🌐 Global & US**"); sgrid(other_gs)
        time.sleep(2); st.rerun(); return

    # GAME OVER ───────────────────────────────────────────────────────────────
    if state=="finished":
        board=lb(room)
        if board:
            st.balloons()
            w=board[0]; wpnl=w["Value"]-w["CashIn"]
            st.markdown(f"<div style='background:linear-gradient(135deg,rgba(255,215,64,.1),rgba(0,212,255,.04));"
                        f"border:1px solid #ffd74044;border-radius:10px;padding:1.2rem;text-align:center;margin:1rem 0'>"
                        f"<div style='font-family:var(--display);font-size:1.4rem;font-weight:700;color:#ffd740'>🏆 GAME OVER</div>"
                        f"<div style='font-family:var(--mono);font-size:.85rem;color:#7a9bb5;margin-top:.3rem'>"
                        f"WINNER: <b style='color:#ffd740'>{w['Player'].upper()}</b>"
                        f" · ${w['Value']:,.0f} · P&L <span style='color:{'#00e676' if wpnl>=0 else '#ff3d57'}'>${wpnl:+,.0f}</span>"
                        f"</div></div>",unsafe_allow_html=True)

    # TABS ────────────────────────────────────────────────────────────────────
    tmkt,tport,ttrade,tboard,thist=st.tabs(
        ["  📊 MARKET  ","  💼 PORTFOLIO  ","  ⚡ TRADE  ","  🏆 LEADERBOARD  ","  📜 HISTORY  "])

    # ── MARKET ───────────────────────────────────────────────────────────────
    with tmkt:
        india_gs={s:v for s,v in gs.items() if "🇮🇳" in v[1]}
        other_gs={s:v for s,v in gs.items() if "🇮🇳" not in v[1]}
        def render_grid(syms):
            cols=st.columns(5)
            for i,(sym,(name,tag)) in enumerate(syms.items()):
                with cols[i%5]:
                    pr=prices[sym]; op=paths[sym][0]; chg=pr-op
                    pct_c=(chg/op*100) if op else 0
                    d="up" if chg>=0 else "down"; arr="▲" if chg>=0 else "▼"
                    st.markdown(
                        f"<div class='ticker-card {d}'>"
                        f"<div style='display:flex;justify-content:space-between;align-items:flex-start'>"
                        f"<div><div class='ticker-sym'>{dtick(sym)}</div>"
                        f"<div class='ticker-name'>{name}</div>"
                        f"<div class='ticker-tag'>{tag}</div></div>"
                        f"<div style='text-align:right'>"
                        f"<div class='ticker-price {d}'>${pr:.2f}</div>"
                        f"<div class='ticker-chg {d}'>{arr} {pct_c:+.1f}%</div>"
                        f"</div></div></div>",unsafe_allow_html=True)
        if india_gs: st.markdown("<div class='section-hdr'>🇮🇳 INDIAN</div>",unsafe_allow_html=True); render_grid(india_gs)
        if other_gs: st.markdown("<div class='section-hdr' style='margin-top:1rem'>🌐 US & GLOBAL</div>",unsafe_allow_html=True); render_grid(other_gs)
        st.markdown("<br>",unsafe_allow_html=True)
        sel=st.selectbox("Chart",sl,key="mkt_sel",format_func=lambda s:f"{dtick(s)} — {gs[s][0]}")
        vis=paths[sel][:tick+1]
        taxs=[(datetime.now().replace(hour=9,minute=30,second=0)+timedelta(minutes=m)).strftime("%H:%M") for m in range(len(vis))]
        lc="#00e676" if vis[-1]>=vis[0] else "#ff3d57"
        fc="rgba(0,230,118,0.05)" if lc=="#00e676" else "rgba(255,61,87,0.05)"
        fig=go.Figure(); fig.add_trace(go.Scatter(x=taxs,y=vis,mode="lines",line=dict(color=lc,width=1.8),
            fill="tozeroy",fillcolor=fc,hovertemplate="<b>$%{y:.2f}</b><extra></extra>"))
        fig.add_hline(y=vis[0],line_dash="dot",line_color="#3d5a73",
                      annotation_text=f"OPEN  {vis[0]:.2f}",annotation_font=dict(family="IBM Plex Mono",size=9,color="#3d5a73"))
        fig.update_layout(**CLAYOUT,title=dict(text=f"{dtick(sel)} · {gs[sel][0]}  ·  {dates.get(sel,'')}",
                          font=dict(family="Chakra Petch",size=11,color="#7a9bb5"),x=0))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    # ── PORTFOLIO ─────────────────────────────────────────────────────────────
    with tport:
        pv=pval(room,user); ti=inj_given*CASH_INJECTION; pnl_t=pv-ti
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Value",f"${pv:,.0f}"); c2.metric("P&L",f"${pnl_t:+,.0f}",f"{(pnl_t/ti*100):+.1f}%" if ti else "—")
        c3.metric("Cash",f"${me['cash']:,.0f}"); c4.metric("Injected",f"${ti:,.0f} ({inj_given}/{MAX_INJ})")
        if me["portfolio"]:
            st.markdown("<div class='section-hdr' style='margin-top:1rem'>HOLDINGS</div>",unsafe_allow_html=True)
            rows=[]
            for sym,qty in me["portfolio"].items():
                pr=prices.get(sym,0); name=gs.get(sym,(sym,""))[0]
                buys=[t for t in room["trade_log"] if t["player"]==user and t["symbol"]==sym and t["action"]=="BUY"]
                avg=(sum(t["price"]*t["qty"] for t in buys)/sum(t["qty"] for t in buys)) if buys else pr
                val=pr*qty; pnl_s=val-avg*qty
                rows.append({"Ticker":dtick(sym),"Company":name,"Qty":qty,"Avg":f"${avg:.2f}",
                             "Price":f"${pr:.2f}","Value":f"${val:,.0f}","P&L":f"${pnl_s:+,.0f}",
                             "P&L%":f"{pnl_s/(avg*qty)*100:+.1f}%" if avg*qty else "—"})
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
            vals=[prices.get(s,0)*q for s,q in me["portfolio"].items()]
            lbls=[dtick(s) for s in me["portfolio"]]
            clrs=["#00d4ff","#00e676","#ffd740","#ff3d57","#a78bfa","#fb923c","#34d399","#f472b6","#60a5fa","#facc15"]
            fp=go.Figure(go.Pie(labels=lbls,values=vals,hole=.55,textinfo="label+percent",
                                marker=dict(colors=clrs[:len(vals)],line=dict(color="#060a0f",width=2))))
            fp.update_layout(height=260,margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor="rgba(0,0,0,0)",
                             legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#7a9bb5",size=9)),font=dict(family="IBM Plex Mono"))
            st.plotly_chart(fp,use_container_width=True,config={"displayModeBar":False})
        else: st.info("No holdings yet — head to ⚡ TRADE.")

    # ── TRADE ─────────────────────────────────────────────────────────────────
    with ttrade:
        if state=="finished": st.warning("🏁 Trading closed.")
        else:
            if inj_left>0:
                ni_m,ni_s=divmod(int(nxt_secs),60)
                st.markdown(f"<div class='cash-banner' style='margin-bottom:.8rem'>"
                            f"💰 <b>${me['cash']:,.0f}</b> available  ·  Next +$50k in <b>{ni_m:02d}:{ni_s:02d}</b></div>",
                            unsafe_allow_html=True)
        left,right=st.columns([3,2])
        with left:
            sym=st.selectbox("Stock",sl,key="trade_sym",
                             format_func=lambda s:f"{dtick(s)} — {gs[s][0]} {gs[s][1]}")
            pr=prices[sym]; name,tag=gs[sym]; owned=me["portfolio"].get(sym,0)
            spark=paths[sym][:tick+1]; cs="#00e676" if spark[-1]>=spark[0] else "#ff3d57"
            chg_s=spark[-1]-spark[0]; pct_s=(chg_s/spark[0]*100) if spark[0] else 0
            st.markdown(
                f"<div style='background:#0c1219;border:1px solid #1e2d3d;border-radius:10px;padding:1rem;margin:.4rem 0'>"
                f"<div style='display:flex;justify-content:space-between;align-items:flex-end'>"
                f"<div><div style='font-family:var(--mono);font-size:.6rem;color:#3d5a73;letter-spacing:.1em'>{tag}</div>"
                f"<div style='font-family:var(--display);font-weight:700;font-size:.95rem;color:#e0eaf4'>{name}</div>"
                f"<div style='font-family:var(--mono);font-size:1.9rem;font-weight:700;color:{cs}'>${pr:.2f}</div></div>"
                f"<div style='text-align:right'>"
                f"<div style='font-family:var(--mono);font-size:.82rem;color:{cs}'>{'▲' if chg_s>=0 else '▼'} {pct_s:+.2f}%</div>"
                f"<div style='font-family:var(--mono);font-size:.68rem;color:#3d5a73'>held: {owned}</div>"
                f"<div style='font-family:var(--mono);font-size:.65rem;color:#3d5a73'>📅 {dates.get(sym,'')}</div>"
                f"</div></div></div>",unsafe_allow_html=True)
            fspark=go.Figure(go.Scatter(y=spark,mode="lines",line=dict(color=cs,width=1.7),
                             fill="tozeroy",fillcolor=f"{'rgba(0,230,118,0.04)' if cs=='#00e676' else 'rgba(255,61,87,0.04)'}"))
            fspark.update_layout(height=100,margin=dict(l=0,r=0,t=0,b=0),xaxis=dict(visible=False),
                                 yaxis=dict(visible=False),plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fspark,use_container_width=True,config={"displayModeBar":False})

        with right:
            st.markdown("<div class='section-hdr'>ORDER</div>",unsafe_allow_html=True)
            qty=st.number_input("Shares",min_value=1,value=10,step=1,key="tqty")
            tc=pr*qty; can_buy=tc<=me["cash"] and state=="running"; can_sell=owned>=qty and state=="running"
            st.markdown(
                f"<div style='background:#0c1219;border:1px solid #1e2d3d;border-radius:8px;padding:.75rem;margin:.4rem 0'>"
                f"<div style='display:flex;justify-content:space-between;font-family:var(--mono);font-size:.76rem'>"
                f"<span style='color:#3d5a73'>ORDER</span><span style='color:#e0eaf4;font-weight:600'>${tc:,.2f}</span></div>"
                f"<div style='display:flex;justify-content:space-between;font-family:var(--mono);font-size:.76rem;margin-top:.25rem'>"
                f"<span style='color:#3d5a73'>AVAILABLE</span><span style='color:#e0eaf4'>${me['cash']:,.0f}</span></div></div>",
                unsafe_allow_html=True)
            st.markdown("""<style>
            div[data-testid="stButton"]>button[kind="primary"]{
              background:linear-gradient(135deg,rgba(0,230,118,.17),rgba(0,230,118,.07))!important;
              border:1.5px solid #00e676!important;color:#00e676!important;
              font-family:'Chakra Petch',sans-serif!important;font-weight:700!important;
              letter-spacing:.1em!important;height:3rem!important;}
            div[data-testid="stButton"]>button[kind="secondary"]{
              background:linear-gradient(135deg,rgba(255,61,87,.17),rgba(255,61,87,.07))!important;
              border:1.5px solid #ff3d57!important;color:#ff3d57!important;
              font-family:'Chakra Petch',sans-serif!important;font-weight:700!important;
              letter-spacing:.1em!important;height:3rem!important;}
            </style>""",unsafe_allow_html=True)
            if st.button(f"▲ BUY  {qty}",use_container_width=True,type="primary",disabled=not can_buy):
                ok,msg=do_trade(code,user,sym,qty,"BUY")
                st.toast(msg,icon="✅" if ok else "❌")
                if not ok: st.error(msg)
                time.sleep(.4); st.rerun()
            if st.button(f"▼ SELL  {qty}",use_container_width=True,type="secondary",disabled=not can_sell):
                ok,msg=do_trade(code,user,sym,qty,"SELL")
                st.toast(msg,icon="💰" if ok else "❌")
                if not ok: st.error(msg)
                time.sleep(.4); st.rerun()
            if not can_buy and state=="running":
                ni_m,ni_s=divmod(int(nxt_secs),60)
                st.caption(f"⚠️ need ${tc-me['cash']:,.0f} more · +$50k in {ni_m:02d}:{ni_s:02d}")

    # ── LEADERBOARD ───────────────────────────────────────────────────────────
    with tboard:
        board=lb(room)
        st.markdown("<div class='section-hdr'>STANDINGS</div>",unsafe_allow_html=True)
        medals=["🥇","🥈","🥉"]
        for i,row in enumerate(board):
            pnl_r=row["Value"]-row["CashIn"]; clr="#00e676" if pnl_r>=0 else "#ff3d57"
            is_me=row["Player"]==user; m=medals[i] if i<3 else f"{i+1}."
            bar=(row["Value"]/board[0]["Value"]*100) if board else 0
            st.markdown(
                f"<div class='lb-row {'me' if is_me else ''}' style='margin-bottom:.4rem'>"
                f"<div style='display:flex;align-items:center;gap:.6rem'><span style='font-size:.95rem'>{m}</span>"
                f"<div><div style='font-family:var(--display);font-size:.88rem;color:var(--text);font-weight:600'>{row['Player']}</div>"
                f"<div style='background:#1e2d3d;height:3px;border-radius:2px;width:110px;margin-top:3px'>"
                f"<div style='background:{clr};height:100%;width:{bar:.0f}%;border-radius:2px'></div></div></div></div>"
                f"<div style='text-align:right'>"
                f"<div style='font-family:var(--mono);font-weight:700;color:#e0eaf4'>${row['Value']:,.0f}</div>"
                f"<div style='font-family:var(--mono);font-size:.7rem;color:{clr}'>{'+' if pnl_r>=0 else ''}{pnl_r:,.0f}</div>"
                f"</div></div>",unsafe_allow_html=True)
        raw=lb(room)
        fig_lb=go.Figure(go.Bar(
            x=[r["Player"] for r in raw],y=[r["Value"] for r in raw],
            marker_color=["#00e676" if r["Value"]-r["CashIn"]>=0 else "#ff3d57" for r in raw],
            marker_line_width=0,
            text=[f"${r['Value']/1000:.1f}k" for r in raw],textposition="outside",
            textfont=dict(family="IBM Plex Mono",size=9,color="#7a9bb5")))
        fig_lb.update_layout(height=240,plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                             yaxis=dict(gridcolor="rgba(30,45,61,.7)",tickprefix="$",color="#3d5a73",tickfont=dict(family="IBM Plex Mono",size=9)),
                             xaxis=dict(color="#3d5a73",tickfont=dict(family="Chakra Petch",size=10)),
                             margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig_lb,use_container_width=True,config={"displayModeBar":False})

    # ── HISTORY ───────────────────────────────────────────────────────────────
    with thist:
        my_t=[t for t in room["trade_log"] if t["player"]==user]
        real=[t for t in my_t if t["action"]!="CASH_IN"]
        ce=[t for t in my_t if t["action"]=="CASH_IN"]
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Trades",len(real)); c2.metric("Buys",sum(1 for t in real if t["action"]=="BUY"))
        c3.metric("Sells",sum(1 for t in real if t["action"]=="SELL")); c4.metric("Cash Events",f"{len(ce)} × $50k")
        if my_t:
            st.markdown("<div class='section-hdr' style='margin-top:.8rem'>TRADE LOG</div>",unsafe_allow_html=True)
            df_h=pd.DataFrame(my_t)[["time","symbol","action","qty","price","total"]]
            df_h["Ticker"]=df_h["symbol"].map(lambda s:dtick(s) if s!="—" else "💰 CASH")
            df_h["Company"]=df_h["symbol"].map(lambda s:gs.get(s,(s,""))[0] if s!="—" else "Cash Injection")
            df_h["Type"]=df_h["action"].map({"BUY":"▲ BUY","SELL":"▼ SELL","CASH_IN":"💰 INJECT"})
            df_h["Time"]=pd.to_datetime(df_h["time"]).dt.strftime("%H:%M:%S")
            df_h["Price"]=df_h["price"].apply(lambda x:f"${x:,.2f}")
            df_h["Total"]=df_h["total"].apply(lambda x:f"${x:,.0f}")
            st.dataframe(df_h[["Time","Ticker","Company","Type","qty","Price","Total"]].rename(columns={"qty":"Qty"})[::-1],
                         use_container_width=True,hide_index=True)
        else: st.info("No activity yet.")

    if state=="running":
        time.sleep(max(.8,TICK_REAL_SECS*.75)); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
if "user" not in st.session_state: show_auth()
elif "room_code" not in st.session_state: show_lobby()
else: show_game()