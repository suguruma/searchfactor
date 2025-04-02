# 🔍 SearchFactor

FastAPI × Azure App Service による  
**「Excel/CSVテンプレートを自動モデル化 → 異常原因検索」**ツールです。

---

## 📌 主な機能

- Excel または CSV ファイルから異常原因テンプレートをアップロード
- SentenceTransformer によりベクトル化（モデル化）
- FAISS による類似検索
- 自然言語で原因を問い合わせ可能
- Web UI でのファイルアップロード・検索対応

---

## 🚀 ローカルでの実行方法

### 1. 必要ライブラリのインストール

```bash
pip install -r requirements.txt