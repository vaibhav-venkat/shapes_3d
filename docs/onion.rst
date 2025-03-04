.. _uni-onion:

Uniform onion
===============

This structure is generated using :ref:`the Onion class <onion-class>`

Constants
-----------
1. :math:`\mathbf{T}` is an array (vector) which contains the thickness (:math:`r_{outer}- r_{inner}`) of each shell, starting from the core. 
   The core's thickness is its radius
2. :math:`\mathbf{d}` is an array which contains the density of each shell

Multilayer shell rejection
-----------------------------
We use the :ref:`box rejection method <box-rejection>` but rather for each shell.

For each :math:`t_i \in \mathbf{T}`, the inner radius is :math:`r_{inner, i} = \sum_{n=0}^{i} t_n` (the sum of previous thicknesses) 
while the outer radius is :math:`r_{outer, i} = r_{inner, i} + t_i`. 

Now, generate a uniform box :math:`U_{box, i}` inside the bound :math:`[-r_{outer, i}, r_{outer, i}]^3`, with density :math:`d_i \in \mathbf{d}`

Instead of rejecting each point :math:`\mathbf{v} \in \mathbb{R}^3` inside :math:`U_{box, i}` with the previous method, 
reject the points such that we only keep :math:`\mathbf{v}` if :math:`r_{inner, i} \le \Vert \mathbf{v} \Vert \le r_{outer, i}`. 

Essentially, we are only keeping points within the given shell. This allows for multiple thicknesses and densities

Example
----------

.. figure:: images/onion_example.png
  :class: with-border

  Cross-section of three onions with a varying amount of thickness, densities, and shells

These images demonstrate how certain onions will look like based on their shell count. 
The cross section showcases their densities, which is similar to that of the :ref:`sphere <uni-sphere>`

Official Schematic
-------------------
.. figure:: images/Core-Corona-Spheroid.png
   
   The official design of the uniform onion

Here, R1 corresponds to :math:`t_0`, and R2 being :math:`t_0 + t_1`


