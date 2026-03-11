.. pyplants documentation master file, created by
   sphinx-quickstart on Fri Jun 20 12:26:45 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyPlants
========

PyPlants is a collection of phenological and disease models for plants. Models in this package can be found in the scientific literature and are implemented in pure python.

Example
-------

This is an example of how to initialize a simple disease model for *powdery mildew*, and how to run it with some example data.

.. code-block:: python

   from pyplants.utils import UpdateCtx
   from pyplants.diseases.pm import Moyer

   model = Moyer()
   # Update the model with input data...
   model.update(dt, UpdateCtx(tmax=10, rain=0))
   # ...
   model.events

UpdateCtx is an utility class that contains the agrometeorological data. In general, once initialized, each model expose a common :code:`update` method that accept a :code:`datetime` object and the update context.

Each model expose an events list containing the output computed to each update.

.. topic:: Note

   For insight regarding each specific model, original papers are quoted in the documentation.

.. toctree::
   usage
   diseases
   phenology
   :hidden:
   :maxdepth: 2

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
