Installation
============

Prerequisites
-------------

* Python 3.9+
* Django 3.2+
* Django REST Framework 3.12+

Package Installation
--------------------

Install the package using pip:

.. code-block:: bash

   pip install drf-shapeless-serializers

Django Configuration
--------------------

Add the package to your ``INSTALLED_APPS``:

.. code-block:: python

   INSTALLED_APPS = [
       # ... other apps
       'shapeless_serializers',
   ]

Upgrading
---------

To upgrade to the latest version:

.. code-block:: bash

   pip install --upgrade drf-shapeless-serializers