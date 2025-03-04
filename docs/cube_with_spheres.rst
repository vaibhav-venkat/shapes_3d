A Box with uniform spheres
===========================

Note that we generate each outer and inner radius on a log-normal distribution

Constants
------------
1. :math:`L` represents the length of the box
2. :math:`R_{\mu}` represents the mean outer radius
3. :math:`R_{\sigma}` represents the outer radius standard deviation
4. :math:`r_{\mu}` represents the mean inner radius
5. :math:`r_{\sigma}` represents the inner radius standard deviation
6. :math:`\phi` represents the volume fraction. This is the ratio of the volume of the spheres to the volume of the box
7. :math:`\rho_{o}` represents the density of the outer shell
8. :math:`\rho_i` represents the density of the inner core


Converting the shell to thickness
----------------------------------
When generating the log-normal distribution, there are cases where the outer radius :math:`R` is less than the inner radius :math:`r`.

One fix is to change the :math:`R_{\mu}` and :math:`R_{\sigma}` to a corresponding thickeness mean and standard deviation 
:math:`T_\mu` and :math:`T_\sigma`. To accurately represent the thickness, 
let :math:`T_\mu = R_\mu - r_\mu` and :math:`T_\sigma = \sqrt{R_\sigma ^ 2 - r_\sigma ^ 2}`

The distribution of radii
--------------------------

First, we convert the means and standard deviations to be compatible with the log normal distribution.

First, create the new standard distribution's 

.. math::
  \sigma_T = \sqrt{\ln \left(1 + \frac{T_\sigma ^ 2}{T_\mu ^ 2} \right)} 

  \sigma_r = \sqrt{\ln \left(1 + \frac{r_\sigma ^ 2}{r_\mu ^ 2} \right)} 

Then, create the new means, 

.. math::
  \mu_T = \ln(T_\mu) - \frac{\sigma_T^2}{2}

  \mu_r = \ln(r_\mu) - \frac{\sigma_r^2}{2}

Next, we will create the outer radii :math:`\mathbf{R}` and the inner radii :math:`\mathbf{r}`.

We systematically choose each outer and inner radii such that the total volume of the spheres (with the radius being the outer radius)
not exceeding :math:`\phi L^3`

In :math:`\mathbf{r}`, each element is chosen with the log-normal distribution of :math:`\mu_r` and :math:`\sigma_r`, with one point chosen at a time.

Similarly, for :math:`\mathbf{R}`, we generate the thickness with the log-normal distribution of 
:math:`\mu_T` and :math:`\sigma_T`, then add it to each inner radius.

We continue doing this until the sum of all outer radii :math:`\sum R_i` exceeds :math:`\phi L^3`.

We will commonly refer to the total number of radii (and thus spheres) as :math:`N`

Generating the centers
-------------------------
In order to avoid errors in scattering, we use a brute force method to generate the centers such that no two points are closer than :math:`2 R_{max}`.
That is, any two points within the list of centers :math:`\mathbf{C}`, :math:`\vec{c_i}` and :math:`\vec{c_j}` must be placed 
such that :math:`\Vert \vec{c_j} - \vec{c_i} \Vert \ge 2 \max(\mathbf{R})`

This prevents any overlapping

Generating each sphere
-----------------------


We now generate the final structure :math:`S`.
For every center :math:`c_i` generate a :ref:`uniform onion <uni-onion>`, with thicknesses :math:`(r_i, R_i)`, then displace it by :math:`c_i`. 
We then add this as an element to :math:`S`.






