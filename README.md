# Markdown to HTML Converter

日本語文書に特化したMarkdown to HTML変換ツールです。A4印刷に最適化された美しいスタイリングと、Python 3.12の型システムを活用した堅牢な設計が特徴です。

## 🎯 主な用途

- **技術文書作成**: API仕様書、開発ドキュメント
- **研究文書**: 論文、研究レポート、学会発表資料
- **ビジネス文書**: 社内マニュアル、報告書、提案書
- **Web公開**: ブログ記事、ドキュメントサイト

## ✨ 特徴

### 1. 日本語文書に最適化
- 美しい日本語フォント設定（BIZ UDPGothic, Hiragino Sans等）
- 文字間隔とレイアウトの最適化
- レスポンシブデザインでの日本語表示調整

### 2. A4印刷サポート
- A4サイズに最適化されたマージン設定（20mm）
- 印刷時の画像サイズ自動調整
- 印刷プレビュー機能
- ヘッダー/フッターのカスタマイズ

### 3. 使いやすい画像処理
- 画像の自動分類（バッジ、アバター、バナー等）
- サイズプリセット（small/medium/large）
- レスポンシブ画像の自動生成
- 印刷時の最適化

### 4. カスタマイズ機能
- ダークモード対応
- カスタムCSSサポート
- フォント設定のカスタマイズ
- 並列処理数の調整

## 🚀 クイックスタート

### uvのインストール
```bash
# Unix系（macOS/Linux）
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows（PowerShell）
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### インストール
```bash
# 安定版のインストール
uv pip install markdown2html

# 開発版のインストール
uv pip install git+https://github.com/tsutomu-n/markdown2html.git
```

## 📝 基本的な使い方

### 1. 単一ファイルの変換
```bash
python -m m2h convert example.md
```

### 2. ディレクトリ一括変換
```bash
python -m m2h convert --input-dir ./docs
```

### 3. カスタマイズオプション
```bash
# ダークモードで変換
python -m m2h convert --dark-mode

# カスタムCSSを適用
python -m m2h convert --custom-css ./style.css

# 並列処理数を設定
python -m m2h convert --max-workers 8
```

### 4. 画像サイズの指定
```markdown
# Markdownファイル内での指定方法
![説明文{:size-small}](image.png)
![説明文{:size-medium}](image.png)
![説明文{:size-large}](image.png)
```

## 🛠️ 開発環境のセットアップ

### 1. リポジトリのクローン
```bash
git clone https://github.com/tsutomu-n/markdown2html.git
cd markdown2html
```

### 2. Python環境のセットアップ
```bash
# Python 3.12のインストール
uv python install 3.12

# 仮想環境の作成と有効化
uv venv
source .venv/bin/activate  # Unix系
# または
.venv\Scripts\Activate.ps1  # Windows
```

### 3. 依存関係のインストール
```bash
# 開発用依存関係を含めてインストール
uv pip install -e ".[dev]"

# 依存関係の同期
uv sync
```

## 📦 依存関係

### 必須パッケージ
```toml
[project]
dependencies = [
    "markdown>=3.7",
    "types-markdown>=3.7.0",
    "pydantic>=2.10.5",
    "typer[all]>=0.9.0",
]
```

### 開発用パッケージ
```toml
[project.optional-dependencies]
dev = [
    "mypy>=1.8.0",
    "ruff>=0.2.0",
    "pytest>=8.0.0",
]
```

## 🔍 トラブルシューティング

### よくある問題と解決方法

1. **変換エラー**
```bash
# デバッグモードで実行
python -m m2h convert --debug
```

2. **フォントの問題**
- カスタムCSSで独自のフォント設定を追加
- システムにフォントがインストールされているか確認

3. **画像の表示問題**
- 画像パスが正しいか確認
- サイズ指定の構文を確認

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。
