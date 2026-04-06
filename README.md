# Property-Based Testing for NetworkX Graph Algorithms

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-29%20passing-brightgreen)](https://github.com/sudiptaghoshsg/networkx-property-testing)
[![Hypothesis](https://img.shields.io/badge/hypothesis-property--based-orange)](https://hypothesis.readthedocs.io/)
[![pytest](https://img.shields.io/badge/pytest-tested-blueviolet)](https://docs.pytest.org/)
[![NetworkX](https://img.shields.io/badge/networkx-graph%20library-yellowgreen)](https://networkx.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow)](https://github.com/sudiptaghoshsg/networkx-property-testing?tab=MIT-1-ov-file)

**Authors:** Sudipta Ghosh, Shambo Samanta  
**Course:** Data Structures and Graph Analytics  
**Institution:** Indian Institute of Science (IISc)

---

## Overview

This project applies **property-based testing** to graph algorithms in NetworkX using the [Hypothesis](https://hypothesis.readthedocs.io/) library.

Instead of relying on hand-crafted test cases, the tests encode fundamental **mathematical properties** (invariants, metamorphic relations, and boundary conditions) that must hold for all valid graphs. Hypothesis automatically generates hundreds of diverse graph instances — varying in size, topology, and edge weights — and searches for counterexamples that violate these properties.

This approach enables systematic validation of core correctness guarantees in graph algorithms such as shortest paths and minimum spanning trees.


---
## Why This Project Matters

Graph algorithms are foundational to networking, transportation, logistics, and optimization. Traditional unit tests validate specific hand-crafted examples but are fundamentally limited — they can only verify anticipated cases, leaving edge cases and subtle bugs undiscovered.

This project demonstrates how **property-based testing** can:

- Validate deep mathematical guarantees — triangle inequality, cut property, cycle property, and optimal substructure  
- Automatically explore thousands of graph structures — 5,000+ examples across varying sizes, topologies, and weight distributions  
- Detect subtle correctness issues that example-based tests miss — floating-point inconsistencies, multigraph edge selection, and negative weight behavior  
- Ground testing in formal theory — properties are derived from classical results (Tarjan, 1983), not ad-hoc checks  

It bridges the gap between theoretical graph algorithms and practical software correctness verification — demonstrating that property-based testing is not merely a testing technique, but a tool for reasoning about algorithm behavior.

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

Run all 29 tests with verbose output:

```bash
pytest test_graph_properties.py -v
```

Run a specific test:

```bash
pytest test_graph_properties.py::test_mst_cut_property -v
```


---

## Properties Covered

### Shortest Path (11 tests)

| Test | Property Type | Description |
|---|---|---|
| `test_shortest_path_minimality` | Invariant | Returned path is shorter than or equal to all other simple paths |
| `test_shortest_path_symmetry` | Invariant | `d(u,v) == d(v,u)` in undirected graphs |
| `test_shortest_path_edge_addition` | Metamorphic | Adding an edge cannot increase shortest path distance |
| `test_shortest_path_triangle_inequality` | Invariant | `d(u,v) ≤ d(u,w) + d(w,v)` for all node triples |
| `test_shortest_path_self_distance` | Boundary | Distance from any node to itself is zero |
| `test_shortest_path_validity` | Postcondition | Every step in the returned path is a real edge in the graph |
| `test_shortest_path_monotonicity_under_weight_increase` | Metamorphic | Increasing any edge weight cannot decrease shortest path distance |
| `test_shortest_path_optimal_substructure` | Invariant | Every sub-path of a shortest path is itself a shortest path |
| `test_dijkstra_varied_weights` | Invariant | Dijkstra finds optimal path with non-uniform positive weights |
| `test_shortest_path_no_repeated_nodes` | Postcondition | Shortest path is a simple path — no node appears twice |
| `test_shortest_path_length_consistency` | Postcondition | `shortest_path_length` equals sum of edge weights along `shortest_path` |

### Minimum Spanning Tree (15 tests)

| Test | Property Type | Description |
|---|---|---|
| `test_mst_edge_count` | Invariant | MST of n-node graph has exactly n-1 edges |
| `test_mst_is_tree` | Invariant | MST is acyclic and connected |
| `test_mst_spans_all_nodes` | Postcondition | MST contains every node from the original graph |
| `test_mst_edge_removal_disconnects` | Metamorphic | Removing any MST edge disconnects it |
| `test_mst_idempotence` | Idempotence | MST(MST(G)) == MST(G) |
| `test_mst_cut_property` | Invariant | Minimum weight cut edge must belong to the MST (foundation of Prim/Kruskal) |
| `test_mst_on_disconnected_graph_returns_forest` | Boundary | MST of disconnected graph returns a valid spanning forest |
| `test_mst_subgraph_property` | Postcondition | All MST edges exist in the original graph |
| `test_mst_minimal_edges_property` | Invariant | Adding any non-tree edge to MST creates a cycle |
| `test_mst_invariant_under_relabeling` | Metamorphic | Node relabeling does not change MST weight or structure |
| `test_mst_weight_scaling` | Metamorphic | Scaling all weights by a constant does not change the MST |
| `test_mst_total_weight_minimality` | Invariant | MST weight ≤ every other spanning tree (direct definition check) |
| `test_mst_cycle_property` | Invariant | Maximum weight edge in any cycle must NOT be in the MST |
| `test_mst_uniqueness_under_distinct_weights` | Invariant | With distinct weights, Kruskal and Prim return identical edge sets |
| `test_mst_cut_and_cycle_duality` | Invariant | Every non-tree edge is heavier than every MST edge it could replace |

### Boundary (1 test)

| Test | Property Type | Description |
|---|---|---|
| `test_small_graph_edge_cases` | Boundary | Correct behaviour on very small graphs (1–3 nodes) |

### Robustness & Bug Exploration Tests (2 tests)

| Test | Property Type | Description |
|---|---|---|
| `test_dijkstra_negative_weight_detection` | Robustness | Dijkstra vs Bellman-Ford consistency on negative weights |
| `test_mst_dense_graph_cut_property` | Robustness | Cut property holds on complete graphs for every possible cut |

---

## Project Structure

```
networkx-property-testing/
├── test_graph_properties.py   # All 29 property-based tests
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── docs/                      # Demo & execution artifacts
│   ├── demo.gif               # Short test execution demo
│   ├── output.jpg             # Screenshot of test results
│   └── test_run.log           # Full pytest output with statistics

```

---

## Key Design Decisions

**Custom Hypothesis Strategy:** A custom composite strategy `connected_weighted_graphs()` is used to generate connected graphs with controlled topology and edge weights. By relying entirely on Hypothesis (instead of Python’s `random` module), failing examples can be automatically minimized (“shrunk”), making debugging significantly easier.

**Deterministic Weight Generation:** All edge weights are generated using deterministic patterns instead of random sampling. This ensures reproducibility, better shrinking behavior, and eliminates flaky test outcomes.

**Increased Test Coverage:** Most tests use `@settings(max_examples=200)` to explore a larger input space than the default, increasing the likelihood of discovering subtle edge cases.

**Property-Based Testing Approach:** Tests verify - invariants (e.g., symmetry, minimality), metamorphic relations (e.g., edge addition effects), structural guarantees (e.g., MST properties)  

This provides stronger correctness guarantees than example-based testing.

**MST Theoretical Foundations:** Tests such as `test_mst_cycle_property`, `test_mst_cut_property`, and `test_mst_cut_and_cycle_duality` collectively validate the fundamental cut and cycle properties of MSTs — forming a near-complete theoretical characterization of minimum spanning trees.

These properties are rooted in classical results (e.g., Tarjan, 1983, *Data Structures and Network Algorithms*), ensuring the test suite is grounded in formal graph theory.

**Test Independence:** Each test operates on a fresh graph instance, avoiding shared state and ensuring reliable execution.


-----

## Hypothesis Statistics

Run with:
```bash
pytest test_graph_properties.py -v --hypothesis-show-statistics
```

Results (Python 3.13, Hypothesis 6.151.9):

| Test | Examples Run | Failures | Stopped Because |
|---|---|---|---|
| `test_shortest_path_minimality` | 200 | 0 | max_examples=200 |
| `test_shortest_path_symmetry` | 200 | 0 | max_examples=200 |
| `test_shortest_path_edge_addition` | 200 | 0 | max_examples=200 |
| `test_shortest_path_triangle_inequality` | 200 | 0 | max_examples=200 |
| `test_shortest_path_self_distance` | 200 | 0 | max_examples=200 |
| `test_shortest_path_validity` | 200 | 0 | max_examples=200 |
| `test_shortest_path_monotonicity_under_weight_increase` | 200 | 0 | max_examples=200 |
| `test_shortest_path_optimal_substructure` | 200 | 0 | max_examples=200 |
| `test_dijkstra_varied_weights` | 200 | 0 | max_examples=200 |
| `test_shortest_path_no_repeated_nodes` | 200 | 0 | max_examples=200 |
| `test_shortest_path_length_consistency` | 200 | 0 | max_examples=200 |
| `test_mst_edge_count` | 200 | 0 | max_examples=200 |
| `test_mst_is_tree` | 200 | 0 | max_examples=200 |
| `test_mst_spans_all_nodes` | 200 | 0 | max_examples=200 |
| `test_mst_edge_removal_disconnects` | 200 | 0 | max_examples=200 |
| `test_mst_idempotence` | 200 | 0 | max_examples=200 |
| `test_mst_cut_property` | 200 | 0 | max_examples=200 |
| `test_mst_on_disconnected_graph_returns_forest` | 200 | 0 | max_examples=200 |
| `test_mst_subgraph_property` | 200 | 0 | max_examples=200 |
| `test_mst_minimal_edges_property` | 200 | 0 | max_examples=200 |
| `test_mst_invariant_under_relabeling` | 200 | 0 | max_examples=200 |
| `test_mst_weight_scaling` | 200 | 0 | max_examples=200 |
| `test_mst_total_weight_minimality` | 200 | 0 | max_examples=200 |
| `test_mst_cycle_property` | 200 | 0 | max_examples=200 |
| `test_mst_uniqueness_under_distinct_weights` | 200 | 0 | max_examples=200 |
| `test_mst_cut_and_cycle_duality` | 200 | 0 | max_examples=200 |

**Total: ~5,203 automatically generated graph examples tested across 26 tests. 0 failures.**

> `test_small_graph_edge_cases` exhausts its search space at 3 examples by design — path graphs of size 1, 2, and 3 are the only valid inputs for that boundary test.

---

## Resources
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- [NetworkX documentation](https://networkx.org/documentation/stable/)
