semanticnet
============

semanticnet is a small python library to create semantic graphs in JSON.
Those created datasets can then be visualized with the 3D graph engine.

## A quick example
![A quick example](/ABC.png "A Quick Example")

To generate and save the graph represented by this image, you would write

```python
import semanticnet as sn

g = sn.Graph()

a = g.add_node({ "label" : "A" })
b = g.add_node({ "label" : "B" })
c = g.add_node({ "label" : "C" })

g.add_edge(a, b, { "type" : "belongs" })
g.add_edge(b, c, { "type" : "owns" })
g.add_edge(c, a, { "type" : "has" })

g.save_json("output.json")
```

which would save the graph to a file `output.json`, which could be used by
[OpenGraphiti](https://github.com/ThibaultReuille/graphiti).

There are several other example scripts included in this repo to demonstrate usage
of SemanticNet. Each example is documented in the wiki.

## JSON representation
When saving graph objects as JSON, the graph is represented internally as one might expect.
Suppose you have a graph G = (V, E), where

V = {0, 1, 2} and
E = {(0, 1), (0, 2), (1, 2)}

Suppose further that:

1. Vertex 0 has the attributes: `{"type": "A", "id": 0}`
2. Vertex 1 has the attributes: `{"type": "B", "id": 1}`
3. Vertex 2 has the attributes: `{"type": "C", "id": 2}`
4. Edge (0, 1) has the attributes: `{'src': 0, 'dst': 1, 'type': 'normal', 'id': 0}`
5. Edge (0, 2) has the attributes: `{'src': 0, 'dst': 2, 'type': 'normal', 'id': 1}`
6. Edge (1, 2) has the attributes: `{'src': 1, 'dst': 2, 'type': 'irregular', 'id': 1}`

then in JSON format, it would look like:

```json
{
 "timeline": [], 
 "nodes": [
  {
   "type": "A", 
   "id": 0
  }, 
  {
   "type": "B", 
   "id": 1
  }, 
  {
   "type": "C", 
   "id": 2
  }
 ], 
 "meta": {}, 
 "edges": [
  {
   "src": 0, 
   "dst": 1, 
   "type": "normal", 
   "id": 0
  }, 
  {
   "src": 0, 
   "dst": 2, 
   "type": "normal", 
   "id": 1
  }, 
  {
   "src": 1, 
   "dst": 2, 
   "type": "irregular", 
   "id": 2
  }
 ]
}
```

As you can see, there is a list of `"node"` objects, each of which contain the node's attributes and IDs,
as well as a list of `"edge"` objects, each of which have the edge's attributes, and the fields `"src"` and `"dst"`,
which indicate the source and destination vertices, respectively.

Without user definition, the `"id"` fields will default to randomly-generated
[UUIDs](http://en.wikipedia.org/wiki/Globally_unique_identifier),
although they can be any hashable type.

## Caching
Should you come across a use case where you'd like quick references to nodes or edges by more than just the ID,
semanticnet provides a mechanism to cache nodes and edges by any of their attributes. For example, suppose you make
the following graph:

```python
>>> g = sn.Graph()
>>> a = g.add_node({"type": "server"}, '3caaa8c09148493dbdf02c574b95526c')
>>> b = g.add_node({"type": "server"}, '2cdfebf3bf9547f19f0412ccdfbe03b7')
>>> c = g.add_node({"type": "client"}, '3cd197c2cf5e42dc9ccd0c2adcaf4bc2')
>>> g.add_edge(a, b, {"method": "GET", "port": 80}, '5f5f44ec7c0144e29c5b7d513f92d9ab')
UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab')
>>> g.add_edge(a, c, {"method": "GET", "port": 80}, '7eb91be54d3746b89a61a282bcc207bb')
UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb')
>>> g.add_edge(b, c, {"method": "POST", "port": 443}, 'c172a3599b7d4ef3bbb688277276b763')
UUID('c172a359-9b7d-4ef3-bbb6-88277276b763')
```

Suppose further that you want to access the nodes by their `"type"` attribute. You can tell semanticnet to
cache the nodes by the `"type"` attribute, and access them like so:

```python
>>> g.cache_nodes_by("type")
>>> g.get_nodes_by_attr("type")
{'client': [{'type': 'client', 'id': UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2')}], 'server': [{'type': 'server', 'id': UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7')}, {'type': 'server', 'id': UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c')}]}
```

Similarly, you could get a list of all connections by port:

```python
>>> g.cache_edges_by("port")
>>> g.get_edges_by_attr("port")
{80: [{'port': 80, 'src': UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'), 'dst': UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'), 'id': UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb'), 'method': 'GET'}, {'port': 80, 'src': UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'), 'dst': UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'), 'id': UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab'), 'method': 'GET'}], 443: [{'port': 443, 'src': UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'), 'dst': UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'), 'id': UUID('c172a359-9b7d-4ef3-bbb6-88277276b763'), 'method': 'POST'}]}
```

and you can specify the attribute value as well, to return the list of connections by, say, port 80:

```python
>>> g.get_edges_by_attr("port", 80)
[{'port': 80, 'src': UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'), 'dst': UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'), 'id': UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb'), 'method': 'GET'}, {'port': 80, 'src': UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'), 'dst': UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'), 'id': UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab'), 'method': 'GET'}]
```

The cache is managed automatically. Any time you add or remove a node/edge with an attribute that you are
caching, or modify an attribute of a node/edge, semanticnet updates the cache.

## Installation
```sh
$ git clone https://github.com/ThibaultReuille/semanticnet.git
$ cd semanticnet
$ ./setup.py install
```

### Tests
If you wish to run the test suite, it uses `py.test`. Install it with:

```sh
pip install pytest
```

and run the tests with:

```sh
py.test -v ./test
```
