"""
Property-Based Testing for Graph Algorithms using NetworkX

Author: Sudipta Ghosh and Shambo Samanta
Course: Data Structures and Graph Analytics

Algorithms Tested:
1. Shortest Path (Dijkstra for weighted graphs, BFS for unweighted cases)
2. Minimum Spanning Tree (Kruskal / Prim)

Description:
    This project applies property-based testing using the Hypothesis library
    to verify fundamental mathematical properties and invariants of graph
    algorithms over a wide range of automatically generated inputs.

    Instead of relying on fixed, hand-crafted examples, each test encodes a
    general property that must hold for all valid graphs. Hypothesis then
    generates diverse graph instances — varying in size, topology, and edge
    weights — to systematically search for counterexamples.

    The focus is on validating correctness guarantees such as optimality,
    symmetry, cut and cycle properties, and robustness under edge cases
    and adversarial conditions.
"""

import networkx as nx
from hypothesis import given, strategies as st, settings

# ================================
# Custom Graph Strategy
# ================================

@st.composite
def connected_weighted_graphs(draw):
    """
    A custom Hypothesis strategy that generates connected weighted graphs
    with varied positive integer edge weights.

    More expressive than primitive strategies — enables Hypothesis to shrink
    entire graph structures rather than individual parameters.

    Generates:
        - n nodes (3 to 10)
        - Connected topology via path graph (deterministic, avoids random module)
        - Additional edges via Hypothesis to create varied graph structures
        - Positive integer weights (1 to 20) assigned via Hypothesis

    Design Guarantees:
        - Ensures connectivity by construction (satisfies algorithm preconditions)
        - Fully Hypothesis-controlled → reproducible, shrinkable failures
        - Additional edges introduce cycles and alternative paths for richer testing
    
    """
    n = draw(st.integers(min_value=3, max_value=10))

    # Use path_graph (deterministic) as base, then add extra edges via Hypothesis
    # to get varied topology without touching Python's random module
    G = nx.path_graph(n)

    # Optionally add extra edges using Hypothesis-controlled choices
    possible_edges = [
        (u, v) for u in range(n) for v in range(u + 2, n)
        if not G.has_edge(u, v)
    ]
    extra = draw(st.lists(
        st.sampled_from(possible_edges) if possible_edges else st.nothing(),
        max_size=min(len(possible_edges), n),
        unique=True,
    )) if possible_edges else []
    G.add_edges_from(extra)

    # Assign weights via Hypothesis (not random module)
    weights = draw(st.lists(
        st.integers(min_value=1, max_value=20),
        min_size=G.number_of_edges(),
        max_size=G.number_of_edges(),
    ))
    for (u, v), w in zip(G.edges(), weights):
        G[u][v]['weight'] = w
    return G

# ================================
# Shortest Path Properties
# ================================
@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_shortest_path_minimality(G):
    """
    Property (Invariant):
        The path returned by nx.shortest_path has the minimum total weight
        among all simple paths between the source and target.

    Mathematical Foundation:
        Dijkstra's algorithm is provably optimal: it always finds a path
        whose total weight is no greater than any other path in the graph
        with non-negative edge weights.This is the global optimality
        guarantee of shortest path algorithms.

    Test Strategy:
        Use the custom connected_weighted_graphs() strategy to generate graphs
        with varied weights (1–20), giving Hypothesis a large search space to
        explore 200 genuinely distinct examples. Select two fixed nodes (first
        and last in node list) for consistency, compute the weighted shortest path length, then
        enumerate ALL simple paths and verify none has lower total weight.

    Preconditions:
        Graph must be connected (guaranteed by strategy) and edge weights
        must be non-negative (all weights ≥ 1 here).

    Why This Matters:
        If this test fails, Dijkstra is returning a sub-optimal path —
        a direct violation of its optimality guarantee. Any application
        relying on shortest paths (e.g., routing, navigation, scheduling)
        would produce incorrect results.   
    """
    nodes = list(G.nodes())
    source, target = nodes[0], nodes[-1]

    shortest_len = nx.shortest_path_length(G, source, target, weight='weight')

    for path in nx.all_simple_paths(G, source, target):
        path_weight = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
        assert shortest_len <= path_weight, (
            f"Found a path of weight {path_weight} cheaper than reported "
            f"shortest path of weight {shortest_len}."
        )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_shortest_path_symmetry(G):
    """
    Property (Invariant):
        In an undirected graph, distance(u, v) == distance(v, u).

    Mathematical Foundation:
        Undirected edges have no orientation, so any path from u to v
        can be traversed in reverse to obtain a path of identical length
        from v to u. Therefore, the shortest-path distance defines a
        symmetric function.

    Test Strategy:
        Use the custom connected_weighted_graphs() strategy to generate connected graphs with varied weights (1–20). 
        Select two fixed nodes (first and last in node list) for consistency, compute shortest
        path length in both directions, and assert equality across 200 generated examples.

    Preconditions:
        Graph must be undirected and connected.

    Why This Matters:
        Asymmetry in an undirected distance function would indicate that the algorithm
        is incorrectly treating the graph as directed — a fundamental correctness error.
    """
    nodes = list(G.nodes())
    u, v = nodes[0], nodes[-1]

    d_uv = nx.shortest_path_length(G, u, v, weight='weight')
    d_vu = nx.shortest_path_length(G, v, u, weight='weight')

    assert d_uv == d_vu, (
        f"distance({u},{v}) = {d_uv} but distance({v},{u}) = {d_vu}. "
        "Symmetry violated in undirected graph."
    )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_shortest_path_edge_addition(G):
    """
    Property (Metamorphic):
        Adding a direct edge between two nodes cannot increase the shortest
        path distance between them.

    Mathematical Foundation:
        Adding an edge (u, v) with weight w introduces a new candidate path
        of length w between u and v. Since all existing paths remain valid,
        the shortest path distance can only stay the same or decrease — it
        can never increase.

    Test Strategy:
        Use the custom strategy for varied-weight graphs. Select two fixed
        nodes (first and last in the node list), compute the weighted shortest
        distance before adding a direct edge between them, then add an edge
        of weight 1 and recompute. Assert the new distance is at most the old across 200 generated examples.

    Preconditions:
        Graph must be connected and edge weights must be non-negative (guaranteed by the strategy).

    Why This Matters:
        If adding an edge increases the reported shortest distance, the algorithm
        is violating a fundamental monotonicity property — indicating
        incorrect path computation or failure to consider valid candidate paths.
    """
    nodes = list(G.nodes())
    u, v = nodes[0], nodes[-1]

    d_before = nx.shortest_path_length(G, u, v, weight='weight')
    G.add_edge(u, v, weight=1)
    d_after = nx.shortest_path_length(G, u, v, weight='weight')

    assert d_after <= d_before, (
        f"Distance increased from {d_before} to {d_after} after adding direct edge."
    )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_shortest_path_triangle_inequality(G):
    """
    Property (Invariant):
        For any three nodes u, v, w:  d(u, v) ≤ d(u, w) + d(w, v).

    Mathematical Foundation:
        This is the triangle inequality — a fundamental axiom of any metric
        space. Graph shortest-path distance is a metric, so it must satisfy
        this property. Intuitively, going through an intermediate node w can
        never be shorter than the direct shortest path.

    Test Strategy:
        Use the custom strategy for varied-weight graphs. Select three fixed
        nodes (first, second, and last in the node list) for consistency, compute
        weighted shortest path distances, and verify the triangle inequality
        holds across 200 generated examples.

    Preconditions:
        Graph must be connected and edge weights must be non-negative
        (guaranteed by the strategy). The graph contains at least 3 nodes.

    Why This Matters:
        Violation of the triangle inequality means the distance function is
        not a true metric — indicating fundamental inconsistency in how shortest paths are computed.
    """
    nodes = list(G.nodes())
    if len(nodes) < 3:
        return
    u, v, w = nodes[0], nodes[1], nodes[-1]

    d_uv = nx.shortest_path_length(G, u, v, weight='weight')
    d_uw = nx.shortest_path_length(G, u, w, weight='weight')
    d_wv = nx.shortest_path_length(G, w, v, weight='weight')

    assert d_uv <= d_uw + d_wv, (
        f"Triangle inequality violated: d({u},{v})={d_uv} > "
        f"d({u},{w})={d_uw} + d({w},{v})={d_wv}."
    )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_shortest_path_self_distance(G):
    """
    Property (Boundary Condition):
        The shortest path distance from any node to itself is zero.

    Mathematical Foundation:
        The trivial path from a node to itself uses zero edges and therefore
        has total weight 0. Since all edge weights are non-negative, no
        alternative path can yield a smaller value.

    Test Strategy:
        Use the custom strategy for varied-weight graphs. Select a fixed node
        (first in the node list) for determinism and verify that its weighted
        self-distance is exactly 0 across all generated examples.

    Preconditions:
        Edge weights must be non-negative (guaranteed by the strategy).

    Why This Matters:
        This is a fundamental base-case invariant of shortest-path algorithms.
        A non-zero self-distance indicates incorrect initialization or
        unnecessary edge traversal — a basic correctness failure.
    """
    node = list(G.nodes())[0]

    assert nx.shortest_path_length(G, node, node, weight='weight') == 0, (
        f"Self-distance of node {node} is not zero."
    )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_shortest_path_validity(G):
    """
    Property (Postcondition):
        Every consecutive pair of nodes in the returned shortest path must
        be connected by an actual edge in the graph.

    Mathematical Foundation:
        A path is defined as a sequence of nodes where each consecutive pair
        is adjacent (connected by an edge). If any consecutive pair
        is not an edge in the graph, the returned sequence is not a valid path,
        violating the definition itself.

    Test Strategy:
        Use the custom connected_weighted_graphs() strategy to generate graphs
        with varied weights. Select fixed nodes (first and last) for determinism,
        compute the shortest path, and verify that every step (u → v) corresponds
        to a real edge in G across all generated examples.

    Preconditions:
        Graph must be connected so a path always exists.

    Why This Matters:
        Returning a path with non-existent edges violates the graph abstraction
        and indicates a fundamental implementation error. Any downstream system
        relying on this path (e.g., routing or scheduling) would operate on
        invalid structure, leading to incorrect results.
    """
    nodes = list(G.nodes())
    source, target = nodes[0], nodes[-1]

    path = nx.shortest_path(G, source, target, weight='weight')

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        assert G.has_edge(u, v), (
            f"Path contains step ({u}→{v}) which is not an edge in the graph."
        )

@settings(max_examples=200)
@given(connected_weighted_graphs(), st.data())
def test_shortest_path_monotonicity_under_weight_increase(G, data):
    """
    Property (Metamorphic — Monotonicity):
        Increasing the weight of any edge can only increase or maintain
        the shortest path distance — it can never decrease it.

    Mathematical Foundation:
        Let d(u,v) be the shortest path distance with original weights.
        If we increase the weight of edge (a,b) by δ > 0, the new distance
        d'(u,v) ≥ d(u,v). This follows because:
        (1) If the shortest path does not use (a,b), d'(u,v) = d(u,v).
        (2) If the shortest path uses (a,b), its cost increases by δ.
            Any alternative path already existed and cost ≥ d(u,v) before
            the increase — so d'(u,v) ≥ d(u,v) in either case.

    Test Strategy:
        Use the custom strategy for a varied-weight graph. Record the
        original distance between first and last node. Use st.data() to
        draw a random edge and a positive increment δ (1–10) via Hypothesis
        — fully reproducible and shrinkable. Increase that edge's weight
        by δ and recompute. Assert the new distance is ≥ the original.

    Preconditions:
        Graph must be connected. Weight increment must be positive (δ ≥ 1).

    Why This Matters:
        If distance decreases after a weight increase, the algorithm is
        not correctly recomputing paths after graph modifications — a
        serious bug that would cause incorrect results in any dynamic
        shortest-path application.
    """
    nodes = list(G.nodes())
    source, target = nodes[0], nodes[-1]

    d_before = nx.shortest_path_length(G, source, target, weight='weight')

    # Draw a random edge and increment fully via Hypothesis — reproducible
    edge = data.draw(st.sampled_from(list(G.edges())))
    delta = data.draw(st.integers(min_value=1, max_value=10))

    u, v = edge
    G[u][v]['weight'] += delta

    d_after = nx.shortest_path_length(G, source, target, weight='weight')

    assert d_after >= d_before, (
        f"Monotonicity violated: distance decreased from {d_before} to "
        f"{d_after} after increasing edge ({u},{v}) weight by {delta}."
    )
        

@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_shortest_path_optimal_substructure(G):
    """
    Property (Invariant — Optimal Substructure):
        Every sub-path of a shortest path is itself a shortest path.

    Mathematical Foundation:
        This is the principle of optimal substructure, which is WHY Dijkstra's
        algorithm and dynamic programming work on shortest paths. Formally:
        if P = (v0, v1, ..., vk) is a shortest path from v0 to vk, then for
        any i < j, the sub-path P[i:j] = (vi, ..., vj) is a shortest path
        from vi to vj. Proof by contradiction: if a shorter path from vi to vj
        existed, we could substitute it into P to get a shorter path from
        v0 to vk — contradicting P being shortest.

    Test Strategy:
        Compute the shortest path P from source to target. For each intermediate
        node w in P, verify that the sub-path from source to w has the same
        length as the direct shortest path from source to w.

    Preconditions:
        Graph must be connected. Path must have at least 3 nodes (length ≥ 2)
        to have a meaningful intermediate node.

    Why This Matters:
        If this property fails, Dijkstra is not exploiting optimal substructure
        correctly — meaning its dynamic programming foundation is broken, and
        it cannot guarantee globally optimal paths.
    """
    nodes = list(G.nodes())
    source, target = nodes[0], nodes[-1]

    path = nx.shortest_path(G, source, target, weight='weight')

    if len(path) < 3:
        return  # Need at least one intermediate node to test substructure

    for i in range(1, len(path)):
        subpath = path[:i+1]

        # Compute weight of subpath (actual path taken)
        subpath_weight = sum(
            G[subpath[j]][subpath[j+1]]['weight']
            for j in range(len(subpath) - 1)
        )

        # Compute true shortest path weight independently
        shortest_weight = nx.shortest_path_length(
            G, source, subpath[-1], weight='weight'
        )

        assert subpath_weight == shortest_weight, (
            f"Optimal substructure violated: subpath weight {subpath_weight} "
            f"!= shortest weight {shortest_weight}"
        )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_dijkstra_varied_weights(G):
    """
    Property (Invariant):
        Dijkstra's algorithm returns the correct shortest path even with
        varied positive edge weights (not just unit weights).

    Mathematical Foundation:
        With varied weights, the shortest path by total weight may differ
        from the path with fewest hops. Dijkstra's algorithm must correctly
        minimize total edge weight, not hop count. This property verifies
        that the weighted shortest path length from u to v is at most the
        weight of any other path found via all_simple_paths.

    Test Strategy:
        Use the custom strategy to generate graphs with random positive
        weights (1–20). Compute the weighted shortest path length, then
        enumerate all simple paths and compute their total weights to verify
        none is cheaper.

    Preconditions:
        All edge weights must be positive (guaranteed by strategy: min=1).
        Graph must be connected.

    Why This Matters:
        Unit-weight tests only verify BFS correctness. This test exercises
        the priority-queue logic that makes Dijkstra handle varied weights —
        a much stronger correctness check.
    """
    nodes = list(G.nodes())
    source, target = nodes[0], nodes[-1]

    if source == target:
        return

    best = nx.shortest_path_length(G, source, target, weight='weight')

    for path in nx.all_simple_paths(G, source, target):
        path_weight = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
        assert best <= path_weight, (
            f"Dijkstra returned length {best} but a path with weight "
            f"{path_weight} exists — shortest path is not minimal."
        )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_shortest_path_no_repeated_nodes(G):
    """
    Property (Postcondition):
        The shortest path returned by Dijkstra must be a simple path —
        no node appears more than once.

    Mathematical Foundation:
        In a graph with non-negative edge weights, an optimal path can
        never contain a repeated node. If a path visited node v twice,
        it would contain a cycle v → ... → v. Removing that cycle gives
        a shorter or equal path to the same destination (since all weights
        ≥ 1, the cycle adds strictly positive weight). Therefore the
        optimal path is always simple.

    Test Strategy:
        Use the custom strategy to generate varied-weight graphs. Compute
        the weighted shortest path between the first and last node, then
        check that the list of nodes has no duplicates by comparing
        len(path) with len(set(path)).

    Preconditions:
        Graph must be connected so a path always exists.
        Edge weights must be non-negative (guaranteed by strategy: min=1).

    Why This Matters:
        A repeated node in the returned path means Dijkstra traversed a
        cycle — adding unnecessary positive weight. This would indicate
        the algorithm is not correctly tracking visited nodes, causing
        it to loop and return a provably suboptimal result.
    """
    nodes = list(G.nodes())
    source, target = nodes[0], nodes[-1]

    path = nx.shortest_path(G, source, target, weight='weight')

    assert len(path) == len(set(path)), (
        f"Shortest path contains repeated nodes: {path}. "
        f"Repeated: {[n for n in path if path.count(n) > 1]}"
    )

    
@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_shortest_path_length_consistency(G):
    """
    Property (Postcondition — Consistency):
        The value returned by nx.shortest_path_length must equal the sum
        of edge weights along the path returned by nx.shortest_path.

    Mathematical Foundation:
        nx.shortest_path and nx.shortest_path_length are two separate
        NetworkX functions — one returns the path (list of nodes), the
        other returns the distance (total weight). They must be consistent:
        manually summing the weights of edges along the returned path must
        give exactly the same number as shortest_path_length. Any discrepancy
        means the two functions are computing different things internally,
        which would silently corrupt any application that uses both.

    Test Strategy:
        Use the custom strategy for varied-weight graphs. Compute both the
        path and the length between the first and last node. Manually sum
        edge weights along the path and assert equality with reported length.

    Preconditions:
        Graph must be connected. Edge weights must be non-negative
        (guaranteed by strategy: min=1).

    Why This Matters:
        If this test fails, shortest_path and shortest_path_length are
        internally inconsistent — one of them is computing a different
        quantity. Any code that uses the path for routing and the length
        for cost estimation would silently produce wrong answers.
    """
    nodes = list(G.nodes())
    source, target = nodes[0], nodes[-1]

    reported_length = nx.shortest_path_length(G, source, target, weight='weight')
    path = nx.shortest_path(G, source, target, weight='weight')

    actual_length = sum(
        G[path[i]][path[i + 1]]['weight']
        for i in range(len(path) - 1)
    )

    assert reported_length == actual_length, (
        f"Inconsistency: shortest_path_length reports {reported_length} "
        f"but sum of edge weights along shortest_path is {actual_length}. "
        f"Path: {path}"
    )


# ================================
# Minimum Spanning Tree Properties
# ================================

@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_edge_count(G):
    """
    Property (Invariant):
        A spanning tree of a connected graph with n nodes has exactly n-1 edges.

    Mathematical Foundation:
        Any tree on n vertices has exactly n-1 edges. This is provable by
        induction: a single node has 0 edges; each additional node added to
        a tree requires exactly 1 new edge to connect it. Fewer edges would
        leave some node disconnected; more edges would create a cycle.
        Conversely, any connected graph with n−1 edges is a tree.

    Test Strategy:
        Use the custom strategy to generate varied-weight connected graphs.
        Compute the MST and verify it has exactly n-1 edges across 200
        distinct graph structures.

    Preconditions:
        The input graph must be connected so that a spanning tree exists.

    Why This Matters:
        If the MST has fewer than n-1 edges, it does not span all nodes.
        If it has more, it contains a cycle and violates the definition of a tree.      
    """
    n = G.number_of_nodes()
    T = nx.minimum_spanning_tree(G)

    assert T.number_of_nodes() == n  # ensures spanning
    assert T.number_of_edges() == n - 1, (
        f"MST has {T.number_of_edges()} edges, expected {n - 1}."
    )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_is_tree(G):
    """
    Property (Invariant):
        The result of nx.minimum_spanning_tree must be acyclic and connected,
        i.e., a valid tree.

    Mathematical Foundation:
        A graph is a tree if and only if it is both connected and acyclic.
        A spanning tree is therefore a subgraph that includes all vertices,
        is connected, and contains no cycles. NetworkX's nx.is_tree checks both conditions simultaneously.

    Test Strategy:
        Use the custom strategy for 200 varied-weight graphs. Compute the MST
        and verify structural correctness using nx.is_tree. This test focuses
        on structural validity (connectivity + acyclicity), independent of edge count.

    Preconditions:
        Input graph must be connected.

    Why This Matters:
        If nx.is_tree returns False, the algorithm has produced a structure
        that violates the definition of a tree — either disconnected or cyclic —
        indicating a fundamental correctness failure.
    """
    T = nx.minimum_spanning_tree(G)

    assert nx.is_tree(T), (
        "MST result is not a valid tree (either contains a cycle or is disconnected)."
    )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_spans_all_nodes(G):
    """
    Property (Postcondition):
        The MST must contain every node present in the original graph.

    Mathematical Foundation:
        The word 'spanning' in 'spanning tree' means the tree covers all
        vertices of the original graph. Therefore, the node set of the MST
        must be identical to the node set of the original graph.

    Test Strategy:
        Use the custom strategy for 200 varied-weight graphs. Compute the MST
        and assert exact equality between the node sets of the MST and the
        original graph.

    Preconditions:
        Input graph must be connected.

    Why This Matters:
        If this test fails, the MST has dropped a vertex — it is not spanning,
        violating the definition of a spanning tree and corrupting any
        downstream computation relying on full vertex coverage.
    """
    T = nx.minimum_spanning_tree(G)

    assert set(T.nodes()) == set(G.nodes()), (
        f"MST is missing nodes: {set(G.nodes()) - set(T.nodes())}"
    )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_edge_removal_disconnects(G):
    """
    Property (Invariant):
        Removing any single edge from the MST must disconnect it.

    Mathematical Foundation:
        A tree is minimally connected: it has exactly enough edges to keep
        all vertices connected. Every edge in a tree is a bridge (cut-edge) — 
        removing it splits the tree into exactly two components. TThis follows
        from the fact that a tree has n−1 edges and contains no cycles.

    Test Strategy:
        Use the custom strategy for 200 varied-weight graphs. Compute the MST,
        remove a fixed edge (first in the edge list) for determinism, and assert
        that the resulting graph is disconnected.

    Preconditions:
        Graph must have at least 2 nodes (guaranteed by the strategy, n ≥ 3).

    Why This Matters:
        If the graph remains connected after removing an MST edge, the structure
        is not minimally connected — implying the presence of a cycle and
        violating the definition of a tree.
    """
    T = nx.minimum_spanning_tree(G)

    edge = list(T.edges())[0]
    T.remove_edge(*edge)

    assert not nx.is_connected(T), (
        f"Removing edge {edge} did not disconnect the MST — "
        "MST must contain a cycle (not a valid tree)."
    )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_idempotence(G):
    """
    Property (Idempotence):
        Applying the MST algorithm to an MST yields the same tree.

    Mathematical Foundation:
        An MST T of a graph G is itself a tree. An MST T of a graph G is itself a tree.
        A tree has exactly one spanning tree — itself — since it is already connected and acyclic.
        Therefore, applying the MST algorithm to T must return T unchanged, independent of edge weights.

    Test Strategy:
        Use the custom strategy for 200 varied-weight graphs. Compute
        T1 = MST(G), then T2 = MST(T1), and assert that their edge sets
        are identical (up to unordered edge representation).
        
    Preconditions:
        Input graph must be connected.

    Why This Matters:
        If MST(MST(G)) ≠ MST(G), the algorithm is not stable under repeated
        application — indicating a violation of fundamental tree properties.
    """
    T1 = nx.minimum_spanning_tree(G)
    T2 = nx.minimum_spanning_tree(T1)
    
    edges_T1 = set(map(frozenset, T1.edges()))
    edges_T2 = set(map(frozenset, T2.edges()))
    
    assert edges_T1 == edges_T2, (
        "MST is not idempotent: MST(MST(G)) ≠ MST(G)."
    )

@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_cut_property(G):
    """
    Property (Invariant — Cut Property):
        For any cut of the graph, the minimum weight edge crossing the cut
        must belong to the MST (assuming unique edge weights).

    Mathematical Foundation:
        The Cut Property is the theoretical foundation of both Prim's and
        Kruskal's algorithms. Formally: given any partition of vertices into
        two non-empty sets S and V\\S, the minimum weight edge with one
        endpoint in S and the other in V\\S must be in every MST.
        Proof: suppose edge e = (u,v) is the minimum cut edge but not in MST T.
        Adding e to T creates a cycle. That cycle must cross the cut at least
        twice, so another cut edge e' is in T. Since e is the minimum cut edge,
        w(e) ≤ w(e'). Swapping e' for e gives a spanning tree of equal or
        lesser weight — contradicting T being the unique MST if weights differ.

    Test Strategy:
        Use the custom strategy (varied weights) to generate graphs. Take the
        first node as the cut set S = {nodes[0]}, and V\\S = all other nodes.
        Find the minimum weight edge crossing this cut and assert it is in the MST.

    Preconditions:
        Graph must be connected. Works best with unique edge weights (varied
        weights from strategy reduce ties). For graphs with many weight ties,
        the property holds for at least one MST but may not hold for all.

    Why This Matters:
        This is arguably the deepest property in this test suite — it validates
        the core theoretical guarantee that makes MST algorithms correct. A
        failure here would mean the algorithm is not implementing the greedy
        criterion properly.
    """
    nodes = list(G.nodes())
    if len(nodes) < 2:
        return

    T = nx.minimum_spanning_tree(G)

    # Cut: S = {nodes[0]}, complement = all other nodes
    S = {nodes[0]}

    # Find all edges crossing the cut and pick the minimum weight one
    cut_edges = [
        (u, v, G[u][v]['weight'])
        for u, v in G.edges()
        if (u in S) != (v in S)
    ]

    if not cut_edges:
        return

    min_weight = min(w for _, _, w in cut_edges)
    min_cut_edges = [(u, v) for u, v, w in cut_edges if w == min_weight]

    # At least one minimum cut edge must be in the MST
    assert any(T.has_edge(u, v) or T.has_edge(v, u) for u, v in min_cut_edges), (
        f"Cut property violated: no minimum-weight cut edge {min_cut_edges} "
        f"(weight={min_weight}) is in the MST."
    )   

@settings(max_examples=200)
@given(connected_weighted_graphs(), connected_weighted_graphs())
def test_mst_on_disconnected_graph_returns_forest(G1, G2):
    """
    Property (Boundary Condition):
        Applying nx.minimum_spanning_tree to a disconnected graph returns a
        spanning forest — one tree per connected component.

    Mathematical Foundation:
        When a graph is disconnected, no single spanning tree can connect all
        vertices (by definition, spanning trees require connectivity). Instead,
        the algorithm produces a spanning forest: a set of trees, one for each
        connected component. If component i has k_i nodes, its spanning tree
        has k_i - 1 edges. The total edges in the forest = sum(k_i - 1) =
        n - (number of components).

    Test Strategy:
        Use two independent connected_weighted_graphs() draws to create two
        separate components with varied topologies and weights. Relabel G2 to
        avoid node ID collisions, compose into a disconnected graph, and verify:
        (1) total edges = (n1 - 1) + (n2 - 1)
        (2) the forest has exactly 2 connected components.

    Preconditions:
        The two sub-graphs must be non-empty and not connected to each other.

    Why This Matters:
        Many MST implementations assume connected input. Testing on disconnected
        graphs reveals whether the algorithm gracefully handles the forest case
        or incorrectly assumes a single spanning tree always exists.
    """
    n1 = G1.number_of_nodes()
    n2 = G2.number_of_nodes()

    # Relabel G2 nodes to avoid overlap with G1
    offset = max(G1.nodes()) + 100
    mapping = {node: node + offset for node in G2.nodes()}
    G2 = nx.relabel_nodes(G2, mapping)

    G = nx.compose(G1, G2)  # disjoint union — no edges between components

    F = nx.minimum_spanning_tree(G)

    expected_edges = (n1 - 1) + (n2 - 1)
    assert F.number_of_edges() == expected_edges, (
        f"Spanning forest should have {expected_edges} edges, got {F.number_of_edges()}."
    )

    components = list(nx.connected_components(F))
    assert len(components) == 2, (
        f"Spanning forest should have 2 components, got {len(components)}."
    )

@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_subgraph_property(G):
    """
    Property (Postcondition):
        Every edge in the MST must be an edge in the original graph.

    Mathematical Foundation:
        A spanning tree is by definition a subgraph of the original graph.
        It cannot introduce new edges that were not in G — it can only
        select a subset of G's edges.

    Test Strategy:
        Use the custom strategy for 200 varied-weight graphs. Iterate over
        all MST edges and assert each exists in G.

    Preconditions:
        Input graph must be connected.

    Why This Matters:
        If the MST contains an edge not in G, the algorithm has fabricated
        a connection — a critical bug invalidating any result depending on
        actual graph structure.
    """
    T = nx.minimum_spanning_tree(G)

    for u, v in T.edges():
        assert G.has_edge(u, v), (
            f"MST contains edge ({u}, {v}) which does not exist in original graph."
        )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_minimal_edges_property(G):
    """
    Property (Invariant):
        Adding any non-tree edge from the original graph to the MST creates a cycle.

    Mathematical Foundation:
        A spanning tree has n-1 edges. Adding any additional edge between two
        vertices already connected by the tree creates a cycle (the new edge
        plus the unique path between its endpoints in the tree). This is the
        cycle property of trees.

    Test Strategy:
        Use the custom strategy for 200 varied-weight graphs. Find an edge in G
        not in the MST, add it to a copy of the MST, and verify the result is
        no longer a valid tree.

    Preconditions:
        The graph must have at least one edge not in the MST (typical for
        random graphs which have more edges than n-1).

    Why This Matters:
        If adding a non-tree edge does NOT create a cycle, the MST is missing
        an edge it should have — meaning it does not span all vertices.
    """
    T = nx.minimum_spanning_tree(G)

    for u, v in G.edges():
        if not T.has_edge(u, v):
            T_copy = T.copy()
            T_copy.add_edge(u, v)
            assert not nx.is_tree(T_copy), (
                f"Adding non-tree edge ({u},{v}) to MST did not create a cycle."
            )
            break


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_invariant_under_relabeling(G):
    """
    Property (Metamorphic):
        Relabeling nodes does not change the number of MST edges or total weight.

    Mathematical Foundation:
        Graph algorithms operate on structure (topology and weights), not on
        the names of nodes. Relabeling is an isomorphism — it produces a
        structurally identical graph. The MST must have the same number of
        edges and the same total weight, since the optimal spanning structure
        is determined entirely by edge weights and connectivity.

    Test Strategy:
        Use the custom strategy for 200 varied-weight graphs. Compute MST of G,
        relabel all nodes by adding 100, compute MST of relabeled graph, and
        compare edge counts and total weights.

    Preconditions:
        Input graph must be connected.

    Why This Matters:
        If the MST changes under relabeling, the algorithm is incorrectly
        using node identities to make structural decisions — a subtle but
        serious implementation flaw.
    """
    mapping = {i: i + 100 for i in G.nodes()}
    G2 = nx.relabel_nodes(G, mapping)

    T1 = nx.minimum_spanning_tree(G)
    T2 = nx.minimum_spanning_tree(G2)

    assert len(T1.edges()) == len(T2.edges()), (
        "MST edge count changed under node relabeling."
    )

    w1 = sum(d.get('weight', 1) for _, _, d in T1.edges(data=True))
    w2 = sum(d.get('weight', 1) for _, _, d in T2.edges(data=True))
    assert w1 == w2, (
        f"MST total weight changed under relabeling: {w1} vs {w2}."
    )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_weight_scaling(G):
    """
    Property (Metamorphic):
        Multiplying all edge weights by a positive constant does not change
        the set of edges selected for the MST.

    Mathematical Foundation:
        Kruskal's and Prim's algorithms select edges based on their relative
        ordering by weight. Scaling all weights by a constant factor k > 0
        preserves the total order of edge weights (w_i < w_j iff k*w_i < k*w_j).
        Therefore, the same edges are selected in the same order, producing an
        identical MST.

    Test Strategy:
        Use the custom strategy for 200 varied-weight graphs. Compute T1 = MST(G),
        then multiply all weights by 5 and compute T2 = MST(G). Assert identical
        edge sets.

    Preconditions:
        All edge weights must be positive (guaranteed by strategy: min=1).

    Why This Matters:
        If the MST changes after uniform weight scaling, the algorithm uses
        absolute weight values rather than relative ordering — indicating it is
        not correctly implementing the greedy selection criterion.
    """
    G2 = G.copy()
    T1 = nx.minimum_spanning_tree(G2)

    for u, v in G2.edges():
        G2[u][v]['weight'] *= 5

    T2 = nx.minimum_spanning_tree(G2)

    assert set(T1.edges()) == set(T2.edges()), (
        "MST edge set changed after uniform weight scaling."
    )

@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_total_weight_minimality(G):
    """
    Property (Invariant — Global Optimality):
        The total weight of the MST must be less than or equal to the
        total weight of every other spanning tree of the graph.

    Mathematical Foundation:
        This is the direct definition of a minimum spanning tree —
        it is the spanning tree with the lowest possible total edge weight.
        All other spanning trees must have weight ≥ MST weight.
        This test verifies global optimality by exhaustive comparison:
        enumerate every spanning tree of G and assert none is cheaper.

        A spanning tree of G is any connected acyclic subgraph that includes
        all vertices. NetworkX's nx.SpanningTreeIterator enumerates all of
        them in order of increasing weight.

    Test Strategy:
        Use the custom strategy for small varied-weight graphs (≤ 7 nodes
        to keep enumeration tractable). Compute the MST weight, then use
        nx.SpanningTreeIterator to enumerate ALL spanning trees and verify
        none has a lower total weight than the MST.

    Preconditions:
        Graph must be connected. Kept small (n ≤ 7) because the number of
        spanning trees grows exponentially — Cayley's formula gives n^(n-2)
        for complete graphs, so n=7 gives at most 7^5 = 16,807 trees.

    Why This Matters:
        This is the most direct possible correctness check — it literally
        verifies the definition of "minimum" by comparing against every
        alternative. All other MST tests verify structural properties
        (tree shape, edge count, cut/cycle conditions). This test directly
        verifies the weight optimality guarantee.
    """
    # Keep small for tractability — limit to graphs with ≤ 7 nodes
    if G.number_of_nodes() > 7:
        return

    T = nx.minimum_spanning_tree(G)
    mst_weight = sum(d['weight'] for _, _, d in T.edges(data=True))

    for spanning_tree in nx.SpanningTreeIterator(G):
        tree_weight = sum(d['weight'] for _, _, d in spanning_tree.edges(data=True))
        assert mst_weight <= tree_weight, (
            f"MST weight {mst_weight} is greater than another spanning tree "
            f"with weight {tree_weight} — MST is not globally minimum."
        )

@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_cycle_property(G):
    """
    Property (Invariant — Cycle Property):
        For any cycle in the graph, the maximum weight edge in that cycle
        must NOT be in the MST (when all edge weights are distinct).

    Mathematical Foundation:
        The Cycle Property is the exact dual of the Cut Property, and
        together they completely characterize minimum spanning trees:

            Cut Property:   min weight cut edge  → MUST be in MST
            Cycle Property: max weight cycle edge → MUST NOT be in MST

        Proof by contradiction: suppose the maximum weight edge e = (u,v)
        in some cycle C IS in the MST T. Removing e splits T into two
        components. Since C is a cycle, there must be another path in C
        from u to v not using e. That path contains at least one edge e'
        crossing the same cut, and since e is the MAX weight edge in C,
        w(e') ≤ w(e). Replacing e with e' gives a spanning tree of equal
        or lesser weight — contradicting e being in the unique MST when
        all weights are distinct.

    Test Strategy:
        Use the custom strategy to generate varied-weight graphs. For each
        cycle found via nx.cycle_basis (which returns a set of fundamental
        cycles), find the maximum weight edge in that cycle and verify it
        is NOT in the MST. Only run this check when all edge weights in
        the cycle are distinct (to avoid tie-breaking ambiguity).

    Preconditions:
        Graph must be connected and have at least one cycle (i.e., more
        edges than n-1). Cycle Property applies cleanly only when the
        maximum weight edge in the cycle is unique (no ties).

    Why This Matters:
        Together with the Cut Property (already tested), the Cycle Property
        forms the complete mathematical characterization of MSTs. A violation
        means the algorithm kept a provably sub-optimal edge — the greedy
        exclusion criterion at the heart of Kruskal's algorithm is broken.
    """
    T = nx.minimum_spanning_tree(G)

    # nx.cycle_basis returns a minimal set of cycles that span all cycles
    cycles = nx.cycle_basis(G)

    if not cycles:
        return  # graph is already a tree, no cycles to check

    for cycle_nodes in cycles:
        # Reconstruct the cycle edges from the node sequence
        cycle_edges = []
        for i in range(len(cycle_nodes)):
            u = cycle_nodes[i]
            v = cycle_nodes[(i + 1) % len(cycle_nodes)]
            if G.has_edge(u, v):
                cycle_edges.append((u, v, G[u][v]['weight']))

        if len(cycle_edges) < 2:
            continue

        max_weight = max(w for _, _, w in cycle_edges)
        max_edges = [(u, v) for u, v, w in cycle_edges if w == max_weight]

        # Only assert when the maximum is unique (no tie-breaking ambiguity)
        if len(max_edges) == 1:
            u, v = max_edges[0]
            assert not (T.has_edge(u, v) or T.has_edge(v, u)), (
                f"Cycle property violated: maximum weight edge ({u},{v}) "
                f"with weight={max_weight} is in the MST but should not be."
            )

@settings(max_examples=200)
@given(connected_weighted_graphs(), st.data())
def test_mst_uniqueness_under_distinct_weights(G, data):
    """
    Property (Invariant — MST Uniqueness):
        When all edge weights in a graph are distinct, the MST is unique —
        Kruskal's algorithm and Prim's algorithm must return identical edge sets.

    Mathematical Foundation:
        Theorem: If all edge weights are distinct, the MST is unique.
        Proof sketch: Suppose two different MSTs T1 and T2 exist. Let e be
        the minimum weight edge in T1 that is not in T2. Adding e to T2
        creates a cycle. That cycle must contain an edge e' not in T1
        (otherwise T1 would have a cycle). Since e is chosen as the minimum
        weight edge in T1 \\ T2, and e' is in T2 \\ T1, we must have
        w(e) < w(e') (by distinctness). Replacing e' with e in T2 gives a
        spanning tree of strictly lesser weight — contradicting T2 being
        an MST. Therefore T1 = T2.

        This means with distinct weights, ANY correct MST algorithm must
        return the same edge set, regardless of implementation details
        like tie-breaking or traversal order.

    Test Strategy:
        Use the custom strategy to generate graphs. Draw a random permutation
        of 1..m (where m = number of edges) via st.permutations() to assign
        strictly unique weights — fully controlled by Hypothesis so failing
        examples can be reliably shrunk and replayed. Compute MST using both
        Kruskal ('kruskal') and Prim ('prim') and assert identical edge sets.

    Preconditions:
        All edge weights must be strictly distinct (enforced by permutation).
        Graph must be connected.

    Why This Matters:
        If Kruskal and Prim return different edge sets under distinct weights,
        at least one implementation is wrong — both should converge to the
        same unique MST. This is the strongest possible correctness check:
        two independent algorithms must agree on every single edge.
    """
    edges = list(G.edges())
    m = len(edges)

    # Draw a permutation via Hypothesis — fully reproducible, shrinkable
    unique_weights = data.draw(st.permutations(range(1, m + 1)))

    for (u, v), w in zip(edges, unique_weights):
        G[u][v]['weight'] = w

    T_kruskal = nx.minimum_spanning_tree(G, algorithm='kruskal')
    T_prim    = nx.minimum_spanning_tree(G, algorithm='prim')

    edges_kruskal = set(tuple(sorted(e)) for e in T_kruskal.edges())
    edges_prim    = set(tuple(sorted(e)) for e in T_prim.edges())

    assert edges_kruskal == edges_prim, (
        f"MST uniqueness violated under distinct weights:\n"
        f"  Kruskal edges: {edges_kruskal}\n"
        f"  Prim edges:    {edges_prim}\n"
        f"  Both algorithms should return the same unique MST."
    )


@settings(max_examples=200)
@given(connected_weighted_graphs())
def test_mst_cut_and_cycle_duality(G):
    """
    Property (Invariant — Cut-Cycle Duality):
        For every edge e in the MST, e is the minimum weight edge crossing
        some cut (Cut Property). For every edge e NOT in the MST, e is the
        maximum weight edge in some cycle (Cycle Property). Together these
        two conditions are necessary AND sufficient to characterize the MST.

    Mathematical Foundation:
        This test unifies the Cut Property and Cycle Property into a single
        duality check — the complete characterization theorem for MSTs:

            e ∈ MST  ↔  e is min weight on some cut
            e ∉ MST  ↔  e is max weight on some cycle

        The "fundamental cycle" of a non-tree edge e = (u,v) is the unique
        cycle formed by adding e to the MST (the cycle consists of e plus
        the unique path from u to v in the MST). By the Cycle Property,
        e must be the maximum weight edge in this fundamental cycle —
        otherwise the MST could be improved.

    Test Strategy:
        For each non-tree edge e = (u,v) with weight w_e:
        1. Find the unique path from u to v in the MST (the fundamental cycle path)
        2. Find the maximum weight edge on that path
        3. Assert w_e ≥ max path weight (e must be at least as heavy as
           every MST edge on the path, otherwise e should have replaced it)

        When weights are unique, w_e > max path weight strictly.
        With possible ties, w_e ≥ max path weight is the correct form.

    Preconditions:
        Graph must be connected and have at least one non-tree edge
        (i.e., more edges than n-1). Edge weights from the custom strategy
        (1–20) may have ties, so we use ≥ instead of >.

    Why This Matters:
        This is the most comprehensive single test in the suite. It directly
        verifies the optimality condition that makes the MST minimal: every
        excluded edge is heavier than every edge it could replace. A failure
        means a non-tree edge is lighter than an MST edge it could swap with
        — proving the MST is not actually minimum.
    """
    T = nx.minimum_spanning_tree(G)

    for u, v in G.edges():
        if T.has_edge(u, v) or T.has_edge(v, u):
            continue  # skip tree edges, only check non-tree edges

        w_e = G[u][v]['weight']

        # Find the unique path from u to v in the MST
        try:
            path = nx.shortest_path(T, u, v)
        except nx.NetworkXNoPath:
            continue

        # Find max weight edge along the MST path (the fundamental cycle)
        max_path_weight = max(
            T[path[i]][path[i + 1]]['weight']
            for i in range(len(path) - 1)
        )

        assert w_e >= max_path_weight, (
            f"Cut-Cycle duality violated: non-tree edge ({u},{v}) has weight "
            f"{w_e} which is LESS than max MST path weight {max_path_weight}. "
            f"This edge should have replaced the heavier MST edge — "
            f"the MST is not actually minimum."
        )


# ================================
# Boundary / Stress Tests
# ================================

@given(st.integers(min_value=1, max_value=3))
def test_small_graph_edge_cases(n):
    """
    Property (Boundary Condition):
        Algorithms behave correctly on very small graphs (1–3 nodes).

    Mathematical Foundation:
        Edge cases (n=1: isolated node, n=2: single edge) are where
        off-by-one errors and incorrect base cases most often appear.
        A path graph P_n is connected for n ≥ 2 and trivially a single
        node for n = 1.

    Test Strategy:
        Generate path graphs of size 1–3 and verify both structural
        properties and algorithm correctness, including shortest path
        lengths and MST properties.

    Preconditions:
        None — this test is designed to work even for degenerate inputs.

    Why This Matters:
        Algorithms that work correctly on large graphs often fail silently
        on boundary inputs. Testing small graphs catches missing base cases
        and incorrect handling of trivial inputs.
    """
    G = nx.path_graph(n)

    if n == 1:
        assert G.number_of_nodes() == 1

        # Shortest path: trivial
        assert nx.shortest_path_length(G, 0, 0) == 0

        # MST: no edges
        T = nx.minimum_spanning_tree(G)
        assert T.number_of_edges() == 0

    else:
        assert nx.is_connected(G)

        # Shortest path from first to last node
        assert nx.shortest_path_length(G, 0, n - 1) == n - 1

        # MST properties
        T = nx.minimum_spanning_tree(G)
        assert T.number_of_edges() == n - 1
        assert nx.is_tree(T)


@settings(max_examples=200)
@given(st.integers(min_value=3, max_value=10))
def test_single_edge_weight_perturbation(n):
    """
    Property (Boundary + Sensitivity Test):
        Small local changes in edge weights should produce predictable
        and consistent changes in shortest paths and MST.

    Mathematical Foundation:
        In a path graph, there is exactly one simple path between any
        two nodes. Therefore, increasing the weight of any edge on
        that path must increase the total shortest path length.

        Similarly, for a tree (like a path graph), the MST is the graph
        itself. Changing weights should not change its structure.

    Test Strategy:
        1. Generate a path graph (unique paths)
        2. Assign unit weights
        3. Increase weight of one edge
        4. Verify:
            - shortest path increases correctly
            - MST structure remains unchanged

    Why This Matters:
        Ensures algorithms respond correctly to small perturbations
        and do not exhibit unstable or inconsistent behavior.
    """
    G = nx.path_graph(n)

    # Assign unit weights
    for u, v in G.edges():
        G[u][v]['weight'] = 1

    source, target = 0, n - 1

    # Original shortest path
    original_dist = nx.shortest_path_length(G, source, target, weight='weight')

    # Pick one edge and increase weight
    edge = list(G.edges())[n // 2]
    G[edge[0]][edge[1]]['weight'] = 5

    new_dist = nx.shortest_path_length(G, source, target, weight='weight')

    # Shortest path must increase
    assert new_dist > original_dist, (
        "Shortest path did not increase after increasing edge weight."
    )

    # MST should still be the same structure (tree)
    T = nx.minimum_spanning_tree(G)
    assert nx.is_tree(T)
    assert T.number_of_edges() == n - 1


# ================================
# Robustness & Bug Exploration Tests
# We systematically attempted to identify potential issues in NetworkX by testing:
# 1. Negative weights — comparing Dijkstra vs Bellman-Ford for consistency
# 2. Dense/complete graphs — stress testing algorithm behavior under high connectivity
# 3. Floating-point precision — checking for rounding error effects
# 4. MultiGraph parallel edges — verifying correct edge selection in presence of duplicates
# 
# All tests passed consistently across hundreds of generated examples.
# No discrepancies or failures were observed, indicating that NetworkX
# handles these edge cases robustly under the tested conditions
# ================================

@settings(max_examples=500)
@given(connected_weighted_graphs())
def test_dijkstra_negative_weight_detection(G):
    """
    Property (Robustness — Negative Weights):
        Dijkstra’s algorithm is not guaranteed to produce correct results
        in the presence of negative edge weights. If it returns a result,
        it must match the result from Bellman-Ford.

    Mathematical Foundation:
        Dijkstra’s algorithm relies on a greedy assumption that once a node’s
        shortest distance is finalized, it cannot be improved. This assumption
        fails when negative edge weights are present. In contrast, Bellman-Ford
        correctly computes shortest paths even with negative weights (as long
        as no negative cycle exists).

    Assumptions:
        - Graph is connected
        - At least one edge has a negative weight
        - No negative cycle is introduced (otherwise shortest path is undefined)

    Test Strategy:
        Assign uniform positive weights, then introduce a single negative edge.
        Run Dijkstra’s algorithm:
            - If it raises an exception → acceptable behavior
            - If it returns a result → compare with Bellman-Ford (ground truth)

    Why This Matters:
        If Dijkstra silently returns an incorrect result without raising an
        error, it can lead to undetected failures in real-world applications
        relying on shortest path computations.
    """

    # Step 1: Normalize all weights to positive
    for u, v in G.edges():
        G[u][v]['weight'] = 1

    # Step 2: Introduce a single negative edge
    u0, v0 = list(G.edges())[0]
    G[u0][v0]['weight'] = -1

    nodes = list(G.nodes())
    source, target = nodes[0], nodes[-1]

    # Optional safety: skip if negative cycle exists
    if nx.negative_edge_cycle(G, weight='weight'):
        return

    # Step 3: Run Dijkstra
    try:
        d_dijkstra = nx.shortest_path_length(G, source, target, weight='weight')
    except Exception:
        return  # Acceptable: algorithm rejected invalid input

    # Step 4: Compare with Bellman-Ford (ground truth)
    d_bellman = nx.shortest_path_length(
        G, source, target, weight='weight', method='bellman-ford'
    )

    # Step 5: Validate consistency
    assert d_dijkstra == d_bellman, (
        f"BUG FOUND: Dijkstra={d_dijkstra}, Bellman-Ford={d_bellman}"
    )


@settings(max_examples=300)
@given(st.integers(min_value=4, max_value=10))
def test_mst_dense_graph_cut_property(n):
    """
    Property (Invariant — Cut Property on Dense Graphs):
        For any cut in a graph, the minimum-weight edge crossing the cut
        must belong to the MST when the minimum is unique.

    Mathematical Foundation:
        The cut property is a fundamental theorem underlying MST algorithms
        such as Kruskal’s and Prim’s. Dense graphs (complete graphs) maximize
        the number of edges and cuts, providing a strong stress test.

    Assumptions:
        - Graph is complete (dense)
        - Edge weights are positive
        - The minimum crossing edge for a cut is unique

    Test Strategy:
        Generate a complete graph with deterministically assigned positive weights.
        For each single-node cut S = {v}, identify the minimum crossing edge and
        verify it is included in the MST.

    Why This Matters:
        Violating the cut property indicates a fundamental correctness issue in MST
        construction, as the cut property is both necessary and sufficient for
        optimality in greedy MST algorithms like Kruskal’s and Prim’s.
    """


    G = nx.complete_graph(n)

    for i, (u, v) in enumerate(G.edges()):
        G[u][v]['weight'] = (i % 20) + 1

    T = nx.minimum_spanning_tree(G)

    for node in G.nodes():
        S = {node}

        cut_edges = [
            (u, v, G[u][v]['weight'])
            for u, v in G.edges()
            if (u in S) != (v in S)
        ]

        if not cut_edges:
            continue

        min_weight = min(w for _, _, w in cut_edges)
        min_cut_edges = [(u, v) for u, v, w in cut_edges if w == min_weight]

        if len(min_cut_edges) == 1:
            u, v = min_cut_edges[0]
            assert T.has_edge(u, v) or T.has_edge(v, u), (
                f"BUG FOUND: Cut property violated. Edge ({u},{v}) "
                f"with weight={min_weight} missing from MST."
            )


@settings(max_examples=500)
@given(connected_weighted_graphs())
def test_dijkstra_floating_point_consistency(G):    
    """
    Property (Robustness — Floating Point Consistency):
        Shortest path results from Dijkstra and Bellman-Ford should be
        numerically consistent within floating-point tolerance.

    Mathematical Foundation:
        Floating-point arithmetic is not exact (IEEE 754). Different
        accumulation orders may introduce small rounding differences.
        Both algorithms should still agree within a small tolerance.

    Assumptions:
        - Graph is connected
        - Edge weights are floating-point values (non-negative)

    Test Strategy:
        Assign floating-point weights to edges and compare shortest
        path lengths computed by Dijkstra and Bellman-Ford within
        a tolerance (1e-9).

    Why This Matters:
        Ensures numerical stability and consistency across algorithms,
        preventing discrepancies due to floating-point precision issues.
    """

    # Assign floating-point weights
    float_weights = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for i, (u, v) in enumerate(G.edges()):
        G[u][v]['weight'] = float_weights[i % len(float_weights)]

    nodes = list(G.nodes())
    source, target = nodes[0], nodes[-1]

    d_dijkstra = nx.shortest_path_length(G, source, target, weight='weight')
    d_bellman  = nx.shortest_path_length(
        G, source, target, weight='weight', method='bellman-ford'
    )

    # Use tolerance comparison
    assert abs(d_dijkstra - d_bellman) < 1e-9, (
        f"BUG FOUND: Dijkstra={d_dijkstra}, Bellman-Ford={d_bellman}, "
        f"diff={abs(d_dijkstra - d_bellman)}"
    )


@settings(max_examples=300)
@given(st.integers(min_value=3, max_value=20))
def test_multigraph_mst_properties(n):
    """
    Property (Robustness — MultiGraph MST):
        The MST of a MultiGraph must satisfy tree properties and correctly
        select the minimum-weight edge among parallel edges.

    Mathematical Foundation:
        In a MultiGraph, multiple edges may connect the same pair of nodes.
        MST algorithms must choose the minimum-weight edge among parallel
        edges while maintaining a valid spanning tree.

    Assumptions:
        - Graph is connected
        - Parallel edges exist with distinct weights

    Test Strategy:
        Construct a MultiGraph with duplicate edges:
            - One high-weight edge (weight = 5)
            - One low-weight edge (weight = 1)
        for each pair of consecutive nodes.
        Verify:
            - MST has n−1 edges
            - MST is connected
            - MST selects only minimum-weight edges
            - MST edges belong to the original graph

    Why This Matters:
        Incorrect handling of parallel edges can lead to suboptimal MSTs
        or incorrect edge selection in real-world multigraph scenarios.
    """

    MG = nx.MultiGraph()
    MG.add_nodes_from(range(n))

    # Add parallel edges: high weight and low weight
    for i in range(n - 1):
        MG.add_edge(i, i + 1, weight=5)  # high-weight edge
        MG.add_edge(i, i + 1, weight=1)  # low-weight edge (should be chosen)

    T = nx.minimum_spanning_tree(MG)

    # Tree properties
    assert T.number_of_edges() == n - 1
    assert nx.is_connected(T)

    # Subgraph property
    for u, v, data in T.edges(data=True):
        assert MG.has_edge(u, v)

    # Total weight must be minimal (all edges weight = 1)
    mst_weight = sum(d['weight'] for _, _, d in T.edges(data=True))
    assert mst_weight == n - 1, (
        f"Incorrect MST weight: {mst_weight}, expected {n - 1}"
    )

    # Strong check: ensure only lowest-weight edges are chosen
    for _, _, d in T.edges(data=True):
        assert d['weight'] == 1, (
            "MST selected a higher-weight parallel edge instead of the minimum."
        )
