Usage
=====

Installation
------------

Before using pyplants it is needed to install it. For the moment, if you have been provided with a source distribution (a *tar.gz* file), you can install it locally by using the following command:

.. code-block:: console

	(.venv) $ python -m pip install pyplants-x.y.z.tar.gz

Please change *x.y.z* with the provided package version. Alternatively, you can install pyplants in edit mode by running this command inside the root of the project:

.. code-block:: console

	(.venv) $ python -m pip install -e .

This method is suggested only if you are activly working to the package source code.

Contribute
----------

If you are working on the source code and you want to distribute it to other tester, you can build a source distribution in this way:

.. code-block:: console

	(.venv) $ python -m build --sdist

Of course you need a properly set python build environment.
