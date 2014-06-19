import pytest
import semanticnet as sn
import uuid
import os
import time
import json

### FIXTURES ###
@pytest.fixture
def uuid_str():
    return '3caaa8c09148493dbdf02c574b95526c'

@pytest.fixture
def uuid_obj():
    return uuid.UUID('3caaa8c09148493dbdf02c574b95526c')

@pytest.fixture
def graph():
    return sn.Graph()

@pytest.fixture
def populated_graph():
    g = sn.Graph()
    a = g.add_node({"type": "A"}, '3caaa8c09148493dbdf02c574b95526c')
    b = g.add_node({"type": "B"}, '2cdfebf3bf9547f19f0412ccdfbe03b7')
    c = g.add_node({"type": "C"}, '3cd197c2cf5e42dc9ccd0c2adcaf4bc2')
    g.add_edge(a, b, {"type": "normal"}, '5f5f44ec7c0144e29c5b7d513f92d9ab')
    g.add_edge(a, c, {"type": "normal"}, '7eb91be54d3746b89a61a282bcc207bb')
    g.add_edge(b, c, {"type": "irregular"}, 'c172a3599b7d4ef3bbb688277276b763')
    return g

@pytest.fixture
def test_output():
    graph = sn.Graph()

    a = graph.add_node({"label" : "A"}, '6cf546f71efe47578f7a1400871ef6b8')
    b = graph.add_node({"label" : "B"}, 'bcb388bb24a74d978fa2006ed278b2fe')
    c = graph.add_node({"label" : "C"}, 'd6523f4f9d5240d2a92e341f4ca00a78')

    graph.add_edge(a, b, {"type" : "belongs"}, 'ff8a8a8093cf436aa3b0127c71ddc11d')
    graph.add_edge(b, c, {"type" : "owns"}, '081369f6197b467abe97b3efe8cc4640')
    graph.add_edge(c, a, {"type" : "has"}, 'b3a245098d5d482f893c6d63606c7e91')

    graph.save_json("test_output.json")

    with open("test_output.json") as f:
        jsonObj = json.load(f)

    return jsonObj

@pytest.fixture
def correct_output():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_output_correct.json")) as f:
        jsonObj = json.load(f)

    return jsonObj

@pytest.fixture
def correct_output_graph():
    g = sn.Graph()
    g.load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_output_correct.json"))
    return g

### TESTS ###
def test__create_uuid(graph):
    id_ = graph._create_uuid()
    assert id_.__class__.__name__ == 'UUID'

def test__extract_uuid(graph, uuid_str, uuid_obj):
    assert graph._extract_uuid(uuid_str) == uuid_obj

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
    with pytest.raises(sn.GraphException):
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

    with pytest.raises(sn.GraphException):
        graph.add_edge(a, '3caaa8c09148493dbdf02c57deadbeef')

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
    with pytest.raises(sn.GraphException):
        populated_graph.set_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'id',
            '5f5f44ec7c0144e29c5b7d51deadbeef')

    with pytest.raises(sn.GraphException):
        populated_graph.set_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'src',
            '3caaa8c09148493dbdf02c57deadbeef')

    with pytest.raises(sn.GraphException):
        populated_graph.set_edge_attribute('5f5f44ec7c0144e29c5b7d513f92d9ab', 'dst',
            '3caaa8c09148493dbdf02c57deadbeef')

def test_remove_edge(populated_graph):
    populated_graph.remove_edge('5f5f44ec7c0144e29c5b7d513f92d9ab')
    assert uuid.UUID('5f5f44ec7c0144e29c5b7d513f92d9ab') not in populated_graph.get_edges()
    with pytest.raises(sn.GraphException):
        populated_graph.remove_edge('5f5f44ec7c0144e29c5b7d51deadbeef')

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

def test_save_json(test_output, correct_output):
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

    os.remove("test_output.json")

def test_load_json(correct_output_graph):
    nodes = {
        uuid.UUID('6cf546f71efe47578f7a1400871ef6b8'): {'label': 'A'},
        uuid.UUID('bcb388bb24a74d978fa2006ed278b2fe'): {'label': 'B'},
        uuid.UUID('d6523f4f9d5240d2a92e341f4ca00a78'): {'label': 'C'}
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
