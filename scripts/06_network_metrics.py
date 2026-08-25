"""
Ucitava mrezu (network_nodes.csv / network_edges.csv) kao networkx
DiGraph, racuna mere centralnosti, detektuje zajednice (community
detection) i identifikuje kljucne aktere u kontekstu teme (akademije,
feeder timovi, "hub" organizacije).
"""
import pathlib
import ast

import pandas as pd
import networkx as nx
import community as community_louvain  # python-louvain

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def load_graph():
    nodes = pd.read_csv(PROCESSED_DIR / "network_nodes.csv")
    edges = pd.read_csv(PROCESSED_DIR / "network_edges.csv")

    G = nx.DiGraph()
    for _, row in nodes.iterrows():
        G.add_node(row["node_id"], node_type=row["node_type"])
    for _, row in edges.iterrows():
        G.add_edge(row["source"], row["target"], weight=int(row["weight"]), drivers=row["drivers"])
    return G


def main():
    G = load_graph()
    print(f"Mreza: {G.number_of_nodes()} cvorova, {G.number_of_edges()} usmerenih grana")
    print(f"Gustina (density): {nx.density(G):.4f}")
    print(f"Da li je slabo povezana (weakly connected): {nx.is_weakly_connected(G)}")
    n_components = nx.number_weakly_connected_components(G)
    print(f"Broj slabo povezanih komponenti: {n_components}")

    # --- centralnost ---
    in_deg = dict(G.in_degree(weight="weight"))
    out_deg = dict(G.out_degree(weight="weight"))
    betw = nx.betweenness_centrality(G, weight=None, normalized=True)  # topoloska (broj puteva)
    betw_w = nx.betweenness_centrality(G, weight="weight", normalized=True)
    close = nx.closeness_centrality(G.reverse())  # koliko je cvor "dostizan" od ostalih (obrnuti graf)
    try:
        eig = nx.eigenvector_centrality(G, weight="weight", max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        eig = {n: float("nan") for n in G.nodes()}
    pagerank = nx.pagerank(G, weight="weight")

    metrics = pd.DataFrame({
        "node_id": list(G.nodes()),
        "node_type": [G.nodes[n]["node_type"] for n in G.nodes()],
        "in_degree_w": [in_deg[n] for n in G.nodes()],
        "out_degree_w": [out_deg[n] for n in G.nodes()],
        "betweenness": [betw[n] for n in G.nodes()],
        "betweenness_weighted": [betw_w[n] for n in G.nodes()],
        "closeness_reverse": [close[n] for n in G.nodes()],
        "eigenvector_w": [eig[n] for n in G.nodes()],
        "pagerank_w": [pagerank[n] for n in G.nodes()],
    }).sort_values("pagerank_w", ascending=False)

    metrics.to_csv(PROCESSED_DIR / "network_metrics.csv", index=False)
    print(f"\nMere centralnosti sacuvane -> {PROCESSED_DIR / 'network_metrics.csv'}")

    print("\n=== Top 10 po tezinskom ulaznom stepenu (in-degree) — 'ponori' talenta (F1 timovi koji primaju najvise vozaca) ===")
    print(metrics.sort_values("in_degree_w", ascending=False)[["node_id", "node_type", "in_degree_w"]].head(10).to_string(index=False))

    print("\n=== Top 10 po tezinskom izlaznom stepenu (out-degree) — 'izvori' talenta (najprodukivnije akademije/feeder timovi) ===")
    print(metrics.sort_values("out_degree_w", ascending=False)[["node_id", "node_type", "out_degree_w"]].head(10).to_string(index=False))

    print("\n=== Top 10 po (netezinskoj) betweenness centralnosti — 'mostovi' izmedju delova mreze ===")
    print(metrics.sort_values("betweenness", ascending=False)[["node_id", "node_type", "betweenness"]].head(10).to_string(index=False))

    print("\n=== Top 10 po PageRank-u (tezinski) ===")
    print(metrics.sort_values("pagerank_w", ascending=False)[["node_id", "node_type", "pagerank_w"]].head(10).to_string(index=False))

    # --- community detection (Louvain, na neusmerenoj tezinskoj projekciji) ---
    UG = G.to_undirected()
    # spoji tezine paralelnih grana (A->B i B->A) sabiranjem
    UG2 = nx.Graph()
    for u, v, d in UG.edges(data=True):
        w = d.get("weight", 1)
        if UG2.has_edge(u, v):
            UG2[u][v]["weight"] += w
        else:
            UG2.add_edge(u, v, weight=w)
    for n, d in G.nodes(data=True):
        UG2.add_node(n, **d)

    partition = community_louvain.best_partition(UG2, weight="weight", random_state=42)
    modularity = community_louvain.modularity(partition, UG2, weight="weight")
    print(f"\n=== Community detection (Louvain) ===")
    print(f"Modularnost: {modularity:.3f}")
    n_comms = len(set(partition.values()))
    print(f"Broj detektovanih zajednica: {n_comms}")

    comm_df = pd.DataFrame({
        "node_id": list(partition.keys()),
        "node_type": [G.nodes[n]["node_type"] for n in partition.keys()],
        "community": list(partition.values()),
    }).sort_values(["community", "node_type"])
    comm_df.to_csv(PROCESSED_DIR / "network_communities.csv", index=False)

    for c in sorted(set(partition.values())):
        members = comm_df[comm_df["community"] == c]["node_id"].tolist()
        print(f"\n  Zajednica {c} ({len(members)} clanova):")
        for m in members:
            print(f"    - {m} [{G.nodes[m]['node_type']}]")


if __name__ == "__main__":
    main()
