# Property-Based Testing for Graph Algorithms

## 📌 Overview
This project implements **property-based testing** for graph algorithms using:

- NetworkX (graph algorithms)
- Hypothesis (property-based testing)

Instead of testing fixed inputs, this approach validates **mathematical properties**
across automatically generated graph structures.

---

## 🧠 Algorithms Covered

### 1. Shortest Path (Dijkstra)
- Computes minimum distance between nodes in a graph.

### 2. Minimum Spanning Tree (MST)
- Finds a tree connecting all nodes with minimum total edge weight.

---

## 🔍 Properties Tested

### 🔹 Shortest Path Properties
- **Minimality (Invariant)**: Shortest path is minimal among all paths
- **Symmetry (Invariant)**: d(u, v) = d(v, u) in undirected graphs
- **Edge Addition (Metamorphic)**: Adding edges does not increase shortest path
- **Triangle Inequality (Invariant)**: `d(u,v) ≤ d(u,w) + d(w,v)` for all node triples
- **Self Distance (Boundary)**: Distance from any node to itself is zero
- **Path Validity (Postcondition)**: Every step in the returned path is a real edge in the graph

---

### 🌲 Minimum Spanning Tree (MST) Properties
- **Edge Count (Invariant)**: MST has exactly n - 1 edges
- **Tree Structure (Invariant)**: MST is acyclic and connected
- **Spanning (Postcondition)**: Includes all nodes
- **Edge Removal (Metamorphic)**: Removing any edge disconnects the MST
- **Cut Property (Invariant)**: Minimum weight cut edge must belong to the MST (theoretical foundation of Prim/Kruskal)

---

### ⚡ Advanced Properties
- **Idempotence**: MST(MST(G)) = MST(G)

---


## ⚙️ Setup

```bash
pip install -r requirements.txt
pytest test_graph_properties.py
