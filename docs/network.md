# A "network""-like structure

The structure consists of a system of spheres (nodes) which are
attached to each other via cylinders (branches).

## Model definition

### Structural features

1. $\mu_r$: Mean radius of each node
2. $\sigma_r$: Standard deviation of each node
3. $N$: Number of nodes
4. $L_\text{box}$: The total length of the bounding box (encapsulating cube)
5. $\mu_{l}$: Mean branch length
6. $\sigma_{l}$: The standard deviation of the length of each branch
7. $M$: Number of branches per node
8. $R_c$ is the radius of each branch/cylinder
9. $\rho$ is the density of the scatters in points per unit volume

### [1] The components of the system

The core system is extremely similar to the graph data structure.

#### Nodes

The vertices of the graph, a.k.a the core components. Let this set of vertices be
$\mathbf{V} = (v_0, v_1, \dots, v_{N-1})$. Each vertex is a sphere in $\mathbb{R}^3$ with
center $p_i = (x_i, y_i, z_i)$ and radius $r_i$, whose creation will
be discussed further down.

#### Branches

These are the edges of the graph, $\mathbf{E}$, with each edge $e_k = (v_i, v_j)$
connects two nodes. Branch $k$ has a desired length of $l_k$. Let there be $B$ branches
total, which is derived from $N$ and $M$.

#### Generating the lengths and radii

The lengths (branches) and radii (nodes) are formed by a log-normal distribution
with values $\mu_l$, $\sigma_l$ and $\mu_r$, $\sigma_r$ respectively. For more
information on this, see previous pages ("distribution of x").

#### Optimization/Simulation parameters

* $I$: The number of iterations of the simulation.
* $S_\text{repel}$: The repulsion strength multiplier of each node.
* $k_{lr}$: The "learning rate" of the simulation. If its lower, its more precise
but requires more iterations.

### [2] The Goal

The goal is to form a system of nodes and branches that do not overlap and have desired
length and key features. Thus, we seek to minimize an energy function $U_{\text{sys}}$,
aiming for an equilibrium state.

$$ U_\text{sys} = U_\text{spring} + U_\text{repel} $$

#### Spring potential energy: $U_\text{spring}$

The Spring potential energy is modeled by Hooke's Law, and sums over all branches.
The key here is to imagine each branch as a spring, with its relaxed length
being $l_k$. Until the very end of the simulation, these branches don't exist,
instead they are modeled between the two node components, as discussed,
forming $e_k$. The formal definition is as follows:

$$ U_\text{spring} = \sum \frac{1}{2} k_{lr} \left(\Vert p_j - p_i \Vert - l_k\right)^2$$

Which sums over all edges $e_k = (v_i, v_j)$

#### Repulsion energy

The repulsion energy tries to mitigate the chance of overlap between objects.
It does this by applying a force to objects that are intersecting, proportional
to the overlap amount.

First, define a function $f(d, d_\text{min})$ which calculates the repulsion force
from the distance between objects, and the minimum allowed.

$$ f(d, d_\text{min}) = k_{lr} S_\text{repel} | d - d_\text{min} | $$

$f$ grows rapidly as $d \to 0$.

$U_\text{repel}$ itself is formed of three main
components.

$$ U_\text{repel} = U_{nn} + U_{nb} + U_{bb} $$

* Node-Node repulsion: $U_{nn} = \sum f(d(p_i, p_j), r_i + r_j)$
* Node-Branch repulsion: $U_{nb} = \sum f(d(p_i, e_k), r_i + R_c)$
* Branch-Branch repulsion $U_{bb} = \sum f(d(e_k, e_i), 2R_c)$

The distance function $d(a, b)$ will be discussed in section 4
