Diseases
========

Each model is implemented as a python class that inherit from one of the possible base classes in :code:`pyplants.core.base`. To run a model, users should invoke the :code:`update` method passing a valid :class:`UpdateCtx <pyplants.core.context.UpdateCtx>` object. The private :code:`_update_imp` method should never be invoked in the client code.

Each model automatically check the presence of the input fields inside the update context, if a required field is left empty or set to :code:`None` an exception is raised. Results are stored inside the :code:`events` property, a list containing an entry for each time the method :code:`update` has been invoked.

.. autoclass:: pyplants.diseases.common.DiseaseEvent
	:members:
	:member-order: bysource

Included Models
---------------

Disease models are separated in sub-modules, one for each crop. A further division is made by disease, where models belonging to the same disease are grouped together. Following, the list of the currently supported crops:

.. toctree::
   :maxdepth: 1

   diseases/grape
   diseases/generic

Infection Manager
-----------------

Some models are capable to keep track of primary infections evolution over time. The :code:`InfectionManager` is a simple utility that serves to this purpose.

.. autoclass:: pyplants.diseases.common.InfectionManager
	:members:
	:member-order: bysource
