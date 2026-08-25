"""
Vizuelizacija mreze: slojeviti (hijerarhijski) raspored po tipu cvora
(akademija -> junior/feeder tim -> F1 tim), boja = detektovana Louvain
zajednica, velicina cvora = tezinski PageRank, debljina grane = tezina
(broj vozaca koji su napravili taj prelaz).
"""
import pathlib

import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIG_DIR = BASE_DIR / "figures"

LAYER_ORDER = {"academy": 0, "junior_team": 1, "f1_team": 2}
LAYER_LABELS = ["Akademija konstruktora", "Junior / feeder tim (F2, GP2, F3...)", "F1 tim"]

COMMUNITY_COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860"]


def main():
    nodes = pd.read_csv(PROCESSED_DIR / "network_nodes.csv")
    edges = pd.read_csv(PROCESSED_DIR / "network_edges.csv")
    metrics = pd.read_csv(PROCESSED_DIR / "network_metrics.csv")
    comms = pd.read_csv(PROCESSED_DIR / "network_communities.csv")

    G = nx.DiGraph()
    for _, row in nodes.iterrows():
        G.add_node(row["node_id"], node_type=row["node_type"])
    for _, row in edges.iterrows():
        G.add_edge(row["source"], row["target"], weight=int(row["weight"]))

    comm_map = comms.set_index("node_id")["community"].to_dict()
    pr_map = metrics.set_index("node_id")["pagerank_w"].to_dict()

    # --- pozicioniranje: slojevi po tipu cvora, unutar sloja rasporedjeno
    # po in-degree da grafikon bude citljiviji (bitniji cvorovi centralnije) ---
    pos = {}
    layer_label_y = {}
    for layer_name, layer_val in LAYER_ORDER.items():
        layer_nodes = [n for n in G.nodes() if G.nodes[n]["node_type"] == layer_name]
        layer_nodes.sort(key=lambda n: -metrics.set_index("node_id").loc[n, "in_degree_w"])
        n = len(layer_nodes)
        spacing = 2.6
        for i, node in enumerate(layer_nodes):
            x = (i - (n - 1) / 2) * spacing
            y = -layer_val * 5.5
            pos[node] = (x, y)
        layer_label_y[layer_name] = -layer_val * 5.5

    fig, ax = plt.subplots(figsize=(26, 13))

    # --- grane ---
    for u, v, d in G.edges(data=True):
        w = d["weight"]
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        same_layer = LAYER_ORDER[G.nodes[u]["node_type"]] == LAYER_ORDER[G.nodes[v]["node_type"]]
        rad = 0.25 if same_layer else 0.08
        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>",
            mutation_scale=10 + 2 * w,
            linewidth=0.5 + 0.9 * w,
            color="#999999",
            alpha=0.55,
            shrinkA=14, shrinkB=14,
            zorder=1,
        )
        ax.add_patch(arrow)

    # --- cvorovi ---
    for layer_name, layer_val in LAYER_ORDER.items():
        layer_nodes = [n for n in G.nodes() if G.nodes[n]["node_type"] == layer_name]
        layer_nodes.sort(key=lambda n: pos[n][0])
        for i, node in enumerate(layer_nodes):
            x, y = pos[node]
            comm = comm_map.get(node, 0)
            color = COMMUNITY_COLORS[comm % len(COMMUNITY_COLORS)]
            size = 300 + 9000 * pr_map.get(node, 0.01)
            marker = {"academy": "s", "junior_team": "o", "f1_team": "D"}[layer_name]
            ax.scatter([x], [y], s=size, c=[color], marker=marker, edgecolors="black",
                       linewidths=0.8, zorder=3)
            # zig-zag vertikalni offset labela da se susedni cvorovi ne preklapaju
            above = (i % 2 == 0)
            yoff = 16 if above else -16
            va = "bottom" if above else "top"
            ax.annotate(node, (x, y), xytext=(0, yoff), textcoords="offset points",
                        ha="center", va=va, fontsize=7.6, zorder=4)

    left_x = min(x for x, y in pos.values()) - 7.0
    for layer_name, label in zip(LAYER_ORDER.keys(), LAYER_LABELS):
        ax.text(left_x, layer_label_y[layer_name], label,
                fontsize=12, fontweight="bold", ha="left", va="center",
                rotation=0, color="#333333")

    legend_elems = [
        Line2D([0], [0], marker="s", color="w", markerfacecolor="gray", markersize=10, label="Akademija"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="gray", markersize=10, label="Junior/feeder tim"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="gray", markersize=10, label="F1 tim"),
    ]
    ax.legend(handles=legend_elems, loc="upper right", fontsize=9, frameon=True)

    ax.set_title(
        "Mreža karijernih prelaza vozača F1 (2018-2025): akademije, feeder timovi i F1 timovi\n"
        "boja = Louvain zajednica | veličina čvora = PageRank | debljina grane = broj vozača",
        fontsize=13,
    )
    ax.set_xlim(min(x for x, y in pos.values()) - 12.5, max(x for x, y in pos.values()) + 1.5)
    ax.set_ylim(min(y for x, y in pos.values()) - 2, max(y for x, y in pos.values()) + 2)
    ax.axis("off")
    fig.tight_layout()
    out_path = FIG_DIR / "network_full.png"
    fig.savefig(out_path, dpi=170)
    plt.close(fig)
    print(f"saved -> {out_path}")


if __name__ == "__main__":
    main()
