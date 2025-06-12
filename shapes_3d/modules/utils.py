from pathlib import Path
import time
import numpy as np
import sys
import collections


def get_intersection_circle(t, R1, R2, c1, c2):
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


def make_centers(
    num_pts: int, min_pt: float, max_pt: float, min_dist: float
) -> np.ndarray:
    """
    Generate random points in 3D space such that no two points are closer than min_dist.

    Parameters
    ----------
    num_pts : int
        The number of points to generate.
    min_pt : float
        The minimum coordinate value for each point.
    max_pt : float
        The maximum coordinate value for each point.
    min_L : float
        The minimum distance between any two points.

    Returns
    -------
    np.ndarray
        A array of shape (N, 3), each representing an (x, y, z) center
    """
    points: np.ndarray = np.zeros((num_pts, 3))
    current_num_of_pts: int = 0
    while current_num_of_pts < num_pts:
        random_radius: np.ndarray = np.random.uniform(min_pt, max_pt, 3)
        point_within_distance = True
        for pt in points:
            if np.linalg.norm(random_radius - pt) <= min_dist:
                point_within_distance = False
                break
        if point_within_distance:
            points[current_num_of_pts] = random_radius
            current_num_of_pts += 1
            print(f"\rcenter {current_num_of_pts} out of {num_pts}", end="")
            sys.stdout.flush()

    return points


def make_centers_iter(
    num_pts: int, min_pt: float, max_pt: float, min_dist: np.ndarray
) -> np.ndarray:
    """
    Iteratively generate random points in 3D space such that no two points are closer than their corresponding min_dist.

    Parameters
    ----------
    num_pts : int
        The number of points to generate.
    min_pt : float
        The minimum bound for each point.
    max_pt : float
        The maximum bound for each point.
    min_dist: np.ndarray
        The minimum distance (outward radius) for each point

    Returns
    -------
    np.ndarray
        A array of shape (N, 3), each representing an (x, y, z) center
    """

    points: np.ndarray = np.zeros((num_pts, 3))
    i: int = 0
    while i < num_pts:
        random_radius: np.ndarray = np.random.uniform(
            min_pt + min_dist[i], max_pt - min_dist[i], 3
        )
        point_within_distance = True
        for j, pt in enumerate(points):
            if np.linalg.norm(random_radius - pt) <= min_dist[i] + min_dist[j]:
                point_within_distance = False
                break
        if point_within_distance:
            points[i] = random_radius
            i += 1
            print(f"\rcenter {i} out of {num_pts}", end="")
            sys.stdout.flush()

    return points


def save_dump(points, filename: str, box_len: float):
    """
    Save coordinates to a dump file, for use with OVITO.

    Parameters
    ----------
    points : list of np.ndarray
        A list of 2D arrays, where each array contains points with their coordinates
        (x, y, z), or (x, y, z, t)
    filename : str
        The name of the file to save the coordinates.
    box_len : float
        The length of the simulation box for the points.

    Returns
    -------
    None
        The function just writes to a file
    """
    print("dumping...")
    num: float = sum(pt.shape[0] for pt in points)
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w") as f:
        f.write("ITEM: TIMESTEP\n0\n")
        f.write(f"ITEM: NUMBER OF ATOMS\n{num}\n")
        f.write(
            f"ITEM: BOX BOUNDS pp pp pp\n{-box_len // 2} {box_len // 2}\n{-box_len // 2} {box_len // 2}\n{-box_len//2} {box_len//2}\n"
        )
        f.write("ITEM: ATOMS id type x y z\n")
        max_type: int = 0
        for i in range(0, len(points)):
            if points[i].shape[1] == 4:
                for j in range(points[i].shape[0]):
                    f.write(
                        f"{j + 1} {int(points[i][j][3] + i)} {points[i][j][0]:.6f} {points[i][j][1]:.6f} {points[i][j][2]:.6f}\n"
                    )
                    max_type = max(max_type, int(points[i][j][3]))
            else:
                for j, (x, y, z) in enumerate(points[i], start=1):
                    f.write(f"{j} {i + 1 + max_type} {x:.6f} {y:.6f} {z:.6f}\n")
        print("dumped to", filename)


def is_connected(adj_list, N):
    """
    Checks if a graph is connected using Breadth-First Search (BFS).

    Args:
        adj_list (dict): The adjacency list of the graph.
        N (int): The number of nodes in the graph.

    Returns:
        bool: True if the graph is connected, False otherwise.
    """
    if not adj_list or N == 0:
        return True

    # A queue for BFS, starting with node 0
    queue = collections.deque([next(iter(adj_list))])
    # A set to keep track of visited nodes
    visited = {next(iter(adj_list))}

    while queue:
        node = queue.popleft()
        for neighbor in adj_list[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    # If the number of visited nodes is equal to the total number of nodes,
    # the graph is connected.
    return len(visited) == N


def create_network_graph(N, M):
    """
    Generates a connected graph with N nodes where each node has approximately M branches.

    Args:
        N (int): The number of nodes in the graph.
        M (int): The desired number of branches (degree) for each node.

    Returns:
        dict: An adjacency list representation of the graph, or None if
              the graph cannot be created.
    """
    # --- Input Validation ---
    if N * M % 2 != 0:
        print(
            "Error: The product of N (nodes) and M (branches) must be an even number."
        )
        return None
    if M >= N:
        print(
            "Error: M must be less than N. A node cannot have more connections than available nodes."
        )
        return None
    if N > 1 and M < 2:
        print("Error: For a connected graph with N > 1, M must be at least 2.")
        return None

    adj_list = {i: [] for i in range(N)}
    degrees = {i: 0 for i in range(N)}

    # --- 1. Create a Hamiltonian cycle to guarantee connectivity ---
    for i in range(N):
        # Connect node i to node (i+1) mod N
        neighbor = (i + 1) % N
        adj_list[i].append(neighbor)
        adj_list[neighbor].append(i)
        degrees[i] += 1
        degrees[neighbor] += 1

    # --- 2. Add remaining edges randomly ---
    potential_edges = []
    for i in range(N):
        for j in range(i + 2, N):
            # Avoid edges that are part of the initial cycle
            if not (i == 0 and j == N - 1):
                potential_edges.append((i, j))

    # Shuffle the potential edges to add them randomly
    np.random.shuffle(potential_edges)

    for node1, node2 in potential_edges:
        # Add the edge if both nodes still need more connections
        if degrees[node1] < M and degrees[node2] < M:
            adj_list[node1].append(node2)
            adj_list[node2].append(node1)
            degrees[node1] += 1
            degrees[node2] += 1

    # This algorithm prioritizes connectivity and M-regularity but may result
    # in some nodes having a degree slightly different from M if constraints are tight.
    # A final check can be performed.

    return adj_list


def get_cartesian_relative(arr: np.ndarray) -> np.ndarray:

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
