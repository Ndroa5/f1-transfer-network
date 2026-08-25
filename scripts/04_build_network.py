"""
Gradi usmerenu, ponderisanu mrezu karijernih prelaza:
cvorovi = {akademije konstruktora} u {junior/feeder timovi (F2/GP2/F3...)}
          u {F1 timovi (kanonizovani kroz rebrendiranja)}
grane = usmereni prelaz izmedju dva UZASTOPNA koraka karijere istog vozaca,
        tezina = broj vozaca koji su napravili tacno taj prelaz.

Kanonizacija F1 timova: isti "fabricki" entitet koji je promenio ime
(sponzorski rebrand) tretira se kao JEDAN cvor, jer nas zanima stvarni
tok talenta kroz organizacije, a ne kroz nazive sezone:
  Toro Rosso -> AlphaTauri -> RB               => "RB (Toro Rosso/AlphaTauri)"
  Force India -> Racing Point -> Aston Martin  => "Aston Martin (Force India/Racing Point)"
  Renault -> Alpine                            => "Alpine (Renault)"
  Sauber -> Alfa Romeo -> Sauber               => "Sauber (Alfa Romeo)"
Ovo je namerna metodoloska odluka, obrazlozena u izvestaju.
"""
import re
import csv
import pathlib
from collections import defaultdict

import pandas as pd

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

CONSTRUCTOR_CANON = {
    "toro_rosso": "RB (Toro Rosso/AlphaTauri)",
    "alphatauri": "RB (Toro Rosso/AlphaTauri)",
    "rb": "RB (Toro Rosso/AlphaTauri)",
    "force_india": "Aston Martin (Force India/Racing Point)",
    "racing_point": "Aston Martin (Force India/Racing Point)",
    "aston_martin": "Aston Martin (Force India/Racing Point)",
    "renault": "Alpine (Renault)",
    "alpine": "Alpine (Renault)",
    "sauber": "Sauber (Alfa Romeo)",
    "alfa": "Sauber (Alfa Romeo)",
    "ferrari": "Ferrari",
    "haas": "Haas",
    "mclaren": "McLaren",
    "mercedes": "Mercedes",
    "red_bull": "Red Bull Racing",
    "williams": "Williams",
}

CATEGORY_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")

# Isti junior/feeder tim je vise puta menjao sponzorski naziv (analogno
# rebrendiranju F1 timova gore) - svodimo na jedan kanonski cvor da se
# "feeder" uticaj tima ne razvodni kroz vise naziva istog entiteta.
JUNIOR_TEAM_CANON = {
    "UNI-Virtuosi Racing": "Virtuosi Racing (ex Russian Time)",
    "Virtuosi Racing": "Virtuosi Racing (ex Russian Time)",
    "Invicta Virtuosi Racing": "Virtuosi Racing (ex Russian Time)",
    "Invicta Racing": "Virtuosi Racing (ex Russian Time)",
    "Hitech Pulse-Eight": "Hitech Grand Prix",
}


def canon_junior_team(name: str) -> str:
    base = CATEGORY_SUFFIX_RE.sub("", name).strip()
    return JUNIOR_TEAM_CANON.get(base, base)


def main():
    results = pd.read_csv(PROCESSED_DIR / "f1_race_results_2018_2025.csv")
    junior = pd.read_csv(PROCESSED_DIR / "junior_career_manual.csv")

    results["team_canon"] = results["constructor_id"].map(CONSTRUCTOR_CANON)
    missing = results[results["team_canon"].isna()]["constructor_id"].unique()
    if len(missing):
        raise ValueError(f"Unmapped constructors: {missing}")

    driver_names = results[["driver_id", "driver_name"]].drop_duplicates().set_index("driver_id")["driver_name"].to_dict()

    # --- build per-driver chronological step sequence ---
    # step = (sort_key, node_id, node_type)
    driver_steps = defaultdict(list)

    for _, row in junior.iterrows():
        etype = row["entity_type"]  # academy | junior_team
        if etype == "junior_team":
            node_id = canon_junior_team(row["entity_name"])
            node_type = "junior_team"
        else:
            node_id = row["entity_name"]
            node_type = "academy"
        sort_key = (int(row["year"]), 0)  # 0 = pre-F1 layer sorts before same-year F1 entries
        driver_steps[row["driver_id"]].append((sort_key, node_id, node_type))

    for _, row in results.sort_values(["driver_id", "season", "round"]).iterrows():
        sort_key = (int(row["season"]), int(row["round"]))
        driver_steps[row["driver_id"]].append((sort_key, row["team_canon"], "f1_team"))

    # --- collapse consecutive duplicates & derive edges ---
    edges = defaultdict(lambda: {"drivers": []})
    node_types = {}
    node_first_seen = {}

    for driver_id, steps in driver_steps.items():
        steps.sort(key=lambda s: s[0])
        collapsed = []
        for sort_key, node_id, node_type in steps:
            if not collapsed or collapsed[-1][1] != node_id:
                collapsed.append((sort_key, node_id, node_type))
            node_types[node_id] = node_type
            node_first_seen.setdefault(node_id, sort_key)

        for (k_from, a, ta), (k_to, b, tb) in zip(collapsed, collapsed[1:]):
            key = (a, b)
            name = driver_names.get(driver_id, driver_id)
            # isti vozac se broji najvise jednom po grani (npr. kratki
            # "cameo" povratak - Williams->Mercedes->Williams->Mercedes -
            # ne treba da naduva tezinu grane)
            if name not in edges[key]["drivers"]:
                edges[key]["drivers"].append(name)

    # --- write nodes ---
    nodes_path = PROCESSED_DIR / "network_nodes.csv"
    with nodes_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["node_id", "node_type"])
        for node_id, ntype in sorted(node_types.items()):
            w.writerow([node_id, ntype])

    # --- write edges ---
    edges_path = PROCESSED_DIR / "network_edges.csv"
    with edges_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source", "target", "weight", "drivers"])
        for (a, b), info in sorted(edges.items(), key=lambda kv: -len(kv[1]["drivers"])):
            w.writerow([a, b, len(info["drivers"]), "; ".join(info["drivers"])])

    print(f"nodes: {len(node_types)} -> {nodes_path}")
    print(f"edges: {len(edges)} -> {edges_path}")

    # quick summary print
    print("\nTop edges by weight:")
    for (a, b), info in sorted(edges.items(), key=lambda kv: -len(kv[1]["drivers"]))[:15]:
        print(f"  {a}  ->  {b}   (w={len(info['drivers'])}: {', '.join(info['drivers'])})")


if __name__ == "__main__":
    main()
