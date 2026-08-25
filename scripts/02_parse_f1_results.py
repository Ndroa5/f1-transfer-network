"""
Parsira sirove JSON fajlove (data/raw/results_{season}.json) u jednu cistu
tabelu: (season, round, race_name, date, driverId, driver_name, constructorId,
constructor_name).

Napomena: Jolpica API ponekad vraca istu trku razdeljenu na dve "stranice"
(paginacija je po broju rezultata, ne po broju trka), pa se ista trka moze
pojaviti dvaput sa razlicitim podskupovima vozaca. Ovde se rezultati za
istu (season, round) spajaju i duplikati po vozacu se uklanjaju.
"""
import json
import pathlib
import csv

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

SEASONS = list(range(2018, 2026))


def main():
    rows = []
    for season in SEASONS:
        path = RAW_DIR / f"results_{season}.json"
        races = json.loads(path.read_text(encoding="utf-8"))

        merged = {}  # round -> dict(raceName, date, results: {driverId: row})
        for race in races:
            rnd = race["round"]
            entry = merged.setdefault(rnd, {
                "raceName": race["raceName"],
                "date": race.get("date", ""),
                "results": {},
            })
            for res in race.get("Results", []):
                drv = res["Driver"]
                con = res["Constructor"]
                driver_id = drv["driverId"]
                entry["results"][driver_id] = {
                    "driver_name": f"{drv.get('givenName','')} {drv.get('familyName','')}".strip(),
                    "constructor_id": con["constructorId"],
                    "constructor_name": con["name"],
                }

        for rnd in sorted(merged.keys(), key=lambda x: int(x)):
            entry = merged[rnd]
            for driver_id, info in entry["results"].items():
                rows.append({
                    "season": season,
                    "round": int(rnd),
                    "race_name": entry["raceName"],
                    "date": entry["date"],
                    "driver_id": driver_id,
                    "driver_name": info["driver_name"],
                    "constructor_id": info["constructor_id"],
                    "constructor_name": info["constructor_name"],
                })

    out_path = PROCESSED_DIR / "f1_race_results_2018_2025.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "season", "round", "race_name", "date",
            "driver_id", "driver_name", "constructor_id", "constructor_name",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} rows -> {out_path}")

    # quick sanity check: races per season
    from collections import Counter
    season_rounds = Counter()
    for r in rows:
        season_rounds[(r["season"], r["round"])] = 1
    per_season = Counter(s for s, _ in season_rounds)
    for s in SEASONS:
        print(f"  {s}: {per_season.get(s, 0)} races")


if __name__ == "__main__":
    main()
