from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import (
    Annotated,
    Any,
    Final,
    Optional,
    Pattern,
)
from urllib.parse import urlparse
from xml.etree.ElementTree import Element

import typer
from loguru import logger
from pydantic import BaseModel, Field, field_validator
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.tree import Tree
from typing_extensions import Self  # Python 3.11未満で必要

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

"""
単一ファイル版:
日本語最適化 & A4印刷対応 & 型安全性を備えたMarkdown→HTML変換ツール
"""

app = typer.Typer(help="Markdown to HTML Converter with Typer+loguru+rich")


# ==========================
# 基本設定
# ==========================
LOG_DIR: Final[Path] = Path("logs")
LOG_ARCHIVE_DIR: Final[Path] = LOG_DIR / "archive"
MAX_LOG_SIZE_MB: Final[int] = 10
MAX_LOG_SIZE: Final[int] = MAX_LOG_SIZE_MB * 1024 * 1024


@dataclass
class LogConfig:
    """ログ設定を管理するデータクラス"""

    format: str = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Markdown to HTML Conversion Log
Started at: {time:YYYY-MM-DD HH:mm:ss}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{message}
"""
    rotation: str = "1 week"
    retention: str = "4 weeks"
    encoding: str = "utf-8"


class LogManager:
    """ログ管理クラス"""

    def __init__(self) -> None:
        self.config = LogConfig()
        self._setup_directories()

    def _setup_directories(self) -> None:
        """ログディレクトリの初期設定"""
        LOG_DIR.mkdir(exist_ok=True)
        LOG_ARCHIVE_DIR.mkdir(exist_ok=True)

    def cleanup_old_logs(self) -> None:
        """古いログファイルの管理"""
        try:
            if not LOG_DIR.exists():
                return

            total_size = sum(f.stat().st_size for f in LOG_DIR.glob("*.log"))

            if total_size > MAX_LOG_SIZE:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"logs_until_{timestamp}"
                archive_path = LOG_ARCHIVE_DIR / archive_name

                shutil.make_archive(
                    str(archive_path),
                    "zip",
                    str(LOG_DIR),
                    logger=logger,
                )

                for log_file in LOG_DIR.glob("*.log"):
                    if log_file.stem != f"conversion_{timestamp}":
                        log_file.unlink()

                logger.info(f"Archived old logs to: {archive_name}.zip")

        except Exception as e:
            logger.warning(f"Failed to cleanup logs: {e}")

    def setup_logger(
        self,
        debug: bool = False,
        input_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        dark_mode: bool = False,
        custom_css: Optional[Path] = None,
    ) -> None:
        """ロガーの設定と初期化"""
        try:
            self.cleanup_old_logs()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = LOG_DIR / f"conversion_{timestamp}.log"

            logger.remove()

            # ファイルログの設定
            logger.add(
                log_file,
                format=self.config.format,
                level="DEBUG" if debug else "INFO",
                rotation=self.config.rotation,
                retention=self.config.retention,
                encoding=self.config.encoding,
                backtrace=debug,
                diagnose=debug,
                enqueue=True,
            )

            # エラーログの設定（ターミナル出力）
            logger.add(
                sys.stderr,
                format="<red>{level: <8}</red> | {message}",
                level="ERROR",
                colorize=True,
                backtrace=False,
            )

            summary = [
                "Configuration Summary:",
                "-------------------",
                f"Input Directory: {input_dir or 'Using default'}",
                f"Output Directory: {output_dir or './html'}",
                f"Debug Mode: {'Enabled' if debug else 'Disabled'}",
                f"Dark Mode: {'Enabled' if dark_mode else 'Disabled'}",
                f"Custom CSS: {custom_css or 'None'}",
                f"Log File: {log_file.name}",
                f"Max Log Size: {MAX_LOG_SIZE_MB}MB",
                f"Archive Directory: {LOG_ARCHIVE_DIR}",
            ]
            logger.info("\n".join(summary))

        except Exception as e:
            print(f"Failed to setup logger: {e}", file=sys.stderr)
            raise typer.Exit(code=1) from e

    @classmethod
    def create(cls) -> Self:
        """LogManagerのインスタンスを作成するファクトリメソッド"""
        return cls()


# グローバルなログマネージャーのインスタンス
log_manager = LogManager.create()


# カスタム例外の定義
class MarkdownError(Exception):
    """Markdownに関連する基本例外クラス"""

    pass


class ConversionError(MarkdownError):
    """変換処理に関連するエラー"""

    pass


class ConfigurationError(MarkdownError):
    """設定に関連するエラー"""

    pass


class ResourceError(MarkdownError):
    """リソース（ファイル、ディレクトリ）に関連するエラー"""

    pass


# ==========================
# 1. 設定モデル
# ==========================
class ConfigModel(BaseModel):
    input_dir: Path
    output_dir: Path
    max_workers: int = Field(gt=0, description="並列処理数(>0)")

    # カスタマイズオプション
    custom_css_path: Path | None = Field(None, description="カスタムCSSファイルのパス")
    dark_mode: bool = Field(False, description="ダークモードを有効にするか")
    font_settings: dict[str, str] = Field(
        default_factory=lambda: {
            "primary": "BIZ UDPGothic",
            "secondary": "Hiragino Sans",
            "fallback": "Noto Sans JP",
        }
    )

    # Markdown拡張設定
    markdown_extensions: list[str] = Field(
        default_factory=lambda: [
            "extra",
            "nl2br",
            "sane_lists",
            "footnotes",
            "tables",
        ]
    )

    @field_validator("custom_css_path")
    def validate_css_path(cls, v: Path | None) -> Path | None:
        if v and not v.exists():
            raise ValueError(f"Custom CSS file not found: {v}")
        return v

    def load_custom_css(self) -> str:
        """カスタムCSSの読み込み"""
        if not self.custom_css_path:
            return ""
        try:
            return self.custom_css_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to load custom CSS: {e}")
            return ""

    def get_font_family(self) -> str:
        """フォントファミリー設定の生成"""
        fonts = [
            self.font_settings["primary"],
            self.font_settings["secondary"],
            self.font_settings["fallback"],
            "sans-serif",
        ]
        return ", ".join(f'"{f}"' if " " in f else f for f in fonts)


# ==========================
# 2. HTMLテンプレート(A4印刷 & 日本語用CSS)
# ==========================
@dataclass(frozen=True)
class ImagePattern:
    """画像パターンの定義クラス（イミュータブル）"""

    name: str
    patterns: tuple[Pattern[str], ...]
    css_class: str
    priority: int = 0

    @classmethod
    def compile(
        cls, name: str, patterns: list[str], css_class: str, priority: int = 0
    ) -> "ImagePattern":
        """パターンをコンパイルしてImagePatternを作成"""
        return cls(
            name=name,
            patterns=tuple(re.compile(p, re.IGNORECASE) for p in patterns),
            css_class=css_class,
            priority=priority,
        )


class ImageConfig:
    """画像設定の管理クラス"""

    DEFAULT_PATTERNS = (
        ImagePattern.compile(
            name="badge",
            patterns=[
                r"crates\.io",
                r"pypi",
                r"zenodo",
                r"badge",
                r"shields\.io",
                r"passing",
                r"build",
                r"status",
                r"version",
                r"doi",
                r"\.svg$",
            ],
            css_class="badge",
            priority=100,
        ),
        ImagePattern.compile(
            name="avatar",
            patterns=[r"avatars\.[^/]+\.com", r"/avatar/", r"gravatar\.com"],
            css_class="avatar",
            priority=50,
        ),
        ImagePattern.compile(
            name="banner",
            patterns=[r"/banner/", r"banner\.", r"logo", r"header"],
            css_class="banner",
            priority=25,
        ),
    )

    def __init__(self, patterns: tuple[ImagePattern, ...] | None = None) -> None:
        self.patterns = patterns or self.DEFAULT_PATTERNS
        self._pattern_cache: dict[str, str] = {}

    def get_css_class(self, src: str) -> str:
        """画像URLからCSSクラスを決定（キャッシュ付き）"""
        if not src:
            return "content-image"

        if src in self._pattern_cache:
            return self._pattern_cache[src]

        try:
            normalized_src = urlparse(src).path.lower()

            for pattern in sorted(
                self.patterns, key=lambda p: p.priority, reverse=True
            ):
                if any(p.search(normalized_src) for p in pattern.patterns):
                    self._pattern_cache[src] = pattern.css_class
                    return pattern.css_class

            self._pattern_cache[src] = "content-image"
            return "content-image"

        except Exception as e:
            logger.warning(f"Error determining image class for {src}: {e}")
            return "content-image"


class ImageClassExtension(Extension):
    """Markdown拡張: 画像クラスの処理"""

    def __init__(
        self, image_config: Optional[ImageConfig] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.image_config = image_config or ImageConfig()

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.treeprocessors.register(
            ImageClassTreeprocessor(md, self.image_config), "image_class", 15
        )


class ImageClassTreeprocessor(Treeprocessor):
    """画像要素の処理"""

    def __init__(self, md: markdown.Markdown, image_config: ImageConfig) -> None:
        super().__init__(md)
        self.image_config = image_config

    def run(self, root: Element) -> None:
        for elem in root.iter("img"):
            try:
                self._process_image(elem)
                logger.debug(
                    "Processing image: src=%s, class=%s",
                    elem.get("src", ""),
                    elem.get("class", ""),
                )
            except Exception as e:
                logger.warning("Error processing image %s: %s", elem.get("src", ""), e)

    def _process_image(self, elem: Element) -> None:
        src = elem.get("src", "")
        classes = set(filter(None, elem.get("class", "").split()))

        css_class = self.image_config.get_css_class(src)
        classes.add(css_class)

        alt = elem.get("alt", "")
        size_match = re.search(r"\{:.*?size-(small|medium|large).*?\}", alt)
        if size_match:
            classes.add(f"img-{size_match.group(1)}")
            elem.set("alt", re.sub(r"\{:.*?\}", "", alt).strip())

        elem.set("class", " ".join(sorted(classes)))


# ==========================
# HTMLテンプレート生成
# ==========================
@dataclass(frozen=True)
class HtmlTemplate:
    """HTMLテンプレート設定"""

    title: str
    content: str
    dark_mode: bool = False
    custom_css: str = ""
    font_family: str = '"BIZ UDPGothic", "Hiragino Sans", "Noto Sans JP", sans-serif'

    def generate(self) -> str:
        """HTMLテンプレートを生成"""
        theme_script = """
        function toggleTheme() {
            const root = document.documentElement;
            const currentTheme = root.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            root.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }

        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        });
        """

        base_css = (
            """
        /* ベーススタイル */
        :root {
            --color-text: #1a1a1a;
            --color-bg: #ffffff;
            --color-link: #0066cc;
            --color-code-bg: #f6f8fa;
            --color-border: #e1e4e8;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.12);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.15);
            --shadow-lg: 0 8px 24px rgba(0,0,0,0.2);
        }

        [data-theme="dark"] {
            --color-text: #e1e1e1;
            --color-bg: #1a1a1a;
            --color-link: #58a6ff;
            --color-code-bg: #2d333b;
            --color-border: #30363d;
        }

        /* 基本スタイル */
        body {
            font-family: """
            + self.font_family
            + """;
            line-height: 1.8;
            color: var(--color-text);
            background: var(--color-bg);
            margin: 0 auto;
            padding: 2rem;
            max-width: 800px;
            transition: color 0.3s, background-color 0.3s;
        }

        /* 見出し */
        h1, h2, h3, h4, h5, h6 {
            color: var(--color-text);
            margin-top: 2em;
            margin-bottom: 0.5em;
            line-height: 1.3;
        }

        h1 { font-size: 2em; font-weight: 700; }
        h2 {
            font-size: 1.7em;
            font-weight: 600;
            border-bottom: 2px solid var(--color-border);
            padding-bottom: 0.3em;
        }
        h3 { font-size: 1.4em; font-weight: 600; }

        /* リンク */
        a {
            color: var(--color-link);
            text-decoration: none;
            transition: color 0.2s;
        }
        a:hover {
            text-decoration: underline;
        }

        /* コードブロック */
        pre {
            background: var(--color-code-bg);
            padding: 1em;
            overflow-x: auto;
            border-radius: 4px;
            margin: 1.5em 0;
        }
        code {
            font-family: "Source Code Pro", Consolas, Monaco, monospace;
            font-size: 0.9em;
        }

        /* テーブル */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 2em 0;
            font-size: 0.95em;
        }
        th, td {
            padding: 0.75em;
            border: 1px solid var(--color-border);
            text-align: left;
        }
        th {
            background: var(--color-code-bg);
            font-weight: 600;
        }

        /* 引用 */
        blockquote {
            margin: 1.5em 0;
            padding: 1em 1.5em;
            border-left: 4px solid var(--color-border);
            background: var(--color-code-bg);
            color: var(--color-text);
        }

        /* 画像スタイル */
        img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            margin: 1em 0;
        }

        /* バッジ画像 */
        img.badge {
            height: 20px !important;
            margin: 0 4px;
            vertical-align: middle;
        }

        /* アバター画像 */
        img.avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin: 0;
        }

        /* バナー画像 */
        img.banner {
            max-height: 100px;
            object-fit: contain;
            margin: 1em 0;
        }

        /* 通常のコンテンツ画像 */
        img.content-image {
            max-height: 600px;
            object-fit: contain;
        }

        /* 画像サイズクラス */
        img.img-small { max-height: 300px; }
        img.img-medium { max-height: 500px; }
        img.img-large { max-height: 800px; }

        /* 印刷時の画像サイズ制御 */
        @media print {
            body {
                width: 210mm;  /* A4幅 */
                padding: 20mm;  /* マージン */
            }
            img.content-image {
                max-height: 500px;  /* A4サイズに収まるように調整 */
                break-inside: avoid;
            }
            img.banner { max-height: 80px; }
            img.badge { height: 16px !important; }
            .utility-buttons { display: none; }
        }

        /* モバイル対応 */
        @media (max-width: 768px) {
            body { padding: 1rem; }
            img.content-image { max-height: 400px; }
            img.banner { max-height: 80px; }
        }

        /* ユーティリティボタン */
        .utility-buttons {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            z-index: 900;
        }

        .utility-button {
            width: 3rem;
            height: 3rem;
            border-radius: 50%;
            border: none;
            background: var(--color-bg);
            color: var(--color-text);
            box-shadow: var(--shadow-md);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }

        .utility-button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .utility-button:focus {
            outline: 2px solid var(--color-link);
            outline-offset: 2px;
        }

        .utility-button svg {
            width: 1.5rem;
            height: 1.5rem;
            fill: currentColor;
        }

        /* アクセシビリティ対応 */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation: none !important;
                transition: none !important;
            }
        }
        """
            + self.custom_css
        )

        template = f"""<!DOCTYPE html>
<html lang="ja" data-theme="{'dark' if self.dark_mode else 'light'}">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>{self.title}</title>
    <style>
{base_css}
    </style>
</head>
<body>
    <div class="utility-buttons">
        <button class="utility-button" onclick="window.print()" aria-label="印刷">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/>
            </svg>
        </button>
        <button class="utility-button" onclick="toggleTheme()" aria-label="テーマ切り替え">🌓</button>
    </div>
    {self.content}
    <script>
{theme_script}
    </script>
</body>
</html>"""

        return template


def get_html_template(
    title: str,
    content: str,
    *,
    dark_mode: bool = False,
    custom_css: str = "",
    font_family: str | None = None,
) -> str:
    """HTMLテンプレートを生成する関数"""
    template = HtmlTemplate(
        title=title,
        content=content,
        dark_mode=dark_mode,
        custom_css=custom_css,
        font_family=(
            font_family
            or '"BIZ UDPGothic", "Hiragino Sans", "Noto Sans JP", sans-serif'
        ),
    )
    return template.generate()


# ==========================
# 3. Markdown→HTML 変換関数
# ==========================
@dataclass
class ConversionStatus:
    """変換状態を管理するデータクラス"""

    total: int = 0
    success: int = 0
    errors: dict[Path, str] = field(default_factory=dict)

    @property
    def failed(self) -> int:
        return len(self.errors)


def convert_markdown_content(
    content: str,
    extensions: list[str | Extension] | None = None,
) -> str:
    """
    Markdownテキストを変換する共通関数

    Args:
        content: 変換するMarkdownテキスト
        extensions: 使用する拡張機能のリスト。デフォルトでは画像処理拡張を含む基本セット
    """
    if extensions is None:
        extensions = [
            "extra",
            "nl2br",
            "sane_lists",
            "footnotes",
            "tables",
            ImageClassExtension(),  # 画像の自動クラス付与
        ]

    try:
        return markdown.markdown(content, extensions=extensions)
    except Exception as e:
        logger.error(f"Markdown conversion error: {e}")
        msg = f"Failed to convert markdown: {e}"
        raise ConversionError(msg) from e


def convert_markdown_to_html(
    file_path: Path, status: ConversionStatus, progress: Progress, task: TaskID
) -> None:
    """単一ファイルの変換処理"""
    try:
        # ファイルの存在確認
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        # Markdown変換
        content = file_path.read_text(encoding="utf-8")
        html_content = convert_markdown_content(content)

        # 出力パス設定と保存
        base_path = str(file_path).replace("markdown", "html")
        output_path = Path(base_path).with_suffix(".html")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        full_html = get_html_template(file_path.stem, html_content)
        output_path.write_text(full_html, encoding="utf-8")

        # 成功を記録
        status.success += 1
        logger.info("Successfully converted: %s", file_path.name)

    except Exception as e:
        # エラーを記録
        status.errors[file_path] = str(e)
        logger.error("Failed to convert %s: %s", file_path, e)

    finally:
        # 進捗を更新
        progress.advance(task)


# ==========================
# 型定義
# ==========================
InputDirArg = Annotated[Optional[Path], typer.Argument(help="入力フォルダ")]

OutputDirOpt = Annotated[Optional[Path], typer.Option(help="出力フォルダ")]

CssFileOpt = Annotated[Optional[Path], typer.Option(help="CSSファイル")]


# ==========================
# メイン処理
# ==========================
@app.command()
def convert(
    input_dir: InputDirArg = None,
    output_dir: OutputDirOpt = None,
    max_workers: Annotated[int, typer.Option(help="並列処理数")] = 4,
    custom_css: CssFileOpt = None,
    dark_mode: Annotated[bool, typer.Option(help="ダークモード")] = False,
    debug: Annotated[bool, typer.Option(help="デバッグモード")] = False,
) -> None:
    """
    Markdownファイルの一括変換処理

    Args:
        input_dir: 入力ディレクトリ。未指定時は'markdown'または'md'を使用
        output_dir: 出力ディレクトリ。未指定時は'html'を使用
        max_workers: 並列処理数
        custom_css: カスタムCSSファイルのパス
        dark_mode: ダークモードの有効化
        debug: デバッグモードの有効化
    """
    # ロガーの設定を追加
    log_manager.setup_logger(
        debug=debug,
        input_dir=input_dir,
        output_dir=output_dir,
        dark_mode=dark_mode,
        custom_css=custom_css,
    )

    # 既存の処理をそのまま維持
    console = Console()
    status = ConversionStatus()

    try:
        # 入力ディレクトリの検証
        if input_dir is None:
            input_dir = next(
                (p for p in [Path("markdown"), Path("md")] if p.exists()), None
            )
        if not input_dir or not input_dir.exists():
            logger.error("Input directory not found")
            raise typer.Exit(code=1) from None

        # 出力ディレクトリの設定
        output_dir = output_dir or Path("html")
        output_dir.mkdir(parents=True, exist_ok=True)

        # ファイル検索
        md_files = sorted(input_dir.glob("**/*.md"))
        if not md_files:
            logger.warning(f"No markdown files found in {input_dir}")
            raise typer.Exit(code=0) from None

        status.total = len(md_files)

        # 開始メッセージ
        console.print(
            Panel(
                "\n".join(
                    [
                        f"Source directory: {input_dir}",
                        f"Output directory: {output_dir}",
                        f"Files to process: {status.total}",
                    ]
                ),
                title="🚀 Starting Conversion",
                border_style="cyan",
            )
        )

        # 変換処理
        tree = Tree("[bold cyan]Conversion Status[/]")
        success_branch = tree.add("[green]Completed[/]")
        error_branch = tree.add("[red]Errors[/]")

        for file_path in md_files:
            try:
                # 相対パスを維持した出力パスの生成
                rel_path = file_path.relative_to(input_dir)
                output_path = output_dir / rel_path.with_suffix(".html")
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # ファイル変換
                content = file_path.read_text(encoding="utf-8")
                html_content = convert_markdown_content(content)

                full_html = get_html_template(file_path.stem, html_content)
                output_path.write_text(full_html, encoding="utf-8")

                # 成功を記録
                status.success += 1
                success_branch.add(f"[green]✓[/] {rel_path}")
                logger.info(f"Successfully converted: {rel_path}")

            except Exception as e:
                # エラーを記録
                status.errors[file_path] = str(e)
                error_branch.add(f"[red]✗[/] {rel_path} - {str(e)}")
                logger.error(f"Failed to convert {rel_path}: {e}")

        # 最終結果の表示
        console.print("\n")
        console.print(tree)
        console.print(
            Panel(
                "\n".join(
                    [
                        f"Processed all .md files in '{input_dir}'",
                        f"Generated HTML files in '{output_dir}'",
                        "",
                        f"Total files processed: {status.total}",
                        f"Successfully converted: {status.success}",
                        f"Failed to convert: {status.failed}",
                        "",
                        "[red]⚠️ Some files failed to convert[/]"
                        if status.failed
                        else "[green]✨ All files converted successfully[/]",
                    ]
                ).strip(),
                title="📊 Conversion Summary",
                border_style="green" if status.failed == 0 else "red",
            )
        )

        if status.failed > 0:
            raise typer.Exit(code=1) from None

    except Exception as e:
        logger.error(f"Conversion process failed: {e}")
        raise typer.Exit(code=1) from e

    finally:
        if status.failed > 0:
            logger.info(
                f"Conversion completed with {status.failed} errors. "
                f"See {LOG_DIR} for details."
            )
        else:
            logger.info("Conversion completed successfully")

        # 実行完了時のサマリーを追加
        logger.info(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Conversion Complete
Finished at: {datetime.now():%Y-%m-%d %H:%M:%S}
Total files: {status.total}
Successful: {status.success}
Failed: {status.failed}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


def main() -> None:
    """メインエントリーポイント"""
    try:
        app()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


# スクリプトとして直接実行されたとき
if __name__ == "__main__":
    main()


class MarkdownConverter:
    """Markdown to HTML converter with Japanese optimization"""

    def __init__(self, debug_mode: bool = False) -> None:
        self.debug_mode = debug_mode
        # ロガーの設定
        logger.remove()  # デフォルトハンドラを削除
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        # 標準出力へのログ
        logger.add(
            sys.stdout, format=log_format, level="DEBUG" if debug_mode else "INFO"
        )
        # ファイルへのログ
        logger.add(
            "converter.log",
            format=log_format,
            level="DEBUG",
            rotation="1 day",
            retention="7 days",
        )

    def convert_file(self, file_path: Path) -> Optional[str]:
        """1つのファイルを変換"""
        try:
            if not file_path.exists():
                logger.error(f"Input file not found: {file_path}")
                return None

            content = file_path.read_text(encoding="utf-8")
            html_content = convert_markdown_content(content)

            output_path = Path(str(file_path).replace("markdown", "html")).with_suffix(
                ".html"
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)

            full_html = get_html_template(file_path.stem, html_content)
            output_path.write_text(full_html, encoding="utf-8")

            logger.info(f"Successfully converted: {file_path.name}")
            return str(output_path)

        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to convert {file_path}: {e}")
            return None
