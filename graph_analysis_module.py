import pandas as pd
import networkx as nx
from sklearn.preprocessing import MinMaxScaler


def compute_graph_features(nodes_df, edges_df):
    G = nx.Graph()
    for _, row in nodes_df.iterrows():
        node_id = row.get("id")
        if not node_id:
            continue
        G.add_node(node_id, **row.to_dict())
    for _, row in edges_df.iterrows():
        src = row.get("src")
        dst = row.get("dst")
        if not src or not dst:
            continue
        G.add_edge(src, dst)

    if G.number_of_nodes() == 0:
        return G

    degree = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    clustering = nx.clustering(G)

    for node in G.nodes():
        G.nodes[node]["degree"] = degree.get(node, 0)
        G.nodes[node]["betweenness"] = betweenness.get(node, 0)
        G.nodes[node]["clustering"] = clustering.get(node, 0)

    return G


def score_c2_nodes(G):
    rows = []
    for node, attrs in G.nodes(data=True):
        score = (
            0.45 * attrs.get("degree", 0) +
            0.45 * attrs.get("betweenness", 0) +
            0.10 * attrs.get("clustering", 0)
        )
        rows.append({
            "id": node,
            "type": attrs.get("type"),
            "degree": attrs.get("degree", 0),
            "betweenness": attrs.get("betweenness", 0),
            "clustering": attrs.get("clustering", 0),
            "c2_score": round(score, 6)
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    for col in ["degree", "betweenness", "clustering", "c2_score"]:
        df[f"{col}_pct"] = MinMaxScaler().fit_transform(df[[col]])

    return df.sort_values("c2_score", ascending=False)