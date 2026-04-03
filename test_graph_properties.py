"""
Property-Based Testing for Graph Algorithms using NetworkX

Author: Sudipta Ghosh and Shambo Samanta
Course: Data Structures and Graph Analytics

Algorithms Tested:
1. Shortest Path (Dijkstra)
2. Minimum Spanning Tree (MST)

Description:
This project uses property-based testing with the Hypothesis library to verify
fundamental mathematical properties and invariants of graph algorithms across
automatically generated graphs of varying sizes, densities, and topologies.
Rather than testing specific hand-crafted examples, each test captures a general
truth about the algorithm that must hold for ALL valid inputs.
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
    with varied positive integer edge weights. More idiomatic than passing
    raw integers — Hypothesis can shrink graph inputs directly on failure.

    Generates:
        - n nodes (3 to 10)
        - Connected topology via path graph (deterministic, avoids random module)
        - Random positive integer weights (1 to 20) per edge drawn via Hypothesis
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
@settings(max_examples=100)
@given(connected_weighted_graphs())
def test_shortest_path_minimality(G):
    """
    Property (Invariant):
        The path returned by nx.shortest_path has the minimum total weight
        among all simple paths between the source and target.

    Mathematical Foundation:
        Dijkstra's algorithm is provably optimal: it always finds a path
        whose total weight is no greater than any other path in the graph
        with non-negative edge weights.

    Test Strategy:
        Use the custom connected_weighted_graphs() strategy to generate graphs
        with varied weights (1–20), giving Hypothesis a large search space to
        explore 100 genuinely distinct examples. Pick the first and last node
        as source and target, compute the weighted shortest path length, then
        enumerate ALL simple paths and verify none has lower total weight.

    Preconditions:
        Graph must be connected (guaranteed by strategy) and edge weights
        must be non-negative (all weights ≥ 1 here).

    Why This Matters:
        If this test fails, Dijkstra is returning a sub-optimal path — the
        most fundamental correctness guarantee of the algorithm is broken.
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


@settings(max_examples=100)
@given(connected_weighted_graphs())
def test_shortest_path_symmetry(G):
    """
    Property (Invariant):
        In an undirected graph, distance(u, v) == distance(v, u).

    Mathematical Foundation:
        Undirected edges have no orientation, so any path from u to v
        can be traversed in reverse to obtain a path of identical length
        from v to u. Therefore the distance function must be symmetric.

    Test Strategy:
        Use the custom strategy for varied-weight graphs. Pick the first
        and last node, compute shortest path length in both directions,
        and assert equality.

    Preconditions:
        Graph must be undirected and connected.

    Why This Matters:
        Asymmetry in an undirected distance function would mean the algorithm
        is treating edges as directed internally — a serious implementation bug.
    """
    nodes = list(G.nodes())
    u, v = nodes[0], nodes[-1]

    d_uv = nx.shortest_path_length(G, u, v, weight='weight')
    d_vu = nx.shortest_path_length(G, v, u, weight='weight')

    assert d_uv == d_vu, (
        f"distance({u},{v}) = {d_uv} but distance({v},{u}) = {d_vu}. "
        "Symmetry violated in undirected graph."
    )


@settings(max_examples=100)
@given(connected_weighted_graphs())
def test_shortest_path_edge_addition(G):
    """
    Property (Metamorphic):
        Adding a direct edge between two nodes cannot increase the shortest
        path distance between them.

    Mathematical Foundation:
        Adding an edge (u, v) with weight w introduces a new candidate path
        of length w between u and v. The shortest path length can only stay
        the same or decrease — it can never increase, because the old paths
        still exist.

    Test Strategy:
        Use the custom strategy for varied-weight graphs. Compute the weighted
        shortest distance before adding a direct edge between source and target,
        then add the edge and recompute. Assert the new distance is at most the old.

    Preconditions:
        Graph must be connected. The new edge added has weight = 1.

    Why This Matters:
        If adding an edge increases the reported shortest distance, the algorithm
        has a caching or state-mutation bug that causes it to ignore valid paths.
    """
    nodes = list(G.nodes())
    u, v = nodes[0], nodes[-1]

    d_before = nx.shortest_path_length(G, u, v, weight='weight')
    G.add_edge(u, v, weight=1)
    d_after = nx.shortest_path_length(G, u, v, weight='weight')

    assert d_after <= d_before, (
        f"Distance increased from {d_before} to {d_after} after adding direct edge."
    )


@settings(max_examples=100)
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
        Use the custom strategy for varied-weight graphs. Pick three distinct
        nodes and verify the triangle inequality holds with weighted distances.

    Preconditions:
        Graph must be connected so all pairwise distances are finite.
        Must have at least 3 nodes (guaranteed by strategy min_value=3).

    Why This Matters:
        Violation of the triangle inequality means the distance function is
        not a true metric — indicating fundamental inconsistency in how the
        algorithm computes distances.
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


@settings(max_examples=100)
@given(connected_weighted_graphs())
def test_shortest_path_self_distance(G):
    """
    Property (Boundary Condition):
        The shortest path distance from any node to itself is zero.

    Mathematical Foundation:
        The trivial path from a node to itself uses zero edges and has
        zero total weight. No path can have negative length (weights ≥ 1
        here), so zero is both the minimum and the correct answer.

    Test Strategy:
        Use the custom strategy for varied-weight graphs. Verify that the
        weighted self-distance of the first node is exactly 0.

    Preconditions:
        Edge weights must be non-negative (all weights ≥ 1 here).

    Why This Matters:
        A non-zero self-distance would mean the algorithm is traversing
        unnecessary edges or miscounting path lengths — a basic correctness failure.
    """
    node = list(G.nodes())[0]

    assert nx.shortest_path_length(G, node, node, weight='weight') == 0, (
        f"Self-distance of node {node} is not zero."
    )


@settings(max_examples=100)
@given(connected_weighted_graphs())
def test_shortest_path_validity(G):
    """
    Property (Postcondition):
        Every consecutive pair of nodes in the returned shortest path must
        be connected by an actual edge in the graph.

    Mathematical Foundation:
        A path is defined as a sequence of nodes where each consecutive pair
        is adjacent (connected by an edge). If the algorithm returns a sequence
        where any consecutive pair is NOT an edge, it has returned something
        that is not a valid path at all — regardless of its length.

    Test Strategy:
        Use the custom connected_weighted_graphs() strategy to generate graphs
        with varied weights. Compute the shortest path between the first and
        last node, then verify every step (u→v) in the path is a real edge in G.

    Preconditions:
        Graph must be connected so a path always exists.

    Why This Matters:
        An invalid path (containing non-existent edges) would mean the algorithm
        is fabricating connections — a catastrophic correctness failure that
        would corrupt any application relying on the path.
    """
    nodes = list(G.nodes())
    source, target = nodes[0], nodes[-1]

    path = nx.shortest_path(G, source, target, weight='weight')

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        assert G.has_edge(u, v), (
            f"Path contains step ({u}→{v}) which is not an edge in the graph."
        )


@settings(max_examples=100)
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


@settings(max_examples=100)
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


@settings(max_examples=100)
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

    
# ================================
# Minimum Spanning Tree Properties
# ================================

@settings(max_examples=100)
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

    Test Strategy:
        Use the custom strategy to generate varied-weight connected graphs.
        Compute the MST and verify it has exactly n-1 edges across 100
        distinct graph structures.

    Preconditions:
        The input graph must be connected so that a spanning tree exists.

    Why This Matters:
        If the MST has fewer than n-1 edges, some nodes are not spanned.
        If it has more, it contains a cycle and is not a tree at all.
    """
    n = G.number_of_nodes()
    T = nx.minimum_spanning_tree(G)

    assert T.number_of_edges() == n - 1, (
        f"MST has {T.number_of_edges()} edges, expected {n - 1}."
    )


@settings(max_examples=100)
@given(connected_weighted_graphs())
def test_mst_is_tree(G):
    """
    Property (Invariant):
        The result of nx.minimum_spanning_tree must be acyclic and connected,
        i.e., a valid tree.

    Mathematical Foundation:
        By definition, a spanning tree is a subgraph that (1) connects all
        vertices (is connected) and (2) contains no cycles (is acyclic).
        A graph that is both connected and acyclic is called a tree.
        NetworkX's nx.is_tree checks both conditions simultaneously.

    Test Strategy:
        Use the custom strategy for 100 varied-weight graphs. Compute the MST
        and pass it to nx.is_tree, which returns True iff connected and acyclic.

    Preconditions:
        Input graph must be connected.

    Why This Matters:
        If nx.is_tree returns False, the algorithm has produced either a
        disconnected subgraph (not spanning) or a subgraph with cycles
        (not a tree) — both are fundamental correctness failures.
    """
    T = nx.minimum_spanning_tree(G)

    assert nx.is_tree(T), (
        "MST result is not a valid tree (either contains a cycle or is disconnected)."
    )


@settings(max_examples=100)
@given(connected_weighted_graphs())
def test_mst_spans_all_nodes(G):
    """
    Property (Postcondition):
        The MST must contain every node present in the original graph.

    Mathematical Foundation:
        The word 'spanning' in 'spanning tree' means the tree covers all
        vertices of the original graph. A subgraph that misses even one
        vertex is not a spanning tree.

    Test Strategy:
        Use the custom strategy for 100 varied-weight graphs. Compare the
        node set of the MST with the node set of the original graph.

    Preconditions:
        Input graph must be connected.

    Why This Matters:
        dropped a vertex — corrupting any downstream computation relying
        on full vertex coverage.
    """
    T = nx.minimum_spanning_tree(G)

    assert set(T.nodes()) == set(G.nodes()), (
        f"MST is missing nodes: {set(G.nodes()) - set(T.nodes())}"
    )


@settings(max_examples=100)
@given(connected_weighted_graphs())
def test_mst_edge_removal_disconnects(G):
    """
    Property (Metamorphic):
        Removing any single edge from the MST must disconnect it.

    Mathematical Foundation:
        A tree is minimally connected: it has exactly enough edges to keep
        all vertices connected. Every edge in a tree is a bridge — removing
        it splits the tree into exactly two components. This is a direct
        consequence of having n-1 edges for n vertices with no cycles.

    Test Strategy:
        Use the custom strategy for 100 varied-weight graphs. Compute the MST,
        remove its first edge, and assert the resulting graph is disconnected.

    Preconditions:
        MST must have at least one edge (n ≥ 2, guaranteed by strategy).

    Why This Matters:
        If the graph remains connected after removing an MST edge, the MST
        contained a redundant edge — meaning it has a cycle and is not a tree.
    """
    T = nx.minimum_spanning_tree(G)

    edge = list(T.edges())[0]
    T.remove_edge(*edge)

    assert not nx.is_connected(T), (
        f"Removing edge {edge} did not disconnect the MST — "
        "MST must contain a cycle (not a valid tree)."
    )


@settings(max_examples=100)
@given(connected_weighted_graphs())
def test_mst_idempotence(G):
    """
    Property (Idempotence):
        Applying the MST algorithm to an MST yields the same tree.

    Mathematical Foundation:
        An MST T of a graph G is itself a tree. The MST of a tree T is T
        itself, because T is already acyclic and connected — there is only
        one spanning tree of a tree (the tree itself), so the algorithm
        must return it unchanged.

    Test Strategy:
        Use the custom strategy for 100 varied-weight graphs. Compute
        T1 = MST(G), then T2 = MST(T1), and assert identical edge sets.

    Preconditions:
        Input graph must be connected.

    Why This Matters:
        If MST(MST(G)) ≠ MST(G), the algorithm is not stable — producing
        different results depending on how many times it is applied.
    """
    T1 = nx.minimum_spanning_tree(G)
    T2 = nx.minimum_spanning_tree(T1)

    assert set(T1.edges()) == set(T2.edges()), (
        "MST is not idempotent: MST(MST(G)) ≠ MST(G)."
    )


@settings(max_examples=100)
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
        Use the custom strategy for 100 varied-weight graphs. Iterate over
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


@settings(max_examples=100)
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
        Use the custom strategy for 100 varied-weight graphs. Find an edge in G
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


@settings(max_examples=100)
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
        Use the custom strategy for 100 varied-weight graphs. Compute MST of G,
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

