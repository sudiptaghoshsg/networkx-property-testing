# Property-Based Testing for NetworkX Graph Algorithms

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Tests](https://img.shields.io/badge/tests-17%20passing-brightgreen)
![Hypothesis](https://img.shields.io/badge/hypothesis-property--based-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**Authors:** Sudipta Ghosh, Shambo Samanta  
**Course:** E0 251o - Data Structures and Graph Analytics (2026)  
**Institution:** Indian Institute of Science (IISc)

---

## Overview

This project applies **property-based testing** to graph algorithms in NetworkX using the [Hypothesis](https://hypothesis.readthedocs.io/) library.

Instead of relying on hand-crafted test cases, the tests encode fundamental **mathematical properties** (invariants, metamorphic relations, and boundary conditions) that must hold for all valid graphs. Hypothesis automatically generates hundreds of diverse graph instances — varying in size, topology, and edge weights — and searches for counterexamples that violate these properties.

This approach enables systematic validation of core correctness guarantees in graph algorithms such as shortest paths and minimum spanning trees.


---
## Why This Project Matters

Graph algorithms are widely used in networking, transportation, and optimization.
Traditional unit tests validate specific cases, but often miss edge cases and hidden bugs.

This project demonstrates how property-based testing can:
- Validate deep mathematical guarantees (e.g., triangle inequality, cut property)
- Automatically explore thousands of graph structures
- Detect subtle correctness issues that example-based tests miss

It bridges theory (graph properties) with practical testing.

---

## Algorithms Tested

| Algorithm | Module |
|---|---|
| Shortest Path (Dijkstra for weighted graphs / BFS for unit-weight graphs) | `networkx.shortest_path`, `networkx.shortest_path_length` |
| Minimum Spanning Tree (Kruskal / Prim) | `networkx.minimum_spanning_tree` |

---

## Requirements

```bash
pip install networkx hypothesis pytest
```

Or install from the requirements file:

```bash
pip install -r requirements.txt
```

---

## How to Run

Run all 17 tests with verbose output:

```bash
pytest test_graph_properties.py -v
```

Run a specific test:

```bash
pytest test_graph_properties.py::test_mst_cut_property -v
```


---

## Properties Covered

### Shortest Path (8 tests)

| Test | Property Type | Description |
|---|---|---|
| `test_shortest_path_minimality` | Invariant | Returned path is shorter than or equal to all other simple paths |
| `test_shortest_path_symmetry` | Invariant | `d(u,v) == d(v,u)` in undirected graphs |
| `test_shortest_path_edge_addition` | Metamorphic | Adding an edge cannot increase shortest path distance |
| `test_shortest_path_triangle_inequality` | Invariant | `d(u,v) ≤ d(u,w) + d(w,v)` for all node triples |
| `test_shortest_path_self_distance` | Boundary | Distance from any node to itself is zero |
| `test_shortest_path_validity` | Postcondition | Every step in the returned path is a real edge in the graph |
| `test_shortest_path_optimal_substructure` | Invariant | Every sub-path of a shortest path is itself a shortest path |
| `test_dijkstra_varied_weights` | Invariant | Dijkstra finds optimal path with non-uniform positive weights |

### Minimum Spanning Tree (9 tests)

| Test | Property Type | Description |
|---|---|---|
| `test_mst_edge_count` | Invariant | MST of n-node graph has exactly n-1 edges |
| `test_mst_is_tree` | Invariant | MST is acyclic and connected |
| `test_mst_spans_all_nodes` | Postcondition | MST contains every node from the original graph |
| `test_mst_edge_removal_disconnects` | Metamorphic | Removing any MST edge disconnects it |
| `test_mst_idempotence` | Idempotence | MST(MST(G)) == MST(G) |
| `test_mst_cut_property` | Invariant | Minimum weight cut edge must belong to the MST (theoretical foundation of Prim/Kruskal) |
| `test_mst_subgraph_property` | Postcondition | All MST edges exist in the original graph |
| `test_mst_minimal_edges_property` | Invariant | Adding any non-tree edge to MST creates a cycle |
| `test_mst_invariant_under_relabeling` | Metamorphic | Node relabeling does not change MST weight or structure |



---

## Project Structure

```
networkx-property-testing/
├── test_graph_properties.py   # All 17 property-based tests
├── requirements.txt           # Python dependencies
├── README.md                  # This file

```

---

## Key Design Decisions

**Custom Hypothesis strategy:** The `connected_weighted_graphs()` composite strategy generates connected graphs with Hypothesis-controlled topology and edge weights. This allows Hypothesis to shrink failing inputs automatically, producing minimal counterexamples and improving debuggability.

**Varied edge weights:** Tests such as `test_dijkstra_varied_weights` and `test_mst_cut_property` use non-uniform weights (1–20) to exercise the full behavior of Dijkstra’s algorithm and MST algorithms (Kruskal/Prim), rather than limiting evaluation to unit-weight (BFS-equivalent) scenarios.


-----

- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- [NetworkX documentation](https://networkx.org/documentation/stable/)
