# 📊 daily-data-sync

Automated daily pipeline that fetches cryptocurrency market data from the [CoinGecko API](https://www.coingecko.com/en/api), cleans and normalises the records, and stores them as dated JSON files — all orchestrated by **GitHub Actions** on a daily cron.

---

## Architecture

```
daily-data-sync/
├── main.py                       # Entry point — orchestrates the pipeline
├── src/
│   ├── __init__.py
│   ├── fetcher.py                # Queries the CoinGecko public API
│   ├── transformer.py            # Validates, cleans & normalises records
│   └── storage.py                # Local JSON persistence + S3 placeholder
├── data/
│   └── YYYY-MM-DD.json           # Auto-generated daily snapshots
├── .github/workflows/
│   └── daily_sync.yml            # GitHub Actions cron workflow
├── requirements.txt              # Pinned Python dependencies
├── .env.example                  # Environment variable template
├── .gitignore                    # Standard Python ignores
└── README.md                     # ← You are here
```

### Pipeline stages

```
┌─────────┐      ┌─────────────┐      ┌─────────┐
│  FETCH  │─────▶│  TRANSFORM  │─────▶│  STORE  │
└─────────┘      └─────────────┘      └─────────┘
 CoinGecko        Validate keys        data/YYYY-MM-DD.json
 /coins/markets   Normalise ISO 8601   (optional S3 upload)
                  Drop extraneous
```

| Stage       | File                   | Description                                                                 |
|-------------|------------------------|-----------------------------------------------------------------------------|
| **Fetch**   | `src/fetcher.py`       | Hits the CoinGecko `/coins/markets` endpoint for top coins by market cap.   |
| **Transform** | `src/transformer.py` | Validates required keys, normalises timestamps to ISO 8601 UTC, filters fields. |
| **Store**   | `src/storage.py`       | Writes JSON to `data/YYYY-MM-DD.json`. Optional `upload_to_s3()` hook.      |

---

## Quick Start

### Prerequisites

- Python **3.10+** (3.11 recommended)
- `pip`

### 1 — Clone & install

```bash
git clone https://github.com/<your-username>/daily-data-sync.git
cd daily-data-sync

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2 — Configure (optional)

```bash
cp .env.example .env
# Edit .env to override defaults
```

### 3 — Run

```bash
python main.py
```

The pipeline will create a file like `data/2026-10-29.json` containing today's snapshot.

---

## Environment Variables

| Variable          | Default  | Description                              |
|-------------------|----------|------------------------------------------|
| `LOG_LEVEL`       | `INFO`   | Python logging level                     |
| `COINS_PER_PAGE`  | `25`     | Number of top coins to fetch (max 250)   |
| `VS_CURRENCY`     | `usd`    | Fiat currency for price data             |
| `DATA_DIR`        | `data`   | Output directory for JSON files          |
| `AWS_S3_BUCKET`   | *(none)* | S3 bucket name (enables cloud upload)    |

---

## GitHub Actions — Automated Daily Runs

The workflow at `.github/workflows/daily_sync.yml` runs automatically:

- **⏰ Scheduled:** Every day at **00:00 UTC** (`cron: "0 0 * * *"`)
- **🖱️ Manual:** Click **Run workflow** from the *Actions* tab

### What the workflow does

1. Checks out the repository
2. Sets up Python 3.11
3. Installs pinned dependencies
4. Runs `python main.py`
5. Commits & pushes the new `data/YYYY-MM-DD.json` file back to the repo

> [!NOTE]
> The workflow uses `permissions: contents: write` so the `github-actions[bot]` can push commits directly.

### Enable S3 uploads in CI

1. Add these as **repository secrets** (Settings → Secrets → Actions):
   - `AWS_S3_BUCKET`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
2. Uncomment the corresponding `env:` lines in `daily_sync.yml`.
3. Add `boto3` to `requirements.txt`.

---

## Project Setup for GitHub

```bash
cd daily-data-sync
git init
git add .
git commit -m "Initial commit: daily-data-sync pipeline"
git remote add origin https://github.com/<your-username>/daily-data-sync.git
git branch -M main
git push -u origin main
```

---

## License

MIT — see [LICENSE](LICENSE) for details.
