Phenology
=========

Phenological models are used to predict growth stage of the crop. In literature many models exists, but for  the moment, in this package, only one is implemented.

In general, every phenological model in pyplants will use the BBCH scale as a common way to keep track of phenology. BBCH is composed by two scales that must always be reported:

- Vegetative
- Reproductive

The vegetative and reproductive scales may occasionally overlap, for this reason phenology results are stored separately for both the scale.

BBCH Scale
----------

In general users should not use directly the *BBCH* utilities, phenological models should handle them automatically. But if you want to develop your own model this simple implementation can be useful. Disease models that requires phenology data to run expect that phenology model expose data using the BBCHScale class.  

.. autoclass:: pyplants.phenology.scales.BBCHScale
	:members:
	:member-order: bysource

.. autoclass:: pyplants.phenology.scales.BBCHStage
	:members:
	:member-order: bysource

Iphen
-----

This model implementation currently supports only grape plants.

.. autoclass:: pyplants.phenology.iphen.Iphen
	:show-inheritance:
	:members:
	:member-order: bysource
	:class-doc-from: both

.. autoclass:: pyplants.phenology.base.BasePhenology
	:members:
	:member-order: bysource

.. rubric:: References

.. [1] Mariani, L., Alilla, R., Cola, G., Monte, G. D., Epifani, C., Puppi, G., & Osvaldo, F. (2013). IPHEN—a real-time network for phenological monitoring and modelling in Italy. International journal of biometeorology, 57(6), 881-893.

.. [2] Wang, E., & Engel, T. (1998). Simulation of phenological development of wheat crops. Agricultural systems, 58(1), 1-24.