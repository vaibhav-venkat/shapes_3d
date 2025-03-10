A box with patchy onions
==================================

Structural features
----------------------
1. :math:`L` is the length of the box
2. :math:`\phi` is the volume fraction. :math:`\phi = \frac{\sum V_{i}}{L^3}`, :math:`V_i` is the volume of sphere :math:`i`
3. :math:`\mathbf{T_\mu}` is a vector that represents the mean thicknesses of each shell.
4. :math:`\mathbf{T_\sigma}` is an vectorthat represents the standard deviation of the thicknesses .
5. :math:`\mathbf{d}` is an vector that represents each shell's density of scatters. 
   Each density is represented in scatters (points) per unit volume.
6. :math:`\mathbf{Y}` is a vector representing the area of the patches. 
7. :math:`X` is the number of patches for each onion
8. :math:`\rho_\text{patch}` is the density of scatters for all patches, in scatters per unit area.


There are two parts to this, the actual onions, and the patches on each onion

Creating the onions
---------------------
We use the exact same method as we did with the :ref:`box with onions <box-onion>`, 
with the same structural features (and notation).

Creating the patches
---------------------
For each onion :math:`O`, we use the steps outlined in the :ref:`patchy onions <patchy-onion>`,
with the same structural features. The randomization in step 3 combined with the different distributions ensures
that all onions look different.


Examples
----------------

TODO: add examples

