import pytest
import semanticnet as sn
import uuid

def test_diff(populated_digraph):
    A = populated_digraph
    B = A.copy()

    # remove node C. Will consequently also remove edges (A, C) and (B, C)
    B.remove_node('3cd197c2cf5e42dc9ccd0c2adcaf4bc2')

    node_d = B.add_node({"type": "D"}, 'da30015efe3c44dbb0b3b3862cef704a') # add a new node of type D
    da = B.add_edge(node_d, '3caaa8c09148493dbdf02c574b95526c', {"type": "irregular"}) # add an edge from D to A
    B.remove_edge('5f5f44ec7c0144e29c5b7d513f92d9ab') # remove (A, B)
    # change node A to type Z to check for modifications
    B.set_node_attribute('3caaa8c09148493dbdf02c574b95526c', 'type', 'Z')

    D = sn.diff(A, B, mods=True) # compute the diff graph D

    correct_nodes = {
        uuid.UUID('3caaa8c09148493dbdf02c574b95526c'): {
            'id': uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            'type': "Z",
            'diffstatus': 'modified'
        },
        uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'): {
            'id': uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            'type': "B",
            'diffstatus': 'same'
        },
        uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'): {
            'id': uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'),
            'type': "C",
            'diffstatus': 'removed'
        },
        node_d: {
            'id': node_d,
            'type': "D",
            'diffstatus': 'added'
        }
    }
    assert D.get_nodes() == correct_nodes

    correct_edges = {
        # (A, B)
        uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab'): {
            'id': uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab'),
            'src': uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            'dst': uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            'type': 'normal',
            'diffstatus': 'removed'
        },
        # (B, A)
        uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'): {
            'id': uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'),
            'src': uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            'dst': uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            'type': 'normal',
            'diffstatus': 'same'
        },
        # (A, C)
        uuid.UUID('7eb91be54d3746b89a61a282bcc207bb'): {
            'id': uuid.UUID('7eb91be54d3746b89a61a282bcc207bb'),
            'src': uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            'dst': uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'),
            'type': 'normal',
            'diffstatus': 'removed'
        },
        # (B, C)
        uuid.UUID('c172a3599b7d4ef3bbb688277276b763'): {
            'id': uuid.UUID('c172a3599b7d4ef3bbb688277276b763'),
            'src': uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            'dst': uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'),
            'type': 'irregular',
            'diffstatus': 'removed'
        },
        # (D, A)
        da: {
            'id': da,
            'src': uuid.UUID('da30015efe3c44dbb0b3b3862cef704a'),
            'dst': uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            'type': 'irregular',
            'diffstatus': 'added'
        },
    }
    assert D.get_edges() == correct_edges
