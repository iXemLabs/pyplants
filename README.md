# PyPlants

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://github.com/iXemLabs/pyplants/actions/workflows/tests.yml/badge.svg)](https://github.com/iXemLabs/pyplants/actions/workflows/tests.yml)
[![Documentation](https://app.readthedocs.org/projects/pyplants/badge/?version=latest)](https://pyplants.readthedocs.io/latest/)

PyPlants is a collection of disease and phenological models for plants. The main purpose of this library is to enable both developers and researchers to use models described in the scientific literature.

### Installation

PyPlants is available on PyPI and can be installed as follow:

```console
$ python -m pip install pyplants
```

As for now, we support Python 3.8+.

### Usage

The package is subdivided in two main sub-packages, `pyplants.phenology` and `pyplants.diseases`. In general, each model implements its own logic that can be invoked with the `update` method. Models accept in input an `UpdateCtx` object, which collect classic agrometeorological parameters.

```python
>>> from datetime import datetime
>>> from pyplants.core.context import UpdateCtx
>>> from pyplants.diseases.grape.pm import Moyer

>>> model = Moyer()
>>> uctx = UpdateCtx(dt=datetime(2026, 1, 1, 0, 0), tmax=5, rain=0, step="d")
>>> model.update(uctx)
>>> # You call update when a new update context is available
>>> # The output of the model is stored inside the events property
>>> model.events[0]
DiseaseEvent(
  dt=datetime.datetime(2026, 1, 1, 0, 0),
  spore_release=0.0,
  infection=None,
  extra_fields={'asc_p': 0.035371388525063274})
```

### Documentation

Full documentation is available at: [ReadTheDocs](https://pyplants.readthedocs.io/latest/)

Enjoy.
