<div align="center">
<h1 align="center">Property-Based Testing for NetworkX Graph Algorithms</h1>
 <br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-32%20Passing-22C55E?style=for-the-badge&logo=checkmarx&logoColor=white)](https://github.com/sudiptaghoshsg/networkx-property-testing)
[![Hypothesis](https://img.shields.io/badge/Hypothesis-Property--Based-F97316?style=for-the-badge)](https://hypothesis.readthedocs.io/)
[![pytest](https://img.shields.io/badge/pytest-Tested-7C3AED?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![NetworkX](https://img.shields.io/badge/NetworkX-Graph%20Library-84CC16?style=for-the-badge)](https://networkx.org/)
[![License](https://img.shields.io/badge/License-MIT-EAB308?style=for-the-badge)](https://github.com/sudiptaghoshsg/networkx-property-testing/blob/main/LICENSE)

<div align="center">
<h4>Authors</h4>
</div>
<table cellpadding="10" cellspacing="0" border="0">
  <tr>
    <td align="center" valign="top" style="padding: 0 32px;">
      <strong>Sudipta Ghosh</strong><br/>
      SR No: 13-19-02-19-52-24-1-24485<br/>
    </td>
    <td align="center" valign="top" style="padding: 0 32px; border-left: 1px solid #555;">
      <strong>Shambo Samanta</strong><br/>
      SR No: 13-19-02-19-52-24-1-24505<br/>
    </td>
  </tr>
</table>


**Course:** E0 251o: Data Structures and Graph Analytics <br/> **Institution:** Indian Institute of Science (IISc)

<br/>

> *"Instead of asking 'does this example work?' — we ask 'does this property always hold?'"*


</div>

---

## ◈ Overview

This project applies **property-based testing** to graph algorithms in [NetworkX](https://networkx.org/) using the [Hypothesis](https://hypothesis.readthedocs.io/) library.

Instead of relying on hand-crafted test cases, each test encodes a fundamental **mathematical property** — an invariant, postcondition, or metamorphic relation — that must hold for *all* valid graphs. Hypothesis automatically generates hundreds of diverse graph instances, varying in size, topology, and edge weights, and systematically searches for counterexamples that violate these properties.

**6,200+ automatically generated graph examples. 32 tests. 0 failures.**

---

## ◈ Why This Matters

Graph algorithms underpin networking, transportation, logistics, and optimization. Traditional unit tests can only verify anticipated cases — they are fundamentally limited to the inputs a developer thought to write down.

| Traditional Testing | Property-Based Testing |
|---|---|
| Tests specific hand-crafted examples | Tests mathematical properties over thousands of inputs |
| Finds bugs you anticipated | Finds bugs you didn't think of |
| Hard to reason about correctness | Properties derived directly from formal graph theory |
| Brittle to refactoring | Compact, expressive, and theory-grounded |

This project bridges **formal graph theory** and **practical software verification** — demonstrating that property-based testing is not just a testing technique, but a tool for reasoning about algorithmic correctness.

---

## ◈ Algorithms Tested

```
┌──────────────────────────────────────────────────────────────────────┐
│  SHORTEST PATH                                                       │
│  └─ Dijkstra (weighted graphs) · BFS (unit-weight graphs)           │
│     nx.shortest_path  ·  nx.shortest_path_length                    │
│                                                                      │
│  MINIMUM SPANNING TREE                                               │
│  └─ Kruskal  ·  Prim                                                 │
│     nx.minimum_spanning_tree                                         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## ◈ Project Structure

```
networkx-property-testing/
│
├── test_graph_properties.py     # Property-based test suite (32 tests)
├── requirements.txt             # Project dependencies
├── README.md                    # This file
│
└── docs/
    ├── output.gif               # Full test run (animated)
    ├── output.png               # Full test run (screenshot)
    ├── output.log               # Test execution log
    └── output_single_test.jpg   # Single test execution (example)
```

---

## ◈ Requirements

```bash
pip install networkx hypothesis pytest
```

Or from the requirements file:

```bash
pip install -r requirements.txt
```

---

## ◈ Running the Tests

```bash
# Run all tests with verbose output
pytest test_graph_properties.py -v

# Run a specific test
pytest test_graph_properties.py::test_mst_cut_property -v

# Show Hypothesis statistics (examples generated per test)
pytest test_graph_properties.py -v --hypothesis-show-statistics
```

---

## ◈ Test Run Output

![Test Run Output](docs/output.gif)

---

## ◈ Custom Graph Strategy

All tests are powered by a shared `connected_weighted_graphs()` Hypothesis composite strategy that generates connected graphs with full Hypothesis control over topology and weights.

```python
@st.composite
def connected_weighted_graphs(draw):
    n = draw(st.integers(min_value=3, max_value=10))
    G = nx.path_graph(n)           # deterministic connected base
    # extra edges added via Hypothesis-controlled choices
    # weights 1–20 assigned via Hypothesis (not random module)
    return G
```

**Why this matters:**
- Uses Hypothesis throughout (not `random`) → failing examples are **automatically shrunk** to the smallest reproducible case
- Guaranteed connectivity → algorithms always receive valid inputs
- Varied topology and weights → broad, meaningful coverage of the input space

---

## ◈ Full Test Suite

### 1 · Shortest Path &nbsp;*(11 tests)*

---

#### `test_shortest_path_minimality` — *Invariant*
> The path returned by Dijkstra has the minimum total weight among all simple paths between source and target.

**Foundation:** Dijkstra's algorithm is provably optimal for non-negative edge weights. No other simple path can have lower total weight.  
**Verification:** Enumerates all simple paths via `nx.all_simple_paths` and asserts none has a lower weight than the reported shortest path.

---

#### `test_shortest_path_symmetry` — *Invariant*
> In an undirected graph, `d(u, v) == d(v, u)`.

**Foundation:** Any path from `u` to `v` in an undirected graph can be reversed to yield an identical-weight path from `v` to `u`. Asymmetry would indicate the algorithm is incorrectly treating edges as directed internally.

---

#### `test_shortest_path_edge_addition` — *Metamorphic*
> Adding a direct edge between two nodes cannot increase the shortest path distance between them.

**Foundation:** Adding edge `(u, v)` introduces a new candidate path. All existing paths remain valid. Therefore, distance can only stay the same or decrease — never increase.  
**Mutation:** Adds a weight-1 direct edge between source and target, then recomputes.

---

#### `test_shortest_path_triangle_inequality` — *Invariant*
> For any three nodes `u`, `v`, `w` :&nbsp; `d(u, v) ≤ d(u, w) + d(w, v)`

**Foundation:** Graph shortest-path distance is a metric. The triangle inequality is a fundamental axiom of any metric space. A violation means the distance function is not a true metric — indicating fundamental inconsistency in how the algorithm computes distances.

---

#### `test_shortest_path_self_distance` — *Boundary Condition*
> The shortest path distance from any node to itself is zero.

**Foundation:** The trivial empty path has weight 0. Since all weights ≥ 1, no negative alternative exists. A non-zero self-distance means the algorithm traversed unnecessary edges — a basic correctness failure.

---

#### `test_shortest_path_validity` — *Postcondition*
> Every consecutive pair of nodes in the returned path must be connected by an actual edge in the graph.

**Foundation:** A path is a sequence of adjacent nodes. A returned path containing a non-existent edge is not a valid path at all — the algorithm fabricated a connection, which would corrupt any application relying on the result.

---

#### `test_shortest_path_monotonicity_under_weight_increase` — *Metamorphic*
> Increasing the weight of any edge can only increase or maintain the shortest path distance — it can never decrease it.

**Foundation:** If the shortest path uses the modified edge, its cost increases. If it doesn't, the distance is unchanged. Either way, `d_after ≥ d_before`.  
**Strategy:** Uses `st.data()` to draw a random edge and increment `δ ∈ [1, 10]` fully via Hypothesis — fully reproducible and shrinkable on failure.

---

#### `test_shortest_path_optimal_substructure` — *Invariant*
> Every sub-path of a shortest path is itself a shortest path.

**Foundation:** This is the principle of **optimal substructure** — the theoretical reason Dijkstra and dynamic programming work at all. Formally: if `P = (v₀, …, vₖ)` is shortest from `v₀` to `vₖ`, then for any `i < j`, sub-path `P[i..j]` is shortest from `vᵢ` to `vⱼ`. A failure here means the algorithmic foundation is broken, not merely the output.

---

#### `test_dijkstra_varied_weights` — *Invariant*
> Dijkstra returns the correct shortest path with varied positive edge weights — not just unit weights.

**Foundation:** With varied weights, the fewest-hop path may not be the cheapest. This test exercises the priority-queue logic that makes Dijkstra handle heterogeneous weights — a strictly stronger correctness check than unit-weight tests.

---

#### `test_shortest_path_no_repeated_nodes` — *Postcondition*
> The shortest path must be a simple path — no node appears more than once.

**Foundation:** In a graph with non-negative edge weights, any path visiting a node twice contains a cycle of strictly positive weight. Removing the cycle yields a shorter path. An optimal path is therefore always simple.

---

#### `test_shortest_path_length_consistency` — *Postcondition*
> `nx.shortest_path_length` must equal the sum of edge weights along the path returned by `nx.shortest_path`.

**Foundation:** These are two independent NetworkX functions that must be internally consistent. Any discrepancy would silently corrupt applications that use the path for routing and the length for cost estimation simultaneously.

---

### 2 · Minimum Spanning Tree &nbsp;*(15 tests)*

---

#### `test_mst_edge_count` — *Invariant*
> A spanning tree of a connected graph with `n` nodes has exactly `n − 1` edges.

**Foundation:** Provable by induction. Fewer edges leaves some node disconnected; more edges introduces a cycle. Exactly `n − 1` is the unique valid count for any tree.

---

#### `test_mst_is_tree` — *Invariant*
> The MST result must be acyclic and connected — a valid tree by definition.

**Foundation:** A spanning tree is (1) connected and (2) acyclic. `nx.is_tree` checks both simultaneously. Failure means the algorithm produced a disconnected subgraph or one containing a cycle — both are fundamental correctness failures.

---

#### `test_mst_spans_all_nodes` — *Postcondition*
> The MST must contain every node from the original graph.

**Foundation:** "Spanning" means all vertices are covered. A subgraph missing even one vertex is not a spanning tree by definition.

---

#### `test_mst_edge_removal_disconnects` — *Invariant*
> Removing any single edge from the MST must disconnect it.

**Foundation:** A tree is minimally connected — every edge is a bridge. Removing any edge splits the tree into exactly two components. If the graph remains connected after removal, the MST contained a redundant edge, meaning it has a cycle and is not a valid tree.

---

#### `test_mst_idempotence` — *Idempotence*
> `MST(MST(G)) == MST(G)`

**Foundation:** A tree `T` is already acyclic and connected — its own unique spanning tree is itself. Applying the MST algorithm to `T` must return `T` unchanged. Failure means the algorithm is not stable under repeated application.

---

#### `test_mst_cut_property` — *Invariant*
> For any cut of the graph, the minimum weight edge crossing the cut must belong to the MST (when the minimum is unique).

**Foundation:** The **Cut Property** is the theoretical foundation of both Prim's and Kruskal's algorithms. If the minimum cut edge `e` is not in MST `T`, adding `e` creates a cycle. That cycle crosses the cut at least twice, so another cut edge `e'` exists in `T`. Since `w(e) ≤ w(e')`, swapping gives a spanning tree of equal or lesser weight — contradicting `T` being the unique MST.

---

#### `test_mst_on_disconnected_graph_returns_forest` — *Boundary Condition*
> Applying MST to a disconnected graph returns a spanning forest — one tree per connected component.

**Foundation:** When a graph has `k` components with `n₁, …, nₖ` nodes, the spanning forest has `∑(nᵢ − 1) = n − k` total edges and exactly `k` connected components.  
**Strategy:** Composes two independent `connected_weighted_graphs()` draws into a disjoint union by relabelling nodes to avoid overlap.

---

#### `test_mst_subgraph_property` — *Postcondition*
> Every edge in the MST must be an edge in the original graph.

**Foundation:** A spanning tree is by definition a subgraph of `G`. It cannot introduce edges that don't exist in `G`. A fabricated edge is a critical bug that would invalidate any result depending on actual graph structure.

---

#### `test_mst_minimal_edges_property` — *Invariant*
> Adding any non-tree edge from the original graph to the MST creates a cycle.

**Foundation:** A spanning tree uses exactly `n − 1` edges to connect all nodes. Adding any further edge between two nodes already connected in the tree creates a cycle. If no cycle forms, the MST was missing an edge and does not span all vertices.

---

#### `test_mst_invariant_under_relabeling` — *Metamorphic*
> Node relabeling does not change the MST edge count or total weight.

**Foundation:** Graph algorithms operate on structure (topology + weights), not on node names. Relabeling is a graph isomorphism — the optimal spanning structure is determined entirely by edge weights and connectivity, not node identifiers.

---

#### `test_mst_weight_scaling` — *Metamorphic*
> Multiplying all edge weights by a positive constant does not change the set of edges selected for the MST.

**Foundation:** Kruskal's and Prim's algorithms select edges based on their **relative ordering**. Scaling all weights by `k > 0` preserves the total order: `w_i < w_j ↔ k·w_i < k·w_j`. The same edges are selected in the same order, producing an identical MST.

---

#### `test_mst_total_weight_minimality` — *Invariant (Global Optimality)*
> The MST weight must be ≤ the total weight of every other spanning tree of the graph.

**Foundation:** This is the **direct definition** of a minimum spanning tree. Uses `nx.SpanningTreeIterator` to enumerate every spanning tree exhaustively and compare — the strongest possible optimality check, verifying the definition literally.  
**Note:** Limited to `n ≤ 7` nodes for tractability (Cayley's formula gives `n^(n−2)` spanning trees for complete graphs; `n=7` gives at most 16,807).

---

#### `test_mst_cycle_property` — *Invariant*
> For any cycle in the graph, the maximum weight edge in that cycle must NOT be in the MST (when the maximum is unique).

**Foundation:** The **Cycle Property** is the exact dual of the Cut Property. If the max-weight cycle edge `e` is in MST `T`, removing `e` splits `T`. The cycle must contain another crossing path with edge `e'` where `w(e') ≤ w(e)`. Replacing `e` with `e'` yields a spanning tree of equal or lesser weight — contradiction.  
**Dual relationship:** Cut Property → edges that *must* be included. Cycle Property → edges that *must* be excluded.

---

#### `test_mst_uniqueness_under_distinct_weights` — *Invariant*
> When all edge weights are distinct, Kruskal's and Prim's algorithms must return identical edge sets.

**Foundation:** **Theorem:** If all edge weights are distinct, the MST is unique. Any two different MSTs `T₁`, `T₂` yield a contradiction by swapping edges — the lighter cross-edge always produces a cheaper spanning tree, disproving either `T₁` or `T₂` being minimum.  
**Strategy:** Uses `st.permutations(range(1, m+1))` to assign strictly distinct integer weights via Hypothesis — fully reproducible and shrinkable.

---

#### `test_mst_cut_and_cycle_duality` — *Invariant (Complete Characterization)*
> For every non-tree edge `e = (u, v)`, its weight must be ≥ the maximum weight of every MST edge on the path from `u` to `v` inside the MST.

**Foundation:** This is the **Cut-Cycle Duality** — the complete characterization theorem for MSTs (Tarjan, 1983):

```
e ∈ MST  ↔  e is the minimum weight edge crossing some cut    [Cut Property]
e ∉ MST  ↔  e is the maximum weight edge in some cycle        [Cycle Property]
```

The fundamental cycle of non-tree edge `e` is the unique cycle formed by adding `e` to the MST. If `w(e)` were less than any MST edge on that cycle, that MST edge should have been replaced by `e` — directly proving the MST is not minimum.

> This is the **most comprehensive single test** in the suite. A failure is direct proof that the MST returned is not actually minimum.

---

### 3 · Boundary Tests &nbsp;*(2 tests)*

---

#### `test_small_graph_edge_cases` — *Boundary Condition*
> Algorithms behave correctly on very small graphs (1–3 nodes).

**Foundation:** Off-by-one errors and missing base cases most often surface at boundary inputs. Tests `n=1` (isolated node — self-distance zero, MST with 0 edges) and `n=2, 3` (path graphs — shortest path length = `n−1`, MST with `n−1` edges, `nx.is_tree` holds).

---

#### `test_single_edge_weight_perturbation` — *Boundary + Sensitivity*
> Increasing the weight of one edge on the only path between two nodes must increase the shortest path length; the MST structure must remain unchanged.

**Foundation:** In a path graph, there is exactly one simple path between any two nodes — any weight increase on it must increase the total distance. The MST of a path graph is the graph itself, so structural changes are not possible without adding edges.

---

### 4 · Robustness & Bug Exploration Tests &nbsp;*(4 tests)*

---

#### `test_dijkstra_negative_weight_detection` — *Robustness*
> If Dijkstra returns a result on a graph containing a negative edge weight, it must match the result from Bellman-Ford.

**Foundation:** Dijkstra's greedy finalization assumption breaks with negative weights — a finalized node's distance may be later improved via a negative-weight edge. Bellman-Ford handles negative weights correctly (absent negative cycles). If Dijkstra silently returns an incorrect result without raising an error, it can corrupt real-world applications with no visible signal.  
**Strategy:** Normalizes all weights to 1, sets one edge to −1, skips if a negative cycle exists, then compares both algorithms. Accepts an exception from Dijkstra as valid behaviour; only asserts when it returns a value.

---

#### `test_mst_dense_graph_cut_property` — *Robustness*
> The Cut Property holds for every single-node cut in a complete (dense) graph.

**Foundation:** Complete graphs `Kₙ` maximize the number of edges and possible cuts — providing a maximum-stress test of the cut property. Tests every `n` single-node cuts and asserts that the unique minimum crossing edge is present in the MST.

---

#### `test_dijkstra_floating_point_consistency` — *Robustness*
> Shortest path results from Dijkstra and Bellman-Ford must agree within floating-point tolerance `1e-9` when edge weights are floats.

**Foundation:** IEEE 754 floating-point arithmetic is not exact. Different internal accumulation orders may introduce small rounding differences between algorithms. Both must remain numerically consistent within tolerance.  
**Strategy:** Assigns repeating float weights `[0.1, 0.2, …, 0.9]` cyclically to edges.

---

#### `test_multigraph_mst_properties` — *Robustness*
> The MST of a MultiGraph must satisfy all tree properties and correctly select the minimum-weight edge among parallel edges.

**Foundation:** In a MultiGraph, multiple edges may connect the same pair of nodes. MST algorithms must choose the minimum-weight parallel edge, not an arbitrary one. Verifies: exactly `n−1` edges, full connectivity, all selected edges have `weight = 1` (not the parallel `weight = 5` edges), and every MST edge exists in the original MultiGraph.

---

## ◈ Property Taxonomy

Each test is classified by the type of correctness guarantee it encodes:

| Type | Meaning |
|---|---|
| **Invariant** | A property that holds unconditionally for all valid inputs |
| **Postcondition** | A structural guarantee the output must satisfy |
| **Metamorphic** | A relation between outputs on two related inputs |
| **Boundary** | Correct behaviour at degenerate or minimal inputs |
| **Idempotence** | Repeated application produces the same result |
| **Robustness** | Correct or graceful behaviour under adversarial or unusual inputs |

---

## ◈ Key Design Decisions

**Custom Hypothesis Strategy**  
`connected_weighted_graphs()` uses only Hypothesis-controlled randomness (no `random` module). Failing examples are automatically **shrunk** to the smallest reproducible case, making debugging significantly faster.

**Deterministic Weight Generation**  
All edge weights are generated using deterministic patterns (modular arithmetic or fixed floating-point sets) instead of random sampling. This ensures reproducibility, better shrinking behaviour, and elimination of flaky test outcomes.

**Increased Coverage**  
Most tests use `@settings(max_examples=200)` — 4× the default — to explore a substantially larger input space and increase the probability of surfacing subtle edge cases. Robustness tests use up to 500 examples.

**MST Theoretical Trinity**  
`test_mst_cut_property`, `test_mst_cycle_property`, and `test_mst_cut_and_cycle_duality` together form a near-complete mathematical characterization of MSTs — necessary and sufficient conditions that describe minimum spanning trees. These properties are rooted in classical results (Tarjan, 1983), ensuring the test suite is grounded in formal graph theory.

**Theory-Grounded Properties**  
Tests are derived from classical results in graph theory, not ad-hoc checks:
- Dijkstra optimality and optimal substructure (Dijkstra, 1959)
- MST Cut and Cycle Properties (Tarjan, 1983, *Data Structures and Network Algorithms*)
- MST Uniqueness Theorem under distinct weights
- Triangle inequality as a metric axiom

**Structured Test Organization**  
Tests are organized into shortest path, MST, boundary, and robustness categories. This improves readability, maintainability, and clarity during evaluation.

**Test Independence**  
Each test receives a fresh graph instance from Hypothesis. There is no shared mutable state between tests, ensuring reliable and reproducible execution.

---

## ◈ Key Theoretical Insights

**The MST Theoretical Trinity**  
`test_mst_cut_property`, `test_mst_cycle_property`, and `test_mst_cut_and_cycle_duality` collectively constitute a **complete correctness argument** for MST algorithms. The Cut Property establishes which edges must be included; the Cycle Property establishes which edges must be excluded; the Cut-Cycle Duality verifies both conditions simultaneously for every edge in the graph. Together they are mathematically equivalent to a full proof of MST optimality (Tarjan, 1983).

**Optimal Substructure as a Foundational Property**  
`test_shortest_path_optimal_substructure` verifies *why* Dijkstra works — not merely that it produces correct outputs. It validates the dynamic programming principle at the algorithm's foundation, not just the final result.

**Metamorphic Testing as a Substitute for Oracles**  
Properties like edge addition, weight increase, weight scaling, and node relabeling are *metamorphic* — they define relationships between outputs on related inputs rather than checking absolute correctness. This is especially powerful for graph algorithms where independently computing the correct answer is as hard as running the algorithm itself.

**Distinct Weights as a Uniqueness Guarantee**  
When all weights are distinct, the MST is unique — Kruskal and Prim must return identical edge sets. Using `st.permutations()` provides the strongest possible cross-algorithm agreement test: two independent implementations must converge on every single edge.

**Bug Hunting as Empirical Robustness Evidence**    
Robustness tests target stress scenarios (negative weights, floating-point precision, dense graphs, multigraphs), each across **300–500 generated examples**.  
All tests passed — providing **strong empirical evidence** of NetworkX’s robustness under adversarial and edge-case conditions.


---

## ◈ Hypothesis Statistics

Full results — Python 3.13 · Hypothesis 6.151.9:

| Test | Category | Examples Run | Failures |
|---|---|:---:|:---:|
| `test_shortest_path_minimality` | Shortest Path | 200 | 0 |
| `test_shortest_path_symmetry` | Shortest Path | 200 | 0 |
| `test_shortest_path_edge_addition` | Shortest Path | 200 | 0 |
| `test_shortest_path_triangle_inequality` | Shortest Path | 200 | 0 |
| `test_shortest_path_self_distance` | Shortest Path | 200 | 0 |
| `test_shortest_path_validity` | Shortest Path | 200 | 0 |
| `test_shortest_path_monotonicity_under_weight_increase` | Shortest Path | 200 | 0 |
| `test_shortest_path_optimal_substructure` | Shortest Path | 200 | 0 |
| `test_dijkstra_varied_weights` | Shortest Path | 200 | 0 |
| `test_shortest_path_no_repeated_nodes` | Shortest Path | 200 | 0 |
| `test_shortest_path_length_consistency` | Shortest Path | 200 | 0 |
| `test_mst_edge_count` | MST | 200 | 0 |
| `test_mst_is_tree` | MST | 200 | 0 |
| `test_mst_spans_all_nodes` | MST | 200 | 0 |
| `test_mst_edge_removal_disconnects` | MST | 200 | 0 |
| `test_mst_idempotence` | MST | 200 | 0 |
| `test_mst_cut_property` | MST | 200 | 0 |
| `test_mst_on_disconnected_graph_returns_forest` | MST | 200 | 0 |
| `test_mst_subgraph_property` | MST | 200 | 0 |
| `test_mst_minimal_edges_property` | MST | 200 | 0 |
| `test_mst_invariant_under_relabeling` | MST | 200 | 0 |
| `test_mst_weight_scaling` | MST | 200 | 0 |
| `test_mst_total_weight_minimality` | MST | 200 | 0 |
| `test_mst_cycle_property` | MST | 200 | 0 |
| `test_mst_uniqueness_under_distinct_weights` | MST | 200 | 0 |
| `test_mst_cut_and_cycle_duality` | MST | 200 | 0 |
| `test_small_graph_edge_cases` | Boundary | 3 | 0 |
| `test_single_edge_weight_perturbation` | Boundary | 8 | 0 |
| `test_dijkstra_negative_weight_detection` | Robustness | 500 | 0 |
| `test_mst_dense_graph_cut_property` | Robustness | 7 | 0 |
| `test_dijkstra_floating_point_consistency` | Robustness | 500 | 0 |
| `test_multigraph_mst_properties` | Robustness | 18 | 0 |

> `test_small_graph_edge_cases` exhausts its full search space at 3 examples by design — path graphs of size 1, 2, and 3 are the only valid inputs for that boundary test.

> `test_single_edge_weight_perturbation` exhausts its search space at 8 examples — path graphs of size 3 to 10 are the only valid inputs.

> `test_mst_dense_graph_cut_property` exhausts its search space at 7 examples — complete graphs of size 4 to 10 are the only valid inputs.

> `test_multigraph_mst_properties` exhausts its search space at 18 examples — MultiGraphs of size 3 to 20 are the only valid inputs.

> `test_dijkstra_negative_weight_detection` and `test_dijkstra_floating_point_consistency` use the custom `connected_weighted_graphs()` strategy with varied topology and weights — Hypothesis explores 500 genuinely distinct examples without exhausting the search space.

**Total: ~6,236 automatically generated graph examples. 32 tests. 0 failures.**

---

## Limitations & Future Work

### Limitations
- **Scalability:** Some properties (e.g., enumeration of all simple paths) are computationally expensive and limit graph size  
- **Restricted domain:** Focus on non-negative and controlled weight distributions  
- **Library-level validation:** Tests validate NetworkX behavior, not internal implementations  
- **Non-exhaustive guarantees:** Property-based testing increases confidence but does not constitute a formal proof of correctness  

### Future Work
- **Formal verification:** Integrate property-based testing with formal methods (e.g., SMT solvers or theorem provers) to obtain stronger correctness guarantees
- **Adversarial input generation:** Develop strategies that actively construct worst-case graphs targeting algorithmic weaknesses
- **Extended graph models:** Incorporate directed graphs, weighted directed cycles, and flow-based algorithms (e.g., max-flow, min-cut)  
- **Probabilistic analysis:** Study statistical failure probabilities and confidence bounds for property-based testing at scale  
- **Distributed / large-scale testing:** Extend testing to very large graphs using parallel or distributed frameworks  
- **Cross-library validation:** Compare behavior across multiple graph libraries to detect inconsistencies in algorithm implementations

-----------

## ◈ Resources

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/) — Property-based testing library
- [NetworkX Documentation](https://networkx.org/documentation/stable/) — Graph algorithms library
- [pytest Documentation](https://docs.pytest.org/) — Test runner
- Tarjan, R. E. (1983). *Data Structures and Network Algorithms*. SIAM.
- Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik*, 1, 269–271.

---

<div align="center">

<br/>

*Made with rigour at the intersection of graph theory and software correctness.*

<br/>

**[IISc](https://iisc.ac.in/) · Data Structures and Graph Analytics**

</div>
