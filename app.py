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
page_title=&quot;EQUITY RESEARCH TERMINAL&quot;,
layout=&quot;wide&quot;,
initial_sidebar_state=&quot;expanded&quot;
)
st.markdown(
&quot;&quot;&quot;
&lt;style&gt;
@import
url(&#39;https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,400&amp;display=swap&#39;);
.stApp, html, body, [class*=&quot;css&quot;] {
background-color: #0A0A0A;
color: #EAEAEA;
font-family: &#39;Merriweather&#39;, Georgia, serif !important;
}
section[data-testid=&quot;stSidebar&quot;] {
background-color: #0F0F0F;
border-right: 1px solid #262626;
}
h1, h2, h3, h4 {
font-family: &#39;Merriweather&#39;, Georgia, serif !important;
color: #F5F5F5 !important;
font-weight: 400 !important;
letter-spacing: -0.01em;
}
.terminal-header {
font-family: &#39;Merriweather&#39;, Georgia, serif;
font-size: 0.78rem;
letter-spacing: 0.1em;
text-transform: uppercase;
color: #8E8E93;
border-bottom: 1px solid #262626;
padding-bottom: 8px;
margin-bottom: 20px;
}
.section-label {
font-family: &#39;Merriweather&#39;, Georgia, serif;
font-size: 0.76rem;
letter-spacing: 0.08em;
text-transform: uppercase;
color: #A1A1AA;
border-bottom: 1px solid #222222;
padding-bottom: 6px;
margin-top: 16px;
margin-bottom: 14px;
}
div[data-testid=&quot;stMetric&quot;] {
background-color: #111111;
border: 1px solid #262626;
border-radius: 2px;
padding: 12px 14px;

}
div[data-testid=&quot;stMetricLabel&quot;] {
font-family: &#39;Merriweather&#39;, Georgia, serif;
font-size: 0.70rem;
text-transform: uppercase;
letter-spacing: 0.05em;
color: #8E8E93;
}
div[data-testid=&quot;stMetricValue&quot;] {
font-family: &#39;Merriweather&#39;, Georgia, serif;
font-size: 1.30rem;
font-weight: 700;
color: #F5F5F5;
}
button[data-baseweb=&quot;tab&quot;] {
font-family: &#39;Merriweather&#39;, Georgia, serif;
font-size: 0.85rem;
letter-spacing: 0.06em;
color: #8E8E93;
background-color: transparent !important;
border-radius: 0px !important;
}
button[data-baseweb=&quot;tab&quot;][aria-selected=&quot;true&quot;] {
color: #FFFFFF !important;
border-bottom: 2px solid #EAEAEA !important;
}
.stButton &gt; button {
background-color: #141414;
color: #EAEAEA;
border: 1px solid #3A3A3C;
border-radius: 2px;
font-family: &#39;Merriweather&#39;, Georgia, serif;
font-size: 0.76rem;
letter-spacing: 0.06em;
text-transform: uppercase;
padding: 6px 14px;
}
.stButton &gt; button:hover {
background-color: #EAEAEA;
color: #0A0A0A;
border-color: #EAEAEA;
}
.news-item {
padding: 10px 0px;
border-bottom: 1px solid #1C1C1E;
}
.news-title a {
font-family: &#39;Merriweather&#39;, Georgia, serif;
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
font-family: &#39;Merriweather&#39;, Georgia, serif;
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
font-family: &#39;Merriweather&#39;, Georgia, serif;
font-size: 0.80rem;
color: #D4D4D8;
margin-bottom: 14px;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
&lt;/style&gt;
&quot;&quot;&quot;,
unsafe_allow_html=True
)
SEC_HEADERS = {
&quot;User-Agent&quot;: &quot;ShadrachResearch your.project.email@gmail.com&quot;,
&quot;Accept-Encoding&quot;: &quot;gzip, deflate&quot;,
&quot;Host&quot;: &quot;data.sec.gov&quot;
}
HIGH_TIER_SOURCES = [
&quot;reuters&quot;, &quot;bloomberg&quot;, &quot;financial times&quot;, &quot;ft.com&quot;, &quot;wall street journal&quot;,
&quot;wsj&quot;, &quot;cnbc&quot;, &quot;barron&quot;, &quot;marketwatch&quot;, &quot;sec.gov&quot;, &quot;investor&quot;, &quot;pr newswire&quot;,
&quot;business wire&quot;, &quot;globe newswire&quot;, &quot;morningstar&quot;
]
NOISE_KEYWORDS = [
&quot;skyrocket&quot;, &quot;soar&quot;, &quot;plunge&quot;, &quot;millionaire&quot;, &quot;billionaire&quot;, &quot;10x&quot;, &quot;100x&quot;,
&quot;meme&quot;, &quot;reddit&quot;, &quot;wallstreetbets&quot;, &quot;next nvidia&quot;, &quot;secret&quot;, &quot;must buy&quot;,
&quot;strong buy right now&quot;, &quot;better buy&quot;, &quot;prediction:&quot;, &quot;here&#39;s why&quot;, &quot;motley fool&quot;,
&quot;investorplace&quot;, &quot;zacks&quot;, &quot;jim cramer&quot;, &quot;cathie wood&quot;
]
THESIS_KEYWORDS = [
&quot;earnings&quot;, &quot;guidance&quot;, &quot;margin&quot;, &quot;revenue&quot;, &quot;acquisition&quot;, &quot;merger&quot;, &quot;antitrust&quot;,
&quot;regulation&quot;, &quot;tariff&quot;, &quot;capex&quot;, &quot;dividend&quot;, &quot;buyback&quot;, &quot;downgrade&quot;, &quot;upgrade&quot;,
&quot;ceo&quot;, &quot;cfo&quot;, &quot;restructuring&quot;, &quot;lawsuit&quot;, &quot;contract&quot;
]
st.markdown(
f&#39;&lt;div class=&quot;terminal-header&quot;&gt;EQUITY RESEARCH &amp;amp; THESIS TERMINAL // LIVE FEED //
{datetime.now().strftime(&quot;%d %b %Y %H:%M GMT&quot;).upper()}&lt;/div&gt;&#39;,
unsafe_allow_html=True
)
st.sidebar.markdown(&#39;&lt;div class=&quot;section-label&quot;&gt;PARAMETERS&lt;/div&gt;&#39;, unsafe_allow_html=True)
tickers_input = st.sidebar.text_input(&quot;TICKERS (COMMA-SEPARATED)&quot;, value=&quot;BRK-B, UNH, TSM, MSFT, ONON&quot;)
min_cluster_insiders = st.sidebar.slider(&quot;INSIDER CLUSTER THRESHOLD&quot;, min_value=2, max_value=6, value=3)

strict_official_only = st.sidebar.checkbox(&quot;TIER-1 / OFFICIAL SOURCES ONLY&quot;, value=False)
if st.sidebar.button(&quot;REFRESH DATA&quot;):
st.cache_data.clear()
tickers = [t.strip().upper() for t in tickers_input.split(&quot;,&quot;) if t.strip()]
@st.cache_data(ttl=86400)
def get_sec_cik_map():
url = &quot;https://www.sec.gov/files/company_tickers.json&quot;
headers = {&quot;User-Agent&quot;: &quot;ShadrachResearch your.project.email@gmail.com&quot;}
try:
resp = requests.get(url, headers=headers, timeout=10)
if resp.status_code == 200:
data = resp.json()
return {
item[&quot;ticker&quot;].upper(): str(item[&quot;cik_str&quot;]).zfill(10)
for item in data.values()
}
except Exception:
pass
return {}
@st.cache_data(ttl=3600)
def fetch_sec_filings(cik):
if not cik:
return pd.DataFrame(), 0
url = f&quot;https://data.sec.gov/submissions/CIK{cik}.json&quot;
try:
resp = requests.get(url, headers=SEC_HEADERS, timeout=10)
if resp.status_code != 200:
return pd.DataFrame(), 0
recent = resp.json().get(&quot;filings&quot;, {}).get(&quot;recent&quot;, {})
df = pd.DataFrame(recent)
if df.empty:
return pd.DataFrame(), 0
form4_count = len(df[df[&quot;form&quot;] == &quot;4&quot;].head(30))
core_filings = df[df[&quot;form&quot;].isin([&quot;10-K&quot;, &quot;10-Q&quot;, &quot;8-K&quot;])].head(8).copy()
cik_int = str(int(cik))
links = []
for _, row in core_filings.iterrows():
acc_no_clean = row[&quot;accessionNumber&quot;].replace(&quot;-&quot;, &quot;&quot;)
doc = row[&quot;primaryDocument&quot;]
links.append(f&quot;https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_no_clean}/{doc}&quot;)
core_filings[&quot;SEC Direct Link&quot;] = links
return core_filings[[&quot;filingDate&quot;, &quot;form&quot;, &quot;primaryDocDescription&quot;, &quot;SEC Direct Link&quot;]], form4_count
except Exception:
return pd.DataFrame(), 0
@st.cache_data(ttl=900)
def fetch_filtered_news(ticker, company_name, strict_mode=False):
clean_name = re.sub(
r&quot;\b(Inc|Corp|Corporation|Ltd|Limited|Holdings|Holding|PLC|N\.V\.|S\.A\.)\b\.?&quot;,
&quot;&quot;,
company_name,
flags=re.IGNORECASE
).strip()
query = urllib.parse.quote(f&#39;&quot;{ticker}&quot; OR &quot;{clean_name}&quot; stock OR earnings OR guidance&#39;)
rss_url = f&quot;https://news.google.com/rss/search?q={query}&amp;hl=en-US&amp;gl=US&amp;ceid=US:en&quot;
feed = feedparser.parse(rss_url)
scored_articles = []
word_counter = Counter()
stop_words = {
&quot;the&quot;, &quot;and&quot;, &quot;for&quot;, &quot;with&quot;, &quot;from&quot;, &quot;that&quot;, &quot;this&quot;, &quot;stock&quot;, &quot;shares&quot;,
&quot;news&quot;, &quot;says&quot;, &quot;after&quot;, &quot;over&quot;, &quot;into&quot;, &quot;will&quot;, &quot;more&quot;, &quot;than&quot;, &quot;amid&quot;,
&quot;as&quot;, &quot;to&quot;, &quot;in&quot;, &quot;of&quot;, &quot;on&quot;, &quot;at&quot;, &quot;by&quot;, &quot;is&quot;, &quot;are&quot;, &quot;its&quot;

}
for entry in feed.entries[:25]:
title = entry.title
title_lower = title.lower()
source_title = entry.get(&quot;source&quot;, {}).get(&quot;title&quot;, &quot;&quot;).lower()
if any(noise in title_lower or noise in source_title for noise in NOISE_KEYWORDS):
continue
is_high_tier = any(src in source_title or src in title_lower for src in HIGH_TIER_SOURCES)
if strict_mode and not is_high_tier:
continue
matched_thesis = [kw for kw in THESIS_KEYWORDS if kw in title_lower]
score = (3 if is_high_tier else 0) + len(matched_thesis)
words = [w for w in re.findall(r&quot;[a-z]{4,}&quot;, title_lower) if w not in stop_words and w !=
ticker.lower()]
word_counter.update(words)
scored_articles.append({
&quot;title&quot;: title,
&quot;source&quot;: entry.get(&quot;source&quot;, {}).get(&quot;title&quot;, &quot;NEWS&quot;),
&quot;published&quot;: entry.get(&quot;published&quot;, &quot;&quot;),
&quot;link&quot;: entry.link,
&quot;is_high_tier&quot;: is_high_tier,
&quot;thesis_tags&quot;: matched_thesis,
&quot;score&quot;: score
})
recurring_themes = [word.upper() for word, count in word_counter.most_common(5) if count &gt;= 2]
scored_articles.sort(key=lambda x: x[&quot;score&quot;], reverse=True)
return scored_articles[:7], recurring_themes
@st.cache_data(ttl=900)
def fetch_fundamentals_and_insiders(ticker):
stock = yf.Ticker(ticker)
hist = stock.history(period=&quot;5d&quot;)
price, pct_change = None, None
if len(hist) &gt;= 2:
prev = hist[&quot;Close&quot;].iloc[-2]
curr = hist[&quot;Close&quot;].iloc[-1]
price = round(curr, 2)
pct_change = round(((curr - prev) / prev) * 100, 2)
elif len(hist) == 1:
price = round(hist[&quot;Close&quot;].iloc[-1], 2)
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
text_col = &quot;Text&quot; if &quot;Text&quot; in insiders.columns else (&quot;Transaction&quot; if &quot;Transaction&quot; in
insiders.columns else None)
if text_col:
buys = insiders[insiders[text_col].astype(str).str.contains(&quot;Purchase|Buy&quot;, case=False,
na=False)].copy()
if not buys.empty and &quot;Insider&quot; in buys.columns:
unique_buyers = buys[&quot;Insider&quot;].nunique()
cluster_buys = buys.head(10)
except Exception:
pass
return price, pct_change, info, cluster_buys, unique_buyers
if not tickers:
st.markdown(&#39;&lt;div class=&quot;titanium-box&quot;&gt;ENTER TICKER SYMBOLS IN THE LEFT PANEL TO INITIALISE FEED.&lt;/div&gt;&#39;,
unsafe_allow_html=True)

st.stop()
cik_map = get_sec_cik_map()
tabs = st.tabs(tickers)
for tab, ticker in zip(tabs, tickers):
with tab:
price, pct_change, info, cluster_buys, unique_buyers = fetch_fundamentals_and_insiders(ticker)
company_name = info.get(&quot;shortName&quot;, ticker)
sector = info.get(&quot;sector&quot;, &quot;N/A&quot;)
industry = info.get(&quot;industry&quot;, &quot;N/A&quot;)
st.markdown(f&quot;## {company_name} [{ticker}]&quot;)
st.markdown(
f&#39;&lt;div style=&quot;font-family: Merriweather, Georgia, serif; font-size: 0.78rem; color: #8E8E93; margin-
bottom: 14px;&quot;&gt;SECTOR: {sector.upper()} // INDUSTRY: {industry.upper()}&lt;/div&gt;&#39;,
unsafe_allow_html=True
)
st.markdown(&#39;&lt;div class=&quot;section-label&quot;&gt;01 // VALUATION &amp;amp; FUNDAMENTAL METRICS&lt;/div&gt;&#39;,
unsafe_allow_html=True)
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric(&quot;LAST CLOSE&quot;, f&quot;${price:.2f}&quot; if price else &quot;N/A&quot;, f&quot;{pct_change:+.2f}%&quot; if pct_change is not
None else None)
fwd_pe = info.get(&quot;forwardPE&quot;)
m2.metric(&quot;FWD P/E&quot;, f&quot;{fwd_pe:.1f}x&quot; if isinstance(fwd_pe, (int, float)) else &quot;N/A&quot;)
ev_ebitda = info.get(&quot;enterpriseToEbitda&quot;)
m3.metric(&quot;EV / EBITDA&quot;, f&quot;{ev_ebitda:.1f}x&quot; if isinstance(ev_ebitda, (int, float)) else &quot;N/A&quot;)
op_margin = info.get(&quot;operatingMargins&quot;)
m4.metric(&quot;OP. MARGIN&quot;, f&quot;{op_margin * 100:.1f}%&quot; if isinstance(op_margin, (int, float)) else &quot;N/A&quot;)
rev_growth = info.get(&quot;revenueGrowth&quot;)
m5.metric(&quot;REV. GROWTH&quot;, f&quot;{rev_growth * 100:.1f}%&quot; if isinstance(rev_growth, (int, float)) else &quot;N/A&quot;)
target_price = info.get(&quot;targetMeanPrice&quot;)
if isinstance(target_price, (int, float)) and price:
upside = ((target_price - price) / price) * 100
m6.metric(&quot;MEAN TARGET&quot;, f&quot;${target_price:.2f}&quot;, f&quot;{upside:+.1f}%&quot;)
else:
m6.metric(&quot;MEAN TARGET&quot;, &quot;N/A&quot;)
with st.expander(&quot;BUSINESS OVERVIEW &amp; MOAT PROFILE&quot;):
st.write(info.get(&quot;longBusinessSummary&quot;, &quot;Business description unavailable.&quot;))
col_news, col_sec = st.columns([1.35, 1])
with col_news:
st.markdown(&#39;&lt;div class=&quot;section-label&quot;&gt;02 // FILTERED NEWS &amp;amp; CATALYSTS&lt;/div&gt;&#39;,
unsafe_allow_html=True)
articles, recurring_themes = fetch_filtered_news(ticker, company_name, strict_official_only)
if recurring_themes:
st.markdown(
f&#39;&lt;div class=&quot;titanium-box&quot;&gt;RECURRING CATALYST KEYWORDS: {&quot;,
&quot;.join(recurring_themes)}&lt;/div&gt;&#39;,
unsafe_allow_html=True
)
if not articles:
st.markdown(&#39;&lt;div class=&quot;news-meta&quot;&gt;NO ARTICLES PASSED NOISE FILTER.&lt;/div&gt;&#39;,
unsafe_allow_html=True)
else:
for art in articles:
tier_html = &#39;&lt;span class=&quot;tag-tier1&quot;&gt;TIER-1&lt;/span&gt;&#39; if art[&quot;is_high_tier&quot;] else &quot;&quot;
cat_html = f&#39;&lt;span class=&quot;tag-catalyst&quot;&gt;{&quot;, &quot;.join(art[&quot;thesis_tags&quot;]).upper()}&lt;/span&gt;&#39; if
art[&quot;thesis_tags&quot;] else &quot;&quot;
st.markdown(

f&#39;&lt;div class=&quot;news-item&quot;&gt;&lt;div class=&quot;news-title&quot;&gt;{tier_html}&lt;a href=&quot;{art[&quot;link&quot;]}&quot;
target=&quot;_blank&quot;&gt;{art[&quot;title&quot;]}&lt;/a&gt;{cat_html}&lt;/div&gt;&lt;div class=&quot;news-meta&quot;&gt;{art[&quot;source&quot;].upper()} //
{art[&quot;published&quot;]}&lt;/div&gt;&lt;/div&gt;&#39;,
unsafe_allow_html=True
)
with col_sec:
st.markdown(&#39;&lt;div class=&quot;section-label&quot;&gt;03 // SEC EDGAR FILINGS&lt;/div&gt;&#39;, unsafe_allow_html=True)
cik = cik_map.get(ticker.replace(&quot;-&quot;, &quot;.&quot;)) or cik_map.get(ticker)
if not cik:
st.markdown(&#39;&lt;div class=&quot;news-meta&quot;&gt;NON-US LISTING OR CIK UNAVAILABLE.&lt;/div&gt;&#39;,
unsafe_allow_html=True)
else:
filings_df, form4_count = fetch_sec_filings(cik)
st.markdown(
f&#39;&lt;div class=&quot;news-meta&quot; style=&quot;margin-bottom: 10px;&quot;&gt;CIK: {cik} // RECENT FORM 4 COUNT:
{form4_count}&lt;/div&gt;&#39;,
unsafe_allow_html=True
)
if not filings_df.empty:
for _, row in filings_df.iterrows():
desc = row[&quot;primaryDocDescription&quot;] or row[&quot;form&quot;]
st.markdown(
f&#39;&lt;div class=&quot;news-item&quot;&gt;&lt;div class=&quot;news-title&quot;&gt;&lt;span class=&quot;tag-
tier1&quot;&gt;{row[&quot;form&quot;]}&lt;/span&gt;&lt;a href=&quot;{row[&quot;SEC Direct Link&quot;]}&quot; target=&quot;_blank&quot;&gt;{desc}&lt;/a&gt;&lt;/div&gt;&lt;div class=&quot;news-
meta&quot;&gt;FILED: {row[&quot;filingDate&quot;]}&lt;/div&gt;&lt;/div&gt;&#39;,
unsafe_allow_html=True
)
else:
st.markdown(&#39;&lt;div class=&quot;news-meta&quot;&gt;NO RECENT 10-K, 10-Q, OR 8-K FILINGS FOUND.&lt;/div&gt;&#39;,
unsafe_allow_html=True)
st.markdown(&#39;&lt;div class=&quot;section-label&quot;&gt;04 // INSIDER CLUSTER ACTIVITY&lt;/div&gt;&#39;, unsafe_allow_html=True)
if unique_buyers &gt;= min_cluster_insiders:
st.markdown(
f&#39;&lt;div class=&quot;titanium-box&quot;&gt;CLUSTER BUY SIGNAL: {unique_buyers} DISTINCT INSIDERS RECORDED
PURCHASES (THRESHOLD: {min_cluster_insiders}+).&lt;/div&gt;&#39;,
unsafe_allow_html=True
)
st.dataframe(cluster_buys, use_container_width=True, hide_index=True)
else:
st.markdown(
f&#39;&lt;div class=&quot;news-meta&quot;&gt;NO CLUSTER BUY SIGNAL ({unique_buyers} DISTINCT BUYER(S) // THRESHOLD:
{min_cluster_insiders}+). ROUTINE SINGLE-INSIDER ACTIVITY SUPPRESSED.&lt;/div&gt;&#39;,
unsafe_allow_html=True
)

