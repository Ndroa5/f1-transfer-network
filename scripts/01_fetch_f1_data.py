"""
Prikuplja sirove podatke o F1 rezultatima (2018-2025) sa Jolpica-F1 API-ja
(https://api.jolpi.ca/ergast/), koji je nastavak/kompatibilna zamena za
ugaseni Ergast Developer API. Svrha: dobiti hronologiju voznog tima
(konstruktora) za svakog vozaca, po trci, kako bismo mogli da rekonstruisemo
tacne trenutke prelaza izmedju timova (ukljucujuci prelaske tokom sezone).

Datum prikupljanja: 2026-08-24
Metod: HTTP GET, javni REST API, bez autentifikacije.
Ogranicenja: API je community-odrzavan nastavak Ergast-a; moguce su povremene
neusaglasenosti sa zvanicnim rezultatima za vrlo skoreje trke, kao i rate-limit
(reseno sa pauzom izmedju poziva).
"""
import json
import time
import pathlib
import requests

BASE = "https://api.jolpi.ca/ergast/f1"
RAW_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

SEASONS = list(range(2018, 2026))  # 2018-2025 inclusive


def fetch_json(url, params=None):
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_season_results(season):
    """Fetch all race results for a season (paginated)."""
    all_races = []
    offset = 0
    limit = 100
    while True:
        data = fetch_json(f"{BASE}/{season}/results.json", params={"limit": limit, "offset": offset})
        table = data["MRData"]["RaceTable"]
        races = table.get("Races", [])
        all_races.extend(races)
        total = int(data["MRData"]["total"])
        offset += limit
        if offset >= total:
            break
        time.sleep(0.3)
    return all_races


def main():
    for season in SEASONS:
        out_path = RAW_DIR / f"results_{season}.json"
        if out_path.exists():
            print(f"skip {season} (already fetched)")
            continue
        print(f"fetching season {season}...")
        races = fetch_season_results(season)
        out_path.write_text(json.dumps(races, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  saved {len(races)} races -> {out_path}")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
