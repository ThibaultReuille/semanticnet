import pytest
import semanticnet as sn
import uuid

def test_difference(populated_digraph):
    A = populated_digraph
    B = populated_digraph.copy()

    # remove node C. Consequently, also removes edges (A, C) and (B, C)
    B.remove_node('3cd197c2cf5e42dc9ccd0c2adcaf4bc2')
    d = B.add_node({"type": "D"}, 'da30015efe3c44dbb0b3b3862cef704a') # add another node D
    B.add_edge(d, '3caaa8c09148493dbdf02c574b95526c') # add an edge from D to A

    e = A.add_node({"type": "E"}, 'b1b1c6bbbce74a6fb40ee2486cebef26') # add another node
    f = A.add_node({"type": "F"}, '3a668c22b43e4521b3c9f042fb2380c2') # add another node
    A.add_edge(e, f, {"type": "irregular"}, 'a216de41cca8412fa4b3f432b5d3b0e4') # add edge between the two new nodes

    C = sn.difference(A, B) # A - B

    correct_nodes = {
        uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'): {
            "type": "C",
            "id": uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2')
        },
        uuid.UUID('b1b1c6bbbce74a6fb40ee2486cebef26'): {
            "type": "E",
            "id": uuid.UUID('b1b1c6bbbce74a6fb40ee2486cebef26')
        },
        uuid.UUID('3a668c22b43e4521b3c9f042fb2380c2'): {
            "type": "F",
            "id": uuid.UUID('3a668c22b43e4521b3c9f042fb2380c2')
        }
    }
    assert C.get_nodes() == correct_nodes

    correct_edges = {
        # e,f
        uuid.UUID('a216de41cca8412fa4b3f432b5d3b0e4'): {
            "type": "irregular",
            "src": uuid.UUID('b1b1c6bbbce74a6fb40ee2486cebef26'),
            "dst": uuid.UUID('3a668c22b43e4521b3c9f042fb2380c2'),
            "id": uuid.UUID('a216de41cca8412fa4b3f432b5d3b0e4')
        }
    }
    assert C.get_edges() == correct_edges

def test_difference_custom_lambda(populated_digraph):
    # add some attributes
    populated_digraph.set_node_attribute('3caaa8c09148493dbdf02c574b95526c', 'depth', 0)
    populated_digraph.set_node_attribute('2cdfebf3bf9547f19f0412ccdfbe03b7', 'depth', 0)
    populated_digraph.set_node_attribute('3cd197c2cf5e42dc9ccd0c2adcaf4bc2', 'depth', 1)

    # add a node of type D
    d = populated_digraph.add_node({'type': 'D', 'depth': 1}, '63cf70d2762043c29eb5e3e958383f4a')

    populated_digraph.set_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'weight', 1)
    populated_digraph.set_edge_attribute('f3674fcc691848ebbd478b1bfb3e84c3', 'weight', 2) # (B, A)
    populated_digraph.set_edge_attribute('7eb91be54d3746b89a61a282bcc207bb', 'weight', 3)
    populated_digraph.set_edge_attribute('c172a3599b7d4ef3bbb688277276b763', 'weight', 5) # (B, C)

    # make a copy to change around
    new_populated_digraph = populated_digraph.copy()

    # add an edge between the new node d and node B with weight 8
    new_populated_digraph.add_edge(d, '2cdfebf3bf9547f19f0412ccdfbe03b7', {'weight': 8},
        '8ccd176a48284915828e5ac7e13bc43a')

    # remove node C. Will remove the edges (B, C) and (A, C) as well
    new_populated_digraph.remove_node('3cd197c2cf5e42dc9ccd0c2adcaf4bc2')
    new_populated_digraph.remove_edge('f3674fcc691848ebbd478b1bfb3e84c3') # remove edge (B, A)

    # custom lambda that defines membership in the usual way, but only for nodes with
    # a depth greater than 0, and edges with a weight greater than 2
    node_depth_gt_0 = lambda nid, G: sn.node_in(nid, G) and G.get_node_attribute(nid, 'depth') > 0
    edge_weight_gt_2 = lambda eid, G: sn.edge_in(eid, G) and G.get_edge_attribute(eid, 'weight') > 2

    dg = sn.difference(populated_digraph, new_populated_digraph, node_depth_gt_0, edge_weight_gt_2)

    # the first two nodes are "not in B" as we have defined it because their
    # depth is not greater than 0
    correct_nodes = {
        uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'): {
            'depth': 0,
            'id': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
            'type': 'B'
        },
        uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'): {
            'depth': 0,
            'id': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            'type': 'A'
        },
        uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'): {
            "id": uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'),
            "type": "C",
            "depth": 1
        }
    }
    assert dg.get_nodes() == correct_nodes

    correct_edges = {
        # the new graph DOES have edge (B, A), but its weight 1, which is not > 2,
        # so by our definition, (B, A) is "not in" the new graph
        uuid.UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab'): {
            'dst': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
            'id': uuid.UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab'),
            'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            'type': 'normal',
            'weight': 1
        },
        # the new graph removed edge (B, A)
        uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'): {
            'id': uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'),
            'src': uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            'dst': uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            'weight': 2,
            'type': 'normal'
        },
        # the new graph removed edge (A, C)
        uuid.UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb'): {
            'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
            'id': uuid.UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb'),
            'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            'type': 'normal',
            'weight': 3
        },
        # new graph removed edge (B, C)
        uuid.UUID('c172a359-9b7d-4ef3-bbb6-88277276b763'): {
            'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
            'id': uuid.UUID('c172a359-9b7d-4ef3-bbb6-88277276b763'),
            'src': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
            'type': 'irregular',
            'weight': 5
        }
    }
    assert dg.get_edges() == correct_edges

def test_intersection(populated_digraph):
    another_digraph = sn.DiGraph()
    a = another_digraph.add_node({"type": "A"}, '3caaa8c09148493dbdf02c574b95526c')
    b = another_digraph.add_node({"type": "B"}, '2cdfebf3bf9547f19f0412ccdfbe03b7')
    d = another_digraph.add_node({"type": "D"}, 'da30015efe3c44dbb0b3b3862cef704a')
    another_digraph.add_edge(a, b, {"type": "normal"}, '5f5f44ec7c0144e29c5b7d513f92d9ab')
    another_digraph.add_edge(b, a, {"type": "normal"}, 'f3674fcc691848ebbd478b1bfb3e84c3')
    another_digraph.add_edge(a, d, {"type": "normal"}, 'f3674fcc691848ebbd478b1bfb3e84c3')
    another_digraph.add_edge(d, b, {"type": "irregular"}, 'f3674fcc691848ebbd478b1bfb3e84c3')

    I = sn.intersection(populated_digraph, another_digraph)

    correct_nodes = {
        uuid.UUID('3caaa8c09148493dbdf02c574b95526c'): {
            "type": "A",
            "id": uuid.UUID('3caaa8c09148493dbdf02c574b95526c')
        },
        uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'): {
            "type": "B",
            "id": uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7')
        }
    }
    assert I.get_nodes() == correct_nodes

    correct_edges = {
        # a,b
        uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab'): {
            "type": "normal",
            "src": uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            "dst": uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            "id": uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab')
        },
        # b,a
        uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'): {
            "type": "normal",
            "src": uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            "dst": uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            "id": uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3')
        }
    }
    assert I.get_edges() == correct_edges

def test_union_disjoint(populated_digraph):
    g1 = populated_digraph

    g2 = sn.DiGraph()

    a = g2.add_node({"label" : "A"}, 'a')
    b = g2.add_node({"label" : "B"}, 'b')
    c = g2.add_node({"label" : "C"}, 'c')

    ab = g2.add_edge(a, b, {"type" : "belongs"}, 'belongs')
    bc = g2.add_edge(b, c, {"type" : "owns"}, 'owns')
    ca = g2.add_edge(c, a, {"type" : "has"}, 'has')

    gu = sn.union(g1, g2)

    correct_nodes = {
        uuid.UUID('3caaa8c09148493dbdf02c574b95526c'): {
            'id': uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            'type': 'A'
        },
        uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'): {
            'id': uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            'type': 'B'
        },
        uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'): {
            'id': uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'),
            'type': 'C'
        },
        'a': {
            'id': 'a',
            'label': 'A'
        },
        'b': {
            'id': 'b',
            'label': 'B'
        },
        'c': {
            'id': 'c',
            'label': 'C'
        }
    }
    assert gu.get_nodes() == correct_nodes

    correct_edges = {
        uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab'): {
            'id': uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab'),
            'src': uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            'dst': uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            'type': 'normal'
        },
        uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'): {
            'id': uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'),
            'src': uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            'dst': uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            'type': 'normal'
        },
        uuid.UUID('7eb91be54d3746b89a61a282bcc207bb'): {
            'id': uuid.UUID('7eb91be54d3746b89a61a282bcc207bb'),
            'src': uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            'dst': uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'),
            'type': 'normal'
        },
        uuid.UUID('c172a3599b7d4ef3bbb688277276b763'): {
            'id': uuid.UUID('c172a3599b7d4ef3bbb688277276b763'),
            'src': uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            'dst': uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'),
            'type': 'irregular'
        },
        ab: {
            'id': ab,
            'src': a,
            'dst': b,
            'type': 'belongs'
        },
        bc: {
            'id': bc,
            'src': b,
            'dst': c,
            'type': 'owns'
        },
        ca: {
            'id': ca,
            'src': c,
            'dst': a,
            'type': 'has'
        }
    }
    assert gu.get_edges() == correct_edges

def test_union_partial(populated_digraph):
    g1 = populated_digraph
    g2 = sn.DiGraph()
    a = g2.add_node({"type": "A"}, '3caaa8c09148493dbdf02c574b95526c')
    b = g2.add_node({"type": "B"}, '2cdfebf3bf9547f19f0412ccdfbe03b7')
    d = g2.add_node({"type": "D"})
    ab = g2.add_edge(a, b, {"type": "normal"}, '5f5f44ec7c0144e29c5b7d513f92d9ab')
    bd = g2.add_edge(b, d, {"type": "irregular"})

    gu = sn.union(g1, g2)

    correct_nodes = {
        a: {
            'id': a,
            'type': 'A'
        },
        b: {
            'id': b,
            'type': 'B'
        },
        uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'): {
            'id': uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'),
            'type': 'C'
        },
        d: {
            'id': d,
            'type': 'D'
        }
    }
    assert gu.get_nodes() == correct_nodes

    correct_edges = {
        ab: {
            'id': ab,
            'src': a,
            'dst': b,
            'type': 'normal'
        },
        uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'): {
            'id': uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'),
            'src': b,
            'dst': a,
            'type': 'normal'
        },
        uuid.UUID('7eb91be54d3746b89a61a282bcc207bb'): {
            'id': uuid.UUID('7eb91be54d3746b89a61a282bcc207bb'),
            'src': a,
            'dst': uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'),
            'type': 'normal'
        },
        uuid.UUID('c172a3599b7d4ef3bbb688277276b763'): {
            'id': uuid.UUID('c172a3599b7d4ef3bbb688277276b763'),
            'src': uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            'dst': uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'),
            'type': 'irregular'
        },
        bd: {
            'id': bd,
            'src': b,
            'dst': d,
            'type': 'irregular'
        }
    }
    gu.get_nodes() == correct_nodes

def test_union_idempotent(populated_digraph):
    g1 = populated_digraph
    g2 = g1.copy()
    gu = sn.union(g1, g2)
    assert gu.get_nodes() == g1.get_nodes()
    assert gu.get_nodes() == g2.get_nodes()
    assert gu.get_edges() == g1.get_edges()
    assert gu.get_edges() == g2.get_edges()
