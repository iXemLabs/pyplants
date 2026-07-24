Diseases
========

Even though from a black box perspective pant disease models appear similar, internally they are very different. Also the output produced by each model may differ significantly. In general, users should only take care of initialize the selected model and run it using its own data. The result of the computation is stored inside a python :code:`list` accessible using the :code:`events` property available for each model.

Models Output
-------------

Each time the :code:`update` method is invoked, and if the model is in its own running period (bbch range), a :code:`DiseaseEvent` is computed. This generic container hold the output parameters: the :code:`infection` field is used to predict infection risk, while the :code:`spore_release` field can be used, in case of fungal infection, to predict spore release (for example, ascospore in *powdery mildew* of the grape).

.. autoclass:: pyplants.diseases.common.DiseaseEvent
	:members:
	:member-order: bysource

Available Models
----------------

Plant disease models are separated in sub-modules, one for each crop. A further division is made by disease, where models belonging to the same disease are grouped together. Following, the list of the currently supported crops:

.. toctree::
   :maxdepth: 1

   diseases/grape
   diseases/generic

Infection Manager
-----------------

Some models are capable to keep track of primary infections incubation period. The :code:`InfectionManager` is a simple utility that serves to this purpose.

.. autoclass:: pyplants.diseases.common.InfectionManager
	:members:
	:member-order: bysource
