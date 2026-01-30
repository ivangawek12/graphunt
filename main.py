import argparse
import os
import webbrowser
import pandas as pd
from dotenv import load_dotenv

from vt_query import vt_intelligence_search, build_graph_from_search_response, DEFAULT_RELATIONSHIPS
from graph_analysis_module import compute_graph_features, score_c2_nodes
from graph_plot_module import build_2d_network_graph
from report_module import generate_heatmap, render_top_c2_table
from dashboard_module import build_dashboard


def build_demo_data():
    nodes = [
        {"id": "hash_demo_a", "type": "hash"},
        {"id": "hash_demo_b", "type": "hash"},
        {"id": "example.com", "type": "domain"},
        {"id": "8.8.8.8", "type": "ip"},
        {"id": "http://example.com/path", "type": "url"},
        {"id": "malicious.test", "type": "domain"},
    ]
    edges = [
        {"src": "hash_demo_a", "dst": "example.com", "relationship": "contacted_domains"},
        {"src": "hash_demo_a", "dst": "8.8.8.8", "relationship": "contacted_ips"},
        {"src": "hash_demo_a", "dst": "http://example.com/path", "relationship": "contacted_urls"},
        {"src": "hash_demo_b", "dst": "malicious.test", "relationship": "contacted_domains"},
        {"src": "hash_demo_b", "dst": "8.8.8.8", "relationship": "contacted_ips"},
    ]
    return pd.DataFrame(nodes), pd.DataFrame(edges)


def run(query, limit, output_dir, open_outputs, relationships, demo=False):
    load_dotenv()

    if demo:
        nodes_df, edges_df = build_demo_data()
    else:
        if not query:
            raise ValueError("Query is required unless --demo is set.")
        response_json = vt_intelligence_search(
            query=query,
            limit=limit,
            relationships=relationships
        )
        nodes, edges = build_graph_from_search_response(response_json)
        nodes_df = pd.DataFrame(nodes)
        edges_df = pd.DataFrame(edges)

    if nodes_df.empty or edges_df.empty:
        print("No nodes or edges were returned. Try a different query or enable --demo.")
        return

    G = compute_graph_features(nodes_df, edges_df)
    c2_df = score_c2_nodes(G)

    os.makedirs(output_dir, exist_ok=True)

    nodes_path = os.path.join(output_dir, "nodes.csv")
    edges_path = os.path.join(output_dir, "edges.csv")
    c2_path = os.path.join(output_dir, "c2_scores.csv")
    graph_path = os.path.join(output_dir, "graph_network.html")
    heatmap_path = os.path.join(output_dir, "c2_heatmap.html")

    nodes_df.to_csv(nodes_path, index=False)
    edges_df.to_csv(edges_path, index=False)
    if not c2_df.empty:
        c2_df.to_csv(c2_path, index=False)

    fig_graph = build_2d_network_graph(G, c2_df, title="GrapHunt Network Map")
    fig_heatmap = generate_heatmap(c2_df)
    fig_graph.write_html(graph_path)
    fig_heatmap.write_html(heatmap_path)

    print(f"Saved: {nodes_path}")
    print(f"Saved: {edges_path}")
    if not c2_df.empty:
        print(f"Saved: {c2_path}")
    print(f"Saved: {graph_path}")
    print(f"Saved: {heatmap_path}")

    top_table = render_top_c2_table(c2_df, top_n=10)
    if not top_table.empty:
        print("\nTop C2 Candidates:")
        print(top_table.to_string(index=False))

    dashboard_path = build_dashboard(
        nodes_df=nodes_df,
        edges_df=edges_df,
        c2_df=c2_df,
        output_dir=output_dir
    )
    print(f"Saved: {dashboard_path}")

    if open_outputs:
        webbrowser.open(dashboard_path)


def parse_args():
    parser = argparse.ArgumentParser(description="GrapHunt CLI - Threat Infra Mapper")
    parser.add_argument("--query", type=str, help="VT search query string")
    parser.add_argument("--limit", type=int, default=40, help="Limit of results from VT (default=40)")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    parser.add_argument("--open", action="store_true", help="Open HTML reports in browser")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    parser.add_argument(
        "--relationships",
        type=str,
        default=",".join(DEFAULT_RELATIONSHIPS),
        help="Comma-separated VT relationships to include in search"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    relationships = [r.strip() for r in args.relationships.split(",") if r.strip()]
    run(
        query=args.query,
        limit=args.limit,
        output_dir=args.output,
        open_outputs=args.open,
        relationships=relationships,
        demo=args.demo
    )
