semantic-net
============

Semantic-Net is a small python library to create semantic graphs in JSON.
Those created datasets can then be visualized with the 3D graph engine.

## JSON representation
When saving graph objects as JSON, the graph is represented internally as one might expect.
Suppose you have a graph G = (V,E), where 

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

In actuality, the `"id"` fields will be [UUIDs](http://en.wikipedia.org/wiki/Globally_unique_identifier).

## Examples
### File system
To build a graph out of a portion of your file system, run the example script `fs_graph.py`:

```sh
./examples/fs_graph.py ~/src/python
```

This will build a tree out of your `~/src/python` folder save the file `fs.json` in your working directory.
(Obviously, you can change the argument path to any you would like to visualize; although, beware that if
it generates too many nodes, you will run into performance issues during the visualization).
Then, to run the visualizer with this data:

```sh
cd /path/to/Visualization/graphiti
./graphiti demo /path/to/semanticnet/fs.json
```

## Installation

### Dedpendencies
The only dependency is networkx

Either do: `pip install networkx`

or: `pip install -r ./requirements.txt`

### Installation
#### Set your `$PYTHONPATH`
Be sure your `$PYTHONPATH` environment variable is set to the folder you keep all your
python modules in.

e.g., if you keep your Python modules in `~/src/python`, do:

```sh
export PYTHONPATH=.:$HOME/src/python
```

and restart your shell.

#### Download/Install
```sh
cd /path/to/your/python/modules
git clone https://github.com/ThibaultReuille/semantic-net.git semanticnet
```

#### Tests
If you wish to run the test suite, it uses `py.test`. Install it with:

```sh
pip install pytest
```

and run the tests with:

```sh
py.test -v ./test/test_semanticnet.py
```
