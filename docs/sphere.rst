.. _uni-sphere:

===============
Uniform sphere
===============


Structural features
----------------------
1. :math:`R` represents the radius of the sphere
2. :math:`\rho` represents the density of scatters in scatters (points) per unit volume.

Schematic
-------------------
.. figure:: images/Spheroid.png
   
   The official design of the uniform sphere

Structure Generation
----------------------

We can generate a uniform sphere by sampling a uniform distribution in the box around it, then rejecting certain scatters.

First, we generate a uniform distribution :math:`U_{box}` of scatters within the box containing the sphere,
:math:`[-R, R]^3`, with :math:`N = \lfloor (2R)^3\rho \rfloor = \lfloor 8R^3\rho \rfloor` points. 

Then we systematically reject scatters that are outside the cube, such that each vector (point) :math:`\mathbf{v} = (x, y, z)` 
in the distribution must satisfy :math:`\Vert \mathbf{v} \Vert \le R`. 
That is, if the condition is met, the vector will be added to a new collection :math:`U_{sphere}`.
The resulting collection, :math:`U_{sphere}`, is a uniform sphere in :math:`\mathbb{R}^3`.

Example
----------
.. figure:: images/Sphere_obj_example.png
   :class: with-border

   Three examples of uniform spheres, with different densities and radii.

The example above showcases different parameters used to generate these spheres.
The left image contains densely clustered scatters, while the right image contains spread out scatters.

This structure is generated using :ref:`the Ellipsoid class <ellipsoid-class>`
