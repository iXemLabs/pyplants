Diseases
========

Each model is implemented as a python class that inherit from one of the possible base classes in :code:`pyplants.core.base`. To run the model users should invoke the :code:`update` method passing a valid :class:`UpdateCtx <pyplants.core.context.UpdateCtx>` object. It is worth to say that internal :code:`_update_imp` should never be invoked in the client code.

Each model automatically check the presence of the input fields inside the update context, if a required field is left empty or set to :code:`None` an exception is raised. Results are stored inside the :code:`events` property, a list containing an entry for each time the method :code:`update` has been invoked.

Disease models are separated in sub-modules, one for each crop. A further division is made by disease, where models belonging to the same disease are grouped together. This is the list of the currently supported crops:

.. toctree::
   :maxdepth: 1

   diseases/grape

Model output
------------

Disease models create a list of :code:`DiseaseEvent` objects. A disease event includes a reference date, a :code:`spore_release` index and an :code:`infection` index, both expressed as float. Additional fields are supported using the (:code:`extra_fields`) attribute, stored a simple python dictionary.

.. autoclass:: pyplants.diseases.common.DiseaseEvent
	:members:
	:member-order: bysource

Infection Manager
-----------------

Some models are capable to keep track of primary infections evolution, for this purpose the :code:`InfectionManager` can be used.

.. autoclass:: pyplants.diseases.common.InfectionManager
	:members:
	:member-order: bysource
