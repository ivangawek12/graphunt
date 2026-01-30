import plotly.graph_objects as go
import networkx as nx
import numpy as np


def build_2d_network_graph(G, c2_df=None, title="GrapHunt Network Graph"):
    if G.number_of_nodes() == 0:
        fig = go.Figure()
        fig.update_layout(title=title)
        return fig

    pos = nx.spring_layout(G, seed=42, dim=2)
    node_list = list(G.nodes())
    node_xy = np.array([pos[v] for v in node_list])
    edge_xy = [(pos[u], pos[v]) for u, v in G.edges()]

    score_map = {}
    if c2_df is not None and not c2_df.empty:
        score_map = dict(zip(c2_df["id"], c2_df["c2_score"]))

    colors, sizes, hovertexts, symbols = [], [], [], []
    for node in node_list:
        data = G.nodes[node]
        score = score_map.get(node, 0)
        ttype = data.get("type", "")

        colors.append(score)
        sizes.append(8 + (data.get("degree", 0) * 25))
        symbols.append(_symbol_for_type(ttype))

        text = f"{node}<br>type: {ttype}"
        text += f"<br>degree: {round(data.get('degree', 0), 3)}"
        text += f"<br>betweenness: {round(data.get('betweenness', 0), 3)}"
        text += f"<br>c2_score: {round(score, 4)}"
        hovertexts.append(text)

    node_trace = go.Scatter(
        x=node_xy[:, 0], y=node_xy[:, 1],
        mode="markers",
        marker=dict(
            size=sizes,
            color=colors,
            colorscale="Reds",
            opacity=0.9,
            symbol=symbols,
            line=dict(width=0.5, color="white"),
            colorbar=dict(title="c2_score")
        ),
        text=hovertexts,
        hoverinfo="text"
    )

    edge_trace = go.Scatter(
        x=[x for e in edge_xy for x in [e[0][0], e[1][0], None]],
        y=[y for e in edge_xy for y in [e[0][1], e[1][1], None]],
        mode="lines",
        line=dict(color="gray", width=1),
        hoverinfo="none"
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=title,
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=40),
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white"),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig


def _symbol_for_type(ttype):
    ttype = (ttype or "").lower()
    if ttype == "ip":
        return "diamond"
    if ttype == "domain":
        return "circle"
    if ttype == "url":
        return "triangle-up"
    if ttype == "hash":
        return "square"
    return "x"
