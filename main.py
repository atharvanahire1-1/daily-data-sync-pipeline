#!/usr/bin/env python3
"""
main.py — Entry point for the daily-data-sync pipeline.

Orchestrates three stages:
    1. FETCH    → Pull raw data from the CoinGecko API.
    2. TRANSFORM → Validate, clean, and normalise the records.
    3. STORE    → Save to local JSON (and optionally upload to S3).
"""

import sys
import os
import logging
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Ensure the src package is importable when running from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.fetcher import fetch_crypto_prices
from src.transformer import transform_all
from src.storage import save_local, upload_to_s3

# ── Configuration ──────────────────────────────────────────────────
load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
COINS_PER_PAGE = int(os.getenv("COINS_PER_PAGE", "25"))
VS_CURRENCY = os.getenv("VS_CURRENCY", "usd")
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("daily-data-sync")


def run() -> None:
    """Execute the full fetch → transform → store pipeline."""
    today = datetime.now(timezone.utc)
    log.info("Pipeline started  [date=%s]", today.strftime("%Y-%m-%d"))

    # 1. FETCH
    log.info("Fetching top %d coins (vs %s) …", COINS_PER_PAGE, VS_CURRENCY)
    try:
        raw = fetch_crypto_prices(
            vs_currency=VS_CURRENCY,
            per_page=COINS_PER_PAGE,
        )
    except Exception as exc:
        log.error("Fetch failed: %s", exc)
        sys.exit(1)
    log.info("Fetched %d raw records.", len(raw))

    # 2. TRANSFORM
    log.info("Transforming records …")
    try:
        cleaned = transform_all(raw, skip_invalid=True)
    except Exception as exc:
        log.error("Transform failed: %s", exc)
        sys.exit(1)
    log.info("Produced %d clean records.", len(cleaned))

    # 3. STORE (local)
    filepath = save_local(cleaned, base_dir=DATA_DIR, date=today)
    log.info("Saved locally → %s", filepath)

    # 4. STORE (cloud — optional)
    s3_key = upload_to_s3(filepath)
    if s3_key:
        log.info("Uploaded to S3 → %s", s3_key)
    else:
        log.debug("S3 upload skipped (not configured).")

    log.info("Pipeline finished ✓")


if __name__ == "__main__":
    run()
