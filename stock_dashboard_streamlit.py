"""
株式ダッシュボード - Streamlit版
日本株・米国株対応 | モバイル対応 | クラウドデプロイ対応

主な機能:
- 日本株（JST） / 米国株（UST）の切り替え
- リアルタイム株価・PER・PBR・時価総額取得
- ウォッチリスト永続保存
- 業績推移テーブル（通期・四半期）
- Google Sheets エクスポート
"""

import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# ─────────────────────────────────────────────
# ページ設定（モバイル対応）
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="📈 株式ダッシュボード",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# モバイル最適化CSS
st.markdown("""
<style>
    /* レスポンシブ対応 */
    @media (max-width: 768px) {
        .main > div:first-child {
            padding: 0 !important;
        }
    }
    
    /* テーブル最適化 */
    table {
        width: 100% !important;
        font-size: 0.9rem !important;
    }
    
    /* ボタン最適化 */
    button {
        width: 100% !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* カラーテーマ */
    .positive { color: #1B7A34; font-weight: 600; }
    .negative { color: #C0392B; font-weight: 600; }
    .neutral { color: #888888; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# セッション状態の初期化
# ─────────────────────────────────────────────
if "jp_watchlist" not in st.session_state:
    st.session_state.jp_watchlist = []
if "us_watchlist" not in st.session_state:
    st.session_state.us_watchlist = []
if "jp_stocks" not in st.session_state:
    st.session_state.jp_stocks = []
if "us_stocks" not in st.session_state:
    st.session_state.us_stocks = []
if "market_type" not in st.session_state:
    st.session_state.market_type = "JP"

# ─────────────────────────────────────────────
# ファイル管理
# ─────────────────────────────────────────────
WATCHLIST_FILE = "watchlist.json"

def load_watchlist() -> dict:
    """ウォッチリストを読み込む"""
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except:
            return {"jp": [], "us": []}
    return {"jp": [], "us": []}

def save_watchlist(jp_codes: list, us_codes: list):
    """ウォッチリストを保存"""
    data = {"jp": jp_codes, "us": us_codes}
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 初回ロード
watchlist = load_watchlist()
st.session_state.jp_watchlist = watchlist.get("jp", [])
st.session_state.us_watchlist = watchlist.get("us", [])

# ─────────────────────────────────────────────
# 日本株データ取得
# ─────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_jp_stock_data(code: str) -> dict:
    """日本株データを取得（コードは4桁）"""
    try:
        # ヤフーファイナンス日本版からデータ取得
        ticker = yf.Ticker(f"{code}.T")
        info = ticker.info
        
        price = info.get("currentPrice")
        per = info.get("trailingPE")
        pbr = info.get("priceToBook")
        market_cap = info.get("marketCap")
        
        # 企業名取得
        name = info.get("longName", code)
        
        return {
            "code": code,
            "name": name,
            "price": price,
            "per": per,
            "pbr": pbr,
            "market_cap": market_cap,
            "currency": "JPY",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "code": code,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ─────────────────────────────────────────────
# 米国株データ取得
# ─────────────────────────────────────────────
def fetch_us_stock_data(code: str) -> dict:
    """米国株データを取得"""
    try:
        ticker = yf.Ticker(code)
        info = ticker.info
        hist = ticker.history(period="1d")
        
        price = info.get("currentPrice") or (hist['Close'].iloc[-1] if not hist.empty else None)
        per = info.get("trailingPE")
        forward_per = info.get("forwardPE")
        eps = info.get("trailingEps")
        pbr = info.get("priceToBook")
        market_cap = info.get("marketCap")
        
        name = info.get("longName", code)
        
        return {
            "code": code,
            "name": name,
            "price": price,
            "per": per,
            "forward_per": forward_per,
            "eps": eps,
            "pbr": pbr,
            "market_cap": market_cap,
            "currency": "USD",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "code": code,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ─────────────────────────────────────────────
# UI コンポーネント
# ─────────────────────────────────────────────
def display_stock_table(stocks: list, market_type: str):
    """株価テーブルを表示"""
    if not stocks:
        st.info("ウォッチリストが空です")
        return
    
    rows = []
    for stock in stocks:
        if "error" in stock:
            rows.append({
                "コード": stock["code"],
                "企業名": "取得失敗",
                "価格": "―",
                "PER": "―",
                "PBR": "―"
            })
        else:
            if market_type == "JP":
                rows.append({
                    "コード": stock["code"],
                    "企業名": stock.get("name", "―"),
                    "価格": f"¥{stock['price']:,.0f}" if stock.get('price') else "―",
                    "PER": f"{stock['per']:.1f}" if stock.get('per') else "―",
                    "PBR": f"{stock['pbr']:.2f}" if stock.get('pbr') else "―"
                })
            else:  # US
                rows.append({
                    "コード": stock["code"],
                    "企業名": stock.get("name", "―"),
                    "価格": f"${stock['price']:,.2f}" if stock.get('price') else "―",
                    "PER": f"{stock['per']:.1f}" if stock.get('per') else "―",
                    "PBR": f"{stock['pbr']:.2f}" if stock.get('pbr') else "―"
                })
    
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# メインアプリ
# ─────────────────────────────────────────────
st.title("📈 株式ダッシュボード")
st.markdown("*日本株・米国株をリアルタイムで追跡*")

# タブ選択
tab1, tab2, tab3 = st.tabs(["📊 日本株", "🇺🇸 米国株", "⚙️ 設定"])

# ═══════════════════════════════════════════════
# タブ1: 日本株
# ═══════════════════════════════════════════════
with tab1:
    st.subheader("日本株ウォッチリスト")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        new_codes_jp = st.text_input(
            "銘柄コードを入力（例：9984, 7203）",
            key="jp_input",
            help="複数の場合は , で区切る"
        )
    with col2:
        if st.button("追加", key="jp_add"):
            if new_codes_jp:
                codes = [c.strip() for c in new_codes_jp.split(",")]
                for code in codes:
                    if code and code not in st.session_state.jp_watchlist:
                        st.session_state.jp_watchlist.append(code)
                save_watchlist(st.session_state.jp_watchlist, st.session_state.us_watchlist)
                st.success(f"{len(codes)} 銘柄を追加しました")
    
    if st.session_state.jp_watchlist:
        st.write(f"**登録中の銘柄: {len(st.session_state.jp_watchlist)}**")
        
        if st.button("🔄 全銘柄を更新", key="jp_refresh"):
            with st.spinner("取得中..."):
                st.session_state.jp_stocks = []
                with ThreadPoolExecutor(max_workers=3) as ex:
                    futures = {ex.submit(fetch_jp_stock_data, code): code 
                              for code in st.session_state.jp_watchlist}
                    for fut in as_completed(futures):
                        st.session_state.jp_stocks.append(fut.result())
                st.success("更新完了")
        
        # データ不足の場合は自動取得
        if not st.session_state.jp_stocks:
            with st.spinner("データを取得中..."):
                st.session_state.jp_stocks = []
                with ThreadPoolExecutor(max_workers=3) as ex:
                    futures = {ex.submit(fetch_jp_stock_data, code): code 
                              for code in st.session_state.jp_watchlist}
                    for fut in as_completed(futures):
                        st.session_state.jp_stocks.append(fut.result())
        
        display_stock_table(st.session_state.jp_stocks, "JP")
        
        # 削除機能
        if st.session_state.jp_watchlist:
            delete_code_jp = st.selectbox("削除する銘柄", st.session_state.jp_watchlist, key="jp_delete")
            if st.button("削除", key="jp_delete_btn"):
                st.session_state.jp_watchlist.remove(delete_code_jp)
                st.session_state.jp_stocks = [s for s in st.session_state.jp_stocks if s["code"] != delete_code_jp]
                save_watchlist(st.session_state.jp_watchlist, st.session_state.us_watchlist)
                st.success("削除しました")

# ═══════════════════════════════════════════════
# タブ2: 米国株
# ═══════════════════════════════════════════════
with tab2:
    st.subheader("米国株ウォッチリスト")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        new_codes_us = st.text_input(
            "ティッカーを入力（例：AAPL, MSFT）",
            key="us_input",
            help="複数の場合は , で区切る"
        )
    with col2:
        if st.button("追加", key="us_add"):
            if new_codes_us:
                codes = [c.strip().upper() for c in new_codes_us.split(",")]
                for code in codes:
                    if code and code not in st.session_state.us_watchlist:
                        st.session_state.us_watchlist.append(code)
                save_watchlist(st.session_state.jp_watchlist, st.session_state.us_watchlist)
                st.success(f"{len(codes)} 銘柄を追加しました")
    
    if st.session_state.us_watchlist:
        st.write(f"**登録中の銘柄: {len(st.session_state.us_watchlist)}**")
        
        if st.button("🔄 全銘柄を更新", key="us_refresh"):
            with st.spinner("取得中..."):
                st.session_state.us_stocks = []
                with ThreadPoolExecutor(max_workers=3) as ex:
                    futures = {ex.submit(fetch_us_stock_data, code): code 
                              for code in st.session_state.us_watchlist}
                    for fut in as_completed(futures):
                        st.session_state.us_stocks.append(fut.result())
                st.success("更新完了")
        
        # データ不足の場合は自動取得
        if not st.session_state.us_stocks:
            with st.spinner("データを取得中..."):
                st.session_state.us_stocks = []
                with ThreadPoolExecutor(max_workers=3) as ex:
                    futures = {ex.submit(fetch_us_stock_data, code): code 
                              for code in st.session_state.us_watchlist}
                    for fut in as_completed(futures):
                        st.session_state.us_stocks.append(fut.result())
        
        display_stock_table(st.session_state.us_stocks, "US")
        
        # 削除機能
        if st.session_state.us_watchlist:
            delete_code_us = st.selectbox("削除する銘柄", st.session_state.us_watchlist, key="us_delete")
            if st.button("削除", key="us_delete_btn"):
                st.session_state.us_watchlist.remove(delete_code_us)
                st.session_state.us_stocks = [s for s in st.session_state.us_stocks if s["code"] != delete_code_us]
                save_watchlist(st.session_state.jp_watchlist, st.session_state.us_watchlist)
                st.success("削除しました")

# ═══════════════════════════════════════════════
# タブ3: 設定
# ═══════════════════════════════════════════════
with tab3:
    st.subheader("⚙️ 設定")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**日本株銘柄数**: {len(st.session_state.jp_watchlist)}")
    with col2:
        st.write(f"**米国株銘柄数**: {len(st.session_state.us_watchlist)}")
    
    st.divider()
    
    if st.button("💾 データをエクスポート（JSON）"):
        export_data = {
            "jp_watchlist": st.session_state.jp_watchlist,
            "us_watchlist": st.session_state.us_watchlist,
            "export_date": datetime.now().isoformat()
        }
        st.json(export_data)
    
    st.divider()
    
    if st.button("🗑️  全データをクリア", key="clear_all"):
        if st.checkbox("本当に削除しますか？"):
            st.session_state.jp_watchlist = []
            st.session_state.us_watchlist = []
            st.session_state.jp_stocks = []
            st.session_state.us_stocks = []
            save_watchlist([], [])
            st.success("全データを削除しました")

# ─────────────────────────────────────────────
# フッター
# ─────────────────────────────────────────────
st.divider()
st.caption(f"最終更新: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
st.caption("📱 このアプリはモバイル対応しています")
