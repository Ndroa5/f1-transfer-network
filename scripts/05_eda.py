"""
Kratka eksplorativna analiza sirovih/obradjenih podataka (obavezan segment
projekta). Cilj: upoznati se sa podacima, uociti probleme i uraditi
preliminarne vizuelizacije pre finalne mrezne analize.
"""
import json
import pathlib
from collections import Counter

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIG_DIR = BASE_DIR / "figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams["figure.dpi"] = 140
plt.rcParams["font.size"] = 9


def problem_raw_pagination_duplicates():
    """Uocen problem #1: Jolpica API vraca istu trku razdeljenu na 2
    'stranice' (paginacija je po broju REZULTATA, ne po broju trka), pa se
    ista trka pojavljuje 2x u sirovom JSON-u sa razlicitim podskupom
    vozaca. Resen u scripts/02_parse_f1_results.py spajanjem po (season,
    round). Ovde dokumentujemo koliko puta se problem javio."""
    dup_counts = {}
    for season in range(2018, 2026):
        races = json.loads((RAW_DIR / f"results_{season}.json").read_text(encoding="utf-8"))
        names = [r["raceName"] for r in races]
        c = Counter(names)
        dups = {k: v for k, v in c.items() if v > 1}
        if dups:
            dup_counts[season] = dups
    return dup_counts


def problem_edge_double_counting():
    """Uocen problem #2: pri gradnji mreze, vozac koji se u istoj sezoni
    vratio istom timu posle kratkog 'cameo' nastupa za drugi tim (npr.
    George Russell, Williams -> Mercedes -> Williams -> Mercedes zbog
    zamene za Hamiltona na Sakhir GP 2020) je isprva DUPLO brojan na istoj
    grani. Reseno u 04_build_network.py: jedan vozac se broji najvise
    jednom po grani (tezina grane = broj RAZLICITIH vozaca)."""
    pass


def main():
    print("=== Problem 1: paginacioni duplikati u sirovim podacima ===")
    dups = problem_raw_pagination_duplicates()
    for season, races in dups.items():
        print(f"  {season}: {races}")

    results = pd.read_csv(PROCESSED_DIR / "f1_race_results_2018_2025.csv")
    junior = pd.read_csv(PROCESSED_DIR / "junior_career_manual.csv")

    print("\n=== Osnovne dimenzije obradjenog skupa ===")
    print(f"  broj redova (vozac x trka): {len(results)}")
    print(f"  broj sezona: {results['season'].nunique()} ({results['season'].min()}-{results['season'].max()})")
    print(f"  broj trka: {results.groupby(['season','round']).ngroups}")
    print(f"  broj jedinstvenih vozaca: {results['driver_id'].nunique()}")
    print(f"  broj jedinstvenih (kanonizovanih) konstruktora: {results['constructor_id'].nunique()}")

    n_drivers = results["driver_id"].nunique()
    n_with_junior = junior["driver_id"].nunique()
    print("\n=== Pokrivenost rucno kuriranih junior/akademija podataka ===")
    print(f"  vozaca sa bar jednim junior/akademija zapisom: {n_with_junior}/{n_drivers} "
          f"({100*n_with_junior/n_drivers:.0f}%)")
    missing = sorted(set(results["driver_id"]) - set(junior["driver_id"]))
    print(f"  vozaci BEZ zapisa (namerno ili zbog nedostatka pouzdanih podataka): {missing}")

    print("\n=== Provera nedostajucih vrednosti (missing values) ===")
    print(results.isna().sum().to_string())

    # --- Chart 1: races per season ---
    races_per_season = results.groupby("season")["round"].nunique()
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(races_per_season.index.astype(str), races_per_season.values, color="#5b7fd6")
    ax.set_title("Broj trka po sezoni (2018-2025)")
    ax.set_xlabel("Sezona")
    ax.set_ylabel("Broj trka")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "eda_races_per_season.png")
    plt.close(fig)

    # --- Chart 2: driver appearances (career length proxy in window) ---
    apps = results.groupby("driver_name")["round"].count().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.barh(apps.index[::-1], apps.values[::-1], color="#d65b5b", height=0.7)
    ax.set_title("Broj odvoženih trka po vozaču (2018-2025)")
    ax.set_xlabel("Broj trka")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "eda_races_per_driver.png")
    plt.close(fig)

    # --- Chart 3: number of distinct constructors driven for (transfer activity proxy) ---
    n_teams = results.groupby("driver_name")["constructor_id"].nunique().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.barh(n_teams.index[::-1], n_teams.values[::-1], color="#5bd6a0", height=0.7)
    ax.set_title("Broj različitih F1 konstruktora po vozaču (2018-2025, pre kanonizacije)", fontsize=10.5)
    ax.set_xlabel("Broj konstruktora")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "eda_teams_per_driver.png")
    plt.close(fig)

    print(f"\nSacuvane preliminarne vizuelizacije u {FIG_DIR}")


if __name__ == "__main__":
    main()
