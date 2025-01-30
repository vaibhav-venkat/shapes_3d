# Objects

## The cube with spheres

### Calculation of the radii

There are 4 constants given: $\mu_{Ro}$, $\sigma_{Ro}$, $\mu_{Ri}$, $\sigma_{Ri}$
To calculate the log normal distribution, find the corresponding means and variance

$$
\sigma^2 = \log \left(1 + \frac{\sigma_R^2}{\mu_R^2}\right)
$$
$$
\mu = \log \left(\frac{\mu_R^2}{\sqrt{\mu_R^2 + \sigma_R^2}}\right)
$$

Then use numpy's `random` package to generate a log normal distribution:
`np.random.lognormal(mu, sigma)`

Calculate one radii randomly ($R_{outer}$) and set `N = R_outer.shape[0]` to
calculate both the inner radius and the centers

### Centers

There were 4 main methods for calculating the points such that they are at least
a distance $d = 2r$ apart. This is used to constrain the particles to not overlap.

#### Brute force: Highly inefficient

The brute force option was to check the distance by looping through all the points.

It used `np.any` along with `np.linalg.norm` to check if a certain
generated point is not overlapping

Due to its large operations and high rejection rate, this was very slow

#### KDTree

Using `scipy.spatial.KDTree`, a tree can be made to make
nearest particle searches faster.
Although it was faster than a brute force method, the tree had to be
rebuilt every time a new point was added.

The two main methods were:

#### Cell lists

By partitioning the grid into cells of at least $d$ units, we only
have to check the surrounding cells to calculate the distance.

This is way faster than the above methods. The specific outline
for how it works is [here](https://en.wikipedia.org/wiki/Cell_lists)

Although this is faster, there is one more option that still uses
the basic idea of Cell lists but is optimized for searches

#### Faiss with `IVFFlat`

The documentation for Faiss can be found on their [Github](facebookresearch/faiss)

By combining the process of clustering training and optimization, Faiss
is extremely fast.

The `IVFFLAT` model uses the same core principles as Cell lists, but allows
for training data and optimization to make it faster.

The training data is recommended to be `120 * sqrt(N)` to `4096 * sqrt(N)` of size

Thus, is clusters and finds the nearest neighbors efficiently


## Visualizing *.dump files

1. Download [Ovito](https://www.ovito.org/#download) for your specific OS
2. Simply open the dump file within the software
3. It should show the plots of all objects, as specified in the dump file
