"""
Property-Based Testing for Graph Algorithms using NetworkX

Author: Sudipta Ghosh and Shambo Samanta
Course: Data Structures and Graph Analytics

Algorithms Tested:
1. Shortest Path (Dijkstra)
2. Minimum Spanning Tree (MST)

Description:
This project uses property-based testing with Hypothesis to verify
fundamental mathematical properties of graph algorithms across
randomly generated graphs.
"""

import networkx as nx
from hypothesis import given, strategies as st


# ================================
# Graph Generators
# ================================

def generate_connected_graph(n):
    """Generates a connected graph with n nodes."""
    return nx.connected_watts_strogatz_graph(n, k=2, p=0.3)


def generate_weighted_graph(n):
    """Generates a connected weighted graph with unit weights."""
    G = generate_connected_graph(n)
    for u, v in G.edges():
        G[u][v]['weight'] = 1
    return G


# ================================
# Shortest Path Properties
# ================================

@given(st.integers(min_value=3, max_value=10))
def test_shortest_path_minimality(n):
    """
    Property (Invariant):
    The shortest path between two nodes has minimal length among all paths.

    Mathematical Foundation:
    Dijkstra’s algorithm guarantees optimal shortest paths in graphs
    with non-negative weights.

    Why This Matters:
    Failure indicates incorrect computation of shortest paths.
    """
    G = generate_weighted_graph(n)
    nodes = list(G.nodes())

    source, target = nodes[0], nodes[-1]

    shortest = nx.shortest_path(G, source, target)
    shortest_len = len(shortest)

    for path in nx.all_simple_paths(G, source, target):
        assert shortest_len <= len(path)


@given(st.integers(min_value=3, max_value=10))
def test_shortest_path_symmetry(n):
    """
    Property (Invariant):
    In an undirected graph, distance(u, v) = distance(v, u).

    Why This Matters:
    Ensures symmetric path computation in undirected graphs.
    """
    G = generate_weighted_graph(n)
    nodes = list(G.nodes())

    u, v = nodes[0], nodes[-1]

    d1 = nx.shortest_path_length(G, u, v)
    d2 = nx.shortest_path_length(G, v, u)

    assert d1 == d2


@given(st.integers(min_value=4, max_value=10))
def test_shortest_path_edge_addition(n):
    """
    Property (Metamorphic):
    Adding an edge cannot increase shortest path distance.

    Why This Matters:
    Validates correct behavior under graph augmentation.
    """
    G = generate_weighted_graph(n)
    nodes = list(G.nodes())

    u, v = nodes[0], nodes[-1]

    d1 = nx.shortest_path_length(G, u, v)

    G.add_edge(u, v, weight=1)

    d2 = nx.shortest_path_length(G, u, v)

    assert d2 <= d1


# ================================
# Minimum Spanning Tree Properties
# ================================

@given(st.integers(min_value=3, max_value=10))
def test_mst_edge_count(n):
    """
    Property (Invariant):
    A spanning tree of a connected graph with n nodes has n-1 edges.
    """
    G = generate_weighted_graph(n)
    T = nx.minimum_spanning_tree(G)

    assert T.number_of_edges() == n - 1


@given(st.integers(min_value=3, max_value=10))
def test_mst_is_tree(n):
    """
    Property (Invariant):
    MST must be acyclic and connected.
    """
    G = generate_weighted_graph(n)
    T = nx.minimum_spanning_tree(G)

    assert nx.is_tree(T)


@given(st.integers(min_value=3, max_value=10))
def test_mst_spans_all_nodes(n):
    """
    Property (Postcondition):
    MST must include all nodes of the original graph.
    """
    G = generate_weighted_graph(n)
    T = nx.minimum_spanning_tree(G)

    assert set(T.nodes()) == set(G.nodes())


@given(st.integers(min_value=3, max_value=7))
def test_mst_edge_removal_disconnects(n):
    """
    Property (Metamorphic):
    Removing any edge from MST disconnects the graph.

    Mathematical Foundation:
    A tree is minimally connected; removing any edge breaks connectivity.

    Why This Matters:
    Ensures MST is truly minimal and contains no redundant edges.
    """
    G = generate_weighted_graph(n)
    T = nx.minimum_spanning_tree(G)

    edge = list(T.edges())[0]
    T.remove_edge(*edge)

    assert not nx.is_connected(T)


# ================================
# Idempotence Property
# ================================

def test_mst_idempotence():
    """
    Property (Idempotence):
    Applying MST on an MST yields the same tree.

    Why This Matters:
    Ensures stability of MST operation.
    """
    G = generate_weighted_graph(6)

    T1 = nx.minimum_spanning_tree(G)
    T2 = nx.minimum_spanning_tree(T1)

    assert set(T1.edges()) == set(T2.edges())    