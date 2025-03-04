.. _uni-sphere:

===============
Uniform sphere
===============

This structure is generated using :ref:`the Ellipsoid class <ellipsoid-class>`

Constants
------------
1. :math:`R` represents the radius of the sphere
2. :math:`\rho` represents the density in points per unit volume

.. _box-rejection:

Box rejection sampling
-----------------------

We can generate a uniform sphere by sampling a uniform distribution in the box around it.

First, we generate a uniform distribution :math:`U_{box}` of points within the box 
:math:`[-R, R]^3` with :math:`N = \lfloor (2R)^3\rho \rfloor = \lfloor 8R^3\rho \rfloor` points. 

Then we systematically reject points that are outside the cube, such that each point :math:`\mathbf{v} = (x, y, z)` in the distribution must satisfy 
:math:`\Vert \mathbf{v} \Vert \le R`. The resulting collection :math:`U_{sphere}` is a uniform sphere in :math:`\mathbb{R}^3`.

Example
----------
.. figure:: images/Sphere_obj_example.png
   :class: with-border

   Three examples of uniform spheres, with different densities and radii.

The example above showcases different parameters used to generate these spheres.
The left image contains densely clustered points, while the right image contains scattered points.

Official Schematic
-------------------
.. figure:: images/Spheroid.png
   
   The official design of the uniform sphere

