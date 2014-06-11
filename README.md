semantic-net
============

Semantic-Net is a small python library to create semantic graphs in JSON.
Those created datasets can then be visualized with the 3D graph engine.

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
