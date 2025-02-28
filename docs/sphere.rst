===============
Uniform sphere
===============

This structure is generated using :ref:`the Ellipsoid class <ellipsoid-class>`

Box rejection sampling
-------------------------
1. :math:`R` represents the radius of the sphere
2. :math:`\rho` represents the density in points per unit volume

We can generate a uniform sphere by sampling a uniform distribution in the box around it.

First, we generate a uniform distribution of points within the box 
:math:`[-R, R]^3` with :math:`N = \lfloor (2R)^3\rho \rfloor = \lfloor 8R^3\rho \rfloor` points. 

Then we systematically reject points that are outside the cube, such that each point :math:`\vec{v} = (x, y, z)` in the distribution must satisfy 
:math:`\Vert \vec{v} \Vert \le R`

Because we rejected points of a uniform distribution outside a certain range, the new distribution is still uniform.



