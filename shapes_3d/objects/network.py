import numpy as np

from shapes_3d.modules.cylinder import Cylinder
from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import create_network_graph, save_dump

RADIUS_MEAN = 6.0
RADIUS_STD = 0.5
NODE_AMOUNT = 3
BOX_LENGTH = 200
BRANCH_LENGTH_MEAN = 30.0
BRANCH_LENGTH_STD = 0.0
AMOUNT_PER_NODE = 2
branch_amount = NODE_AMOUNT
CYLINDER_RADIUS = 3.0
DENSITY = 0.4


radius_deviation_log: np.ndarray = np.sqrt(np.log(1 + (RADIUS_STD / RADIUS_MEAN) ** 2))
radius_mean_log: np.ndarray = np.log(RADIUS_MEAN) - radius_deviation_log**2 / 2

branch_length_deviation_log: np.ndarray = np.sqrt(
    np.log(1 + (BRANCH_LENGTH_STD / BRANCH_LENGTH_MEAN) ** 2)
)
branch_length_mean_log: np.ndarray = (
    np.log(BRANCH_LENGTH_MEAN) - branch_length_deviation_log**2 / 2
)


radii: np.ndarray = np.random.lognormal(
    radius_mean_log, radius_deviation_log, NODE_AMOUNT
)

length: np.ndarray = np.random.lognormal(
    branch_length_mean_log, branch_length_deviation_log, branch_amount
)

# (x_a, y_a, z_a, R, polar, azimuthal)
centers_nodes: np.ndarray = np.zeros((NODE_AMOUNT, 7))
centers_branches: np.ndarray = np.zeros((branch_amount, 6))
angles_branches: np.ndarray = np.zeros((branch_amount, 2))


graph = create_network_graph(NODE_AMOUNT, AMOUNT_PER_NODE)

visited: np.ndarray = np.full(NODE_AMOUNT, False)
visited[0] = True
if graph is None:
    print("error when creating graph")
    exit(1)

branch_count: int = 0


def get_intersection_circle_point_spherical(t, R1, R2, c1, c2):
    """
    Calculates the spherical coordinates of a point on the intersection circle of two spheres.

    The spherical coordinates (rho, theta, phi) are relative to the center of the first sphere (c1).

    Args:
        t (float): The parametric variable, typically in the range [0, 2*pi],
                   which defines the position on the circle.
        R1 (float): Radius of the first sphere.
        R2 (float): Radius of the second sphere.
        c1 (np.ndarray): A 3-element numpy array for the center of the first sphere (x1, y1, z1).
        c2 (np.ndarray): A 3-element numpy array for the center of the second sphere (x2, y2, z2).

    Returns:
        tuple: A tuple (rho, theta, phi) representing the spherical coordinates
               of the point on the circle with respect to c1.
               - rho: Radial distance (will always be R1).
               - theta: Polar angle (from the Z-axis, in radians, [0, pi]).
               - phi: Azimuthal angle (in the XY-plane from the X-axis, in radians, [-pi, pi]).
               Returns None if the spheres do not intersect in a circle.
    """
    # Ensure inputs are numpy arrays for vector operations
    c1 = np.asarray(c1, dtype=float)
    c2 = np.asarray(c2, dtype=float)

    # === Step 1: Pre-computation and Validation ===

    # Vector from center 1 to center 2
    v = c2 - c1

    # Distance between centers
    d = np.linalg.norm(v)

    # Check for valid intersection
    # No intersection if centers are too far apart or one sphere is inside the other.
    # Also handles the case of concentric spheres (d=0).
    if not (abs(R1 - R2) < d < (R1 + R2)):
        # You can raise an error or return None based on desired behavior
        # raise ValueError("Spheres do not intersect in a circle.")
        return None

    # === Step 2: Find the Circle's Center and Radius ===

    # Distance from c1 to the plane of the intersection circle
    # This is derived from the law of cosines.
    d1 = (R1**2 - R2**2 + d**2) / (2 * d)

    # The radius of the intersection circle
    r_circ = np.sqrt(R1**2 - d1**2)

    # The unit vector in the direction from c1 to c2
    u_hat = v / d

    # The center of the intersection circle in Cartesian coordinates
    c_circ = c1 + d1 * u_hat

    # === Step 3: Create an Orthonormal Basis for the Circle's Plane ===

    # We need two orthogonal vectors (w1, w2) that lie in the circle's plane.
    # The normal to this plane is u_hat.

    # Find a temporary vector that is not parallel to u_hat
    temp_vec = np.array([0.0, 0.0, 1.0])
    if np.allclose(np.abs(np.dot(u_hat, temp_vec)), 1.0):
        # u_hat is parallel to the z-axis, so use x-axis instead
        temp_vec = np.array([1.0, 0.0, 0.0])

    # Use cross product to find the first basis vector in the plane
    w1_hat = np.cross(u_hat, temp_vec)
    w1_hat /= np.linalg.norm(w1_hat)

    # The second basis vector is the cross product of the normal and the first basis vector
    w2_hat = np.cross(u_hat, w1_hat)
    # This will already be a unit vector since u_hat and w1_hat are orthogonal unit vectors.

    # === Step 4: Generate the Point in Cartesian Coordinates ===

    # Parametrically define the point P on the circle
    # This point is in the global Cartesian coordinate system
    P_cartesian = c_circ + r_circ * (np.cos(t) * w1_hat + np.sin(t) * w2_hat)

    # === Step 5: Convert to Spherical Coordinates Relative to c1 ===

    # First, get the vector from c1 to our point P
    p_vec_relative_to_c1 = P_cartesian - c1

    # Now, convert this relative Cartesian vector to spherical coordinates
    px, py, pz = p_vec_relative_to_c1

    # rho: radial distance. This should be extremely close to R1 by definition.
    rho = np.linalg.norm(p_vec_relative_to_c1)

    # theta: polar angle (inclination)
    # Angle from the positive z-axis. arccos is safe since rho is non-zero.
    theta = np.arccos(pz / rho)

    # phi: azimuthal angle
    # Angle in the xy-plane from the positive x-axis. atan2 handles all quadrants.
    phi = np.arctan2(py, px)

    return rho, theta, phi


def get_cartesian(arr: np.ndarray) -> np.ndarray:

    radius_pos_i = arr[3]
    polar_pos_i = arr[4]
    azimuthal_pos_i = arr[5]
    return arr[:3] + radius_pos_i * np.array(
        [
            np.sin(polar_pos_i) * np.cos(azimuthal_pos_i),
            np.sin(polar_pos_i) * np.sin(azimuthal_pos_i),
            np.cos(polar_pos_i),
        ]
    )


for i in range(NODE_AMOUNT):
    branches_in_node = graph.get(i)
    if branches_in_node is None:
        continue
    for j in branches_in_node:
        if j <= i:
            continue
        i_cartesian_coordinates: np.ndarray = get_cartesian(centers_nodes[i])
        branch_eff_radius: float = radii[i] + length[branch_count] / 2
        if not visited[j]:
            polar: float = np.random.uniform(0, np.pi)
            azimuthal: float = np.random.uniform(0, np.pi)

            angles_branches[branch_count][0] = polar
            angles_branches[branch_count][1] = azimuthal
            effective_radius: float = radii[i] + length[branch_count]
            centers_nodes[j] = np.concatenate(
                (
                    i_cartesian_coordinates,
                    np.array([effective_radius, polar, azimuthal, branch_count]),
                )
            )
            centers_branches[branch_count] = np.concatenate(
                (
                    i_cartesian_coordinates,
                    np.array([branch_eff_radius, polar, azimuthal]),
                )
            )
        else:
            R1 = centers_nodes[i][3]
            R2 = radii[j] + length[branch_count]
            j_center: np.ndarray = centers_nodes[j]
            radius_pos_j = j_center[3]
            polar_pos_j = j_center[4]
            azimuthal_pos_j = j_center[5]
            j_cartesian_coordinates: np.ndarray = get_cartesian(centers_nodes[j])
            c1 = np.array(centers_nodes[i][:3])
            c2 = j_cartesian_coordinates
            subtract = i_cartesian_coordinates - j_cartesian_coordinates
            dist = np.linalg.norm(subtract)
            if np.abs(dist - R2) > 0.1:
                spherical = get_intersection_circle_point_spherical(
                    np.pi / 2, R1, R2, c1, c2
                )
                if spherical is not None:
                    rho, theta, phi = spherical
                    centers_nodes[i][4] = theta
                    centers_nodes[i][5] = phi
                    i_cartesian_coordinates: np.ndarray = get_cartesian(
                        centers_nodes[i]
                    )
                    subtract = j_cartesian_coordinates - i_cartesian_coordinates
                    dist = np.linalg.norm(subtract)
                    azimuthal = np.arctan2(subtract[1], subtract[0])
                    polar = np.arccos(subtract[2] / dist)
                    centers_branches[branch_count] = np.concatenate(
                        (
                            i_cartesian_coordinates,
                            np.array([branch_eff_radius, polar, azimuthal]),
                        )
                    )
                    angles_branches[branch_count][0] = polar
                    angles_branches[branch_count][1] = azimuthal

                    subtract = i_cartesian_coordinates - centers_nodes[i][:3]
                    dist = np.linalg.norm(subtract)
                    azimuthal = np.arctan2(subtract[1], subtract[0])
                    polar = np.arccos(subtract[2] / dist)
                    cnt = int(centers_nodes[i][6])
                    centers_branches[cnt][4] = polar
                    centers_branches[cnt][5] = azimuthal
                    angles_branches[cnt][0] = polar
                    angles_branches[cnt][1] = azimuthal
        visited[j] = True
        branch_count += 1

points_nodes: list = []
points_cylinder: list = []
for i in range(NODE_AMOUNT):
    node = Ellipsoid(DENSITY, radii[i])
    i_cartesian_coordinates: np.ndarray = get_cartesian(centers_nodes[i])
    node_shift = node.make_obj() + i_cartesian_coordinates
    for point in node_shift:
        points_nodes.append(point)
for i in range(branch_amount):
    branch = Cylinder(
        DENSITY,
        length[i],
        CYLINDER_RADIUS,
        angles_branches[i][0],
        angles_branches[i][1],
    )
    i_cartesian_coordinates: np.ndarray = get_cartesian(centers_branches[i])
    branch_shift = branch.make_obj() + i_cartesian_coordinates
    for point in branch_shift:
        points_cylinder.append(point)


points_arr: np.ndarray = np.array(points_nodes)
points_cylinder_arr: np.ndarray = np.array(points_cylinder)
save_dump([points_arr, points_cylinder_arr], "out/network.dump", BOX_LENGTH)
