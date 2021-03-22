{% if not obj.display %}
:orphan:

{% endif %}
{% if obj.name == "wa_simulator" %}
{{ "API Reference" }}
{% else %}
:mod:`{{ obj.name }}`
{% endif %}
======={{ "=" * obj.name|length }}

.. py:module:: {{ obj.name }}

{% block submodules %}
{% set visible_submodules = obj.submodules|selectattr("display")|list %}
{% set visible_subpackages = obj.subpackages|selectattr("display")|list %}
{% if visible_submodules %}
{% set core = ['base', 'core', 'utils', 'path', 'track', 'vehicle_inputs', 'system'] %}

.. toctree::
	:hidden:
	:titlesonly:
	:maxdepth: 3

	{% for subpackage in visible_subpackages %}
	{{ subpackage.short_name }}/index.rst

	{% endfor %}
	{% for submodule in visible_submodules %}
	{{ submodule.short_name }}/index.rst

	{% endfor %}

Core
----
{% if visible_subpackages %}
- :mod:`wa_simulator`
{% else %}
- :mod:`wa_simulator.chrono`
{% endif %}

{% for submodule in visible_submodules %}
{% if submodule.short_name in core %}
  - `{{ submodule.short_name|capitalize|replace("_inputs", "Inputs") }} <{{ submodule.short_name }}/index.html>`_
{% endif %}
{% endfor %}

.. raw::
  </br>

{% for subpackage in visible_subpackages %}

- :mod:`{{ subpackage.id }}`

{% for submodule in subpackage.submodules|selectattr("display")|list %}

{% if submodule.short_name in core %}
  - `{{ submodule.short_name|capitalize }} <{{ submodule.short_name }}/index.html>`_

{% endif %}
{% endfor %}

{% endfor %}



Components
----------

{% if visible_subpackages %}
- :mod:`wa_simulator`
{% else %}
- :mod:`wa_simulator.chrono`
{% endif %}

{% for submodule in visible_submodules %}
{% if submodule.short_name not in core %}
  - `{{ submodule.short_name|capitalize }} <{{ submodule.short_name }}/index.html>`_
{% endif %}
{% endfor %}

.. raw::
  </br>

{% for subpackage in visible_subpackages %}

- :mod:`{{ subpackage.id }}`

{% for submodule in subpackage.submodules|selectattr("display")|list %}

{% if submodule.short_name not in core %}
  - `{{ submodule.short_name|capitalize }} <{{ submodule.short_name }}/index.html>`_

{% endif %}
{% endfor %}

{% endfor %}

{% endif %}
{% endblock %}
{% block content %}
{% if obj.all is not none %}
{% set visible_children = obj.children|selectattr("short_name", "in", obj.all)|list %}
{% elif obj.type is equalto("package") %}
{% set visible_children = obj.children|selectattr("display")|list %}
{% else %}
{% set visible_children = obj.children|selectattr("display")|rejectattr("imported")|list %}
{% endif %}
{% if visible_children %}
.. {{ obj.type|title }} Contents
.. {{ "-" * obj.type|length }}---------

{% set visible_classes = visible_children|selectattr("type", "equalto", "class")|list %}
{% set visible_functions = visible_children|selectattr("type", "equalto", "function")|list %}
{% set visible_attributes = visible_children|selectattr("type", "equalto", "data")|list %}
{% if "show-module-summary" in autoapi_options and (visible_classes or visible_functions or visible_attributes) %}
{% block classes scoped %}
{% if visible_classes %}

.. raw:: html

   <h2>Classes</h2>

.. autoapisummary::
  :nosignatures:

{% for klass in visible_classes %}
  {{ klass.id }}
{% endfor %}

{% for obj_item in visible_children|selectattr("type", "equalto", "class")|list %}
{{ obj_item.render()|indent(0) }}
{% endfor %}

{% endif %}
{% endblock %}

{% block functions scoped %}
{% if visible_functions %}

.. raw:: html

   <h2>Methods</h2>

.. autoapisummary::
  :nosignatures:

{% for function in visible_functions %}
   {{ function.id }}
{% endfor %}

{% for obj_item in visible_children|selectattr("type", "equalto", "function")|list %}
{{ obj_item.render()|indent(0) }}
{% endfor %}

{% endif %}
{% endblock %}

{% block attributes scoped %}
{% if visible_attributes %}

.. raw:: html

   <h2>Attributes</h2>

.. autoapisummary::
  :nosignatures:

{% for attribute in visible_attributes %}
   {{ attribute.id }} 
   :annotation: = {{ attribute.value }}
{% endfor %}

{% for obj_item in visible_children|selectattr("type", "equalto", "data")|list %}
{{ obj_item.render()|indent(0) }}
{% endfor %}


{% endif %}
{% endblock %}
{% endif %}
{% endif %}
{% endblock %}

.. {% if obj.docstring %}
.. .. autoapi-nested-parse::
..
..    {{ obj.docstring|prepare_docstring|indent(3) }}
..
.. {% endif %}
