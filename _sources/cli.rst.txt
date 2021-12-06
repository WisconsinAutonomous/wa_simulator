######################
Command Line Interface
######################

The :code:`wa_simulator` command line interface is another entrypoint for running simulations. Think of it as a tool to make your life easier.

When you install :code:`wa_simulator`, the :code:`wasim` cli is automatically configured. See :doc:`installation/index` for information on how to install :code:`wa_simulator`.

:code:`wasim`
=============

The root entrypoint for the :code:`wa_simulator` CLI is :code:`wasim`. This the first command you need to access the CLI. All subsequent subcommands succeed :code:`wasim`.

Subcommands
===========

Subcommands immediately succeed the :code:`wasim` command. They implement additional logic. Having subcommands rather than arguments directly to :code:`wasim` increases expandability as it will allow for additional features to be implemented without convoluting the help menu of the base :code:`wasim` command.

:code:`docker`
---------------

.. autosimple:: wa_simulator.cli.docker.init

.. raw:: html

  <style>
    h4 {text-transform: lowercase;}
  </style>

:code:`docker start`
"""""""""""""""""""

.. autosimple:: wa_simulator.cli.docker.run_start
