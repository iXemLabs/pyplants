Apple
=====

In this sub-package the disease models related to the apple plants are grouped. Currently, only one model for the scab is included.

Scab
----

The :code:`pyplants.diseases.apple.scab` module currently includes only the classic mills table. As any other model in this library, the infection risk computed using the mills table is normalized in a range [0,1], rather then using the classic categorical values.

==========  ========  =============  =========
Model       Timestep  Spore Release  Infection
==========  ========  =============  =========
Mills [1]_  Hourly    No             Yes
==========  ========  =============  =========

Following the models details.

.. autoclass:: pyplants.diseases.apple.scab.MillsRI
	:show-inheritance:
	:members:
	:member-order: bysource

.. rubric:: References

.. [1] Mills, W. D. (1944). Efficient use of sulfur dust and sprays during rain to control apple scab. NY State Agr. Expt. Sta., Ithaca. Ext. Bul, 630.