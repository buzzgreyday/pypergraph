Introduction
============

The :doc:`account package </pypergraph.account>` handles account functionalities such as key creation and storage, logging in and out, connecting to networks and Metagraphs, and transferring currency and data. This introductory section documents the ``DagAccount`` object, which holds account/wallet information and enables basic wallet functionalities.

This section documents the ``DagAccount`` class. The object is instantiated as follows:

.. code-block:: python

    from pypergraph import DagAccount

    account = DagAccount()

.. table::
   :widths: auto

   ===============  ===================  ======================================================================
   **Variable**     **Value**            **Description**
   ===============  ===================  ======================================================================
   network          DagTokenNetwork()    References the network configuration used to interact with APIs.
   _session_change  Subject()            RxPy emitter.
   key_trio         KeyTrio()            Pydantic model validates and stores
                                         ``private_key``, ``public_key``, and ``address`` after ``login(...)``.
   ===============  ===================  ======================================================================

-----

Network Configuration
---------------------

The ``network`` property references a ``DagTokenNetwork`` class. The ``DagAccount`` class allows for network reconfiguration to establish connections to different networks and Metagraphs. See :doc:`account network </account/account.network>` and :doc:`network configuration </network/network.configuration>` [missing link] for more in-depth documentation.

RxPy Emitter
------------

An event is emitted when the session changes upon invoking ``DagAccount().login(password="...")`` or ``DagAccount().logout()``. The event is a dictionary with the following structure:

.. table::
   :widths: auto

   =======  ============================
   **Key**  **Value**
   =======  ============================
   module   ``"account"``
   event    ``"login"`` or ``"logout"``
   =======  ============================

See also the ``Monitor`` [missing link].

Key Trio
--------

The ``KeyTrio`` class and related key methods are documented in the next section.