import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quantitative Market Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background-color: #080c14; color: #e2e8f0; }
.main .block-container { padding: 1.5rem 2.5rem 2rem; max-width: 1600px; }

/* Header */
.dash-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 1.6rem 2rem 1.4rem;
    margin-bottom: 1.6rem;
    position: relative; overflow: hidden;
}
.dash-header::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #1d4ed8, #7c3aed, #0ea5e9);
}
.dash-title   { font-size: 22px; font-weight: 700; color: #f1f5f9; letter-spacing: -.3px; margin: 0 0 4px; }
.dash-subtitle{ font-size: 13px; color: #64748b; font-weight: 400; letter-spacing: .3px; margin: 0; }

/* Metrics */
[data-testid="metric-container"] {
    background: #0f1929; border: 1px solid #1e3a5f; border-radius: 10px;
    padding: .85rem 1rem; transition: border-color .2s;
}
[data-testid="metric-container"]:hover { border-color: #2d5f9e; }
[data-testid="metric-container"] label {
    color: #64748b !important; font-size: 11px !important;
    font-weight: 500 !important; letter-spacing: .6px !important; text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="metric-value"] {
    color: #f1f5f9 !important; font-size: 20px !important; font-weight: 700 !important;
}
[data-testid="metric-container"] [data-testid="metric-delta"] { font-size: 12px !important; font-weight: 500 !important; }

/* Inputs */
.stTextInput > div > div > input {
    background: #0f1929; border: 1px solid #1e3a5f; color: #e2e8f0;
    border-radius: 8px; font-size: 14px; font-weight: 500;
}
.stTextInput > div > div > input:focus { border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37,99,235,.25); }
.stTextInput label { color: #64748b !important; font-size: 11px !important; font-weight: 500 !important; letter-spacing: .5px; text-transform: uppercase; }
.stSelectbox > div > div { background: #0f1929; border: 1px solid #1e3a5f; border-radius: 8px; color: #e2e8f0; }
.stSelectbox label { color: #64748b !important; font-size: 11px !important; font-weight: 500 !important; letter-spacing: .5px; text-transform: uppercase; }

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb); color: white; border: none;
    border-radius: 8px; padding: .5rem 1.8rem; font-weight: 600; font-size: 14px;
    letter-spacing: .3px; transition: all .2s; margin-top: 1.6rem;
}
.stButton > button:hover { background: linear-gradient(135deg, #2563eb, #3b82f6); transform: translateY(-1px); }

/* Section headers */
.section-header {
    font-size: 11px; font-weight: 600; color: #475569; letter-spacing: 1.2px;
    text-transform: uppercase; margin: 1.4rem 0 .6rem;
    padding-bottom: 6px; border-bottom: 1px solid #1e293b;
}

/* Insight box */
.insight-box {
    background: #0c1628; border-left: 3px solid #2563eb;
    border-radius: 0 8px 8px 0; padding: .9rem 1.2rem; margin: .6rem 0 1rem;
}
.insight-box p { color: #94a3b8; font-size: 13px; line-height: 1.65; margin: 0; }
.insight-box strong { color: #cbd5e1; }

/* What This Means */
.wtm-card {
    background: linear-gradient(135deg, #0f1f3d 0%, #0f1929 100%);
    border: 1px solid #1e3a5f; border-radius: 14px;
    padding: 1.4rem 1.6rem; margin: 1rem 0;
}
.wtm-title { font-size: 11px; font-weight: 600; color: #475569; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; }
.wtm-text  { font-size: 14px; color: #cbd5e1; line-height: 1.8; }
.wtm-text span.bull { color: #4ade80; font-weight: 600; }
.wtm-text span.bear { color: #f87171; font-weight: 600; }
.wtm-text span.neut { color: #fbbf24; font-weight: 600; }
.wtm-text span.hi   { color: #e2e8f0; font-weight: 600; }

/* Regime / risk badges */
.regime-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 14px; border-radius: 20px; font-weight: 600; font-size: 13px; letter-spacing: .3px;
}
.regime-bull { background:#052e16; color:#4ade80; border:1px solid #166534; }
.regime-bear { background:#450a0a; color:#f87171; border:1px solid #991b1b; }
.regime-side { background:#1c1a07; color:#fbbf24; border:1px solid #92400e; }
.risk-high   { background:#450a0a; color:#f87171; border:1px solid #991b1b; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600; }
.risk-mod    { background:#1c1a07; color:#fbbf24; border:1px solid #92400e; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600; }
.risk-low    { background:#052e16; color:#4ade80; border:1px solid #166534; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600; }

/* Score card */
.score-outer { background:#0f1929; border:1px solid #1e3a5f; border-radius:12px; padding:1.2rem; text-align:center; height:100%; }
.score-label { font-size:10px; color:#64748b; font-weight:600; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px; }
.score-value { font-size:38px; font-weight:800; line-height:1; margin:4px 0; }
.score-sub   { font-size:12px; font-weight:500; margin-top:4px; }
.score-bar-bg { background:#1e293b; border-radius:4px; height:6px; margin-top:10px; overflow:hidden; }
.score-bar-fill { height:6px; border-radius:4px; }

/* Summary card */
.summary-card { background:#0f1929; border:1px solid #1e3a5f; border-radius:12px; padding:1.3rem 1.5rem; }
.summary-row  { display:flex; justify-content:space-between; align-items:center; padding:7px 0; border-bottom:1px solid #1e293b; }
.summary-row:last-child { border-bottom:none; }
.summary-key  { font-size:12px; color:#64748b; font-weight:500; }
.summary-val  { font-size:13px; color:#e2e8f0; font-weight:600; }

/* Corr card */
.corr-card   { background:#0f1929; border:1px solid #1e3a5f; border-radius:12px; padding:1.3rem 1.5rem; text-align:center; }
.corr-value  { font-size:40px; font-weight:800; line-height:1.1; }
.corr-label  { font-size:11px; color:#64748b; font-weight:500; margin-top:4px; }
.corr-desc   { font-size:12px; font-weight:500; margin-top:6px; }

/* Expander */
.streamlit-expanderHeader { color: #475569 !important; font-size: 12px !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background:#0f1929; border-radius:10px; padding:4px; gap:2px; border:1px solid #1e3a5f; }
.stTabs [data-baseweb="tab"]      { background:transparent; color:#64748b; border-radius:8px; font-size:13px; font-weight:500; padding:6px 16px; }
.stTabs [aria-selected="true"]    { background:#1e3a5f !important; color:#e2e8f0 !important; }

hr { border-color: #1e293b !important; margin: 1.2rem 0 !important; }
.footer-note { color:#334155; font-size:11px; margin-top:2rem; text-align:center; }
h1, h2, h3, h4 { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
BLUE   = "#3b82f6"
ORANGE = "#f97316"
PURPLE = "#a78bfa"
GREEN  = "#4ade80"
RED    = "#f87171"
YELLOW = "#fbbf24"
TEAL   = "#2dd4bf"
DARK_BG   = "#080c14"
DARK_CARD = "#0f1929"
GRID_COL  = "#1e293b"
LABEL_COL = "#94a3b8"
TEXT_COL  = "#e2e8f0"

PLOTLY_LAYOUT = dict(
    paper_bgcolor=DARK_BG, plot_bgcolor=DARK_CARD,
    font=dict(family="Inter, sans-serif", color=LABEL_COL, size=11),
    xaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, tickfont=dict(color=LABEL_COL, size=10), showgrid=True, gridwidth=1),
    yaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, tickfont=dict(color=LABEL_COL, size=10), showgrid=True, gridwidth=1),
    margin=dict(l=50, r=20, t=50, b=40),
    legend=dict(bgcolor="rgba(15,25,41,0.9)", bordercolor=GRID_COL, borderwidth=1,
                font=dict(color=TEXT_COL, size=10)),
    hoverlabel=dict(bgcolor="#1e293b", bordercolor=GRID_COL, font=dict(color=TEXT_COL, size=12)),
)

TIMEFRAME_MAP = {
    "1 Month": 30, "3 Months": 90, "6 Months": 180, "1 Year": 365, "5 Years": 1825,
}

# ── Metric tooltip definitions ────────────────────────────────────────────────
TOOLTIPS = {
    "price":    "The most recent closing price of the asset. This is the last traded price at market close.",
    "ma20":     "20-Day Moving Average: the average closing price over the last 20 trading days. When price is above MA20, short-term momentum is positive. A rising MA20 suggests an uptrend.",
    "ma50":     "50-Day Moving Average: the average closing price over the last 50 trading days. Acts as a key medium-term support/resistance level. Price above MA50 is generally considered bullish.",
    "avg_ret":  "Average Daily Return: the mean percentage gain or loss per trading day over the selected period. Positive values indicate the asset has been trending upward on average.",
    "ann_vol":  "Annualised Volatility: how much the asset's price fluctuates, scaled to a yearly figure. Higher volatility means larger price swings and more risk. Under 20% is low; over 40% is high.",
    "period_ret":"Total price return over the selected timeframe. Shows how much your investment would have grown (or shrunk) if held for the entire period.",
    "sentiment":"Sentiment Score (0–100): a composite signal built from moving averages, momentum, volatility, RSI, and recent returns. Above 60 = bullish conditions. Below 40 = bearish conditions. 40–60 = neutral.",
    "trend":    "Trend direction based on the relationship between price, MA20, and MA50. Bullish: price > MA20 > MA50. Bearish: price < MA20 < MA50. Sideways: mixed signals.",
    "momentum": "20-Day Momentum: the percentage price change over the past 20 trading days. Positive momentum suggests the asset has been rising recently; negative suggests it has been falling.",
    "corr":     "Pearson Correlation Coefficient (−1 to +1): measures how closely two assets move together. +1 = perfect sync, −1 = perfect opposite, 0 = no relationship. Useful for portfolio diversification.",
    "risk":     "Risk Level based on annualised volatility. Low (<20%): stable, predictable moves. Moderate (20–45%): typical market risk. High (>45%): large swings, elevated uncertainty.",
    "vol":      "Volatility category derived from annualised rolling volatility. Low (<20%) assets tend to be less risky; high volatility (>45%) assets can move dramatically in short periods.",
}

# ── Data & indicators ─────────────────────────────────────────────────────────
def fetch_data(ticker: str, period_days: int = 365) -> pd.DataFrame:
    end = datetime.today()
    start = end - timedelta(days=period_days)
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if df.empty:
        return pd.DataFrame()
    close = df["Close"]
    vol   = df["Volume"]
    if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
    if isinstance(vol,   pd.DataFrame): vol   = vol.iloc[:, 0]
    return pd.DataFrame({"Close": close, "Volume": vol}).dropna()

def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["MA20"]     = df["Close"].rolling(20).mean()
    df["MA50"]     = df["Close"].rolling(50).mean()
    df["Returns"]  = df["Close"].pct_change()
    df["RolVol"]   = df["Returns"].rolling(20).std() * np.sqrt(252)
    df["Momentum"] = df["Close"].pct_change(20)
    df["RSI"]      = _rsi(df["Close"])
    df["BB_mid"]   = df["Close"].rolling(20).mean()
    df["BB_std"]   = df["Close"].rolling(20).std()
    df["BB_upper"] = df["BB_mid"] + 2 * df["BB_std"]
    df["BB_lower"] = df["BB_mid"] - 2 * df["BB_std"]
    return df

def classify_regime(df: pd.DataFrame) -> dict:
    last  = df.dropna().iloc[-1]
    price = float(last["Close"])
    ma20  = float(last["MA20"])
    ma50  = float(last["MA50"])
    vol   = float(last["RolVol"])
    mom   = float(last["Momentum"])

    trend = ("Bullish" if price > ma20 and ma20 > ma50
             else "Bearish" if price < ma20 and ma20 < ma50
             else "Sideways")

    if vol > 0.45:   vol_label, risk = "High",     "High"
    elif vol > 0.20: vol_label, risk = "Moderate", "Moderate"
    else:            vol_label, risk = "Low",       "Low"

    if trend == "Bearish" and vol_label == "High":   risk = "High"
    elif trend == "Bullish" and vol_label == "Low":  risk = "Low"

    mom_label = "Positive" if mom > 0.03 else ("Negative" if mom < -0.03 else "Neutral")

    return {
        "trend": trend, "vol_label": vol_label, "momentum": mom_label,
        "risk": risk, "price": price, "ma20": ma20, "ma50": ma50, "vol": vol,
        "daily_return_avg": float(df["Returns"].mean()),
        "regime": f"{trend} · {vol_label} Volatility",
        "rsi": float(last["RSI"]) if not np.isnan(last["RSI"]) else 50,
    }

def compute_sentiment(df: pd.DataFrame) -> int:
    last  = df.dropna().iloc[-1]
    price = float(last["Close"]); ma20 = float(last["MA20"]); ma50 = float(last["MA50"])
    vol   = float(last["RolVol"]); mom = float(last["Momentum"])
    rsi   = float(last["RSI"]) if not np.isnan(last["RSI"]) else 50
    score = 50
    if price > ma20 and ma20 > ma50:   score += 15
    elif price < ma20 and ma20 < ma50: score -= 15
    elif price > ma20: score += 5
    elif price < ma20: score -= 5
    score += float(np.clip(mom * 100, -15, 15))
    if vol > 0.55: score -= 10
    elif vol > 0.35: score -= 6
    elif vol > 0.18: score -= 2
    if rsi > 70: score -= 5
    elif rsi > 55: score += 7
    elif rsi > 45: score += 3
    elif rsi < 30: score += 5
    elif rsi < 45: score -= 7
    if len(df) >= 6:
        score += float(np.clip((float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-6]) - 1) * 100, -10, 10))
    return int(np.clip(round(score), 0, 100))

def compute_correlation(df1, df2):
    r1 = df1["Close"].pct_change().dropna()
    r2 = df2["Close"].pct_change().dropna()
    aligned = pd.concat([r1, r2], axis=1, join="inner").dropna()
    aligned.columns = ["r1", "r2"]
    return float(aligned["r1"].corr(aligned["r2"])), aligned["r1"], aligned["r2"]

# ── Natural language interpretation ──────────────────────────────────────────
def generate_interpretation(info: dict, df: pd.DataFrame, ticker: str, score: int, timeframe: str) -> str:
    trend     = info["trend"]
    vol_label = info["vol_label"]
    mom       = info["momentum"]
    risk      = info["risk"]
    ma20      = info["ma20"]
    ma50      = info["ma50"]
    price     = info["price"]
    rsi       = info["rsi"]
    period_ret = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[0]) - 1) * 100

    trend_tag = "bull" if trend == "Bullish" else ("bear" if trend == "Bearish" else "neut")
    risk_tag  = "bear" if risk == "High" else ("neut" if risk == "Moderate" else "bull")

    parts = []

    # Trend sentence
    if trend == "Bullish":
        parts.append(f'<span class="bull">📈 {ticker} is in a bullish trend</span>, trading above both its 20-day (${ma20:,.2f}) and 50-day (${ma50:,.2f}) moving averages.')
    elif trend == "Bearish":
        parts.append(f'<span class="bear">📉 {ticker} is in a bearish trend</span>, trading below both its 20-day (${ma20:,.2f}) and 50-day (${ma50:,.2f}) moving averages.')
    else:
        parts.append(f'<span class="neut">↔ {ticker} is moving sideways</span>, with mixed signals between its 20-day and 50-day moving averages, suggesting indecision in the market.')

    # MA cross
    if ma20 > ma50:
        parts.append('The MA20 is above the MA50 — a <span class="bull">golden cross</span>, which historically signals continued upside.')
    else:
        parts.append('The MA20 has crossed below the MA50 — a <span class="bear">death cross</span>, which is often seen as a bearish warning sign.')

    # Momentum
    if mom == "Positive":
        parts.append(f'<span class="bull">Momentum is positive</span> over the past 20 days, reinforcing the upward move.')
    elif mom == "Negative":
        parts.append(f'<span class="bear">Momentum is negative</span> over the past 20 days, adding downside pressure.')
    else:
        parts.append('Momentum is <span class="neut">neutral</span> — no strong directional push in either direction recently.')

    # Volatility / Risk
    if vol_label == "High":
        parts.append(f'Annualised volatility is <span class="bear">elevated at {info["vol"]*100:.1f}%</span>, meaning price swings are large — this environment carries <span class="bear">higher risk</span>.')
    elif vol_label == "Moderate":
        parts.append(f'Volatility is at a <span class="neut">moderate {info["vol"]*100:.1f}%</span> annually — typical market conditions with manageable risk.')
    else:
        parts.append(f'Volatility is <span class="bull">low at {info["vol"]*100:.1f}%</span> annually, suggesting a calm and stable price environment.')

    # RSI
    if rsi > 70:
        parts.append(f'The RSI stands at <span class="bear">{rsi:.0f} — overbought territory</span>. A pullback or consolidation may be near.')
    elif rsi < 30:
        parts.append(f'The RSI is at <span class="bull">{rsi:.0f} — oversold territory</span>. This sometimes precedes a recovery bounce.')
    else:
        parts.append(f'The RSI is at <span class="neut">{rsi:.0f}</span>, within a neutral range — no extreme conditions detected.')

    # Period return
    ret_tag = "bull" if period_ret > 0 else "bear"
    parts.append(f'Over the selected {timeframe} window, {ticker} has returned <span class="{ret_tag}">{period_ret:+.1f}%</span>.')

    # Sentiment summary
    if score >= 65:
        parts.append(f'Overall sentiment score of <span class="bull">{score}/100</span> indicates <span class="bull">bullish conditions</span>.')
    elif score >= 40:
        parts.append(f'Overall sentiment score of <span class="neut">{score}/100</span> suggests <span class="neut">neutral market conditions</span> — wait for clearer signals.')
    else:
        parts.append(f'Overall sentiment score of <span class="bear">{score}/100</span> signals <span class="bear">bearish conditions</span> — proceed with caution.')

    return " ".join(parts)

def generate_corr_interpretation(t1: str, t2: str, corr: float) -> str:
    a = abs(corr)
    direction = "move in the <span class='bull'>same direction</span>" if corr >= 0 else "move in <span class='bear'>opposite directions</span>"
    if a >= 0.85:
        strength = "very strongly correlated"
    elif a >= 0.65:
        strength = "strongly correlated"
    elif a >= 0.40:
        strength = "moderately correlated"
    elif a >= 0.20:
        strength = "weakly correlated"
    else:
        return f"<span class='hi'>{t1}</span> and <span class='hi'>{t2}</span> show <span class='neut'>no meaningful correlation</span>. They behave largely independently — holding both may provide meaningful diversification."

    if corr >= 0.65:
        diversification = "Holding both assets together <span class='bear'>may not provide much diversification</span> since they tend to rise and fall together."
    elif corr <= -0.65:
        diversification = "Holding both together <span class='bull'>may reduce portfolio risk</span>, as they tend to offset each other."
    else:
        diversification = "There is <span class='neut'>some diversification benefit</span> to holding both assets together."

    return (f"<span class='hi'>{t1}</span> and <span class='hi'>{t2}</span> are <span class='neut'>{strength}</span> "
            f"(ρ = {corr:+.3f}) and tend to {direction}. {diversification}")

# ── Chart helpers ─────────────────────────────────────────────────────────────
def _apply_layout(fig, title: str, yaxis_title: str = "", height: int = 380):
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=title, font=dict(color=TEXT_COL, size=13, family="Inter"), x=0, pad=dict(l=4)),
        yaxis_title=yaxis_title,
        height=height,
        hovermode="x unified",
    )
    fig.update_xaxes(showspikes=True, spikecolor=GRID_COL, spikethickness=1, spikedash="dot")
    fig.update_yaxes(showspikes=False)
    return fig

def plot_price_ma(df: pd.DataFrame, ticker: str, color: str = BLUE) -> go.Figure:
    fig = go.Figure()

    # Bollinger band fill
    fig.add_trace(go.Scatter(
        x=list(df.index) + list(df.index[::-1]),
        y=list(df["BB_upper"]) + list(df["BB_lower"][::-1]),
        fill="toself", fillcolor="rgba(59,130,246,0.05)",
        line=dict(color="rgba(0,0,0,0)"), showlegend=True, name="Bollinger Band",
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_upper"], line=dict(color="rgba(59,130,246,0.25)", width=1, dash="dot"),
        showlegend=False, name="BB Upper", hovertemplate="BB Upper: $%{y:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_lower"], line=dict(color="rgba(59,130,246,0.25)", width=1, dash="dot"),
        showlegend=False, name="BB Lower", hovertemplate="BB Lower: $%{y:,.2f}<extra></extra>",
    ))

    # MA lines
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MA50"], line=dict(color=PURPLE, width=1.5, dash="dash"),
        name="MA 50", hovertemplate="MA50: $%{y:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MA20"], line=dict(color=ORANGE, width=1.5, dash="dash"),
        name="MA 20", hovertemplate="MA20: $%{y:,.2f}<extra></extra>",
    ))

    # Price line
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"], line=dict(color=color, width=2.2),
        name="Price", hovertemplate="<b>%{x|%b %d, %Y}</b><br>Price: $%{y:,.2f}<extra></extra>",
    ))

    # Crossover markers
    cross_up   = df[(df["MA20"].shift(1) <= df["MA50"].shift(1)) & (df["MA20"] > df["MA50"])]
    cross_down = df[(df["MA20"].shift(1) >= df["MA50"].shift(1)) & (df["MA20"] < df["MA50"])]
    if not cross_up.empty:
        fig.add_trace(go.Scatter(
            x=cross_up.index, y=cross_up["MA20"],
            mode="markers", marker=dict(symbol="triangle-up", color=GREEN, size=12, line=dict(color="white", width=1)),
            name="Golden Cross ↑", hovertemplate="Golden Cross<br>%{x|%b %d, %Y}<extra></extra>",
        ))
    if not cross_down.empty:
        fig.add_trace(go.Scatter(
            x=cross_down.index, y=cross_down["MA20"],
            mode="markers", marker=dict(symbol="triangle-down", color=RED, size=12, line=dict(color="white", width=1)),
            name="Death Cross ↓", hovertemplate="Death Cross<br>%{x|%b %d, %Y}<extra></extra>",
        ))

    return _apply_layout(fig,
        title=f"<b>{ticker}</b>  ·  Price & Trend Analysis  —  MA20, MA50 & Bollinger Bands",
        yaxis_title="Price (USD)", height=420)

def plot_volatility(df: pd.DataFrame, ticker: str) -> go.Figure:
    vol = df["RolVol"].dropna() * 100
    fig = go.Figure()
    fig.add_hrect(y0=0,  y1=20, fillcolor="rgba(74,222,128,0.04)", line_width=0, annotation_text="Low Risk", annotation_position="right", annotation_font=dict(color=GREEN, size=9))
    fig.add_hrect(y0=20, y1=45, fillcolor="rgba(251,191,36,0.04)", line_width=0, annotation_text="Moderate", annotation_position="right", annotation_font=dict(color=YELLOW, size=9))
    fig.add_hrect(y0=45, y1=200,fillcolor="rgba(248,113,113,0.04)", line_width=0, annotation_text="High Risk", annotation_position="right", annotation_font=dict(color=RED, size=9))
    fig.add_trace(go.Scatter(
        x=vol.index, y=vol, fill="tozeroy", fillcolor="rgba(248,113,113,0.15)",
        line=dict(color=RED, width=2), name="Volatility",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Volatility: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=45, line=dict(color=RED,    width=1, dash="dot"), annotation_text="High threshold (45%)",  annotation_font=dict(color=RED, size=9))
    fig.add_hline(y=20, line=dict(color=GREEN,  width=1, dash="dot"), annotation_text="Low threshold (20%)",   annotation_font=dict(color=GREEN, size=9))
    return _apply_layout(fig,
        title=f"<b>{ticker}</b>  ·  Rolling Volatility Analysis  —  20-Day Ann. Volatility (%)",
        yaxis_title="Volatility %", height=320)

def plot_returns(df: pd.DataFrame, ticker: str) -> go.Figure:
    ret = df["Returns"].dropna() * 100
    colors = [GREEN if v >= 0 else RED for v in ret]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ret.index, y=ret, marker_color=colors, name="Daily Return",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Return: %{y:+.2f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line=dict(color=LABEL_COL, width=0.8))
    avg = float(ret.mean())
    fig.add_hline(y=avg, line=dict(color=TEAL, width=1.2, dash="dash"),
                  annotation_text=f"Avg {avg:+.2f}%", annotation_font=dict(color=TEAL, size=9))
    return _apply_layout(fig,
        title=f"<b>{ticker}</b>  ·  Daily Return Distribution  —  Green = Gain, Red = Loss",
        yaxis_title="Return %", height=300)

def plot_rsi(df: pd.DataFrame, ticker: str) -> go.Figure:
    rsi = df["RSI"].dropna()
    fig = go.Figure()
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(248,113,113,0.08)", line_width=0)
    fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(74,222,128,0.08)",  line_width=0)
    fig.add_trace(go.Scatter(
        x=rsi.index, y=rsi, line=dict(color=TEAL, width=2), name="RSI",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>RSI: %{y:.1f}<extra></extra>",
    ))
    fig.add_hline(y=70, line=dict(color=RED,   width=1, dash="dot"), annotation_text="Overbought (70)", annotation_font=dict(color=RED,   size=9))
    fig.add_hline(y=30, line=dict(color=GREEN, width=1, dash="dot"), annotation_text="Oversold (30)",   annotation_font=dict(color=GREEN, size=9))
    fig.add_hline(y=50, line=dict(color=LABEL_COL, width=0.8, dash="dot"))
    return _apply_layout(fig,
        title=f"<b>{ticker}</b>  ·  RSI (14)  —  Relative Strength Index",
        yaxis_title="RSI", height=280)

def plot_comparison(df1, df2, t1, t2) -> go.Figure:
    n1 = df1["Close"] / df1["Close"].iloc[0] * 100
    n2 = df2["Close"] / df2["Close"].iloc[0] * 100
    fig = go.Figure()
    fig.add_hline(y=100, line=dict(color=GRID_COL, width=1, dash="dash"))
    fig.add_trace(go.Scatter(
        x=n1.index, y=n1, line=dict(color=BLUE, width=2.2), name=t1,
        hovertemplate=f"<b>%{{x|%b %d, %Y}}</b><br>{t1}: %{{y:.1f}}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=n2.index, y=n2, line=dict(color=ORANGE, width=2.2), name=t2,
        hovertemplate=f"<b>%{{x|%b %d, %Y}}</b><br>{t2}: %{{y:.1f}}<extra></extra>",
    ))
    return _apply_layout(fig,
        title=f"<b>Normalised Performance</b>  ·  {t1} vs {t2}  —  Base = 100 at Period Start",
        yaxis_title="Indexed Price (Base 100)", height=400)

def plot_rolling_corr(r1, r2, t1, t2) -> go.Figure:
    combined = pd.concat([r1, r2], axis=1, join="inner")
    combined.columns = ["r1", "r2"]
    rc = combined["r1"].rolling(30).corr(combined["r2"])
    colors = [GREEN if v >= 0 else RED for v in rc.fillna(0)]
    fig = go.Figure()
    fig.add_hrect(y0=0.7,  y1=1.1,  fillcolor="rgba(74,222,128,0.05)",  line_width=0)
    fig.add_hrect(y0=-1.1, y1=-0.7, fillcolor="rgba(248,113,113,0.05)", line_width=0)
    fig.add_trace(go.Scatter(
        x=rc.index, y=rc, fill="tozeroy", fillcolor="rgba(167,139,250,0.15)",
        line=dict(color=PURPLE, width=2), name="Rolling Corr.",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Correlation: %{y:+.3f}<extra></extra>",
    ))
    fig.add_hline(y=0,    line=dict(color=LABEL_COL, width=0.8))
    fig.add_hline(y=0.7,  line=dict(color=GREEN, width=1, dash="dot"), annotation_text="Strong positive (0.7)",  annotation_font=dict(color=GREEN, size=9))
    fig.add_hline(y=-0.7, line=dict(color=RED,   width=1, dash="dot"), annotation_text="Strong negative (−0.7)", annotation_font=dict(color=RED,   size=9))
    fig.update_yaxes(range=[-1.15, 1.15])
    return _apply_layout(fig,
        title=f"<b>30-Day Rolling Correlation</b>  ·  {t1} vs {t2}",
        yaxis_title="Correlation", height=300)

def plot_scatter(r1, r2, t1, t2, corr) -> go.Figure:
    m, b = np.polyfit(r1, r2, 1)
    xs = np.linspace(r1.min(), r1.max(), 100)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=r1 * 100, y=r2 * 100, mode="markers",
        marker=dict(color=BLUE, size=5, opacity=0.45),
        name="Daily Returns",
        hovertemplate=f"{t1}: %{{x:.2f}}%<br>{t2}: %{{y:.2f}}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=xs * 100, y=(m * xs + b) * 100,
        line=dict(color=ORANGE, width=2), name=f"Fit line (ρ={corr:+.3f})",
        hoverinfo="skip",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=f"<b>Return Scatter</b>  ·  ρ = {corr:+.3f}", font=dict(color=TEXT_COL, size=13), x=0),
        xaxis_title=f"{t1} Daily Return %",
        yaxis_title=f"{t2} Daily Return %",
        height=360,
    )
    return fig

# ── UI component helpers ──────────────────────────────────────────────────────
def score_color(s):  return GREEN if s >= 65 else (YELLOW if s >= 40 else RED)
def score_label(s):
    if s >= 72: return "Very Bullish"
    if s >= 58: return "Bullish"
    if s >= 45: return "Neutral"
    if s >= 30: return "Bearish"
    return "Very Bearish"

def render_score_card(score, ticker):
    col = score_color(score); lbl = score_label(score)
    st.markdown(f"""
    <div class="score-outer">
        <div class="score-label">SENTIMENT SCORE · {ticker}</div>
        <div class="score-value" style="color:{col}">{score}</div>
        <div class="score-sub" style="color:{col}">{lbl}</div>
        <div class="score-bar-bg"><div class="score-bar-fill" style="width:{score}%; background:{col};"></div></div>
        <div style="display:flex; justify-content:space-between; margin-top:4px;">
            <span style="font-size:10px; color:#475569">0 — Bearish</span>
            <span style="font-size:10px; color:#475569">100 — Bullish</span>
        </div>
    </div>""", unsafe_allow_html=True)

def render_corr_card(corr):
    if corr >= 0.65:    col, arrow = GREEN,     "↑"
    elif corr >= 0.20:  col, arrow = YELLOW,    "↗"
    elif corr >= -0.20: col, arrow = LABEL_COL, "→"
    elif corr >= -0.65: col, arrow = YELLOW,    "↘"
    else:               col, arrow = RED,       "↓"
    st.markdown(f"""
    <div class="corr-card">
        <div class="score-label">PEARSON CORRELATION</div>
        <div class="corr-value" style="color:{col}">{arrow} {corr:+.3f}</div>
        <div class="corr-desc" style="color:{col}">{_corr_desc(corr)}</div>
        <div class="corr-label" style="margin-top:8px;">Based on overlapping daily returns</div>
    </div>""", unsafe_allow_html=True)

def _corr_desc(c):
    a = abs(c); d = "positive" if c >= 0 else "negative"
    if a >= 0.85: return f"Very strong {d}"
    if a >= 0.65: return f"Strong {d}"
    if a >= 0.40: return f"Moderate {d}"
    if a >= 0.20: return f"Weak {d}"
    return "No meaningful correlation"

def render_summary(info, ticker, score):
    tc  = {"Bullish": GREEN, "Bearish": RED}.get(info["trend"], YELLOW)
    rc  = {"High": "risk-high", "Moderate": "risk-mod", "Low": "risk-low"}[info["risk"]]
    rc2 = {"Bullish": "regime-bull", "Bearish": "regime-bear"}.get(info["trend"], "regime-side")
    ti  = "▲" if info["trend"] == "Bullish" else ("▼" if info["trend"] == "Bearish" else "◆")
    mi  = {"Positive": "▲", "Negative": "▼", "Neutral": "◆"}[info["momentum"]]
    cx  = "MA20 above MA50 (golden cross)" if info["ma20"] > info["ma50"] else "MA20 below MA50 (death cross)"
    st.markdown(f"""
    <div class="summary-card">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
            <span style="font-size:10px; color:#475569; font-weight:600; letter-spacing:1px; text-transform:uppercase;">Market Summary · {ticker}</span>
            <span class="regime-badge {rc2}">{ti} {info['regime']}</span>
        </div>
        <div class="summary-row"><span class="summary-key">Trend</span><span class="summary-val" style="color:{tc}">{ti} {info['trend']}</span></div>
        <div class="summary-row"><span class="summary-key">Volatility</span><span class="summary-val">{info['vol_label']} ({info['vol']*100:.1f}% ann.)</span></div>
        <div class="summary-row"><span class="summary-key">Momentum (20d)</span><span class="summary-val">{mi} {info['momentum']}</span></div>
        <div class="summary-row"><span class="summary-key">Risk Level</span><span class="summary-val"><span class="{rc}">{info['risk']}</span></span></div>
        <div class="summary-row"><span class="summary-key">RSI (14)</span><span class="summary-val">{info['rsi']:.1f}</span></div>
        <div class="summary-row"><span class="summary-key">MA Cross</span><span class="summary-val" style="font-size:12px">{cx}</span></div>
        <div class="summary-row"><span class="summary-key">MA 20 / MA 50</span><span class="summary-val">${info['ma20']:,.2f} / ${info['ma50']:,.2f}</span></div>
    </div>""", unsafe_allow_html=True)

def insight(text: str):
    st.markdown(f'<div class="insight-box"><p>{text}</p></div>', unsafe_allow_html=True)

def section(label: str):
    st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)

def learn(label: str, content: str):
    with st.expander(f"📖  Learn: {label}"):
        st.markdown(content)

# ── KPI row ───────────────────────────────────────────────────────────────────
def kpi_row(info, df, ticker, timeframe):
    price      = info["price"]
    prev_price = float(df["Close"].iloc[-2])
    delta_pct  = (price - prev_price) / prev_price * 100
    avg_ret    = info["daily_return_avg"] * 100
    vol_pct    = info["vol"] * 100
    period_ret = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[0]) - 1) * 100
    cols = st.columns(6)
    cols[0].metric(f"{ticker} Price",    f"${price:,.2f}",     f"{delta_pct:+.2f}% 1d",  help=TOOLTIPS["price"])
    cols[1].metric("MA 20",              f"${info['ma20']:,.2f}",                          help=TOOLTIPS["ma20"])
    cols[2].metric("MA 50",              f"${info['ma50']:,.2f}",                          help=TOOLTIPS["ma50"])
    cols[3].metric("Avg Daily Return",   f"{avg_ret:+.3f}%",                               help=TOOLTIPS["avg_ret"])
    cols[4].metric("Ann. Volatility",    f"{vol_pct:.1f}%",                                help=TOOLTIPS["ann_vol"])
    cols[5].metric(f"{timeframe} Return",f"{period_ret:+.1f}%",                            help=TOOLTIPS["period_ret"])

# ── Single ticker section ─────────────────────────────────────────────────────
def render_single(df, info, ticker, score, timeframe):
    section("Key Metrics")
    kpi_row(info, df, ticker, timeframe)

    section("Signal Overview")
    sc1, sc2 = st.columns([1, 2.5])
    with sc1: render_score_card(score, ticker)
    with sc2: render_summary(info, ticker, score)

    with st.expander("📖  What is the Sentiment Score?"):
        st.markdown(TOOLTIPS["sentiment"])

    section("What This Means")
    interp = generate_interpretation(info, df, ticker, score, timeframe)
    st.markdown(f'<div class="wtm-card"><div class="wtm-title">AI-Style Market Interpretation — {ticker}</div><div class="wtm-text">{interp}</div></div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    section("Price & Trend Analysis")
    insight(f"This chart shows <strong>{ticker}'s</strong> closing price alongside its 20-day (MA20) and 50-day (MA50) moving averages. "
            "The shaded Bollinger Bands widen during volatile periods and narrow during calm ones. "
            "<strong>Look for:</strong> price crossing above/below the MAs, and golden/death cross events (marked with triangles) which often signal trend changes.")
    st.plotly_chart(plot_price_ma(df, ticker), width="stretch")
    learn("Moving Averages & Bollinger Bands",
          "**Moving Averages (MA)** smooth out daily price noise to reveal the underlying trend direction.\n\n"
          "- **MA20** reacts quickly to recent price changes — useful for short-term signals.\n"
          "- **MA50** is slower and shows the medium-term trend — widely watched by institutional investors.\n\n"
          "**Bollinger Bands** show a price channel ±2 standard deviations from the 20-day average. "
          "Prices touching the upper band may be overextended; touching the lower band may signal a bounce.\n\n"
          "**Golden Cross**: MA20 crosses *above* MA50 → historically bullish signal.\n"
          "**Death Cross**: MA20 crosses *below* MA50 → historically bearish signal.")

    section("Rolling Volatility Analysis")
    insight(f"Volatility measures how dramatically {ticker}'s price swings day-to-day. "
            "The chart shows annualised 20-day rolling volatility with colour zones: "
            "<strong>green = stable, yellow = moderate, red = elevated risk</strong>. "
            f"Current volatility: <strong>{info['vol']*100:.1f}%</strong> — classified as <strong>{info['vol_label']}</strong>.")
    st.plotly_chart(plot_volatility(df, ticker), width="stretch")
    learn("Volatility & Risk",
          "**Volatility** measures the degree of price variation over time. High volatility means larger, less predictable price moves.\n\n"
          "- **< 20% (Low):** Stable asset — typical of large-cap stocks or bonds in calm markets.\n"
          "- **20–45% (Moderate):** Normal equity market range — manageable risk.\n"
          "- **> 45% (High):** Large swings — common in small caps, growth stocks, or crypto.\n\n"
          "Volatility is *not* inherently bad — it cuts both ways. High volatility means bigger potential gains *and* losses.")

    section("RSI — Momentum Indicator")
    insight("The RSI measures the speed and magnitude of recent price changes. "
            "<strong>Above 70:</strong> the asset may be overbought and due for a pullback. "
            "<strong>Below 30:</strong> potentially oversold and may bounce. "
            f"Current RSI for {ticker}: <strong>{info['rsi']:.0f}</strong>.")
    st.plotly_chart(plot_rsi(df, ticker), width="stretch")
    learn("RSI (Relative Strength Index)",
          "The **RSI** is a momentum oscillator ranging from 0 to 100.\n\n"
          "- **> 70:** Overbought — the asset has risen quickly and may be due for a correction.\n"
          "- **< 30:** Oversold — the asset has fallen sharply and could be due for a rebound.\n"
          "- **40–60:** Neutral zone — no extreme signal.\n\n"
          "RSI works best as a *confirmation* tool alongside trend and MA analysis, not in isolation.")

    section("Daily Return Distribution")
    insight(f"Each bar represents {ticker}'s gain or loss on a single trading day. "
            "Green bars are positive days; red bars are negative. The teal dashed line marks the average daily return. "
            "<strong>Wide bars</strong> (large swings) indicate volatile periods; <strong>clustered small bars</strong> indicate stability.")
    st.plotly_chart(plot_returns(df, ticker), width="stretch")
    learn("Daily Returns",
          "**Daily returns** show the percentage price change from one trading day to the next.\n\n"
          "- A long string of **green bars** suggests sustained positive momentum.\n"
          "- Alternating red/green bars with large swings indicate high volatility and uncertainty.\n"
          "- The **average daily return** × 252 (trading days) approximates the annualised return.\n\n"
          "Investors generally prefer consistent small positive returns over erratic large swings.")

# ── Comparison section ────────────────────────────────────────────────────────
def render_comparison(df1, info1, t1, score1, df2, info2, t2, score2, timeframe):
    corr_val, r1, r2 = compute_correlation(df1, df2)

    section("Key Metrics")
    kpi_row(info1, df1, t1, timeframe)
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    kpi_row(info2, df2, t2, timeframe)

    section("Signal Overview")
    sc1, sc2, sc3, sc4 = st.columns([1.6, 1.6, 1.6, 1.2])
    with sc1: render_score_card(score1, t1)
    with sc2: render_score_card(score2, t2)
    with sc3: render_summary(info1, t1, score1)
    with sc4: render_corr_card(corr_val)

    with st.expander("📖  What is the Sentiment Score?"):
        st.markdown(TOOLTIPS["sentiment"])
    with st.expander("📖  What is the Correlation?"):
        st.markdown(TOOLTIPS["corr"])

    section("What This Means")
    i1 = generate_interpretation(info1, df1, t1, score1, timeframe)
    i2 = generate_interpretation(info2, df2, t2, score2, timeframe)
    ic = generate_corr_interpretation(t1, t2, corr_val)
    st.markdown(f"""
    <div class="wtm-card">
        <div class="wtm-title">AI-Style Market Interpretation — {t1}</div>
        <div class="wtm-text">{i1}</div>
    </div>
    <div class="wtm-card" style="margin-top:0.8rem">
        <div class="wtm-title">AI-Style Market Interpretation — {t2}</div>
        <div class="wtm-text">{i2}</div>
    </div>
    <div class="wtm-card" style="margin-top:0.8rem">
        <div class="wtm-title">Correlation Analysis — {t1} vs {t2}</div>
        <div class="wtm-text">{ic}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    tab_comp, tab_t1, tab_t2, tab_corr = st.tabs([
        f"⚖️  Comparison", f"📈  {t1}", f"📈  {t2}", "🔗  Correlation"
    ])

    with tab_comp:
        section("Normalised Performance")
        insight(f"Both assets are indexed to 100 at the start of the period, making them directly comparable regardless of their absolute prices. "
                f"A line <strong>above 100</strong> means the asset has gained since the period started; <strong>below 100</strong> means it has declined. "
                f"Hover to see exact levels on any date.")
        st.plotly_chart(plot_comparison(df1, df2, t1, t2), width="stretch")

    with tab_t1:
        section("Price & Trend Analysis")
        insight(f"<strong>{t1}</strong> price vs moving averages with Bollinger Bands. "
                "Triangle markers highlight golden/death crossover events.")
        st.plotly_chart(plot_price_ma(df1, t1, color=BLUE), width="stretch")
        learn("Moving Averages & Bollinger Bands",
              "**MA20** = short-term trend. **MA50** = medium-term trend. "
              "Price above both = bullish. Bollinger Bands widen in volatile periods.")
        section("Rolling Volatility Analysis")
        insight(f"Current {t1} volatility is <strong>{info1['vol']*100:.1f}%</strong> annualised — <strong>{info1['vol_label']}</strong> risk zone.")
        st.plotly_chart(plot_volatility(df1, t1), width="stretch")
        section("RSI Momentum")
        insight(f"RSI at <strong>{info1['rsi']:.0f}</strong> — {'overbought zone, watch for pullback' if info1['rsi'] > 70 else ('oversold zone, possible bounce' if info1['rsi'] < 30 else 'neutral range')}")
        st.plotly_chart(plot_rsi(df1, t1), width="stretch")
        section("Daily Return Distribution")
        insight(f"Daily gains and losses for {t1} over the selected period. Average daily return: <strong>{info1['daily_return_avg']*100:+.3f}%</strong>.")
        st.plotly_chart(plot_returns(df1, t1), width="stretch")

    with tab_t2:
        section("Price & Trend Analysis")
        insight(f"<strong>{t2}</strong> price vs moving averages with Bollinger Bands. "
                "Triangle markers highlight golden/death crossover events.")
        st.plotly_chart(plot_price_ma(df2, t2, color=ORANGE), width="stretch")
        learn("Moving Averages & Bollinger Bands",
              "**MA20** = short-term trend. **MA50** = medium-term trend. "
              "Price above both = bullish. Bollinger Bands widen in volatile periods.")
        section("Rolling Volatility Analysis")
        insight(f"Current {t2} volatility is <strong>{info2['vol']*100:.1f}%</strong> annualised — <strong>{info2['vol_label']}</strong> risk zone.")
        st.plotly_chart(plot_volatility(df2, t2), width="stretch")
        section("RSI Momentum")
        insight(f"RSI at <strong>{info2['rsi']:.0f}</strong> — {'overbought zone, watch for pullback' if info2['rsi'] > 70 else ('oversold zone, possible bounce' if info2['rsi'] < 30 else 'neutral range')}")
        st.plotly_chart(plot_rsi(df2, t2), width="stretch")
        section("Daily Return Distribution")
        insight(f"Daily gains and losses for {t2} over the selected period. Average daily return: <strong>{info2['daily_return_avg']*100:+.3f}%</strong>.")
        st.plotly_chart(plot_returns(df2, t2), width="stretch")
        section("Summary")
        render_summary(info2, t2, score2)

    with tab_corr:
        section("30-Day Rolling Correlation")
        insight(f"This chart tracks how the correlation between <strong>{t1}</strong> and <strong>{t2}</strong> has changed over time. "
                "Values near <strong>+1</strong> mean they move in lockstep; near <strong>−1</strong> means they move opposite; near <strong>0</strong> means they're independent. "
                f"Current overall correlation: <strong>{corr_val:+.3f}</strong>.")
        st.plotly_chart(plot_rolling_corr(r1, r2, t1, t2), width="stretch")

        section("Return Scatter Plot")
        insight("Each dot represents one day's returns for both assets plotted against each other. "
                "A tight cluster along a rising diagonal line shows strong positive correlation. "
                "A scattered cloud shows weak or no correlation. The orange line is the linear best fit.")
        cc1, cc2 = st.columns([1, 2])
        with cc1: render_corr_card(corr_val)
        with cc2: st.plotly_chart(plot_scatter(r1, r2, t1, t2, corr_val), width="stretch")

        learn("Correlation & Diversification",
              "**Correlation** measures how two assets move relative to each other.\n\n"
              "- **+0.8 to +1.0:** Very highly correlated — they mostly rise and fall together.\n"
              "- **+0.4 to +0.8:** Moderately correlated — similar directional bias but not identical.\n"
              "- **-0.2 to +0.2:** Uncorrelated — largely independent movements.\n"
              "- **-0.8 to -0.4:** Negatively correlated — one tends to rise when the other falls.\n\n"
              "For portfolio diversification, holding assets with **low or negative correlation** reduces overall risk, "
              "because losses in one asset may be offset by gains in the other.")

# ── APP ENTRY POINT ───────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
    <div class="dash-title">📊 Quantitative Market Intelligence Dashboard</div>
    <div class="dash-subtitle">Real-Time Trend, Volatility, and Correlation Analysis</div>
</div>""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
with c1:
    ticker1_raw = st.text_input("Primary Ticker", value="NVDA", placeholder="e.g. AAPL")
with c2:
    ticker2_raw = st.text_input("Compare Ticker (optional)", value="AMD", placeholder="e.g. AMD")
with c3:
    timeframe = st.selectbox("Timeframe", list(TIMEFRAME_MAP.keys()), index=3)
with c4:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    run_btn = st.button("Run Analysis →", use_container_width=True)

ticker1 = ticker1_raw.strip().upper()
ticker2 = ticker2_raw.strip().upper() if ticker2_raw.strip() else None
period  = TIMEFRAME_MAP[timeframe]

if ticker1:
    with st.spinner("Fetching market data and computing indicators…"):
        df1_raw = fetch_data(ticker1, period)
        df2_raw = fetch_data(ticker2, period) if ticker2 else pd.DataFrame()

    if df1_raw.empty:
        st.error(f"Could not fetch data for **{ticker1}**. Please check the ticker symbol and try again.")
        st.stop()

    df1   = compute_indicators(df1_raw)
    info1 = classify_regime(df1)
    score1 = compute_sentiment(df1)

    has_t2 = ticker2 is not None and not df2_raw.empty
    if ticker2 and df2_raw.empty:
        st.warning(f"Could not fetch data for **{ticker2}**. Showing single-ticker analysis.")

    if has_t2:
        df2    = compute_indicators(df2_raw)
        info2  = classify_regime(df2)
        score2 = compute_sentiment(df2)
        render_comparison(df1, info1, ticker1, score1, df2, info2, ticker2, score2, timeframe)
    else:
        render_single(df1, info1, ticker1, score1, timeframe)

    st.markdown("""
    <div class="footer-note">
        ⚠ For educational and analytical purposes only. Not financial advice or a trading signal.
        Data sourced from Yahoo Finance and may be delayed up to 15 minutes.
    </div>""", unsafe_allow_html=True)
