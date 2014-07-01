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
