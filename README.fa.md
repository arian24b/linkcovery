<div align="center">
  <img src="https://raw.githubusercontent.com/arian24b/linkcovery/refs/heads/main/linkcovery.png" alt="LinkCovery logo" width="400"/>
</div>

# LinkCovery

[English](README.md)

مدیر بوکمارک برای ترمینال، با یک رابط وب کوچک. لینک‌ها را اضافه کنید، با متن، دامنه یا برچسب جست‌وجو کنید، لینک‌های خوانده‌شده را علامت بزنید و داده‌ها را با قالب JSON، HTML یا TXT وارد و خارج کنید.

## نصب

پایتون ۳٫۱۲ تا ۳٫۱۵.

```bash
uv tool install linkcovery      # یا: pipx install linkcovery
linkcovery --help
```

از روی کلون: `uv sync && uv run linkcovery --help`.

## شروع سریع

```bash
linkcovery add https://github.com/arian24b/linkcovery --tag python,cli    # توضیح صفحه را خودش می‌گیرد
linkcovery list --unread-only
linkcovery search python --tag cli
linkcovery mark 1                      # جابه‌جایی بین خوانده و نخوانده
linkcovery export my-bookmarks.md      # .json یا .md یا .html؛ از پسوند فایل تشخیص می‌دهد
linkcovery import bookmarks.html
linkcovery webui                       # http://127.0.0.1:8000
```

## دستورها

| دستور | کار |
|---|---|
| `add URL [-d DESC] [-t TAG] [-r] [--no-fetch] [--timeout S]` (مترادف `new`) | ذخیرهٔ یک لینک |
| `list [-l N] [--read-only] [--unread-only] [--full]` (مترادف `ls`) | نمایش لینک‌ها |
| `search [QUERY] [--domain D] [-t TAG] [--read-only] [--unread-only] [-l N]` (مترادف `find`) | جست‌وجو؛ همهٔ فیلترها باید با هم برقرار باشند |
| `show ID` | جزئیات یک لینک |
| `edit ID [--url U] [-d DESC] [-t TAG] [-r] [-u]` | ویرایش یک لینک |
| `delete ID... [-f] [-y]` (مترادف `rm`) | حذف لینک‌ها، با تأیید |
| `mark ID... [-r] [-u]` | علامت خوانده یا نخوانده؛ بدون گزینه، وضعیت را برعکس می‌کند |
| `open ID...` | باز کردن لینک‌ها در مرورگر |
| `normalize [ID...] [-a] [-y]` | حذف اسلش پایانی، `http` به `https`، حذف `www` |
| `describe [ID...] [-a] [-y] [-c N] [--timeout S]` | گرفتن توضیح برای لینک‌های بی‌توضیح |
| `random [-n N] [--include-read]` | چند لینک نخواندهٔ تصادفی انتخاب و خوانده‌شده علامت می‌زند |
| `export [FILE] [-f] [-y]` | نوشتن همهٔ لینک‌ها (پیش‌فرض `links.json`) |
| `import [FILE] [--chrome] [-y]` | خواندن `.json`، `.html`، `.txt` یا فایل بوکمارک Chrome |
| `stats` | شمارش کل و دامنه‌های پرتکرار |
| `paths` | محل تنظیمات، پایگاه‌داده و داده‌ها |
| `webui [--host H] [--port P] [--reload] [--background]` | اجرای رابط وب |
| `config show\|get\|set\|reset\|edit\|validate` | تنظیمات |

گزینه‌های سراسری: `--json` خروجی ماشینی می‌دهد (خطاها هم روی stderr به شکل JSON درمی‌آیند) و `--no-color` رنگ را خاموش می‌کند. اگر برای دستوری شناسه یا آدرس لازم باشد و ننوشته باشید، ابزار می‌پرسد.

## تنظیمات

روی همهٔ سیستم‌عامل‌ها در `~/.config/linkcovery/config.json` ذخیره می‌شود. ترتیب اولویت: متغیر محیطی، سپس فایل، سپس مقدار پیش‌فرض. دستور `linkcovery config show` هر مقدار را با منبعش نشان می‌دهد.

| تنظیم | پیش‌فرض | معنی |
|---|---|---|
| `database_path` | خودکار | فایل پایگاه‌داده (`LINKCOVERY_DB` آن را بازنویسی می‌کند) |
| `default_export_format` | `json` | قالب خروجی |
| `max_search_results` | `50` | حد نتایج جست‌وجو |
| `allowed_extensions` | `[".json"]` | پسوندهای مجاز برای ورود داده |
| `debug` | `false` | حالت اشکال‌زدایی |

## رابط وب

یک برنامهٔ کوچک FastAPI: افزودن، ویرایش و حذف لینک، ورود و خروج داده، فهرست با بارگذاری تنبل، و تصویر پیش‌نمایش که در `~/.cache/linkcovery/previews` کش می‌شود. لاگ اجرای پس‌زمینه در `~/.local/state/linkcovery/logs/webui.log` است؛ `linkcovery paths` مسیرهای دقیق را چاپ می‌کند.

## دستورهای مشترک

این ابزار روی [cfuicli](https://github.com/arian24b/cfui) ساخته شده و ظاهر و رفتارش با بقیهٔ ابزارهای این مجموعه یکی است.

```bash
linkcovery help [command]     # راهنما؛ -h روی هر دستور کار می‌کند
linkcovery version            # نسخه و مخزن گیت (همچنین: -v)
linkcovery update [--check]   # به‌روزرسانی خود ابزار؛ --check فقط نسخه‌ها را مقایسه می‌کند
linkcovery -q ...             # حالت آرام: بدون بنر و یادداشت (یا LINKCOVERY_QUIET=1)
```

- اگر گزینهٔ اجباری جا افتاده باشد و ابزار را در ترمینال اجرا کرده باشید، مقدارش را می‌پرسد. در pipe یا CI با پیام `--flag is required. Pass --flag <value> or run interactively.` متوقف می‌شود (کد خروج ۲).
- خطاها در یک کادر قرمز روی stderr و با کد خروج غیرصفر نمایش داده می‌شوند. با Ctrl-C کد خروج ۱۳۰ است.
- رنگ فقط در ترمینال استفاده می‌شود. با `NO_COLOR=1` خاموش می‌شود.
- با `--json` فقط JSON روی stdout نوشته می‌شود.

## توسعه

```bash
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

ابزارهای مرتبط: [PEM](https://github.com/arian24b/pem)، [ollama-tool-cli](https://github.com/arian24b/ollamatools)، [ThroneTools](https://github.com/arian24b/thronetools).

## مجوز

MIT
