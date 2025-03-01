Uniform Ellipsoid
===================

This structure is generated using :ref:`the Ellipsoid class <ellipsoid-class>`

We use a similar method as defined in :ref:`the uniform sphere <uni-sphere>`

1. :math:`a` represents the radius of the ellipsoid on the :math:`x` axis
2. :math:`b` represents the radius of the ellipsoid on the :math:`y` axis
3. :math:`c` represents the ellipsoid radius on the :math:`z` axis
4. :math:`\rho` represents the density in points per unit volume

Rejection sampling with a cuboid
------------------------------------
Instead of a box with equal lengths, we use a cuboid of length :math:`a`, width :math:`b`, and height :math:`c`

Create a uniform distribution :math:`U_{c}` with :math:`N = \lfloor \rho V_{c} \rfloor = \lfloor a\cdot b\cdot c\cdot \rho \rfloor` points.
The points are created such that they are bounded by the cuboid :math:`\left[ -a, a \right] \times \left[ -b, b \right] \times \left[ -c, c \right]`

Then, let the ellipsoid :math:`U = \left\{(x, y, z) \in U_c \mid \frac{x^2}{a^2} + \frac{y^2}{b^2} + \frac{z^2}{c^2} \le 1 \right\}`

Example
----------

.. figure:: images/ellipsoid_obj_example.png
  :class: with-border

  Three examples of the uniform ellipsoid object, each with different densities

The left image is very dense, due to a high :math:`\rho`, while the right image contains loosely scattered points.

Official Schematic
-------------------
.. figure:: images/Ellipsoid.png
   
   The official design of the uniform ellipsoid

