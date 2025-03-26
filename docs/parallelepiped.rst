Parallelepiped shells
=======================

Structural features
--------------------
1. We represent the length difference of each shell as an :math:`N\times3` 
   matrix :math:`\mathbf{L}`. Similar to the onion, each component of the matrix
   :math:`(x, y, z)` is the amount the object *extends* in the plane, rather
   than the actual length.

2. The density :math:`\rho` of the structure is represented in points per 
   unit volume.
3. :math:`\theta` represents the slant rotation in the :math:`xz` plane.
4. :math:`\phi` is the slant rotation in the :math:`yz` plane.


Schematic
----------

.. figure:: images/parra_scheme.png

   The design of a two-shelled parallelepiped. 




Shell-by-shell process
-----------------------
For any shell :math:`i`, we first obtain the maximum distance in the :math:`x, y, z` 
planes, which is **not** the length.
We treat each length as a vector. The inner length vector is
:math:`\mathbf{l}_{i,\text{inner}} = \sum_{j=0}^{i-1} L_j`, and the outer length 
vector :math:`\mathbf{l}_{i, \text{outer}} = L_i + \mathbf{l}_{i, \text{inner}}`


For the :math:`x` distance, this is simply the dot product 
:math:`x_{l, \text{outer}} = l_{x, \text{outer}} l_{z, \text{outer}} \cos \theta`,
which is analogous to the :math:`y` distance  
:math:`y_{l, \text{outer}} = l_{y, \text{outer}} l_{z, \text{outer}} \cos \phi`. 

The :math:`z` distance is affected by the slant angles, thus becoming 
:math:`z_{l, \text{outer}} = l_{z, \text{outer}} \sin \theta \sin \phi`

Finally, we define the inner length's distance.

.. math::
   x_{l, \text{inner}} = l_{x, \text{inner}} l_{z, \text{inner}} \cos \theta\\
   y_{l, \text{inner}} = l_{y, \text{inner}} l_{z, \text{inner}} \cos \phi\\
   z_{l, \text{inner}} = l_{z, \text{inner}} \sin \theta \sin \phi


We now generate 
:math:`n = \rho (x_{l, \text{outer}} y_{l, \text{outer}} z_{l, \text{outer}})`
points in a uniform range. 
