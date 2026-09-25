# PyPlants

[![Tests](https://github.com/iXemLabs/pyplants/actions/workflows/tests.yml/badge.svg)](https://github.com/iXemLabs/pyplants/actions/workflows/tests.yml)
[![Documentation](https://app.readthedocs.org/projects/pyplants/badge/?version=latest)](https://pyplants.readthedocs.io/latest/)
[![Elsevier Paper](https://img.shields.io/badge/DOI-10.1016%2Fj.softx.2026.103062-blue)](https://doi.org/10.1016/j.softx.2026.103062)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

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

### Citation

If you use this package in your research, please consider citing the original publication.

```
@article{PyPlants2026,
  title = {PyPlants: an open-source python package implementing disease and phenological models for plants},
  journal = {SoftwareX},
  volume = {36},
  pages = {103062},
  year = {2026},
  issn = {2352-7110},
  doi = {https://doi.org/10.1016/j.softx.2026.103062},
  url = {https://www.sciencedirect.com/science/article/pii/S2352711026005534},
  author = {Giovanni Paolo Colucci and Irene Salotti and Paola Battilani and Daniele Trinchero}
}
```

Enjoy.