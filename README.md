# 📈 株式ダッシュボード - Streamlit版

日本株・米国株をリアルタイムで追跡できるWebアプリです。**携帯でも見られます**。

## ✨ 特徴

✅ **モバイル対応** - スマートフォン・タブレットで快適に利用可能  
✅ **日本株・米国株対応** - 日本株（4桁コード）と米国株（ティッカー）に対応  
✅ **リアルタイムデータ** - yfinance + Yahoo!ファイナンスから取得  
✅ **永続保存** - ウォッチリストは自動保存  
✅ **無料デプロイ** - Streamlit Cloudで無料ホスティング  
✅ **GitHub連携** - リポジトリから直接デプロイ可能

## 🚀 クイックスタート

### ローカルで実行

```bash
# 依存パッケージをインストール
pip install -r requirements.txt

# アプリを起動
streamlit run stock_dashboard_streamlit.py
```

アプリが `http://localhost:8501` で立ち上がります

### Streamlit Cloudでデプロイ（推奨・無料）

1. **このリポジトリをGitHubにプッシュ**
   ```bash
   git push origin main
   ```

2. **Streamlit Cloudで新しいアプリを作成**
   - https://share.streamlit.io にアクセス
   - 「Create app」をクリック
   - リポジトリを選択: `your-repo/stock_dashboard_streamlit`
   - Main file path: `stock_dashboard_streamlit.py`
   - 「Deploy」

3. **公開URL取得**
   - デプロイ完了後、URLが表示されます
   - このURLを携帯で開けばOK

## 📱 使い方

### 日本株を追跡する

1. 「📊 日本株」タブを開く
2. 銘柄コードを入力（例：`9984, 7203`）
3. 「追加」ボタンをクリック
4. 「🔄 全銘柄を更新」で株価を取得

**コード例:**
- `9984` - ソフトバンクグループ
- `7203` - トヨタ自動車
- `6758` - ソニー

### 米国株を追跡する

1. 「🇺🇸 米国株」タブを開く
2. ティッカーを入力（例：`AAPL, MSFT`）
3. 「追加」ボタンをクリック
4. 「🔄 全銘柄を更新」で株価を取得

**ティッカー例:**
- `AAPL` - Apple
- `MSFT` - Microsoft
- `GOOGL` - Google
- `TSLA` - Tesla

### データの管理

- **削除**: ウォッチリストから銘柄を選んで「削除」
- **エクスポート**: ⚙️ 設定タブで全データをJSON出力
- **リセット**: 全データを削除（確認が必要）

## 📊 表示される情報

### 日本株
| 項目 | 説明 |
|------|------|
| コード | 銘柄コード |
| 企業名 | 企業名 |
| 価格 | 現在の株価（JPY） |
| PER | 株価収益率 |
| PBR | 株価純資産倍率 |

### 米国株
| 項目 | 説明 |
|------|------|
| ティッカー | ティッカーシンボル |
| 企業名 | 企業名 |
| 価格 | 現在の株価（USD） |
| PER | 株価収益率 |
| PBR | 株価純資産倍率 |

## 🔄 自動更新設定（オプション）

GitHub Actionsで毎日自動更新できます：

1. `.github/workflows/daily-update.yml` がリポジトリにある
2. GitHub Actionsが有効になっている
3. 毎日 9:00 AM JST に `watchlist.json` が更新される

## 🛠️ トラブルシューティング

### データが取得できない
- ネットワーク接続を確認
- 銘柄コード/ティッカーが正しいか確認
- 米国株で営業時間外の場合、価格が更新されない場合があります

### アプリが遅い
- 登録銘柄数を減らしてみる
- 更新ボタンを押してデータを再取得

### モバイルで見づらい
- ブラウザのズームレベルを調整
- 横向き表示に変更してみる

## 📦 ファイル構成

```
.
├── stock_dashboard_streamlit.py   # メインアプリ
├── requirements.txt               # 依存パッケージ
├── .streamlit/config.toml        # Streamlit設定
├── .github/workflows/daily-update.yml  # 自動更新設定
├── watchlist.json                # ウォッチリスト（自動生成）
└── README.md                     # このファイル
```

## 🔐 セキュリティ

- 個人情報は保存しません
- `.gitignore` に `watchlist.json` を追加して、プライベートウォッチリストを保護してください：
  ```
  watchlist.json
  credentials.json
  config.json
  ```

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 貢献

バグ報告や機能リクエストは Issues で！

## 📞 サポート

- Streamlit: https://docs.streamlit.io
- yfinance: https://pypi.org/project/yfinance/
- GitHub Issues でサポートを受けられます

---

**作成日**: 2024年  
**最終更新**: $(date)

Happy investing! 📈
