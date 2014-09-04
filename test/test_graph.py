import os
import pytest
import semanticnet as sn
import time
import uuid

def test_json_constructor(fixture_dir, correct_output_filename, correct_output_graph):
    g = sn.DiGraph(json_file=os.path.join(fixture_dir, correct_output_filename))
    assert g.get_nodes() == correct_output_graph.get_nodes()
    assert g.get_edges() == correct_output_graph.get_edges()

def test__create_uuid(graph):
    id_ = graph._create_uuid()
    assert id_.__class__.__name__ == 'UUID'

def test__extract_id(graph, uuid_str, uuid_obj):
    assert graph._extract_id(uuid_str) == uuid_obj

def test_add_event(graph):
    t = time.time()
    e = sn.Event(t, "Generic Event", {"type": "test"})
    graph.add_event(e.timecode, e.name, e.attributes)
    in_timeline = graph.timeline[0]
    assert e.timecode == in_timeline.timecode
    assert e.name == in_timeline.name
    assert e.attributes == in_timeline.attributes

def test_add_node(graph):
    a = graph.add_node({"type": "A"})

    nodes = graph.get_nodes()
    assert a in nodes

    node = graph.get_node_attributes(a)
    assert "type" in node
    assert node["type"] == "A"

    # adding a node with reserved attributes should throw an exception
    with pytest.raises(sn.ReservedAttributeException):
        graph.add_node({"id": 0})

def test_add_nodes():
    dg = sn.DiGraph()
    nodes = {
        uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'): {
            "id": uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
            'type': 'B'
        },
        uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'): {
            "id": uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            'type': 'A'
        },
        uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'): {
            "id": uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
            'type': 'C'
        }
    }
    dg.add_nodes(nodes)
    assert dg.get_nodes() == nodes

    dg = sn.DiGraph()
    nodes = [ {'type': 'A'}, {'type': 'B'}, {'type': 'C'} ]
    ids = dg.add_nodes(nodes)

    dg_nodes = dg.get_nodes()
    assert dg_nodes[ids[0]]['type'] == 'A'
    assert dg_nodes[ids[1]]['type'] == 'B'
    assert dg_nodes[ids[2]]['type'] == 'C'

def test_has_node(populated_graph):
    assert populated_graph.has_node('3caaa8c09148493dbdf02c574b95526c')
    assert populated_graph.has_node('2cdfebf3bf9547f19f0412ccdfbe03b7')
    assert populated_graph.has_node('3cd197c2cf5e42dc9ccd0c2adcaf4bc2')

def test_get_node(populated_graph):
    assert (
        populated_graph.get_node('3caaa8c09148493dbdf02c574b95526c') ==
        {
            "type": "A",
            "id": uuid.UUID('3caaa8c09148493dbdf02c574b95526c')
        }
    )

def test_get_or_add_node():
    dg = sn.DiGraph()
    key = 'test_key'

    # node is not in before we add it
    with pytest.raises(KeyError):
        dg.get_node('test_key')

    # node is in after we add it
    dg.get_or_add_node(key, data={"type": "test"})

    correct_node = {
        "id": key,
        "type": "test"
    }
    test_node = dg.get_node(key)
    assert test_node == correct_node

    # if we call again with the same key, it does not add a node, it returns it
    # Will also discard the argument data
    dg.get_or_add_node(key, data={"type": "test2"})
    correct_nodes = {
        key: {
            "id": key,
            "type": "test" # not test2
        }
    }
    assert dg.get_nodes() == correct_nodes

def test_get_nodes(populated_graph):
    output = {
        uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'): {
            "id": uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
            'type': 'B'
        },
        uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'): {
            "id": uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            'type': 'A'
        },
        uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'): {
            "id": uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
            'type': 'C'
        }
    }
    assert populated_graph.get_nodes() == output

def test_get_node_ids(populated_graph):
    correct_output = [
        uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
        uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
        uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2')
    ]
    assert populated_graph.get_node_ids() == correct_output

def test_get_node_attribute(populated_graph):
    assert populated_graph.get_node_attribute('3caaa8c09148493dbdf02c574b95526c', 'type') == 'A'
    assert populated_graph.get_node_attribute('2cdfebf3bf9547f19f0412ccdfbe03b7', 'type') == 'B'
    assert populated_graph.get_node_attribute('3cd197c2cf5e42dc9ccd0c2adcaf4bc2', 'type') == 'C'

    with pytest.raises(sn.GraphException):
        populated_graph.get_node_attribute('3caaa8c09148493dbdf02c57deadbeef', 'type')

def test_get_node_attributes(populated_graph):
    assert ( populated_graph.get_node_attributes('3caaa8c09148493dbdf02c574b95526c') == 
        {
            "id": uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            'type': 'A'
        }
    )
    with pytest.raises(sn.GraphException):
        populated_graph.get_node_attributes('3caaa8c09148493dbdf02c57deadbeef')

def test_neighbors(populated_digraph):
   neighbors = populated_digraph.neighbors(uuid.UUID( '3caaa8c09148493dbdf02c574b95526c') )
   correct_neighbors = {
           uuid.UUID( '2cdfebf3bf9547f19f0412ccdfbe03b7' ): {
               'id': uuid.UUID( '2cdfebf3bf9547f19f0412ccdfbe03b7' ),
               'type': 'B',
           },
           uuid.UUID( '3cd197c2cf5e42dc9ccd0c2adcaf4bc2' ): {
               'id': uuid.UUID( '3cd197c2cf5e42dc9ccd0c2adcaf4bc2' ),
               'type': 'C',
           }
   }
   assert neighbors == correct_neighbors

def test_predecessors(populated_digraph):
   predecessors = populated_digraph.predecessors(uuid.UUID( '3cd197c2cf5e42dc9ccd0c2adcaf4bc2') )
   correct_predecessors = {
           uuid.UUID( '2cdfebf3bf9547f19f0412ccdfbe03b7' ): {
               'id': uuid.UUID( '2cdfebf3bf9547f19f0412ccdfbe03b7' ),
               'type': 'B',
           },
           uuid.UUID( '3caaa8c09148493dbdf02c574b95526c' ): {
               'id': uuid.UUID( '3caaa8c09148493dbdf02c574b95526c' ),
               'type': 'A',
           }
   }
   assert predecessors == correct_predecessors

def test_set_node_attribute(populated_graph):
    populated_graph.set_node_attribute('3caaa8c09148493dbdf02c574b95526c', 'depth', 5)
    assert populated_graph.get_node_attribute('3caaa8c09148493dbdf02c574b95526c', 'depth') == 5
    
    populated_graph.set_node_attribute('3caaa8c09148493dbdf02c574b95526c', 'type', 'D')
    assert populated_graph.get_node_attribute('3caaa8c09148493dbdf02c574b95526c', 'type') != 'A'
    assert populated_graph.get_node_attribute('3caaa8c09148493dbdf02c574b95526c', 'type') == 'D'

    # set non-existant edge
    with pytest.raises(sn.GraphException):
        populated_graph.set_node_attribute('3caaa8c09148493dbdf02c57deadbeef', 'depht', 5)

    # set reserved attribute
    with pytest.raises(sn.ReservedAttributeException):
        populated_graph.set_node_attribute('3caaa8c09148493dbdf02c574b95526c', 'id',
            '3caaa8c09148493dbdf02c57deadbeef')

def test_add_edge(graph):
    a = graph.add_node({"type": "A"})
    b = graph.add_node({"type": "B"})
    e = graph.add_edge(a, b, {"type": "normal"})

    assert len(graph.get_edges()) != 0
    assert e in graph.get_edges()

    attrs = graph.get_edge_attributes(e)
    assert "type" in attrs
    assert attrs["type"] == "normal"

    # use a non-existant node. Should throw an exception
    with pytest.raises(sn.GraphException):
        graph.add_edge(a, '3caaa8c09148493dbdf02c57deadbeef')

    # adding an edge with reserved attributes should throw an exception
    with pytest.raises(sn.ReservedAttributeException):
        graph.add_edge(a, b, {"id": 0})

    with pytest.raises(sn.ReservedAttributeException):
        graph.add_edge(a, b, {"src": a})

    with pytest.raises(sn.ReservedAttributeException):
        graph.add_edge(a, b, {"dst": b})

    with pytest.raises(sn.ReservedAttributeException):
        graph.add_edge(a, b, {"src": a, "dst": b, "id": 0})

def test_add_edges(populated_digraph):
    g = sn.DiGraph()
    g.add_nodes(populated_digraph.get_nodes())
    edges = [
        (
            '3caaa8c09148493dbdf02c574b95526c',
            '2cdfebf3bf9547f19f0412ccdfbe03b7',
            {"type": "normal"},
            '5f5f44ec7c0144e29c5b7d513f92d9ab'
        ),
        (
            '2cdfebf3bf9547f19f0412ccdfbe03b7',
            '3caaa8c09148493dbdf02c574b95526c',
            {"type": "normal"},
            'f3674fcc691848ebbd478b1bfb3e84c3'
        ),
        (
            '3caaa8c09148493dbdf02c574b95526c',
            '3cd197c2cf5e42dc9ccd0c2adcaf4bc2',
            {"type": "normal"},
            '7eb91be54d3746b89a61a282bcc207bb'
        ),
        (
            '2cdfebf3bf9547f19f0412ccdfbe03b7',
            '3cd197c2cf5e42dc9ccd0c2adcaf4bc2',
            # include some dummy reserved attributes
            # to make sure they correctly get removed
            {
                "type": "irregular", "id": "foo",
                "src": "bar", "dst": "baz"
            },
            'c172a3599b7d4ef3bbb688277276b763'
        ),
        # (b, c). leave out id to test that mixing tuple variations works
        (
            '3cd197c2cf5e42dc9ccd0c2adcaf4bc2',
            '2cdfebf3bf9547f19f0412ccdfbe03b7',
            {"type": "irregular"}
        )
    ]
    g.add_edges(edges)
    gedges = g.get_edges()
    # make sure all the edges from populated_digraph are present
    for eid, attrs in populated_digraph.get_edges().iteritems():
        assert eid in gedges
        assert gedges[eid] == attrs

    # make sure the last edge in the list was added
    assert g.get_edges_between('3cd197c2cf5e42dc9ccd0c2adcaf4bc2', '2cdfebf3bf9547f19f0412ccdfbe03b7')

    g = sn.DiGraph()
    g.add_node({"type": "A"}, '3caaa8c09148493dbdf02c574b95526c')
    g.add_node({"type": "B"}, '2cdfebf3bf9547f19f0412ccdfbe03b7')
    g.add_node({"type": "C"}, '3cd197c2cf5e42dc9ccd0c2adcaf4bc2')
    edges = populated_digraph.get_edges()
    g.add_edges(edges)
    assert g.get_edges() == populated_digraph.get_edges()

def test_get_edge(populated_graph):
    assert ( populated_graph.get_edge('7eb91be5-4d37-46b8-9a61-a282bcc207bb') ==
        {
            'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
            'type': 'normal',
            'id': uuid.UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb')
        }
    )

    with pytest.raises(sn.GraphException):
        populated_graph.get_edge('7eb91be5-4d37-46b8-9a61-a282deadbeef')

def test_has_edge(populated_graph):
    assert populated_graph.has_edge('5f5f44ec7c0144e29c5b7d513f92d9ab')
    assert populated_graph.has_edge('7eb91be54d3746b89a61a282bcc207bb')
    assert populated_graph.has_edge('c172a3599b7d4ef3bbb688277276b763')

def test_has_edge_between(populated_graph):
    assert populated_graph.has_edge_between('3caaa8c09148493dbdf02c574b95526c', '2cdfebf3bf9547f19f0412ccdfbe03b7')
    assert populated_graph.has_edge_between('3caaa8c09148493dbdf02c574b95526c', '3cd197c2cf5e42dc9ccd0c2adcaf4bc2')
    assert populated_graph.has_edge_between('2cdfebf3bf9547f19f0412ccdfbe03b7', '3cd197c2cf5e42dc9ccd0c2adcaf4bc2')

def test_get_edges_between(populated_graph):
    populated_graph.add_node(id_='261b076580434c299361f4a3c05db55d')
    populated_graph.add_edge('3caaa8c09148493dbdf02c574b95526c', '2cdfebf3bf9547f19f0412ccdfbe03b7',
        {"type": "irregular"}, '9ad0b719d681459584f7e2c962910526')

    edges_a_b = populated_graph.get_edges_between('3caaa8c09148493dbdf02c574b95526c', '2cdfebf3bf9547f19f0412ccdfbe03b7')
    correct = {
        uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab'): {
            "src": uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            "dst": uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            "type": "normal",
            "id": uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab')
        },
        uuid.UUID('9ad0b719d681459584f7e2c962910526'): {
            "src": uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            "dst": uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            "type": "irregular",
            "id": uuid.UUID('9ad0b719d681459584f7e2c962910526')
        }
    }
    assert edges_a_b == correct

    assert (
        not populated_graph.get_edges_between('3caaa8c09148493dbdf02c574b95526c',
            '261b076580434c299361f4a3c05db55d')
    )

def test_get_edges_between_digraph(populated_digraph):
    edges_a_b = populated_digraph.get_edges_between('3caaa8c09148493dbdf02c574b95526c',
        '2cdfebf3bf9547f19f0412ccdfbe03b7')

    # for digraphs, should return all edges in both directions
    correct_edges = {
        uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab'): {
            "id": uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab'),
            "src": uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            "dst": uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            "type": "normal"
        },
        uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'): {
            "id": uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'),
            "src": uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            "dst": uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            "type": "normal"
        }
    }
    assert edges_a_b == correct_edges

def test_get_edges(populated_graph):
    output = {
        uuid.UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb'): {
            'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
            'type': 'normal',
            'id': uuid.UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb')
        },
        uuid.UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab'): {
            'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            'dst': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
            'type': 'normal',
            'id': uuid.UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab')
        },
        uuid.UUID('c172a359-9b7d-4ef3-bbb6-88277276b763'): {
            'src': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
            'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
            'type': 'irregular',
            'id': uuid.UUID('c172a359-9b7d-4ef3-bbb6-88277276b763')
        }
    }
    assert populated_graph.get_edges() == output

def test_get_edge_ids(populated_graph):
    correct_edge_ids = [
        uuid.UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb'),
        uuid.UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab'),
        uuid.UUID('c172a359-9b7d-4ef3-bbb6-88277276b763')
    ]
    assert populated_graph.get_edge_ids() == correct_edge_ids

def test_get_node(populated_graph):
    assert (
        populated_graph.get_node('3caaa8c09148493dbdf02c574b95526c') ==
        {
            "type": "A",
            "id": uuid.UUID('3caaa8c09148493dbdf02c574b95526c')
        }
    )

def test_get_edge_attribute(populated_graph):
    assert populated_graph.get_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'type') == 'normal'

    # get nonexistent edge attribute on a valid edge
    assert populated_graph.get_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'weight') == None

    # nonexistent id
    with pytest.raises(sn.GraphException):
        populated_graph.get_edge_attribute('5f5f44ec7c0144e29c5b7d51deadbeef', 'type')

def test_get_edge_attributes(populated_graph):
    assert ( populated_graph.get_edge_attributes('5f5f44ec7c0144e29c5b7d513f92d9ab') ==
        {
            "type": "normal",
            "src": uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            "dst": uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            "id": uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab')
        }
    )

    # nonexistent id
    with pytest.raises(sn.GraphException):
        populated_graph.get_edge_attributes('5f5f44ec7c0144e29c5b7d51deadbeef')

def test_set_edge_attribute(populated_graph):
    populated_graph.set_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'weight', 5)
    assert populated_graph.get_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'weight') == 5
    
    populated_graph.set_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'type', 'irregular')
    assert populated_graph.get_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'type') != 'normal'
    assert populated_graph.get_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'type') == 'irregular'

    # nonexistent id
    with pytest.raises(sn.GraphException):
        populated_graph.set_edge_attribute('5f5f44ec7c0144e29c5b7d51deadbeef', 'weight', 5)

    # set reserved attribute
    with pytest.raises(sn.ReservedAttributeException):
        populated_graph.set_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'id',
            '5f5f44ec7c0144e29c5b7d51deadbeef')

    with pytest.raises(sn.ReservedAttributeException):
        populated_graph.set_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'src',
            '3caaa8c09148493dbdf02c57deadbeef')

    with pytest.raises(sn.ReservedAttributeException):
        populated_graph.set_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'dst',
            '3caaa8c09148493dbdf02c57deadbeef')

def test_remove_edge(populated_graph):
    populated_graph.remove_edge('5f5f44ec7c0144e29c5b7d513f92d9ab')
    assert uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab') not in populated_graph.get_edges()
    with pytest.raises(sn.GraphException):
        populated_graph.remove_edge('5f5f44ec7c0144e29c5b7d51deadbeef')

def test_remove_edges(populated_digraph):
    # remove the edges (a, b) and (a, c)
    populated_digraph.remove_edges(['5f5f44ec7c0144e29c5b7d513f92d9ab', '7eb91be54d3746b89a61a282bcc207bb'])

    correct_edges = {
        uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'): {
            "id": uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3'),
            "src": uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            "dst": uuid.UUID('3caaa8c09148493dbdf02c574b95526c'),
            "type": "normal"
        },
        uuid.UUID('c172a3599b7d4ef3bbb688277276b763'): {
            "id": uuid.UUID('c172a3599b7d4ef3bbb688277276b763'),
            "src": uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'),
            "dst": uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'),
            "type": "irregular"
        }
    }
    assert populated_digraph.get_edges() == correct_edges

def test_remove_node(populated_graph):
    node_a_id = uuid.UUID('3caaa8c09148493dbdf02c574b95526c')
    node_b_id = uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7')
    node_c_id = uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2')

    edge_a_b_id = uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab')
    edge_a_c_id = uuid.UUID('7eb91be54d3746b89a61a282bcc207bb')
    edge_b_c_id = uuid.UUID('c172a3599b7d4ef3bbb688277276b763')

    populated_graph.remove_node('3caaa8c09148493dbdf02c574b95526c')
    
    # make sure a is gone, and b and c are not
    assert node_a_id not in populated_graph.get_nodes()
    assert node_b_id in populated_graph.get_nodes()
    assert node_c_id in populated_graph.get_nodes()

    # make sure the edges from a to b and a to c are gone
    # but the edge from b to c is not
    edges = populated_graph.get_edges()
    assert edge_a_b_id not in edges
    assert edge_a_c_id not in edges
    assert edge_b_c_id in edges

    with pytest.raises(sn.GraphException):
        populated_graph.remove_node('3caaa8c09148493dbdf02c57deadbeef')

def test_remove_nodes(populated_graph):
    # remove A and B
    populated_graph.remove_nodes(['3caaa8c09148493dbdf02c574b95526c', '2cdfebf3bf9547f19f0412ccdfbe03b7'])

    # only C should remain
    correct_nodes = {
        uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2'): {
            "type": "C",
            "id": uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2')
        }
    }
    assert populated_graph.get_nodes() == correct_nodes

def test_remove_digraph_node(populated_digraph):
    node_a_id = uuid.UUID('3caaa8c09148493dbdf02c574b95526c')
    node_b_id = uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7')
    node_c_id = uuid.UUID('3cd197c2cf5e42dc9ccd0c2adcaf4bc2')

    edge_a_b_id = uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab')
    edge_b_a_id = uuid.UUID('f3674fcc691848ebbd478b1bfb3e84c3')
    edge_a_c_id = uuid.UUID('7eb91be54d3746b89a61a282bcc207bb')
    edge_b_c_id = uuid.UUID('c172a3599b7d4ef3bbb688277276b763')

    populated_digraph.remove_node('3caaa8c09148493dbdf02c574b95526c')

    # make sure a is gone, and b and c are not
    assert node_a_id not in populated_digraph.get_nodes()
    assert node_b_id in populated_digraph.get_nodes()
    assert node_c_id in populated_digraph.get_nodes()

    # make sure edges (a,b), (b,a), (a,c) are gone but (b,c) is not
    edges = populated_digraph.get_edges()
    assert edge_a_b_id not in edges
    assert edge_b_a_id not in edges
    assert edge_a_c_id not in edges
    assert edge_b_c_id in edges

def test_save_json(fixture_dir, test_output, correct_output):
    assert test_output["timeline"] == correct_output["timeline"]
    assert test_output["meta"] == correct_output["meta"]

    for node in test_output["nodes"]:
        assert node in correct_output["nodes"]

    for edge in test_output["edges"]:
        # for an undirected edge, reversing src and dst is valid
        try:
            assert edge in correct_output["edges"]
        except AssertionError:
            edge["src"], edge["dst"] = edge["dst"], edge["src"]
            assert edge in correct_output["edges"]

    os.remove(os.path.join(fixture_dir, "test_output.json"))

def test_save_json_plaintext(test_output_plaintext, test_output_plaintext_correct):
    assert test_output_plaintext["timeline"] == test_output_plaintext_correct["timeline"]
    assert test_output_plaintext["meta"] == test_output_plaintext_correct["meta"]

    for node in test_output_plaintext["nodes"]:
        assert node in test_output_plaintext_correct["nodes"]

    for edge in test_output_plaintext["edges"]:
        # for an undirected edge, reversing src and dst is valid
        try:
            assert edge in test_output_plaintext_correct["edges"]
        except AssertionError:
            edge["src"], edge["dst"] = edge["dst"], edge["src"]
            assert edge in test_output_plaintext_correct["edges"]

def test_load_json(correct_output_graph):
    nodes = {
        uuid.UUID('6cf546f71efe47578f7a1400871ef6b8'): {
            'id': uuid.UUID('6cf546f71efe47578f7a1400871ef6b8'),
            'label': 'A'
        },
        uuid.UUID('bcb388bb24a74d978fa2006ed278b2fe'): {
            'id': uuid.UUID('bcb388bb24a74d978fa2006ed278b2fe'),
            'label': 'B'
        },
        uuid.UUID('d6523f4f9d5240d2a92e341f4ca00a78'): {
            'id': uuid.UUID('d6523f4f9d5240d2a92e341f4ca00a78'),
            'label': 'C'
        }
    }

    assert correct_output_graph.get_nodes() == nodes

    edges = {
        uuid.UUID('081369f6197b467abe97b3efe8cc4640'): {
            'src': uuid.UUID('bcb388bb24a74d978fa2006ed278b2fe'),
            'dst': uuid.UUID('d6523f4f9d5240d2a92e341f4ca00a78'),
            'type': 'owns',
            'id': uuid.UUID('081369f6197b467abe97b3efe8cc4640')
        },
        uuid.UUID('b3a245098d5d482f893c6d63606c7e91'): {
            'src': uuid.UUID('d6523f4f9d5240d2a92e341f4ca00a78'),
            'dst': uuid.UUID('6cf546f71efe47578f7a1400871ef6b8'),
            'type': 'has',
            'id': uuid.UUID('b3a245098d5d482f893c6d63606c7e91')
        },
        uuid.UUID('ff8a8a8093cf436aa3b0127c71ddc11d'): {
            'src': uuid.UUID('6cf546f71efe47578f7a1400871ef6b8'),
            'dst': uuid.UUID('bcb388bb24a74d978fa2006ed278b2fe'),
            'type': 'belongs',
            'id': uuid.UUID('ff8a8a8093cf436aa3b0127c71ddc11d')
        }
    }

    assert correct_output_graph.get_edges() == edges

def test_load_json_with_object(correct_output):
    g = sn.Graph()
    g.load_json(correct_output) # load graph with json object, instead of string
    test_load_json(g)

def test_load_json_plaintext(correct_output_graph_plaintext_from_file):
    nodes = {
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

    assert correct_output_graph_plaintext_from_file.get_nodes() == nodes

    edges = {
        'owns': {
            'src': 'b',
            'dst': 'c',
            'type': 'owns',
            'id': 'owns'
        },
        'has': {
            'src': 'c',
            'dst': 'a',
            'type': 'has',
            'id': 'has'
        },
        'belongs': {
            'src': 'a',
            'dst': 'b',
            'type': 'belongs',
            'id': 'belongs'
        }
    }

    assert correct_output_graph_plaintext_from_file.get_edges() == edges

def test_networkx_graph(populated_graph):
    nx_graph = populated_graph.networkx_graph()

    # make sure all edges and nodes are the same
    for id_, attr in populated_graph.get_edges().iteritems():
        assert nx_graph.edge[attr["src"]][attr["dst"]][id_] == attr

    for id_, attr in populated_graph.get_nodes().iteritems():
        assert nx_graph.node[id_] == attr


    # but that it is not the same object
    assert nx_graph is not populated_graph._g

def test_load_networkx_graph(netx_graph):
    graph = sn.Graph()
    graph.load_networkx_graph(netx_graph)

    correct_nodes = {
        0: {
            "type": "A",
            "id": 0
        },
        1: {
            "type": "B",
            "id": 1
        },
        2: {
            "type": "C",
            "id": 2
        },
    }
    assert graph.get_nodes() == correct_nodes

    correct_edges = {
        0: {
            "src": 0,
            "dst": 1,
            "type": "normal",
            "id": 0
        },
        1: {
            "src": 0,
            "dst": 2,
            "type": "normal",
            "id": 1
        },
        2: {
            "src": 1,
            "dst": 2,
            "type": "irregular",
            "id": 2
        },
    }
    assert graph.get_edges() == correct_edges

def test_cache_by_empty(graph):
    graph.cache_nodes_by("type")
    graph.add_node({"type": "A"}, '8a09b47f77284348878c745741a326aa')
    cache = graph.get_nodes_by_attr("type", "A", nosingleton=True)
    assert (
        cache ==
        {
            "id": uuid.UUID('8a09b47f77284348878c745741a326aa'),
            "type": "A"
        }
    )

def test_get_nodes_by_attr(populated_graph):
    populated_graph.add_node({"type": "A"}, '2b673235a0b94935ab8b6b9de178d341')

    # a non-existent attr should return an empty dict
    assert populated_graph.get_nodes_by_attr("label") == {}

    # cache by the attribute "type"
    populated_graph.cache_nodes_by("type")

    ### get all nodes with attr "type"
    input_ = populated_graph.get_nodes_by_attr("type")
    output = {
        "B": [{
            "id": uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
            'type': 'B'
        }],
        "A": [
            {
                "id": uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
                "type": "A"
            },
            {
                "id": uuid.UUID('2b673235a0b94935ab8b6b9de178d341'),
                "type": "A"
            }
        ],
        "C": [{
            "id": uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
            'type': 'C'
        }]
    }

    assert input_ == output

    ### get all nodes of "type" "B"
    input_ = populated_graph.get_nodes_by_attr("type", "B")
    output = [{
        "id": uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
        'type': 'B'
    }]

    assert input_ == output

    ### if user specifies 'nosingleton=False', return a singleton list
    input_ = populated_graph.get_nodes_by_attr("type", "B", nosingleton=True)
    output = {
        "id": uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
        'type': 'B'
    }

    assert input_ == output

    ### get all nodes of "type" "A"
    input_ = populated_graph.get_nodes_by_attr("type", "A")
    output = [
        {
            "id": uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            "type": "A"
        },
        {
            "id": uuid.UUID('2b673235a0b94935ab8b6b9de178d341'),
            "type": "A"
        }
    ]

    assert input_ == output

    ### if user specifies 'nosingleton=True', but there is more than one,
    ### should still return the same list, having no affect on the output
    input_ = populated_graph.get_nodes_by_attr("type", "A", nosingleton=True)
    output = [
        {
            "id": uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            "type": "A"
        },
        {
            "id": uuid.UUID('2b673235a0b94935ab8b6b9de178d341'),
            "type": "A"
        }
    ]

    assert input_ == output

    ### if the attr is in the cache, but the value is not, return []
    assert populated_graph.get_nodes_by_attr("type", "D") == []
