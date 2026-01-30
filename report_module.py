import pandas as pd
import plotly.express as px


def generate_heatmap(c2_df, max_rows=30):
    if c2_df.empty:
        fig = px.imshow([[0]], labels=dict(x="IOC", y="Metric", color="Normalized Value"))
        fig.update_layout(title="C2 Scoring Heatmap")
        return fig

    pct_cols = [c for c in c2_df.columns if c.endswith("_pct")]
    display_cols = ["id", "type"] + pct_cols
    heatmap_data = c2_df[display_cols].head(max_rows).copy()
    heatmap_data = heatmap_data.set_index("id")

    fig = px.imshow(
        heatmap_data[pct_cols].T,
        labels=dict(x="IOC", y="Metric", color="Normalized Value"),
        x=heatmap_data.index,
        y=pct_cols,
        aspect="auto",
        color_continuous_scale="Reds",
    )

    fig.update_layout(
        title="C2 Scoring Heatmap",
        xaxis_title="IOC",
        yaxis_title="Metric",
        margin=dict(l=40, r=40, t=60, b=60),
        template="plotly_dark"
    )
    return fig


def render_top_c2_table(c2_df, top_n=10):
    if c2_df.empty:
        return pd.DataFrame()
    top_df = c2_df.sort_values("c2_score", ascending=False).head(top_n)
    display_cols = ["id", "type", "c2_score", "degree", "betweenness", "clustering"]
    return top_df[display_cols].round(4)