Parallelepiped shells
=======================

Structural features
--------------------
1. We represent the length difference of each shell as an :math:`N\times3` 
   matrix :math:`\mathbf{L}`. Similar to the onion model, each component 
   :math:`(x, y, z)` is the amount the object *extends* in the plane, rather
   than the actual length.

2. The density :math:`\mathbf{d}` of the structure is represented in points per 
   unit volume.
3. :math:`\theta` represents the slant rotation in the :math:`xz` plane, 
   :math:`\theta \in \left(0, \frac{\pi}{2}\right]`. 

4. :math:`\phi` is the slant rotation in the :math:`yz` plane.
   :math:`\phi \in \left(0, \frac{\pi}{2}\right]`
5. :math:`\theta = \phi = \frac{\pi}{2}` corresponds to a cuboid.


Schematic
----------

.. figure:: images/parra_scheme.png

   The design of a two-shelled parallelepiped. 

Iterative nature
-----------------
The generation follows an iterative process, where we
generate each shell sequentially. The combination of all these points
forms the final structure.


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


We use a rejection method, where we generate the points in the cuboid surrounding
the parallelepiped, then keep the points inside the parallelepiped's range.

We generate 
:math:`n = d_i V_{\text{outer}} = \rho(x_{\text{outer}}y_{\text{outer}}z_{\text{outer}})`
points in the uniform range. Recall that :math:`d_i` is the current density. That is:

.. math::
   \mathbf{U}_{x, \text{box}} \sim \text{Uniform} (\frac{-x_{l, \text{outer}}}{2}, \frac{x_{l, \text{outer}}}{2})\\
   \mathbf{U}_{y, \text{box}} \sim \text{Uniform} (\frac{-y_{l, \text{outer}}}{2}, \frac{y_{l, \text{outer}}}{2})\\
   \mathbf{U}_{z, \text{box}} \sim \text{Uniform} (\frac{-z_{l, \text{outer}}}{2}, \frac{z_{l, \text{outer}}}{2})


We apply the first restrictions (to keep within the parallelepiped's range), which 
are as follows:

.. math::
   \mathbf{U}_1 = \left\{ (x, y, z) \in \mathbf{U}_\text{box} \, \middle| \, \begin{array}{l}
    0 \le  x - \frac{z}{\tan \theta} \le x_{l, \text{outer}}\\
    0 \le  y - \frac{z}{\tan \phi} \le y_{l, \text{outer}}\\
    |z| \le \frac{z_{l, \text{outer}}}{2}
    \end{array} \right\}

To apply the second restrictions to keep the points outside the *inner* thickness,
we apply similar restrictions, exchanging the outer lengths with the inner lengths. 
We instead **reject** any points that fall within
the inner range.

The resulting points will form the shell :math:`U_{i, \text{shell}}`

Example
===========

.. figure:: images/parall_example.png
  :class: with-border

  Cross sections and 3d images for a parallelepiped with changing slant angles. On the 
  left, there is a cross section of the :math:`yz`-plane showcasing :math:`\phi`. The 
  center image shows a complete parallelepiped with the same :math:`\theta` and :math:`\phi`.
  The right image shows a cross section of the :math:`xz` plane showcasing the :math:`\theta` angle.

These images demonstrate how parallelepiped objects respond to the slant angle, with cross sections 
being used. The image on the right is more slanted than the left, despite :math:`\phi_\text{left} = \theta_\text{right}`,
because of the larger :math:`x` length. The density and lengths are constant throughout the example.
