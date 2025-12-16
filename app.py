import streamlit as st
import threading
import asyncio
import pandas as pd

from storage import init_db, get_all_ticks
from ingestion import start_stream, stop_stream
from analytics import (
    prepare_df,
    spread_and_hedge,
    zscore,
    resample_ohlc,
    rolling_correlation,
    adf_test
)

# ================= PAGE CONFIG =================
st.set_page_config(layout="wide", page_title="Gemscap Quant Dashboard")

# ================= SESSION STATE =================
if "streaming" not in st.session_state:
    st.session_state.streaming = False
    st.session_state.thread = None



# ================= SIDEBAR =================
st.sidebar.header("⚙️ Controls")


# ================= GLOBAL CSS =================
st.markdown("""
<style>
/* Layout spacing */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    width: 320px !important;
    background-color: #020617;
}

/* Page background */
body {
    background-color: #0e1117;
    color: #e5e7eb;
}

/* Buttons */
div.stButton > button {
    background-color: #1d4ed8;
    color: white;
    border-radius: 8px;
    font-weight: 600;
    white-space: nowrap;
}

/* Download buttons */
div.stDownloadButton > button {
    background-color: #15803d;
    color: white;
    border-radius: 8px;
    font-weight: 600;
    white-space: nowrap;
}

/* Headers */
h1, h2, h3 {
    margin-bottom: 0.4rem;
    color: #e5e7eb;
}
</style>
""", unsafe_allow_html=True)


# ================= TITLE =================
st.markdown("## 📊 Gemscap – Quant Analytics Dashboard")
init_db()

# ================= SIDEBAR CONTROLS =================
timeframe = st.sidebar.selectbox("Timeframe", ["1s", "1m", "5m"], index=1)

symbols_input = st.sidebar.text_input(
    "Symbols (comma-separated)",
    "btcusdt,ethusdt"
)

window = st.sidebar.slider("Z-score Window", 10, 200, 50)

z_threshold = st.sidebar.number_input(
    "Z-score Alert Threshold",
    value=2.0,
    step=0.1
)

symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]

c1, c2 = st.sidebar.columns(2)
with c1:
    if st.button("▶ Start Stream"):
        if not st.session_state.streaming:
            st.session_state.thread = threading.Thread(
                target=lambda: asyncio.run(start_stream(symbols)),
                daemon=True
            )
            st.session_state.thread.start()
            st.session_state.streaming = True
with c2:
    if st.button("⏹ Stop Stream"):
        stop_stream()
        st.session_state.streaming = False

# ================= LOAD DATA =================
rows = get_all_ticks()
if not rows:
    st.info("Waiting for live data...")
    st.stop()

df = prepare_df(rows)

# ================= KPI ROW =================
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Ticks", len(df))
k2.metric("Symbols", df["symbol"].nunique())
k3.metric("Timeframe", timeframe)
k4.metric("Streaming", "ON" if st.session_state.streaming else "OFF")

st.divider()

# ================= CORE COMPUTATION =================
resampled = []
for sym in symbols:
    sym_df = df[df["symbol"] == sym][["timestamp", "price", "qty"]]
    bars = resample_ohlc(sym_df, timeframe)
    bars["symbol"] = sym
    resampled.append(bars)

price_bars = pd.concat(resampled)

price_chart_df = (
    price_bars
    .pivot_table(
        index="timestamp",
        columns="symbol",
        values="close",
        aggfunc="last"
    )
    .sort_index()
)

spread = zs = hedge = rolling_corr = None

if len(symbols) >= 2:
    s1, s2 = symbols[:2]

    df1 = df[df["symbol"] == s1].sort_values("timestamp")
    df2 = df[df["symbol"] == s2].sort_values("timestamp")

    n = min(len(df1), len(df2))
    df1, df2 = df1.iloc[-n:], df2.iloc[-n:]

    spread, hedge = spread_and_hedge(df1, df2)
    zs = zscore(spread, window)

    corr_df = price_chart_df[[s1, s2]].dropna()
    if len(corr_df) >= window:
        rolling_corr = rolling_correlation(
            corr_df[s1], corr_df[s2], window
        )

# ================= TABS =================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Prices", "📊 Analytics", "🧪 Tests", "📥 Export"]
)

# ---------- TAB 1 ----------
with tab1:
    st.line_chart(price_chart_df.tail(400), height=380)

# ---------- TAB 2 (ANALYTICS – CORRELATION INCLUDED) ----------
with tab2:
    if spread is None:
        st.info("Select at least two symbols")
    else:
        cA, cB = st.columns(2)
        with cA:
            st.subheader("Spread")
            st.line_chart(spread.tail(400), height=280)

        with cB:
            st.subheader("Z-score")
            st.line_chart(zs.tail(400), height=280)

        st.metric("Hedge Ratio", round(hedge, 4))

        st.subheader("Rolling Correlation")
        if rolling_corr is not None:
            st.line_chart(rolling_corr.tail(400), height=280)
        else:
            st.info("Collecting more data for correlation...")

# ---------- TAB 3 ----------
with tab3:
    if spread is not None and st.button("Run ADF Test"):
        p = adf_test(spread)
        st.metric("ADF p-value", round(p, 6))
        st.success("Stationary" if p < 0.05 else "Non-stationary")

    if zs is not None and not zs.dropna().empty:
        latest_z = zs.dropna().iloc[-1]
        z_val = round(latest_z, 3)

        if abs(z_val) >= z_threshold:
            st.markdown(
                f"""
                <div style="
                    padding:10px;
                    border-radius:8px;
                    background-color:#fee2e2;
                    color:#991b1b;
                    font-size:20px;
                    font-weight:600;
                ">
                🚨 Z-score: {z_val} (OUT OF RANGE)
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="
                    padding:10px;
                    border-radius:8px;
                    background-color:#dcfce7;
                    color:#166534;
                    font-size:20px;
                    font-weight:600;
                ">
                ✅ Z-score: {z_val} (NORMAL)
                </div>
                """,
                unsafe_allow_html=True
            )

# ---------- TAB 4 ----------
with tab4:
    price_csv = price_bars.assign(
        timestamp=price_bars["timestamp"].astype(str)
    ).to_csv(index=False)

    st.download_button(
        "Download Price Bars CSV",
        price_csv,
        file_name=f"price_bars_{timeframe}.csv",
        mime="text/csv"
    )
