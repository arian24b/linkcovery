[English](allfeat.md) | [فارسی](allfeat.fa.md)

# LinkCovery: قابلیت‌ها و معماری

نسخهٔ 1.7.8. پایتون 3.12 تا 3.15، SQLite، FastAPI و [cfuicli](https://github.com/arian24b/cfui) برای خط فرمان. فهرست دستورها و گزینه‌ها در [README.fa.md](README.fa.md) است؛ این فایل ساختار کد و API وب را توضیح می‌دهد.

## لایه‌ها

| لایه | مسیر | کار |
|---|---|---|
| CLI | `linkcovery/cli` | `app.py` (برنامهٔ cfui)، `links.py` (add، list، search، show، edit، delete، normalize، random)، `data.py` (import و export)، `config.py` (دستورهای config)، `cli.py` (mark، open، stats، paths، webui، describe و ...) |
| رابط وب | `linkcovery/webui` | برنامهٔ FastAPI، قالب‌های Jinja2، فایل‌های static |
| سرویس‌ها | `linkcovery/services` | `link_service.py` (عملیات لینک)، `data_service.py` (ورود و خروج داده) |
| هسته | `linkcovery/core` | `database.py` (sqlite3 با WAL)، `models.py` (Pydantic)، `config.py`، `chrome_bookmark.py`، `utils.py`، `exceptions.py` |

خط فرمان و رابط وب از یک لایهٔ سرویس و یک پایگاه داده استفاده می‌کنند.

## داده

یک جدول `links`: `id`، `url` (یکتا)، `domain`، `description`، `tag` (جداشده با ویرگول)، `is_read`، `preview_url` و زمان‌ها. قالب‌های ورودی: JSON، HTML، TXT و فایل بوکمارک Chrome. قالب‌های خروجی: JSON، Markdown و HTML (از پسوند فایل تشخیص داده می‌شود).

## API وب (`linkcovery/webui/app.py`)

| مسیر | کار |
|---|---|
| `GET /` | صفحهٔ اصلی |
| `GET /api/links`، `GET /api/links/search`، `GET /api/tags`، `GET /api/stats` | فهرست، جست‌وجو، برچسب‌ها، آمار |
| `POST /links` | افزودن لینک |
| `GET /links/{link_id}/edit` | صفحهٔ ویرایش |
| `POST /api/links/bulk-delete`، `bulk-mark-read`، `bulk-mark-unread`، `bulk-toggle` | عملیات گروهی |
| `POST /import`، `GET /export`، `GET /export/markdown`، `GET /export/html` | ورود و خروج داده |
| `GET /config`، `GET /api/config`، `POST /api/config/update`، `POST /api/config/reset`، `GET /api/config/validate` | تنظیمات |

## روند کار

- افزودن: نرمال‌سازی URL، گرفتن توضیح (با `--no-fetch` رد می‌شود) و درج؛ URL تکراری رد می‌شود.
- جست‌وجو: فیلترهای متن، `--domain`، `--tag` و وضعیت خوانده‌شدن با AND ترکیب می‌شوند.
- تصادفی: `random` لینک‌های نخوانده را انتخاب می‌کند (با `--include-read` همه را) و خوانده علامت می‌زند.
- نرمال‌سازی: اسلش آخر و `www.` را حذف می‌کند و `http` را به `https` ارتقا می‌دهد.
