import json
import os
import pytest
import semanticnet as sn
import uuid

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
def populated_digraph():
    g = sn.DiGraph()
    a = g.add_node({"type": "A"}, '3caaa8c09148493dbdf02c574b95526c')
    b = g.add_node({"type": "B"}, '2cdfebf3bf9547f19f0412ccdfbe03b7')
    c = g.add_node({"type": "C"}, '3cd197c2cf5e42dc9ccd0c2adcaf4bc2')
    g.add_edge(a, b, {"type": "normal"}, '5f5f44ec7c0144e29c5b7d513f92d9ab')
    g.add_edge(b, a, {"type": "normal"}, 'f3674fcc691848ebbd478b1bfb3e84c3')
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
