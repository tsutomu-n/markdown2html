# Markdown to HTML Converter

日本語文書に特化したMarkdown to HTML変換ツールです。A4印刷に最適化された美しいスタイリングと、Python 3.12の型システムを活用した堅牢な設計が特徴です。

## 特徴

### 1. 日本語文書に最適化
- 日本語フォントの最適な設定（Hiragino Sans, BIZ UDPGothic等）
- 文字間隔とレイアウトの日本語最適化
- 和文約物（句読点等）の配置調整
- 日本語フォントのウェイト調整
- 縦書きテキストのサポート
- ルビ（ふりがな）の適切な表示

### 2. A4印刷サポート
- A4サイズに最適化されたマージン設定
- 印刷時の改ページ制御
- 見出しレベルに応じた適切な改ページ
- モノクロ印刷を考慮したコントラスト
- PDFエクスポート対応（WeasyPrint統合）
- ヘッダー/フッターのカスタマイズ
- 印刷プレビュー機能

### 3. 堅牢な型システム
- 静的型チェックに対応（mypy）
- Pydanticによるデータバリデーション
- Optional型による安全な値の取り扱い
- データクラスの活用
- 型安全な設定管理
- カスタム型定義のサポート

### 4. 効率的な並行処理
- ThreadPoolExecutorによる並列処理
- 複数のファイルを同時に処理
- 処理状況のリアルタイムログ出力
- プログレスバー表示（Rich統合）
- キャンセル可能な変換処理
- エラーハンドリングと自動リトライ

### 5. 拡張性とカスタマイズ
- カスタムMarkdown拡張のサポート
- プラグインシステム
- カスタムCSSの適用
- テンプレートのカスタマイズ
- フォントの柔軟な設定
- 独自の変換ルールの追加

### 6. 画像処理機能
- 画像の自動最適化
- レスポンシブ画像の生成
- 画像の自動分類（バッジ、アバター等）
- 画像キャプションの自動生成
- 画像の遅延読み込み対応
- WebP形式への自動変換

### 7. スタイリング機能
- ダークモード対応
- レスポンシブデザイン
- カスタムテーマ
- シンタックスハイライト
- 数式表示（MathJax/KaTeX）
- 図表のスタイリング

### 8. 開発者支援機能
- 詳細なログ出力
- デバッグモード
- パフォーマンス分析
- テストカバレッジ
- コード品質チェック（Ruff）
- ドキュメント生成

### 9. セキュリティ機能
- 安全なリソース読み込み
- XSS対策
- リソースの検証
- アクセス制御
- セキュアな設定管理
- エラーメッセージの制御

### 10. ユーティリティ機能
- 目次の自動生成
- ページ番号の制御
- クロスリファレンス
- メタデータ管理
- バックアップ生成
- 一括変換機能

### 11. アクセシビリティ
- WAI-ARIA対応
- キーボードナビゲーション
- スクリーンリーダー最適化
- 高コントラストモード
- フォントサイズの調整
- 代替テキストの管理

### 12. パフォーマンス最適化
- キャッシュシステム
- 差分変換
- リソースの最適化
- メモリ使用量の制御
- 処理の優先順位付け
- バッチ処理の最適化






# markdown2htmlプロジェクトのセットアップガイド

## 1. 前提条件

### 必要なツール
````bash
# uvのインストール
# Unix系（macOS/Linux）
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows（PowerShell）
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# シェルの再起動または環境変数の更新
exec $SHELL  # Unix系
# Windowsの場合は新しいPowerShellウィンドウを開く
````


## 2. プロジェクトのセットアップ

### リポジトリのクローン
````bash
# SSHを使用する場合
git clone git@github.com:tsutomu-n/markdown2html.git

# HTTPSを使用する場合
git clone https://github.com/tsutomu-n/markdown2html.git

cd markdown2html
````


### Python環境のセットアップ
````bash
# Python 3.12のインストール
uv python install 3.12

# 仮想環境の作成
uv venv

# 仮想環境の有効化
# Unix系（bash/zsh）
source .venv/bin/activate
# Windows（PowerShell）
.venv\Scripts\Activate.ps1
````


### 依存関係のインストール
````bash
# プロジェクトの依存関係をインストール（開発用パッケージを含む）
uv pip install -e ".[dev]"

# 依存関係の同期（requirements.lockの生成/更新）
uv sync
````


## 3. 開発環境のセットアップ

### 開発ツールのインストール
````bash
# 必要な開発ツールをグローバルにインストール
uv tool install ruff mypy pytest
````


### エディタ/IDEの設定

VSCode使用時の推奨設定（`.vscode/settings.json`）:
````json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.analysis.typeCheckingMode": "strict",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true,
        "source.fixAll": true
    },
    "python.formatting.provider": "ruff",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true
}
````


## 4. 動作確認

### テストの実行
````bash
# テストスイートの実行
pytest

# カバレッジレポート付きでテスト実行
pytest --cov=markdown2html --cov-report=term-missing
````


### コード品質チェック
````bash
# 型チェック
mypy markdown2html

# リンティング
ruff check .

# フォーマット
ruff format .
````


### 基本的な動作確認
````bash
# サンプルの変換を実行
mkdir -p markdown
echo "# Test" > markdown/test.md
python -m markdown2html convert
````


## 5. プロジェクト構造の確認

````bash
# 必要なディレクトリの作成
mkdir -p markdown html css logs tests

# ディレクトリ構造
markdown2html/
├── markdown/          # 入力ファイル用
├── html/             # 出力ファイル用
├── css/              # カスタムCSS
├── logs/             # ログファイル
├── tests/            # テストファイル
├── .venv/            # 仮想環境
├── .git/             # Gitリポジトリ
├── .gitignore        # Git除外設定
├── pyproject.toml    # プロジェクト設定
└── README.md         # ドキュメント
````


## 6. 開発時の推奨プラクティス

### コミット前のチェック
````bash
# 全てのチェックを実行
mypy markdown2html && \
ruff check . && \
ruff format . && \
pytest
````


### 依存関係の更新
````bash
# 依存関係の更新が必要な場合
uv pip install -e ".[dev]" --upgrade
uv sync
````


### ログの確認
````bash
# 最新のログファイルを確認
tail -f logs/conversion_*.log
````


## 7. トラブルシューティング

### 一般的な問題の解決
````bash
# 仮想環境のリセット
deactivate  # 既存の仮想環境を無効化
rm -rf .venv
uv venv
source .venv/bin/activate  # または .venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"

# キャッシュのクリア
rm -rf __pycache__ .pytest_cache .mypy_cache
````


このセットアップ方法により、開発環境が適切に構成され、効率的な開発が可能になります。また、コード品質の維持と一貫性のある開発環境の確保が可能です。


## 使用方法

### 基本的な使用方法

1. 入力/出力ディレクトリの設定:
```python
INPUT_DIR: Final[str] = r"C:\tools\2025-yu-plan\markdown"
OUTPUT_DIR: Final[str] = r"C:\tools\2025-yu-plan\html"
```

2. 実行:
```bash
uv run markdown2html.py
```

### 高度な使用方法

1. カスタムスタイルの適用:
```python
CUSTOM_CSS: Final[str] = "path/to/custom.css"
```

2. 並列処理の調整:
```python
MAX_WORKERS: Final[int] = 4  # 並列処理数の設定
```

## 技術的特徴

### 1. 堅牢な型システム
- 静的型チェックに対応（mypy）
- Pydanticによるデータバリデーション
- Optional型による安全な値の取り扱い
- データクラスの活用

### 2. 効率的な並行処理
- ThreadPoolExecutorによる並列処理
- 複数のファイルを同時に処理
- 処理状況のリアルタイムログ出力
- プログレスバー表示

### 3. スタイリング
- レスポンシブデザイン
- ダークモード対応
- A4印刷用に最適化されたCSSスタイル
- アクセシビリティ対応
- カスタムフォント設定

### 4. エラーハンドリング
- 構造化されたエラーログ
- 失敗時の適切なフォールバック
- デバッグモードサポート
- エラー通知機能

## 開発者向け情報

### 開発環境のセットアップ
```bash
# 開発用依存関係のインストール
uv pip install -e ".[dev]"

# 型チェックの実行
mypy .

# コードフォーマット
ruff format .
```

### テスト実行
```bash
pytest tests/
```

## 技術要件

### 必須パッケージ
- markdown>=3.7
- types-markdown>=3.7.0.20241204
- pillow>=11.1.0
- pydantic>=2.10.5
- rich>=13.9.4
- typer[all]>=0.15.1

### 開発用パッケージ
- mypy
- ruff
- pytest
- types-Pillow

## ライセンス
MIT License


---


このファイルについて日本語で解説いたします：

### 概要
このプログラムは、Markdownファイルを日本語に最適化されたHTMLに変換するツールです。A4印刷への対応や型安全性を重視した設計となっています。

### 主要な機能

1. **ログ管理システム**
- 詳細なログ記録
- ログのローテーションと自動アーカイブ
- デバッグモードのサポート

2. **設定管理**
- Pydanticを使用した型安全な設定管理
- カスタムCSSのサポート
- フォント設定のカスタマイズ機能

3. **画像処理機能**
- 画像の自動分類（バッジ、アバター、バナーなど）
- レスポンシブな画像表示
- 印刷時の最適化

4. **HTMLテンプレート**
- ダークモード対応
- A4印刷に最適化されたレイアウト
- レスポンシブデザイン

5. **変換処理**
- 並列処理による高速な変換
- 詳細なエラーハンドリング
- 進捗状況の視覚的表示

### 技術的な特徴

1. **モダンなライブラリの活用**
- Typer: CLIインターフェース
- loguru: 高度なログ管理
- rich: リッチなターミナル出力
- Pydantic: データバリデーション

2. **型安全性**
- データクラスの活用
- 型アノテーションの徹底
- Pydanticモデルによる設定管理

3. **拡張性**
- モジュール化された設計
- カスタマイズ可能なコンポーネント
- 明確な責務分離

このツールは、特に日本語コンテンツを扱う開発者やチーム向けに、高品質なHTML文書を生成するための総合的なソリューションを提供します。


---

<thought_process>
より詳細な機能分析を行います：

1. コードの主要セクション:
   - ログ管理システム
   - 設定モデル
   - HTMLテンプレート
   - 画像処理
   - 変換処理
   - CLI機能

2. 各セクションの重要ポイント:
   - エラーハンドリング方法
   - カスタマイズ可能なポイント
   - 拡張機能の実装方法
   - パフォーマンス最適化
</thought_process>

### 1. ログ管理システム (`LogManager`, `LogConfig`)

#### 主要機能
```python
class LogManager:
    def setup_logger(self, debug: bool, input_dir: Path, ...) -> None
    def cleanup_old_logs(self) -> None
```

- **ログローテーション**
  - 1週間ごとのローテーション
  - 4週間の保持期間
  - 最大ログサイズ（10MB）の制御

- **アーカイブ機能**
  - 古いログの自動ZIP圧縮
  - タイムスタンプ付きアーカイブ
  - ディレクトリ構造の維持

- **デバッグモード**
  - 詳細なスタックトレース
  - 診断情報の出力
  - エラーの詳細表示

### 2. 設定モデル (`ConfigModel`)

#### 設定項目
```python
class ConfigModel(BaseModel):
    input_dir: Path
    output_dir: Path
    max_workers: int
    custom_css_path: Path | None
    dark_mode: bool
    font_settings: dict[str, str]
```

- **フォント設定**
  - 日本語フォントの優先順位設定
  - フォールバックフォントの指定
  - カスタムフォント対応

- **Markdown拡張設定**
  - 基本拡張機能（tables, footnotes等）
  - カスタム拡張機能の追加
  - 設定のバリデーション

### 3. 画像処理システム

#### 画像パターン管理
```python
class ImagePattern:
    name: str
    patterns: tuple[Pattern[str], ...]
    css_class: str
    priority: int
```

- **自動分類機能**
  - バッジ画像の検出
  - アバター画像の識別
  - バナー画像の処理

- **サイズ制御**
  - レスポンシブ対応
  - 印刷時の最適化
  - カスタムサイズクラス

### 4. HTMLテンプレート生成

#### テンプレート機能
```python
@dataclass(frozen=True)
class HtmlTemplate:
    title: str
    content: str
    dark_mode: bool
    custom_css: str
    font_family: str
```

- **スタイル設定**
  - ダークモード対応
  - A4印刷最適化
  - レスポンシブデザイン

- **ユーティリティ機能**
  - テーマ切り替えボタン
  - 印刷ボタン
  - アクセシビリティ対応

### 5. Markdown変換処理

#### 変換機能
```python
def convert_markdown_content(content: str, extensions: list[str | Extension]) -> str
def convert_markdown_to_html(file_path: Path, status: ConversionStatus, ...) -> None
```

- **拡張機能対応**
  - カスタム拡張機能
  - 画像処理拡張
  - 日本語最適化

- **エラーハンドリング**
  - 詳細なエラー報告
  - リカバリー機能
  - ログ記録

### 6. CLI機能 (Typer)

#### コマンドライン機能
```python
@app.command()
def convert(
    input_dir: InputDirArg,
    output_dir: OutputDirOpt,
    max_workers: int,
    custom_css: CssFileOpt,
    dark_mode: bool,
    debug: bool,
) -> None
```

- **オプション設定**
  - 入力/出力ディレクトリ指定
  - 並列処理数制御
  - デバッグモード切替

- **進捗表示**
  - リッチな進捗バー
  - エラー状況の表示
  - 変換サマリーの出力

### 7. パフォーマンス最適化

#### 最適化機能
- **並列処理**
  - マルチスレッド変換
  - プログレスバー表示
  - リソース使用量の制御

- **キャッシュ機能**
  - 画像パターンのキャッシュ
  - 変換結果のキャッシュ
  - メモリ使用量の最適化

### 8. エラーハンドリング

#### カスタム例外
```python
class MarkdownError(Exception): pass
class ConversionError(MarkdownError): pass
class ConfigurationError(MarkdownError): pass
class ResourceError(MarkdownError): pass
```

- **エラー管理**
  - 階層化されたエラー構造
  - 詳細なエラーメッセージ
  - リカバリー処理

このツールは、特に日本語コンテンツの処理に重点を置きながら、高度なカスタマイズ性と拡張性を備えた総合的なMarkdown変換ソリューションを提供します。各機能は独立したモジュールとして設計されており、必要に応じて機能の追加や修正が容易に行えます。


---



# Markdown→HTML変換ツールの使用方法

## 1. 基本的な使い方

### インストールと準備

```bash
# リポジトリをクローン（または必要なファイルをダウンロード）
git clone <repository-url>
cd <project-directory>

# 必要なパッケージのインストール
pip install typer loguru rich pydantic markdown
```

### 基本的なコマンド実行

```bash
# 最もシンプルな使用方法（デフォルトディレクトリを使用）
python m2h.py convert

# 入力ディレクトリを指定
python m2h.py convert --input-dir ./my_markdown

# 出力ディレクトリを指定
python m2h.py convert --input-dir ./my_markdown --output-dir ./my_html
```

## 2. ディレクトリ構造

推奨されるディレクトリ構造:
```
project/
├── markdown/          # デフォルトの入力ディレクトリ
│   ├── doc1.md
│   └── doc2.md
├── html/             # デフォルトの出力ディレクトリ
├── css/              # カスタムCSSファイル用
│   └── custom.css
└── logs/             # ログファイル保存先
```

## 3. 高度な使用方法

### カスタムCSSの適用

```bash
# カスタムCSSファイルを指定して実行
python m2h.py convert --custom-css ./css/custom.css
```

### ダークモードの有効化

```bash
# ダークモードを有効にして実行
python m2h.py convert --dark-mode
```

### 並列処理数の調整

```bash
# 並列処理数を8に設定
python m2h.py convert --max-workers 8
```

### デバッグモードの使用

```bash
# デバッグモードを有効にして実行
python m2h.py convert --debug
```

## 4. 画像の最適化

Markdownファイル内での画像指定方法:

```markdown
# 通常の画像
![説明文](image.png)

# サイズ指定付き画像
![説明文{:size-small}](image.png)
![説明文{:size-medium}](image.png)
![説明文{:size-large}](image.png)
```

## 5. カスタマイズ例

### カスタムCSSファイルの例

```css
/* css/custom.css */
:root {
  --color-text: #333;
  --color-bg: #fff;
  --color-link: #0066cc;
}

body {
  font-family: "游ゴシック", YuGothic, "メイリオ", Meiryo, sans-serif;
  line-height: 1.8;
}

/* カスタムスタイルの追加 */
.custom-box {
  border: 1px solid #ccc;
  padding: 1em;
  margin: 1em 0;
}
```

### 実践的な使用例

#### 1. ドキュメント変換（基本）

```bash
# プロジェクトのドキュメントを変換
python m2h.py convert --input-dir ./docs --output-dir ./public_docs
```

#### 2. ブログ記事の変換（カスタマイズ付き）

```bash
# ブログ記事をダークモードで変換
python m2h.py convert \
  --input-dir ./blog_posts \
  --output-dir ./public_blog \
  --custom-css ./css/blog_style.css \
  --dark-mode
```

#### 3. 技術文書の変換（デバッグモード）

```bash
# 技術文書を詳細なログ付きで変換
python m2h.py convert \
  --input-dir ./technical_docs \
  --output-dir ./public_tech \
  --debug \
  --max-workers 4
```

## 6. エラー対処

よくあるエラーと解決方法:

1. **入力ディレクトリが見つからない**
   ```bash
   # 入力ディレクトリの作成
   mkdir markdown
   # Markdownファイルを配置後に実行
   python m2h.py convert
   ```

2. **カスタムCSSが読み込めない**
   ```bash
   # パスが正しいか確認
   python m2h.py convert --custom-css ./css/custom.css --debug
   ```

3. **変換エラー**
   ```bash
   # デバッグモードで詳細を確認
   python m2h.py convert --debug
   # ログファイルを確認
   cat logs/conversion_YYYYMMDD_HHMMSS.log
   ```

## 7. ベストプラクティス

1. **ディレクトリ構造の整理**
   - Markdownファイルは適切にカテゴリ分けする
   - 画像は専用のディレクトリに配置

2. **定期的なログクリーンアップ**
   - 古いログファイルは自動的にアーカイブされる
   - 必要に応じて手動でログをクリーンアップ

3. **効率的な変換**
   - 大量のファイルを処理する場合は`max-workers`を調整
   - 必要に応じてカスタムCSSを活用

4. **デバッグとトラブルシューティング**
   - 問題が発生した場合は`--debug`オプションを使用
   - ログファイルを確認して詳細を把握

このツールを効果的に使用することで、日本語のMarkdownコンテンツを高品質なHTMLに変換できます。特に技術文書やブログ記事の変換に適しています。

---
