import json
from pathlib import Path
import networkx as nx


def build_dashboard(nodes_df, edges_df, c2_df, output_dir):
    output_path = Path(output_dir) / "dashboard.html"

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

    pos = nx.spring_layout(G, seed=42, dim=2) if G.number_of_nodes() else {}
    positions = {str(k): [float(v[0]), float(v[1])] for k, v in pos.items()}

    score_map = {}
    if not c2_df.empty:
        score_map = dict(zip(c2_df["id"], c2_df["c2_score"]))

    nodes = []
    for _, row in nodes_df.iterrows():
        node_id = row.get("id")
        if not node_id:
            continue
        nodes.append({
            "id": node_id,
            "type": row.get("type", "unknown"),
            "score": float(score_map.get(node_id, 0.0)),
            "x": positions.get(node_id, [0.0, 0.0])[0],
            "y": positions.get(node_id, [0.0, 0.0])[1]
        })

    edges = []
    for _, row in edges_df.iterrows():
        src = row.get("src")
        dst = row.get("dst")
        if not src or not dst:
            continue
        edges.append({"src": src, "dst": dst})

    c2_records = c2_df.to_dict(orient="records") if not c2_df.empty else []

    payload = {
        "nodes": nodes,
        "edges": edges,
        "c2": c2_records
    }

    html = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>GrapHunt Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    :root {{
      --bg: #0b0d12;
      --panel: #141824;
      --text: #e8edf2;
      --muted: #9aa6b2;
      --accent: #e35252;
      --chip: #20263a;
    }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      background: radial-gradient(circle at top, #121622, #0b0d12 60%);
      color: var(--text);
    }}
    header {{
      padding: 24px 28px 10px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    h1 {{
      margin: 0;
      font-size: 26px;
      letter-spacing: 0.5px;
    }}
    .sub {{
      color: var(--muted);
      font-size: 14px;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 10px;
    }}
    .stat {{
      background: var(--panel);
      border-radius: 12px;
      padding: 12px 14px;
      box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    }}
    .stat .label {{
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.6px;
    }}
    .stat .value {{
      font-size: 20px;
      font-weight: 600;
      margin-top: 6px;
    }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }}
    .chip {{
      background: var(--chip);
      border-radius: 999px;
      padding: 6px 12px;
      font-size: 12px;
      color: var(--muted);
    }}
    select, input[type="range"] {{
      background: var(--panel);
      color: var(--text);
      border: 1px solid #2a3147;
      border-radius: 8px;
      padding: 6px 10px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 18px;
      padding: 12px 24px 32px;
    }}
    .panel {{
      background: var(--panel);
      border-radius: 12px;
      padding: 12px;
      box-shadow: 0 12px 30px rgba(0,0,0,0.3);
    }}
    .panel h2 {{
      margin: 4px 8px 12px;
      font-size: 14px;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    .plot {{
      width: 100%;
      height: 520px;
    }}
    #heatmap {{
      height: 300px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      padding: 8px 10px;
      border-bottom: 1px solid #232939;
      text-align: left;
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.6px;
    }}
    @media (min-width: 1100px) {{
      .grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>GrapHunt Dashboard</h1>
      <div class="sub">2D relationship map, heatmap, and top IOC scoring.</div>
    </div>
    <div class="stats" id="stats"></div>
    <div class="controls">
      <span class="chip">Filters</span>
      <label>Type:
        <select id="typeFilter"></select>
      </label>
      <label>Min score:
        <input id="scoreFilter" type="range" min="0" max="1" step="0.01" value="0" />
        <span id="scoreValue">0.00</span>
      </label>
    </div>
  </header>
  <section class="grid">
    <div class="panel">
      <h2>Relationships (Top 10)</h2>
      <div id="network" class="plot"></div>
    </div>
    <div class="panel">
      <h2>Heatmap (Top 10)</h2>
      <div id="heatmap" class="plot"></div>
    </div>
    <div class="panel">
      <h2>Top IOC Table (Top 10)</h2>
      <div id="table"></div>
      <div style="padding: 10px 4px 2px;">
        <button id="downloadCsv" style="background:#e35252;color:#fff;border:none;padding:8px 12px;border-radius:8px;cursor:pointer;">
          Download Full IOC List (CSV)
        </button>
      </div>
    </div>
  </section>
  <script>
    const DATA = {json.dumps(payload)};
    const metricLabelMap = {{
      degree_pct: "Connectivity (normalized)",
      betweenness_pct: "Bridge Role (normalized)",
      clustering_pct: "Local Density (normalized)",
      c2_score_pct: "C2 Risk (normalized)"
    }};
    const metrics = Object.keys(DATA.c2[0] || {{}}).filter(k => k.endsWith("_pct"));
    const typeFilter = document.getElementById("typeFilter");
    const scoreFilter = document.getElementById("scoreFilter");
    const scoreValue = document.getElementById("scoreValue");
    const statsEl = document.getElementById("stats");

    const types = ["all"].concat([...new Set(DATA.nodes.map(n => n.type))].sort());
    types.forEach(t => {{
      const opt = document.createElement("option");
      opt.value = t;
      opt.textContent = t;
      typeFilter.appendChild(opt);
    }});

    function updateStats(filtered) {{
      const counts = filtered.reduce((acc, n) => {{
        acc.total += 1;
        acc[n.type] = (acc[n.type] || 0) + 1;
        return acc;
      }}, {{total: 0}});
      statsEl.innerHTML = "";
      const makeCard = (label, value) => {{
        const div = document.createElement("div");
        div.className = "stat";
        div.innerHTML = '<div class="label">' + label + '</div><div class="value">' + value + '</div>';
        return div;
      }};
      statsEl.appendChild(makeCard("Total IOCs", counts.total || 0));
      Object.keys(counts).filter(k => k !== "total").sort().forEach(k => {{
        statsEl.appendChild(makeCard(k, counts[k]));
      }});
    }}

    function applyFilters() {{
      const type = typeFilter.value;
      const minScore = parseFloat(scoreFilter.value);
      scoreValue.textContent = minScore.toFixed(2);

      const filteredNodes = DATA.nodes.filter(n =>
        (type === "all" || n.type === type) && n.score >= minScore
      );

      const topNodes = filteredNodes
        .sort((a, b) => b.score - a.score)
        .slice(0, 10);

      const nodeIds = new Set(topNodes.map(n => n.id));
      const filteredEdges = DATA.edges.filter(e => nodeIds.has(e.src) && nodeIds.has(e.dst));

      updateStats(filteredNodes);
      drawNetwork(topNodes, filteredEdges);
      drawHeatmap(topNodes);
      drawTable(topNodes);
    }}

    function drawNetwork(nodes, edges) {{
      const traces = [];
      const edgeX = [];
      const edgeY = [];
      edges.forEach(e => {{
        const s = nodes.find(n => n.id === e.src);
        const d = nodes.find(n => n.id === e.dst);
        if (!s || !d) return;
        edgeX.push(s.x, d.x, null);
        edgeY.push(s.y, d.y, null);
      }});
      traces.push({{
        x: edgeX,
        y: edgeY,
        mode: "lines",
        line: {{color: "rgba(180,180,180,0.4)", width: 1}},
        hoverinfo: "none"
      }});

      const typeSymbols = {{
        ip: "diamond",
        domain: "circle",
        url: "triangle-up",
        hash: "square",
        unknown: "x"
      }};

      const nodeTrace = {{
        x: nodes.map(n => n.x),
        y: nodes.map(n => n.y),
        mode: "markers",
        text: nodes.map(n => n.id + "<br>type: " + n.type + "<br>score: " + n.score.toFixed(3)),
        hoverinfo: "text",
        marker: {{
          size: nodes.map(n => 8 + n.score * 18),
          color: nodes.map(n => n.score),
          colorscale: "Reds",
          symbol: nodes.map(n => typeSymbols[n.type] || "circle"),
          line: {{width: 0.5, color: "#fff"}},
          opacity: 0.9
        }}
      }};
      traces.push(nodeTrace);

      Plotly.newPlot("network", traces, {{
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: {{visible: false}},
        yaxis: {{visible: false}},
        margin: {{l: 0, r: 0, b: 0, t: 10}}
      }}, {{displayModeBar: false}});
    }}

    function drawHeatmap(nodes) {{
      if (!metrics.length || nodes.length === 0) {{
        Plotly.newPlot("heatmap", [], {{margin: {{l: 30, r: 30, t: 20, b: 20}}}});
        return;
      }}
      const lookup = new Map(DATA.c2.map(r => [r.id, r]));
      const ids = nodes.map(n => n.id);
      const z = metrics.map(m => ids.map(id => (lookup.get(id)?.[m] ?? 0)));
      const trace = {{
        z: z,
        x: ids,
        y: metrics.map(m => metricLabelMap[m] || m),
        type: "heatmap",
        colorscale: "Reds"
      }};
      Plotly.newPlot("heatmap", [trace], {{
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        margin: {{l: 70, r: 20, t: 10, b: 70}},
        xaxis: {{tickangle: -35, automargin: true, tickfont: {{size: 10}}}},
        yaxis: {{automargin: true, tickfont: {{size: 10}}}}
      }}, {{displayModeBar: false}});
    }}

    function drawTable(nodes) {{
      const header = ["id", "type", "score"];
      const rows = nodes.map(n => [n.id, n.type, n.score.toFixed(4)]);
      let html = "<table><thead><tr>" + header.map(h => "<th>" + h + "</th>").join("") + "</tr></thead><tbody>";
      rows.forEach(r => {{
        html += "<tr>" + r.map(c => "<td>" + c + "</td>").join("") + "</tr>";
      }});
      html += "</tbody></table>";
      document.getElementById("table").innerHTML = html;
    }}

    function downloadCsv() {{
      const records = DATA.c2.slice().sort((a, b) => (b.c2_score || 0) - (a.c2_score || 0));
      if (!records.length) {{
        alert("No IOC data available.");
        return;
      }}
      const headers = Object.keys(records[0]);
      const lines = [headers.join(",")];
      records.forEach(r => {{
        const row = headers.map(h => {{
          const val = r[h] === null || r[h] === undefined ? "" : String(r[h]);
          return '"' + val.replace(/"/g, '""') + '"';
        }});
        lines.push(row.join(","));
      }});
      const blob = new Blob([lines.join("\\n")], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "c2_iocs_full.csv";
      a.click();
      URL.revokeObjectURL(url);
    }}

    document.getElementById("downloadCsv").addEventListener("click", downloadCsv);
    typeFilter.addEventListener("change", applyFilters);
    scoreFilter.addEventListener("input", applyFilters);
    applyFilters();
  </script>
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)
