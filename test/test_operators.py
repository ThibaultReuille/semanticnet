import pytest
import semanticnet as sn
import uuid

def test_difference(populated_digraph):
    A = populated_digraph
    B = populated_digraph.copy()

    B.remove_node('3cd197c2cf5e42dc9ccd0c2adcaf4bc2') # remove node C
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
