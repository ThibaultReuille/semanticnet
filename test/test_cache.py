import pytest
import uuid

def test_cache_nodes_by(populated_graph):
    # add another node with the same type to make sure it works for multiple nodes
    # with the same attribute
    populated_graph.add_node({"type": "A"}, '2b673235a0b94935ab8b6b9de178d341')

    # cache by the attribute "type"
    populated_graph.cache_nodes_by("type")

    in_cache = populated_graph._node_cache
    out_cache = {
        "type": {
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
    }
    assert in_cache == out_cache

    # calling cache_nodes_by() more than once on the same attribute should be ignored
    populated_graph.cache_nodes_by("type")
    in_cache = populated_graph._node_cache
    assert in_cache == out_cache


def test_cache_edges_by(populated_graph):
    populated_graph.cache_edges_by("type")

    assert (
        populated_graph._edge_cache ==
        {
            "type": {
                "normal": [
                    {
                        'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
                        'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
                        'type': 'normal',
                        'id': uuid.UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb')
                    },
                    {
                        'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
                        'dst': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
                        'type': 'normal',
                        'id': uuid.UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab')
                    }
                ],
                "irregular":[
                    {
                        'src': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
                        'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
                        'type': 'irregular',
                        'id': uuid.UUID('c172a359-9b7d-4ef3-bbb6-88277276b763')
                    }
                ]
            }
        }
    )

def test_get_edges_by_attr(populated_graph):
    populated_graph.cache_edges_by("type")

    type_edges = populated_graph.get_edges_by_attr("type")
    correct_output = {
        "normal": [
            {
                'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
                'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
                'type': 'normal',
                'id': uuid.UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb')
            },
            {
                'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
                'dst': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
                'type': 'normal',
                'id': uuid.UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab')
            }
        ],
        "irregular":[
            {
                'src': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
                'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
                'type': 'irregular',
                'id': uuid.UUID('c172a359-9b7d-4ef3-bbb6-88277276b763')
            }
        ]
    }
    assert type_edges == correct_output

    normal_edges = populated_graph.get_edges_by_attr("type", "normal")
    correct_output = [
        {
            'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
            'type': 'normal',
            'id': uuid.UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb')
        },
        {
            'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
            'dst': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
            'type': 'normal',
            'id': uuid.UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab')
        }
    ]
    assert normal_edges == correct_output

    irregular_edges = populated_graph.get_edges_by_attr("type", "irregular")
    correct_output = [
        {
            'src': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
            'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
            'type': 'irregular',
            'id': uuid.UUID('c172a359-9b7d-4ef3-bbb6-88277276b763')
        }
    ]
    assert irregular_edges == correct_output

    # should return a single item, rather than a singleton list
    irregular_edges = populated_graph.get_edges_by_attr("type", "irregular", nosingleton=True)
    correct_output = {
        'src': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
        'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
        'type': 'irregular',
        'id': uuid.UUID('c172a359-9b7d-4ef3-bbb6-88277276b763')
    }
    assert irregular_edges == correct_output

def test_cache_edges_by_build_false(populated_graph):
    populated_graph.cache_edges_by("type", build=False)

    assert (
        populated_graph._edge_cache ==
        {
            "type": {}
        }
    )

def test_add_edge_with_cache(populated_graph):
    test_cache_edges_by(populated_graph) # builds the cache

    populated_graph.add_edge('3caaa8c09148493dbdf02c574b95526c', '2cdfebf3bf9547f19f0412ccdfbe03b7',
        {"type": "irregular"}, 'c332692fcce54ea2ae85ece6788f7f05')

    assert (
        populated_graph._edge_cache ==
        {
            "type": {
                "normal": [
                    {
                        'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
                        'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
                        'type': 'normal',
                        'id': uuid.UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb')
                    },
                    {
                        'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
                        'dst': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
                        'type': 'normal',
                        'id': uuid.UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab')
                    }
                ],
                "irregular":[
                    {
                        'src': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
                        'dst': uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
                        'type': 'irregular',
                        'id': uuid.UUID('c172a359-9b7d-4ef3-bbb6-88277276b763')
                    },
                    {
                        'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
                        'dst': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
                        'type': 'irregular',
                        'id': uuid.UUID('c332692fcce54ea2ae85ece6788f7f05')
                    }
                ]
            }
        }
    )

    # add an edge with an attribute we are not tracking
    # should NOT be in the cache
    populated_graph.add_edge('2cdfebf3bf9547f19f0412ccdfbe03b7', '3cd197c2cf5e42dc9ccd0c2adcaf4bc2',
        {"label": "test"}, 'a0d5f731322e428ca1549296ad1c5f66')

    assert "label" not in populated_graph._edge_cache

def test_cache_by_build_false(populated_graph):
    populated_graph.cache_nodes_by("type", build=False)

    assert (
        populated_graph._node_cache ==
        {
            "type": {}
        }
    )

def test_clear_node_cache(populated_graph):
    # add a node with a different attribute
    populated_graph.add_node(
        {"label": "test"},
        '13624b67282444cb9e038ccd8038e644'
    )

    populated_graph.cache_nodes_by("type")
    populated_graph.cache_nodes_by("label")
    print("node_cache: {}".format(populated_graph._node_cache))
    assert populated_graph._node_cache["type"] # cache is not empty
    assert populated_graph._node_cache["label"] # cache is not empty

    populated_graph.clear_node_cache('type')
    assert not populated_graph._node_cache["type"] # cache IS empty
    assert populated_graph._node_cache["label"] # cache is not empty

    populated_graph.clear_node_cache()
    assert not populated_graph._node_cache # entire cache is gone

def test_add_node_with_cache(populated_graph):
    populated_graph.cache_nodes_by("type")

    ### get all nodes with attr "type"
    input_ = populated_graph.get_nodes_by_attr("type")
    output = {
        "A": [
            {
                "id": uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
                "type": "A"
            }
        ],
        "B": [{
            "id": uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
            'type': 'B'
        }],
        "C": [{
            "id": uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
            'type': 'C'
        }]
    }

    assert input_ == output

    # Add a new node of the same type as another. Should be in the cache.
    populated_graph.add_node({"type": "A"}, '2b673235a0b94935ab8b6b9de178d341')
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

    # add a new node with an attribute that we are not caching.
    # Should NOT be in the cache
    populated_graph.add_node({"label": "test"}, 'fa02d5e82ed54baf828558c70317f20e')
    input_ = populated_graph._node_cache
    output = {
        "type": {
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
            "B": [{
                "id": uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
                'type': 'B'
            }],
            "C": [{
                "id": uuid.UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'),
                'type': 'C'
            }]
        }
    }

    assert input_ == output

def test_set_node_attribute_with_cache(populated_graph):
    populated_graph.cache_nodes_by("type")
    populated_graph.set_node_attribute('3caaa8c09148493dbdf02c574b95526c', 'type', 'B')

    a_nodes = populated_graph.get_nodes_by_attr("type", "A")
    b_nodes = populated_graph.get_nodes_by_attr("type", "B")

    node_a = populated_graph.get_node('3caaa8c09148493dbdf02c574b95526c')

    assert node_a not in a_nodes
    assert node_a in b_nodes

def test_set_edge_attribute_with_cache(populated_graph):
    populated_graph.cache_edges_by("type")
    populated_graph.set_edge_attribute('7eb91be54d3746b89a61a282bcc207bb',
        'type', 'irregular')

    normal_edges = populated_graph.get_edges_by_attr("type", "normal")
    irregular_edges = populated_graph.get_edges_by_attr("type", "irregular")

    edge_a_b = populated_graph.get_edge('5f5f44ec7c0144e29c5b7d513f92d9ab')
    edge_a_c = populated_graph.get_edge('7eb91be54d3746b89a61a282bcc207bb')

    assert edge_a_b in normal_edges
    assert edge_a_c not in normal_edges
    assert edge_a_c in irregular_edges

def test_remove_node_with_cache(populated_graph):
    populated_graph.add_node({"type": "A"}, '2b673235a0b94935ab8b6b9de178d341')
    populated_graph.cache_nodes_by("type")
    populated_graph.remove_node('3caaa8c09148493dbdf02c574b95526c')

    input_ = populated_graph.get_nodes_by_attr("type", "A")
    output = [{
        "id": uuid.UUID('2b673235a0b94935ab8b6b9de178d341'),
        "type": "A"
    }]

    assert input_ == output

def test_remove_edge_with_cache(populated_graph):
    populated_graph.cache_edges_by("type")

    populated_graph.add_edge('3caaa8c09148493dbdf02c574b95526c', '2cdfebf3bf9547f19f0412ccdfbe03b7',
        {"type": "irregular"}, 'c332692fcce54ea2ae85ece6788f7f05')

    populated_graph.remove_edge('c172a359-9b7d-4ef3-bbb6-88277276b763')

    assert (
        populated_graph.get_edges_by_attr("type", "irregular") ==
        [
            {
                'src': uuid.UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'),
                'dst': uuid.UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'),
                'type': 'irregular',
                'id': uuid.UUID('c332692fcce54ea2ae85ece6788f7f05')
            }
        ]
    )
