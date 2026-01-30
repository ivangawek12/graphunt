# Graphunt
GrapHunt is a CLI tool designed to analyze malware command &amp; control (C2) infrastructure through relationship graph analysis. It queries VirusTotal Intelligence for threat data, builds relationship networks, computes graph centrality metrics, and generates interactive HTML dashboards for threat visualization and analysis.
## 🎯 Objective

GrapHunt automates the process of:
- Querying VirusTotal Intelligence for malware samples and their IOCs (Indicators of Compromise)
- Building relationship graphs connecting malware hashes, domains, IPs, and URLs
- Computing network centrality metrics to identify critical C2 infrastructure nodes
- Generating interactive dashboards and heatmaps for threat analysis
- Scoring and ranking suspicious nodes by their importance in the C2 network
- 
<img width="1309" height="639" alt="image" src="https://github.com/user-attachments/assets/ece02a61-5265-4867-bd6c-3c9b34833077" />

## 📋 Project Description

### Overview
GrapHunt takes VirusTotal search queries as input and transforms the results into an analyzable network graph. By computing graph-based metrics such as degree centrality, betweenness centrality, and clustering coefficients, it identifies the most significant nodes in malware C2 networks.

### Key Features
- **VirusTotal Intelligence Integration**: Direct API queries for threat intelligence
- **Graph Analysis**: NetworkX-based computation of network centrality metrics
- **C2 Scoring Algorithm**: Weighted scoring combining:
  - Degree Centrality (45%): Number of connections
  - Betweenness Centrality (45%): Network bottleneck importance
  - Clustering Coefficient (10%): Local network connectivity
- **Interactive Visualizations**: 
  - Network graph visualization (2D layout)
  - C2 heatmaps for quick threat assessment
  - Top C2 nodes ranking table
- **Comprehensive Dashboard**: All-in-one HTML interface with integrated charts and data

### Project Structure

```
GrapHunt/
├── main.py                      # Entry point and orchestration
├── main_orchestrator.py          # Workflow coordination
├── vt_query.py                  # VirusTotal API query interface
├── vt_query_search.py           # Search query builder
├── graph_analysis_module.py     # Graph metrics computation (degree, betweenness, clustering, C2 scoring)
├── graph_plot_module.py         # Network graph visualization (Plotly)
├── dashboard_module.py          # Interactive dashboard generation
├── report_module.py             # Heatmap and summary table generation
├── graphhunt_c2.py             # C2-specific analysis utilities
├── graphhunt_viz.py            # Visualization helpers
├── requirements.txt             # Python dependencies
├── .env                         # Environment configuration (VT API key)
├── run.ps1                      # PowerShell launcher script
└── output/                      # Generated outputs
    ├── dashboard.html           # Interactive dashboard
    ├── graph_network.html       # Network visualization
    ├── c2_heatmap.html         # C2 scoring heatmap
    ├── c2_scores.csv           # C2 node metrics (CSV export)
    ├── nodes.csv               # Node list (CSV export)
    └── edges.csv               # Edge relationships (CSV export)
```

### Output Files

- **dashboard.html**: Main interactive dashboard with all visualizations, charts, and C2 rankings
- **graph_network.html**: Standalone 2D network graph visualization with node positioning
- **c2_heatmap.html**: Color-coded heatmap showing C2 node scores and metrics
- **c2_scores.csv**: Detailed metrics for all nodes including normalized percentile scores
- **nodes.csv**: List of all nodes with their types
- **edges.csv**: List of all relationships between nodes

## 🚀 Installation

### Prerequisites
- Python 3.8+
- VirusTotal Intelligence API key (get one at https://www.virustotal.com/gui/home/upload)

### Step 1: Clone or Download the Repository
```bash
git clone https://github.com/yourusername/GrapHunt.git
cd GrapHunt
```

### Step 2: Create Environment Configuration
Create a `.env` file in the project root with your VirusTotal API key:
```
VT_API_KEY=your_virustotal_intelligence_api_key_here
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `plotly`: Interactive visualizations
- `scikit-learn`: Machine learning utilities (MinMaxScaler for normalization)
- `python-dotenv`: Environment variable management
- `requests`: HTTP library for API calls
- `networkx`: Graph analysis and algorithms

## 📖 Usage

### Basic Usage

#### Query VirusTotal Intelligence
Run a search query against VirusTotal Intelligence (requires valid API key):

```bash
python main.py --query "tag:apk p:3+ fs:30d+" --limit 60 --open
```

#### Command-Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--query` | VirusTotal Intelligence search query | `"tag:apk p:3+"` |
| `--limit` | Maximum number of results to fetch | `60` |
| `--open` | Automatically open dashboard in browser | Flag (no value) |
| `--demo` | Run with demo data (no API key required) | Flag (no value) |
| `--output-dir` | Custom output directory | `./results` |
| `--relationships` | Comma-separated relationships to include | `contacted_domains,contacted_ips` |

#### Example Queries

**Find recently modified Android malware:**
```bash
python main.py --query "tag:apk p:3+ fs:30d+" --limit 60 --open
```

**Analyze phishing samples from the past week:**
```bash
python main.py --query "tag:phishing fs:7d+" --limit 50 --open
```

**Examine high-prevalence trojans:**
```bash
python main.py --query "tag:trojan p:5+" --limit 100 --open
```

### Demo Mode
Run GrapHunt with built-in demo data without needing a VirusTotal API key:

```bash
python main.py --demo --open
```

This generates a sample C2 network with synthetic relationships for testing and evaluation.

## 📊 Understanding the Metrics

### Graph Metrics

- **Degree Centrality**: Number of direct connections to a node, normalized to 0-1 scale
  - High values indicate nodes with many connections (potential C2 infrastructure hubs)

- **Betweenness Centrality**: How often a node appears on shortest paths between other nodes, normalized to 0-1 scale
  - High values indicate critical bottleneck nodes that control network communication

- **Clustering Coefficient**: Measure of local clustering around a node, normalized to 0-1 scale
  - High values indicate densely connected node neighborhoods

### C2 Score

Combined weighted score for identifying Command & Control infrastructure:
```
C2_Score = (0.45 × Degree) + (0.45 × Betweenness) + (0.10 × Clustering)
```

Normalized to 0-1 scale (`c2_score_pct`) for easy ranking and comparison.

### Node Types

- **hash**: File hash (MD5, SHA1, SHA256) representing malware samples
- **domain**: Domain name contacted by malware
- **ip**: IP address contacted by malware
- **url**: Full URL contacted by malware

## 🔍 Workflow

1. **Query VirusTotal**: Fetch malware samples and IOCs based on search criteria
2. **Build Graph**: Create network from relationships between hashes, domains, IPs, and URLs
3. **Compute Metrics**: Calculate degree, betweenness, and clustering for all nodes
4. **Score C2 Nodes**: Apply weighted algorithm to identify critical infrastructure
5. **Generate Visualizations**: Create interactive HTML dashboards and network graphs
6. **Export Data**: Save results as CSV and HTML formats

## 📦 Output Format

### CSV Files
- **c2_scores.csv**: Contains all metrics with both raw and normalized (percentage) values
  - Columns: `id`, `type`, `degree`, `betweenness`, `clustering`, `c2_score`, `degree_pct`, `betweenness_pct`, `clustering_pct`, `c2_score_pct`
  
- **nodes.csv**: List of all network nodes
- **edges.csv**: List of all relationships (source → destination)

### HTML Dashboards
- Interactive charts and visualizations powered by Plotly
- Click-and-drag network graphs
- Sortable data tables
- Color-coded threat scoring

## ⚙️ Configuration

### Environment Variables
Set in `.env` file:
- `VT_API_KEY`: Your VirusTotal Intelligence API key (required for non-demo mode)

### Relationships
Default relationships analyzed:
- `contacted_domains`
- `contacted_ips`
- `contacted_urls`
- `execution_parents`
- `execution_children`

Customize with `--relationships` flag.

## 🛠️ Development

### Project Modules

| Module | Purpose |
|--------|---------|
| `vt_query.py` | VirusTotal API interface and graph building |
| `graph_analysis_module.py` | NetworkX metrics computation |
| `graph_plot_module.py` | Plotly-based network visualization |
| `dashboard_module.py` | Interactive HTML dashboard generation |
| `report_module.py` | Heatmap and summary table generation |
| `main.py` | CLI entry point and orchestration |

## 📝 License

This project is provided as-is for security research and threat intelligence purposes.

## 🙏 Acknowledgments

- **VirusTotal**: Malware and IOC database
- **NetworkX**: Graph analysis algorithms
- **Plotly**: Interactive visualization library

## 📧 Support

For issues, questions, or contributions, please open an issue in the repository.

---

**Note**: GrapHunt requires a valid VirusTotal Intelligence API key for full functionality. Demo mode is available for testing without an API key.
