import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pyvis.network import Network
import streamlit.components.v1 as components
import os
import tempfile
from PIL import Image
import base64

# Konfigurasi halaman dengan tema yang lebih profesional
st.set_page_config(
    page_title="Transaction Network Analysis", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk styling dashboard seperti Power BI/Tableau
st.markdown("""
<style>
    /* Warna tema dan font */
    :root {
        --main-color: #0078D4;  /* Warna utama Power BI */
        --secondary-color: #83C9FF;  /* Warna sekunder */
        --background-color: #F5F5F5;  /* Warna latar belakang */
        --text-color: #252525;  /* Warna teks */
        --accent-color: #FF5733;  /* Warna aksen untuk highlight */
    }
    
    /* Header styling */
    .main-header {
        background-color: var(--main-color);
        color: white;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Card styling seperti di Power BI */
    .metric-card {
        background-color: white;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card h4 {
        color: #0078D4;  /* Changed to blue */
        margin-bottom: 10px;
    }
    
    .metric-card p, .metric-card ul {
        color: #333333;  /* Darker gray for better readability */
    }
    
    .metric-card strong {
        color: #0078D4;  /* Blue for emphasis */
    }
    
    .metric-card li {
        color: #333333;  /* Darker gray for list items */
        margin-bottom: 5px;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #0078D4;  /* Blue for values */
    }
    
    .metric-label {
        font-size: 14px;
        color: #333333;  /* Darker gray for labels */
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: var(--main-color);
    }
    
    .metric-label {
        font-size: 14px;
        color: gray;
    }
    
    /* Styling untuk sidebar */
    .css-1d391kg, .css-12oz5g7 {
        background-color: white;
    }
    
    /* Styling untuk tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f0f0;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        border: none;
        transition: background-color 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--main-color);
        color: white;
    }
    
    /* Styling untuk tabel */
    .dataframe {
        border: none !important;
    }
    
    .dataframe th {
        background-color: var(--main-color);
        color: white;
        font-weight: normal;
        border: none !important;
        text-align: left;
        padding: 12px 15px !important;
    }
    
    .dataframe td {
        text-align: left;
        border-bottom: 1px solid #f0f0f0 !important;
        border-left: none !important;
        border-right: none !important;
        padding: 10px 15px !important;
    }
    
    .dataframe tr:hover {
        background-color: #f5f9ff;
    }
    
    /* Styling untuk visualisasi */
    .plot-container {
        background-color: white;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .plot-container:hover {
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    }
    
    /* Filter pills styling */
    .filter-pill {
        display: inline-block;
        background-color: #e6f2ff;
        border: 1px solid #0078D4;
        border-radius: 20px;
        padding: 5px 15px;
        margin-right: 10px;
        margin-bottom: 10px;
        font-size: 12px;
        color: #0078D4;
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .loading-pulse {
        animation: pulse 1.5s infinite ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# Header dengan logo dan judul (seperti di Power BI/Tableau)
st.markdown("""
<div class="main-header">
    <h1>Transaction Network Analysis Dashboard</h1>
    <p>Analisis Jaringan Transaksi untuk Akuisisi dan Retensi Nasabah</p>
</div>
""", unsafe_allow_html=True)

# Tabs untuk navigasi seperti di Power BI/Tableau
tabs = st.tabs(["📊 Dashboard", "🔍 Network Analysis", "📈 Metrics & Insights", 
                "📋 Recommendations", "🔍 Network Graph"])


# Load data
@st.cache_data
def load_data():
    try:
        # Baca data dari Excel file
        df = pd.read_excel("UNAIR - GRAPH NEW.xlsx")
        
        # Drop duplicate data
        df = df.drop_duplicates()
        
        # Buat kolom 'source' dan 'target' berdasarkan arah transaksi
        def get_transaction_direction(row):
            if row['type'].upper() == 'INCOMING':
                return pd.Series({
                    'source': f"{row['sender_recipient_name']} ({row['sender_recipient_bank']})",
                    'target': f"{row['debitor_name']} ({row['debitor_bank']})"
                })
            elif row['type'].upper() == 'OUTGOING':
                return pd.Series({
                    'source': f"{row['debitor_name']} ({row['debitor_bank']})",
                    'target': f"{row['sender_recipient_name']} ({row['sender_recipient_bank']})"
                })
            else:
                return pd.Series({'source': None, 'target': None})
        
        # Terapkan fungsi untuk membuat kolom source dan target
        transaction_edges = df.copy()
        transaction_edges[['source', 'target']] = transaction_edges.apply(get_transaction_direction, axis=1)
        
        # Pilih kolom penting untuk analisis graf
        graph_df = transaction_edges[['source', 'target', 'amount_tx_idr', 'trx', 'type']]
        
        # Baca data nodes dan edges jika tersedia
        try:
            nodes_df = pd.read_csv("nodes.csv")
            edges_df = pd.read_csv("edges.csv")
        except:
            nodes_df = None
            edges_df = None
        
        return df, graph_df, nodes_df, edges_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

# Load data
df, graph_df, nodes_df, edges_df = load_data()

# Sidebar dengan tema Power BI/Tableau
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #0078D4;'>Filter & Controls</h3>", unsafe_allow_html=True)
    
    # Tambahkan tanggal terakhir update data
    st.markdown("<p style='text-align: center; font-size: 12px; color: gray;'>Last updated: June 2023</p>", unsafe_allow_html=True)
    
    # Filter jumlah node teratas dengan slider yang lebih menarik
    st.markdown("<p class='metric-label'>Top Nodes</p>", unsafe_allow_html=True)
    top_n = st.slider("Jumlah Node Teratas", 5, 1000, 20, label_visibility="collapsed")
    
    # Filter berdasarkan nilai transaksi dengan format yang lebih baik
    st.markdown("<p class='metric-label'>Transaction Value Range (IDR)</p>", unsafe_allow_html=True)
    min_amount = float(df['amount_tx_idr'].min())
    max_amount = float(df['amount_tx_idr'].max())
    amount_range = st.slider("Rentang Nilai Transaksi", 
                           min_amount, max_amount, 
                           (min_amount, max_amount),
                           format="%.0f",
                           label_visibility="collapsed")
    
    # Filter berdasarkan tipe transaksi dengan multiselect yang lebih menarik
    st.markdown("<p class='metric-label'>Transaction Types</p>", unsafe_allow_html=True)
    transaction_types = df['type'].unique().tolist()
    selected_types = st.multiselect("Tipe Transaksi", transaction_types, default=transaction_types, label_visibility="collapsed")
    
    # Tambahkan filter bank
    st.markdown("<p class='metric-label'>Bank Filter</p>", unsafe_allow_html=True)
    all_banks = list(set(
        df['debitor_bank'].unique().tolist() + 
        df['sender_recipient_bank'].unique().tolist()
    ))
    selected_banks = st.multiselect(
        "Filter by Bank", 
        all_banks, 
        default=["B1"],  # Updated default value to match your data
        label_visibility="collapsed"
    )
    
    # Pengaturan visualisasi dengan tema yang lebih menarik
    st.markdown("<h4 style='text-align: center; color: #0078D4; margin-top: 20px;'>Visualization Settings</h4>", unsafe_allow_html=True)
    
    st.markdown("<p class='metric-label'>Node Size</p>", unsafe_allow_html=True)
    node_size_factor = st.slider("Ukuran Node", 10, 1000, 300, label_visibility="collapsed")
    
    st.markdown("<p class='metric-label'>Edge Width</p>", unsafe_allow_html=True)
    edge_width_factor = st.slider("Ketebalan Edge", 0.1, 10.0, 1.0, label_visibility="collapsed")
    
    # Pilihan metrik untuk analisis dengan selectbox yang lebih menarik
    st.markdown("<p class='metric-label'>Analysis Metric</p>", unsafe_allow_html=True)
    metric_options = ["Degree Centrality", "In-Degree Centrality", "Out-Degree Centrality", 
                     "Betweenness Centrality", "PageRank", "Total Transaction Value"]
    selected_metric = st.selectbox("Metrik untuk Analisis", metric_options, label_visibility="collapsed")
    
    # Tambahkan tombol refresh data
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()  # Changed from experimental_rerun() to rerun()

# Filter data berdasarkan pilihan pengguna
filtered_df = df[(df['amount_tx_idr'] >= amount_range[0]) & 
                (df['amount_tx_idr'] <= amount_range[1]) & 
                (df['type'].isin(selected_types))]

# Filter berdasarkan bank yang dipilih jika ada
if selected_banks:
    filtered_df = filtered_df[(filtered_df['debitor_bank'].isin(selected_banks)) | 
                             (filtered_df['sender_recipient_bank'].isin(selected_banks))]

# Buat kolom source dan target untuk data yang difilter
filtered_df[['source', 'target']] = filtered_df.apply(lambda row: pd.Series({
    'source': f"{row['sender_recipient_name']} ({row['sender_recipient_bank']})",
    'target': f"{row['debitor_name']} ({row['debitor_bank']})"
}) if row['type'].upper() == 'INCOMING' else pd.Series({
    'source': f"{row['debitor_name']} ({row['debitor_bank']})",
    'target': f"{row['sender_recipient_name']} ({row['sender_recipient_bank']})"
}), axis=1)

filtered_graph_df = filtered_df[['source', 'target', 'amount_tx_idr', 'trx', 'type']]

# Buat graph dari data yang difilter
G = nx.from_pandas_edgelist(filtered_graph_df, 'source', 'target', 
                           edge_attr=['amount_tx_idr', 'trx', 'type'], 
                           create_using=nx.DiGraph())

# Hitung metrik berdasarkan pilihan pengguna
if selected_metric == "Degree Centrality":
    centrality = nx.degree_centrality(G)
    metric_name = "Degree Centrality"
    metric_desc = "Mengukur jumlah koneksi langsung yang dimiliki setiap node"
    metric_interpretation = "Nilai tinggi menunjukkan entitas yang memiliki banyak koneksi transaksi"
    acquisition_retention = "Entitas dengan degree centrality tinggi adalah kandidat utama untuk retensi karena memiliki banyak koneksi dalam jaringan transaksi"
    
elif selected_metric == "In-Degree Centrality":
    centrality = nx.in_degree_centrality(G)
    metric_name = "In-Degree Centrality"
    metric_desc = "Mengukur jumlah transaksi masuk ke setiap node"
    metric_interpretation = "Nilai tinggi menunjukkan entitas yang menerima banyak transaksi dari entitas lain"
    acquisition_retention = "Entitas dengan in-degree centrality tinggi adalah kandidat utama untuk retensi karena menerima banyak transaksi"
    
elif selected_metric == "Out-Degree Centrality":
    centrality = nx.out_degree_centrality(G)
    metric_name = "Out-Degree Centrality"
    metric_desc = "Mengukur jumlah transaksi keluar dari setiap node"
    metric_interpretation = "Nilai tinggi menunjukkan entitas yang melakukan banyak transaksi ke entitas lain"
    acquisition_retention = "Entitas dengan out-degree centrality tinggi adalah kandidat utama untuk retensi karena aktif melakukan transaksi"
    
elif selected_metric == "Betweenness Centrality":
    centrality = nx.betweenness_centrality(G)
    metric_name = "Betweenness Centrality"
    metric_desc = "Mengukur seberapa sering sebuah node berada di jalur terpendek antara node lainnya"
    metric_interpretation = "Nilai tinggi menunjukkan entitas yang menjadi perantara penting dalam jaringan transaksi"
    acquisition_retention = "Entitas dengan betweenness centrality tinggi adalah kandidat utama untuk retensi karena berperan sebagai perantara penting dalam jaringan"
    
elif selected_metric == "PageRank":
    centrality = nx.pagerank(G)
    metric_name = "PageRank"
    metric_desc = "Mengukur pentingnya sebuah node berdasarkan struktur koneksi dalam jaringan"
    metric_interpretation = "Nilai tinggi menunjukkan entitas yang terhubung dengan entitas penting lainnya"
    acquisition_retention = "Entitas dengan PageRank tinggi adalah kandidat utama untuk retensi karena memiliki pengaruh besar dalam jaringan"
    
elif selected_metric == "Total Transaction Value":
    # Hitung total nilai transaksi untuk setiap node
    centrality = {}
    for node in G.nodes():
        # Transaksi masuk
        in_edges = G.in_edges(node, data=True)
        in_value = sum(edge[2]['amount_tx_idr'] for edge in in_edges)
        
        # Transaksi keluar
        out_edges = G.out_edges(node, data=True)
        out_value = sum(edge[2]['amount_tx_idr'] for edge in out_edges)
        
        # Total nilai transaksi
        centrality[node] = in_value + out_value
    
    metric_name = "Total Transaction Value"
    metric_desc = "Mengukur total nilai transaksi (masuk dan keluar) untuk setiap entitas"
    metric_interpretation = "Nilai tinggi menunjukkan entitas dengan nilai transaksi besar"
    acquisition_retention = "Entitas dengan total nilai transaksi tinggi adalah kandidat utama untuk retensi karena memiliki nilai bisnis yang besar"

# Tambahkan metrik ke node
for node in G.nodes():
    G.nodes[node]['centrality'] = centrality.get(node, 0)

# Identifikasi node Maybank
maybank_nodes = [node for node in G.nodes() if "(PT. BANK MAYBANK INDONESIA, TBK)" in node]

# Identifikasi top nodes berdasarkan metrik yang dipilih
top_nodes = sorted([(node, centrality.get(node, 0)) for node in G.nodes()], 
                  key=lambda x: x[1], reverse=True)[:top_n]
top_node_names = [node[0] for node in top_nodes]

# Buat subgraf untuk top nodes
top_subgraph = G.subgraph(top_node_names)

# Tab 1: Overview
with tabs[0]:
    # Kartu metrik seperti di Power BI
    st.markdown("<h3 style='color: #0078D4;'>Network Overview</h3>", unsafe_allow_html=True)
    
    # Buat kartu metrik dengan styling Power BI
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-label">Total Nodes</p>
            <p class="metric-value">{}</p>
        </div>
        """.format(len(G.nodes())), unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-label">Total Connections</p>
            <p class="metric-value">{}</p>
        </div>
        """.format(len(G.edges())), unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-label">Network Density</p>
            <p class="metric-value">{:.6f}</p>
        </div>
        """.format(nx.density(G)), unsafe_allow_html=True)
        
    with col4:
        try:
            diameter = nx.diameter(G)
            diameter_text = str(diameter)
        except:
            diameter_text = "N/A (Disconnected)"
            
        st.markdown("""
        <div class="metric-card">
            <p class="metric-label">Network Diameter</p>
            <p class="metric-value">{}</p>
        </div>
        """.format(diameter_text), unsafe_allow_html=True)
    
    # Visualisasi distribusi nilai transaksi dengan Plotly (lebih interaktif seperti Power BI)
    st.markdown("<h3 style='color: #0078D4; margin-top: 20px;'>Transaction Insights</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram nilai transaksi dengan Plotly
        fig = px.histogram(filtered_df, x="amount_tx_idr", nbins=30,
                          title="Transaction Value Distribution",
                          labels={"amount_tx_idr": "Transaction Value (IDR)", "count": "Frequency"},
                          color_discrete_sequence=['#0078D4'])
        
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=40, b=10),
            font=dict(color="#252525"),
            xaxis=dict(showgrid=True, gridcolor="#E5E5E5"),
            yaxis=dict(showgrid=True, gridcolor="#E5E5E5")
        )
        
        # Add hover template for better tooltips
        fig.update_traces(hovertemplate='Value: %{x:,.0f} IDR<br>Count: %{y}')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Pie chart untuk tipe transaksi dengan Plotly
        type_counts = filtered_df['type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']
        
        fig = px.pie(type_counts, values='Count', names='Type',
                    title="Transaction Type Distribution",
                    color_discrete_sequence=['#0078D4', '#83C9FF', '#005A9E', '#B3D6FF'])
        
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=40, b=10),
            font=dict(color="#252525"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Segoe UI")
        )
        
        # Add hover template for better tooltips
        fig.update_traces(hovertemplate='%{label}<br>Count: %{value} (%{percent})')
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tampilkan transaksi teratas dengan styling tabel Power BI
    st.markdown("<h3 style='color: #0078D4; margin-top: 20px;'>Top Transactions</h3>", unsafe_allow_html=True)
    
    top_transactions = filtered_df.sort_values('amount_tx_idr', ascending=False).head(10)
    top_transactions_display = top_transactions[['debitor_name', 'sender_recipient_name', 'amount_tx_idr', 'type']].copy()
    top_transactions_display['amount_tx_idr'] = top_transactions_display['amount_tx_idr'].apply(lambda x: f"{x:,.2f} IDR")
    top_transactions_display.columns = ['Debitor Name', 'Sender/Recipient Name', 'Transaction Amount', 'Type']
    
    st.dataframe(top_transactions_display, use_container_width=True)

# Tab 2: Network Analysis
with tabs[1]:
    st.markdown("<h3 style='color: #0078D4;'>Network Visualization</h3>", unsafe_allow_html=True)
    
    # Buat visualisasi interaktif dengan PyVis yang lebih menarik
    net = Network(height="600px", width="100%", directed=True, notebook=False, bgcolor="#ffffff", font_color="#252525")
    
    # Tambahkan node dan edge ke visualisasi dengan styling yang lebih baik
    for node in top_subgraph.nodes():
        # Hitung jumlah koneksi (degree) untuk node
        node_degree = top_subgraph.degree(node)
        size = 10 + (node_degree * 2)  # Ukuran dasar lebih kecil dan faktor pengali lebih kecil
        
        # Warna berbeda untuk node berdasarkan bank
        if "(B1)" in node:
            net.add_node(node, label=node, size=size, title=f"{node}\nJumlah Koneksi: {node_degree}", color="#FF8C00", borderWidth=2, shadow=True)
        elif "(PT. BANK MAYBANK INDONESIA, TBK)" in node:
            net.add_node(node, label=node, size=size, title=f"{node}\nJumlah Koneksi: {node_degree}", color="#0078D4", borderWidth=2, shadow=True)
        else:
            net.add_node(node, label=node, size=size, title=f"{node}\nJumlah Koneksi: {node_degree}", color="#83C9FF", borderWidth=2, shadow=True)
    
    # Tambahkan edge dengan atribut dan styling yang lebih baik
    for source, target, attr in top_subgraph.edges(data=True):
        width = max(2, 1 + (attr.get('amount_tx_idr', 0) / max_amount * edge_width_factor))  # Minimal width 2
        title = f"Amount: {attr.get('amount_tx_idr', 0):,.2f} IDR\nType: {attr.get('type', 'N/A')}"
        net.add_edge(source, target, width=width, title=title, color="#0078D4", arrows={"to": {"enabled": True, "scaleFactor": 1.5}})
    
    # Konfigurasi visualisasi dengan tema Power BI
    net.toggle_physics(True)
    net.set_options("""
    const options = {
        "nodes": {
        "font": {
            "size": 12,
            "face": "Segoe UI"
        },
        "borderWidth": 2,
        "shadow": true
        },
        "edges": {
        "arrows": {
            "to": {
            "enabled": true,
            "scaleFactor": 1.5
            }
        },
        "color": {
            "inherit": false
        },
        "smooth": {
            "type": "continuous",
            "forceDirection": "none"
        },
        "width": 2,
        "shadow": true
        },
        "physics": {
        "forceAtlas2Based": {
            "gravitationalConstant": -50,
            "centralGravity": 0.01,
            "springLength": 100,
            "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {
            "enabled": true,
            "iterations": 1000,
            "updateInterval": 25
        }
        },
        "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true
        }
    }
    """)
    
    # Simpan dan tampilkan visualisasi
    try:
        path = os.path.join(tempfile.gettempdir(), "network_graph.html")
        net.save_graph(path)
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        components.html(html, height=600)
    except Exception as e:
        st.error(f"Error displaying interactive visualization: {e}")

# Tab 3: Metrics
with tabs[2]:
    st.markdown("<h3 style='color: #0078D4;'>Network Metrics Analysis</h3>", unsafe_allow_html=True)
    
    # Informasi metrik dengan styling yang lebih baik
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="height: 200px;">
            <h4 style="color: #0078D4;">{}</h4>
            <p><strong>Description:</strong> {}</p>
            <p><strong>Interpretation:</strong> {}</p>
        </div>
        """.format(metric_name, metric_desc, metric_interpretation), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="height: 200px;">
            <h4 style="color: #0078D4;">Acquisition & Retention Strategy</h4>
            <p><strong>Recommendation:</strong> {}</p>
        </div>
        """.format(acquisition_retention), unsafe_allow_html=True)

# Kesimpulan
st.subheader("Kesimpulan")

st.markdown(f"""
### Berdasarkan analisis jaringan transaksi menggunakan {metric_name}:

1. **Nasabah yang harus diretensi terlebih dahulu:**
   - Nasabah Maybank dengan {metric_name} tertinggi, terutama yang memiliki banyak koneksi dengan entitas lain
   - Nasabah yang menjadi perantara penting dalam jaringan transaksi (betweenness centrality tinggi)
   - Nasabah dengan nilai transaksi total yang besar

2. **Calon nasabah yang harus diakuisisi terlebih dahulu:**
   - Entitas non-Maybank dengan {metric_name} tertinggi
   - Entitas yang sering bertransaksi dengan nasabah Maybank yang penting
   - Entitas dengan nilai transaksi besar ke nasabah Maybank

3. **Strategi akuisisi dan retensi:**
   - Fokus pada entitas yang memiliki peran sentral dalam jaringan transaksi
   - Prioritaskan entitas dengan nilai transaksi besar
   - Perhatikan pola transaksi untuk mengidentifikasi peluang cross-selling dan up-selling

**Insight:** {acquisition_retention}
""", unsafe_allow_html=True)

# Tabel Top Nodes berdasarkan metrik
st.markdown(f"<h4 style='color: #0078D4;'>Top {top_n} Entities by {metric_name}</h4>", unsafe_allow_html=True)

top_nodes_df = pd.DataFrame(top_nodes, columns=['Entity', metric_name])
top_nodes_df[metric_name] = top_nodes_df[metric_name].apply(lambda x: f"{x:,.4f}")
st.dataframe(top_nodes_df, use_container_width=True)

# Tab 4: Recommendations
with tabs[3]:
    st.markdown("<h3 style='color: #0078D4;'>Recommendations for Acquisition & Retention</h3>", unsafe_allow_html=True)

    st.markdown("""
    <div class="metric-card">
        <h4 style="color: #0078D4;">Retention Candidates (Maybank)</h4>
        <ul>
            <li>Maintain and strengthen relationships with top-performing Maybank customers</li>
            <li>Offer loyalty programs or tailored financial products</li>
            <li>Monitor changes in transaction behavior closely</li>
        </ul>
    </div>
    
    <div class="metric-card">
        <h4 style="color: #0078D4;">Acquisition Targets (Non-Maybank)</h4>
        <ul>
            <li>Engage with high-centrality non-Maybank entities that frequently transact with Maybank clients</li>
            <li>Provide competitive offers and onboarding incentives</li>
            <li>Highlight value through targeted marketing using transaction patterns</li>
        </ul>
    </div>
    
    <div class="metric-card">
        <h4 style="color: #0078D4;">Strategic Actions</h4>
        <ul>
            <li>Leverage network analysis to identify hidden influencers and bridge entities</li>
            <li>Integrate network metrics into CRM for proactive client management</li>
            <li>Use transaction patterns to detect risk or fraud early</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
# Tab 6: Retention & Acquisition Visualization
with tabs[4]:
    st.markdown("<h3 style='color: #0078D4;'>Visualisasi Retensi dan Akuisisi</h3>", unsafe_allow_html=True)
    
    vis_option = st.radio("Pilih Jenis Visualisasi:", 
                          ["Berdasarkan Nominal", "Berdasarkan Frekuensi", "Tanpa Pembobotan"], 
                          horizontal=True)
    
    vis_file = ""
    if vis_option == "Berdasarkan Nominal":
        vis_file = "nominal.html"
    elif vis_option == "Berdasarkan Frekuensi":
        vis_file = "frekuensi.html"
    elif vis_option == "Tanpa Pembobotan":
        vis_file = "stuktur_unweighted.html"

    try:
        with open(vis_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=650, scrolling=True)
    except Exception as e:
        st.error(f"Visualisasi tidak ditemukan. Pastikan file `{vis_file}` ada di direktori.")

