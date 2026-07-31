Generic Tools
=============

By applying the proper parameters, generic models can be used on different pairs of crops and diseases.

Magarey Model
-------------

A generic implementation of the Magarey model [1]_, used to compute the amount of required leaf wetness hours for a disease to cause an infection.

.. autoclass:: pyplants.diseases.common.GenericMagarey
	:members:
	:member-order: bysource

Mills Table
-----------

A generic implementation of the Mills table [2]_. Users can initialize one of the built-in table provided, or create a custom one.

.. autoclass:: pyplants.utils.mills.MillsTable
	:members:
	:member-order: bysource

.. autoclass:: pyplants.utils.mills.MillsRisk
	:members:
	:member-order: bysource


.. rubric:: References

.. [1] Magarey, R. D., Sutton, T. B., & Thayer, C. L. (2005). A simple generic infection model for foliar fungal plant pathogens. Phytopathology, 95(1), 92-100.
.. [2] Mills, W. D. (1944). Efficient use of sulfur dust and sprays during rain to control apple scab. NY State Agr. Expt. Sta., Ithaca. Ext. Bul, 630.