"""Panel-grafikon top 8 cvorova po 4 mere centralnosti (za izvestaj)."""
import pathlib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIG_DIR = BASE_DIR / "figures"

TYPE_COLOR = {"academy": "#C44E52", "junior_team": "#4C72B0", "f1_team": "#DD8452"}

METRICS = [
    ("in_degree_w", "Ulazni stepen (in-degree) — ko prima najviše vozača"),
    ("out_degree_w", "Izlazni stepen (out-degree) — ko 'proizvodi' najviše vozača"),
    ("betweenness", "Betweenness centralnost — strukturni mostovi"),
    ("pagerank_w", "PageRank (težinski) — ukupan 'ugled' u mreži"),
]


def main():
    m = pd.read_csv(PROCESSED_DIR / "network_metrics.csv")
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    for ax, (col, title) in zip(axes.flat, METRICS):
        top = m.sort_values(col, ascending=False).head(8).iloc[::-1]
        colors = [TYPE_COLOR[t] for t in top["node_type"]]
        ax.barh(top["node_id"], top[col], color=colors)
        ax.set_title(title, fontsize=10)
        ax.tick_params(axis="y", labelsize=8)

    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in TYPE_COLOR.values()]
    fig.legend(handles, ["akademija", "junior/feeder tim", "F1 tim"], loc="lower center", ncol=3, fontsize=9)
    fig.suptitle("Ključni akteri po merama centralnosti", fontsize=13)
    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    out_path = FIG_DIR / "centrality_panel.png"
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    print(f"saved -> {out_path}")


if __name__ == "__main__":
    main()
