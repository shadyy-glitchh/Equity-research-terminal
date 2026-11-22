
import re
import urllib.parse
from collections import Counter
from datetime import datetime
import feedparser
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="EQUITY RESEARCH TERMINAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,400&display=swap');
        .stApp, html, body, [class*="css"] {
            background-color: #0A0A0A;
            color: #EAEAEA;
            font-family: 'Merriweather', Georgia, serif !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #0F0F0F;
            border-right: 1px solid #262626;
        }
        h1, h2, h3, h4 {
            font-family: 'Merriweather', Georgia, serif !important;
            color: #F5F5F5 !important;
            font-weight: 400 !important;
            letter-spacing: -0.01em;
        }
        .terminal-header {
            font-family: 'Merriweather', Georgia, serif;
            font-size: 0.78rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #8E8E93;
            border-bottom: 1px solid #262626;
            padding-bottom: 8px;
            margin-bottom: 20px;
        }
        .section-label {
            font-family: 'Merriweather', Georgia, serif;
            font-size: 0.76rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #A1A1AA;
            border-bottom: 1px solid #222222;
            padding-bottom: 6px;
            margin-top: 16px;
            margin-bottom: 14px;
        }
        div[data-testid="stMetric"] {
            background-color: #111111;
            border: 1px solid #262626;
            border-radius: 2px;
            padding: 12px 14px;
        }
        div[data-testid="stMetricLabel"] {
            font-family: 'Merriweather', Georgia, serif;
            font-size: 0.70rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #8E8E93;
        }
        div[data-testid="stMetricValue"] {
            font-family: 'Merriweather', Georgia, serif;
            font-size: 1.30rem;
            font-weight: 700;
            color: #F5F5F5;
        }
        button[data-baseweb="tab"] {
            font-family: 'Merriweather', Georgia, serif;
            font-size: 0.85rem;
            letter-spacing: 0.06em;
            color: #8E8E93;
            background-color: transparent !important;
            border-radius: 0px !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #FFFFFF !important;
            border-bottom: 2px solid #EAEAEA !important;
        }
        .stButton > button {
            background-color: #141414;
            color: #EAEAEA;
            border: 1px solid #3A3A3C;
            border-radius: 2px;
            font-family: 'Merriweather', Georgia, serif;
            font-size: 0.76rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 6px 14px;
        }
        .stButton > button:hover {
            background-color: #EAEAEA;
            color: #0A0A0A;
            border-color: #EAEAEA;
        }
        .news-item {
            padding: 10px 0px;
            border-bottom: 1px solid #1C1C1E;
        }
        .news-title a {
            font-family: 'Merriweather', Georgia, serif;
            color: #EAEAEA !important;
            text-decoration: none;
            font-size: 0.92rem;
            font-weight: 400;
            line-height: 1.5;
        }
        .news-title a:hover {
            color: #FFFFFF !important;
            text-decoration: underline;
        }
        .news-meta {
            font-family: 'Merriweather', Georgia, serif;
            font-size: 0.72rem;
            color: #7C7C80;
            margin-top: 4px;
        }
        .tag-tier1 {
            color: #0A0A0A;
            background-color: #EAEAEA;
            padding: 1px 6px;
            font-weight: 700;
            font-size: 0.65rem;
            letter-spacing: 0.04em;
            margin-right: 6px;
        }
        .tag-catalyst {
            color: #D4D4D8;
            border: 1px solid #3F3F46;
            padding: 1px 6px;
            font-size: 0.65rem;
            margin-left: 6px;
        }
        .titanium-box {
            background-color: #111111;
            border: 1px solid #2E2E32;
            border-left: 3px solid #EAEAEA;
            padding: 10px 14px;
            font-family: 'Merriweather', Georgia, serif;
            font-size: 0.80rem;
            color: #D4D4D8;
            margin-bottom: 14px;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

SEC_HEADERS = {
    "User-Agent": "ShadrachResearch shadrachaddotc@gmail.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov"
}

HIGH_TIER_SOURCES = [
    "reuters", "bloomberg", "financial times", "ft.com", "wall street journal",
    "wsj", "cnbc", "barron", "marketwatch", "sec.gov", "investor", "pr newswire",
    "business wire", "globe newswire", "morningstar"
]

NOISE_KEYWORDS = [
    "skyrocket", "soar", "plunge", "millionaire", "billionaire", "10x", "100x",
    "meme", "reddit", "wallstreetbets", "next nvidia", "secret", "must buy",
    "strong buy right now", "better buy", "prediction:", "here's why", "motley fool",
    "investorplace", "zacks", "jim cramer", "cathie wood"
]

THESIS_KEYWORDS = [
    "earnings", "guidance", "margin", "revenue", "acquisition", "merger", "antitrust",
    "regulation", "tariff", "capex", "dividend", "buyback", "downgrade", "upgrade",
    "ceo", "cfo", "restructuring", "lawsuit", "contract"
]

st.markdown(
    f'<div class="terminal-header">EQUITY RESEARCH &amp; THESIS TERMINAL // LIVE FEED // {datetime.now().strftime("%d %b %Y %H:%M GMT").upper()}</div>',
    unsafe_allow_html=True
)

st.sidebar.markdown('<div class="section-label">PARAMETERS</div>', unsafe_allow_html=True)
tickers_input = st.sidebar.text_input("TICKERS (COMMA-SEPARATED)", value="BRK-B, UNH, TSM, MSFT, ONON")
min_cluster_insiders = st.sidebar.slider("INSIDER CLUSTER THRESHOLD", min_value=2, max_value=6, value=3)
strict_official_only = st.sidebar.checkbox("TIER-1 / OFFICIAL SOURCES ONLY", value=False)

if st.sidebar.button("REFRESH DATA"):
    st.cache_data.clear()

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

@st.cache_data(ttl=86400)
def get_sec_cik_map():
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "ShadrachResearch your.project.email@gmail.com"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                item["ticker"].upper(): str(item["cik_str"]).zfill(10)
                for item in data.values()
            }
    except Exception:
        pass
    return {}

@st.cache_data(ttl=3600)
def fetch_sec_filings(cik):
    if not cik:
        return pd.DataFrame(), 0
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    try:
        resp = requests.get(url, headers=SEC_HEADERS, timeout=10)
        if resp.status_code != 200:
            return pd.DataFrame(), 0
        recent = resp.json().get("filings", {}).get("recent", {})
        df = pd.DataFrame(recent)
        if df.empty:
            return pd.DataFrame(), 0
        form4_count = len(df[df["form"] == "4"].head(30))
        core_filings = df[df["form"].isin(["10-K", "10-Q", "8-K"])].head(8).copy()
        cik_int = str(int(cik))
        links = []
        for _, row in core_filings.iterrows():
            acc_no_clean = row["accessionNumber"].replace("-", "")
            doc = row["primaryDocument"]
            links.append(f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_no_clean}/{doc}")
        core_filings["SEC Direct Link"] = links
        return core_filings[["filingDate", "form", "primaryDocDescription", "SEC Direct Link"]], form4_count
    except Exception:
        return pd.DataFrame(), 0

@st.cache_data(ttl=900)
def fetch_filtered_news(ticker, company_name, strict_mode=False):
    clean_name = re.sub(
        r" (Inc|Corp|Corporation|Ltd|Limited|Holdings|Holding|PLC|N\.V\.|S\.A\.) \.?",
        "",
        company_name,
        flags=re.IGNORECASE
    ).strip()
    query = urllib.parse.quote(f'"{ticker}" OR "{clean_name}" stock OR earnings OR guidance')
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    scored_articles = []
    word_counter = Counter()
    stop_words = {
        "the", "and", "for", "with", "from", "that", "this", "stock", "shares",
        "news", "says", "after", "over", "into", "will", "more", "than", "amid",
        "as", "to", "in", "of", "on", "at", "by", "is", "are", "its"
    }
    for entry in feed.entries[:25]:
        title = entry.title
        title_lower = title.lower()
        source_title = entry.get("source", {}).get("title", "").lower()
        if any(noise in title_lower or noise in source_title for noise in NOISE_KEYWORDS):
            continue
        is_high_tier = any(src in source_title or src in title_lower for src in HIGH_TIER_SOURCES)
        if strict_mode and not is_high_tier:
            continue
        matched_thesis = [kw for kw in THESIS_KEYWORDS if kw in title_lower]
        score = (3 if is_high_tier else 0) + len(matched_thesis)
        words = [w for w in re.findall(r"[a-z]{4,}", title_lower) if w not in stop_words and w != ticker.lower()]
        word_counter.update(words)
        scored_articles.append({
            "title": title,
            "source": entry.get("source", {}).get("title", "NEWS"),
            "published": entry.get("published", ""),
            "link": entry.link,
            "is_high_tier": is_high_tier,
            "thesis_tags": matched_thesis,
            "score": score
        })
    recurring_themes = [word.upper() for word, count in word_counter.most_common(5) if count >= 2]
    scored_articles.sort(key=lambda x: x["score"], reverse=True)
    return scored_articles[:7], recurring_themes

@st.cache_data(ttl=900)
def fetch_fundamentals_and_insiders(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    price, pct_change = None, None
    if len(hist) >= 2:
        prev = hist["Close"].iloc[-2]
        curr = hist["Close"].iloc[-1]
        price = round(curr, 2)
        pct_change = round(((curr - prev) / prev) * 100, 2)
    elif len(hist) == 1:
        price = round(hist["Close"].iloc[-1], 2)
        pct_change = 0.0
    info = {}
    try:
        info = stock.info
    except Exception:
        pass
    cluster_buys = pd.DataFrame()
    unique_buyers = 0
    try:
        insiders = stock.insider_transactions
        if insiders is not None and not insiders.empty:
            text_col = "Text" if "Text" in insiders.columns else ("Transaction" if "Transaction" in insiders.columns else None)
            if text_col:
                buys = insiders[insiders[text_col].astype(str).str.contains("Purchase|Buy", case=False, na=False)].copy()
                if not buys.empty and "Insider" in buys.columns:
                    unique_buyers = buys["Insider"].nunique()
                    cluster_buys = buys.head(10)
    except Exception:
        pass
    return price, pct_change, info, cluster_buys, unique_buyers

if not tickers:
    st.markdown('<div class="titanium-box">ENTER TICKER SYMBOLS IN THE LEFT PANEL TO INITIALISE FEED.</div>', unsafe_allow_html=True)
    st.stop()

cik_map = get_sec_cik_map()
tabs = st.tabs(tickers)

for tab, ticker in zip(tabs, tickers):
    with tab:
        price, pct_change, info, cluster_buys, unique_buyers = fetch_fundamentals_and_insiders(ticker)
        company_name = info.get("shortName", ticker)
        sector = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")

        st.markdown(f"## {company_name} [{ticker}]")
        st.markdown(
            f'<div style="font-family: Merriweather, Georgia, serif; font-size: 0.78rem; color: #8E8E93; margin-bottom: 14px;">SECTOR: {sector.upper()} // INDUSTRY: {industry.upper()}</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="section-label">01 // VALUATION &amp; FUNDAMENTAL METRICS</div>', unsafe_allow_html=True)
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("LAST CLOSE", f"${price:.2f}" if price else "N/A", f"{pct_change:+.2f}%" if pct_change is not None else None)
        fwd_pe = info.get("forwardPE")
        m2.metric("FWD P/E", f"{fwd_pe:.1f}x" if isinstance(fwd_pe, (int, float)) else "N/A")
        ev_ebitda = info.get("enterpriseToEbitda")
        m3.metric("EV / EBITDA", f"{ev_ebitda:.1f}x" if isinstance(ev_ebitda, (int, float)) else "N/A")
        op_margin = info.get("operatingMargins")
        m4.metric("OP. MARGIN", f"{op_margin * 100:.1f}%" if isinstance(op_margin, (int, float)) else "N/A")
        rev_growth = info.get("revenueGrowth")
        m5.metric("REV. GROWTH", f"{rev_growth * 100:.1f}%" if isinstance(rev_growth, (int, float)) else "N/A")
        target_price = info.get("targetMeanPrice")
        if isinstance(target_price, (int, float)) and price:
            upside = ((target_price - price) / price) * 100
            m6.metric("MEAN TARGET", f"${target_price:.2f}", f"{upside:+.1f}%")
        else:
            m6.metric("MEAN TARGET", "N/A")

        with st.expander("BUSINESS OVERVIEW & MOAT PROFILE"):
            st.write(info.get("longBusinessSummary", "Business description unavailable."))

        col_news, col_sec = st.columns([1.35, 1])

        with col_news:
            st.markdown('<div class="section-label">02 // FILTERED NEWS &amp; CATALYSTS</div>', unsafe_allow_html=True)
            articles, recurring_themes = fetch_filtered_news(ticker, company_name, strict_official_only)
            if recurring_themes:
                st.markdown(
                    f'<div class="titanium-box">RECURRING CATALYST KEYWORDS: {", ".join(recurring_themes)}</div>',
                    unsafe_allow_html=True
                )
            if not articles:
                st.markdown('<div class="news-meta">NO ARTICLES PASSED NOISE FILTER.</div>', unsafe_allow_html=True)
            else:
                for art in articles:
                    tier_html = '<span class="tag-tier1">TIER-1</span>' if art["is_high_tier"] else ""
                    cat_html = f'<span class="tag-catalyst">{", ".join(art["thesis_tags"]).upper()}</span>' if art["thesis_tags"] else ""
                    st.markdown(
                        f'<div class="news-item"><div class="news-title">{tier_html}<a href="{art["link"]}" target="_blank">{art["title"]}</a>{cat_html}</div><div class="news-meta">{art["source"].upper()} // {art["published"]}</div></div>',
                        unsafe_allow_html=True
                    )

        with col_sec:
            st.markdown('<div class="section-label">03 // SEC EDGAR FILINGS</div>', unsafe_allow_html=True)
            cik = cik_map.get(ticker.replace("-", ".")) or cik_map.get(ticker)
            if not cik:
                st.markdown('<div class="news-meta">NON-US LISTING OR CIK UNAVAILABLE.</div>', unsafe_allow_html=True)
            else:
                filings_df, form4_count = fetch_sec_filings(cik)
                st.markdown(
                    f'<div class="news-meta" style="margin-bottom: 10px;">CIK: {cik} // RECENT FORM 4 COUNT: {form4_count}</div>',
                    unsafe_allow_html=True
                )
                if not filings_df.empty:
                    for _, row in filings_df.iterrows():
                        desc = row["primaryDocDescription"] or row["form"]
                        st.markdown(
                            f'<div class="news-item"><div class="news-title"><span class="tag-tier1">{row["form"]}</span><a href="{row["SEC Direct Link"]}" target="_blank">{desc}</a></div><div class="news-meta">FILED: {row["filingDate"]}</div></div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown('<div class="news-meta">NO RECENT 10-K, 10-Q, OR 8-K FILINGS FOUND.</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">04 // INSIDER CLUSTER ACTIVITY</div>', unsafe_allow_html=True)
        if unique_buyers >= min_cluster_insiders:
            st.markdown(
                f'<div class="titanium-box">CLUSTER BUY SIGNAL: {unique_buyers} DISTINCT INSIDERS RECORDED PURCHASES (THRESHOLD: {min_cluster_insiders}+).</div>',
                unsafe_allow_html=True
            )
            st.dataframe(cluster_buys, use_container_width=True, hide_index=True)
        else:
            st.markdown(
                f'<div class="news-meta">NO CLUSTER BUY SIGNAL ({unique_buyers} DISTINCT BUYER(S) // THRESHOLD: {min_cluster_insiders}+). ROUTINE SINGLE-INSIDER ACTIVITY SUPPRESSED.</div>',
                unsafe_allow_html=True
            )
        st.markdown('<div class="section-label">05 // THESIS &amp; RESEARCH NOTE BUILDER</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        action_choice = c1.selectbox("ACTION", ["WATCHLIST", "BUY (STARTER 5-7%)", "BUY (HIGH CONVICTION 8-10%)", "HOLD", "SELL / EXIT"], key=f"act_{ticker}")
        target_input = c2.text_input("MY TARGET PRICE ($)", placeholder="e.g. 45.00", key=f"tgt_{ticker}")
        conviction = c3.selectbox("CONVICTION", ["HIGH", "MODERATE", "LOW"], key=f"conv_{ticker}")

        thesis_text = st.text_area(
            "3-SENTENCE THESIS (1. BUSINESS SHIFT // 2. GROWTH & MARGINS // 3. VALUATION EDGE)",
            height=110,
            key=f"thesis_{ticker}"
        )
        col_bull, col_bear = st.columns(2)
        bull_text = col_bull.text_area("BULL CASE & CATALYSTS", height=90, key=f"bull_{ticker}")
        bear_text = col_bear.text_area("BEAR CASE // WHAT KILLS THE THESIS?", height=90, key=f"bear_{ticker}")

        report_md = f"""# EQUITY RESEARCH NOTE: {company_name} [{ticker}]
**Date:** {datetime.now().strftime("%d %b %Y")} | **Action:** {action_choice} | **Conviction:** {conviction} | **Target Price:** ${target_input or 'N/A'}

## Live Snapshot at Entry
- **Last Close:** ${price if price else 'N/A'}
- **Forward P/E:** {f"{fwd_pe:.1f}x" if isinstance(fwd_pe, (int, float)) else 'N/A'}
- **EV / EBITDA:** {f"{ev_ebitda:.1f}x" if isinstance(ev_ebitda, (int, float)) else 'N/A'}
- **Operating Margin:** {f"{op_margin * 100:.1f}%" if isinstance(op_margin, (int, float)) else 'N/A'}
- **Revenue Growth:** {f"{rev_growth * 100:.1f}%" if isinstance(rev_growth, (int, float)) else 'N/A'}

## 3-Sentence Investment Thesis
{thesis_text or 'N/A'}

## Bull Case & Catalysts
{bull_text or 'N/A'}

## Bear Case & Thesis Killers
{bear_text or 'N/A'}
"""
        st.download_button(
            label=f"EXPORT {ticker} RESEARCH NOTE (.MD)",
            data=report_md,
            file_name=f"{ticker}_Research_Note_{datetime.now().strftime('%Y-%m-%d')}.md",
            mime="text/markdown",
            key=f"dl_{ticker}"
        )
