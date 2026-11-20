Utility
=======

In this page some generic utility tools, useful to simplify models development and usage, are reported.

Models Usage
------------

Running multiple models togheter is a well know use case, therefore, to simplify to process by taking into acount different models, input data and timesteps, the following utilities are provided. 

.. autoclass:: pyplants.utils.helpers.DailyUpdater
	:members:
	:member-order: bysource

.. autoclass:: pyplants.utils.helpers.BulkUpdater
	:members:
	:member-order: bysource

Models Internals
----------------

Utilities used internally by models to perform computations.

.. autoclass:: pyplants.utils.helpers.LeafWetnessCounter
	:members:
	:member-order: bysource

.. autofunction:: pyplants.utils.vpd_h
.. autofunction:: pyplants.utils.gd_sum
.. autofunction:: pyplants.utils.equiv_temp
.. autofunction:: pyplants.utils.kdbeta
