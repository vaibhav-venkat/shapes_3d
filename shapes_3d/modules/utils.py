from pathlib import Path
import time
import numpy as np
import sys
import collections


def relax_network_positions_alt(
    initial_positions: np.ndarray,
    graph: dict,
    branches: list[tuple[int, int]],
    node_radii: np.ndarray,
    cylinder_radius: float,
    box_length: float,
    iterations: int = 2000,
    learning_rate: float = 0.05,
    repulsion_strength: float = 2.5,
    force_stop_threshold: float = 1e-6,
) -> np.ndarray:
    positions = np.copy(initial_positions)
    num_nodes = len(positions)

    num_branches = len(branches)

    print("Relaxing network layout with collision mitigation")
    for i in range(iterations):
        forces = np.zeros_like(positions)
        # Node-Wall repulsion
        for n in range(num_nodes):
            displacement = np.zeros(3)
            position = positions[n]
            for i in range(3):
                coord = position[i]
                if coord > box_length / 2 - 1:
                    displacement[i] = coord - box_length / 2 + 1
                elif coord < -box_length / 2 + 1:
                    displacement[i] = box_length / 2 - 1 + coord
            dist = np.linalg.norm(displacement)
            if dist < 1e-6:
                dist = 1e-6
                displacement = np.random.rand(3) * 1e-6
            direction = displacement / dist
            repulsion = learning_rate * repulsion_strength * displacement * direction
            forces[n] -= repulsion
        # Node-Node Repulsion
        for n1 in range(num_nodes):
            for n2 in range(n1 + 1, num_nodes):
                # some breathing room
                min_dist = node_radii[n1] + node_radii[n2] + 0.1
                vec = positions[n2] - positions[n1]
                dist = np.linalg.norm(vec)
                if dist < 1e-6:
                    dist = 1e-6
                    vec = np.random.rand(3) * 1e-6
                if dist < min_dist:
                    overlap = min_dist - dist
                    direction = vec / dist
                    repulsion = (
                        learning_rate * repulsion_strength * overlap * direction / 2.0
                    )
                    forces[n1] -= repulsion
                    forces[n2] += repulsion

        # Node-Branch Repulsion
        for node_k in range(num_nodes):
            for branch_i, branch_j in branches:
                # don't repel if it is the node's own branch
                if node_k == branch_i or node_k == branch_j:
                    continue
                dist, closest_pt = point_segment_distance(
                    positions[node_k], positions[branch_i], positions[branch_j]
                )
                min_allowed = node_radii[node_k] + cylinder_radius + 0.1
                if dist < min_allowed:
                    overlap = min_allowed - dist
                    direction = (
                        (positions[node_k] - closest_pt) / dist
                        if dist > 1e-6
                        else np.random.rand(3)
                    )
                    force_on_node = (
                        learning_rate * repulsion_strength * overlap * direction
                    )
                    forces[node_k] += force_on_node
                    vec_branch = positions[branch_j] - positions[branch_i]
                    len_sq = np.dot(vec_branch, vec_branch)
                    t = (
                        np.dot(closest_pt - positions[branch_i], vec_branch) / len_sq
                        if len_sq > 1e-12
                        else 0.5
                    )
                    forces[branch_i] -= force_on_node * (1.0 - t)
                    forces[branch_j] -= force_on_node * t

        # Branch-Branch
        min_branch_dist = 2 * cylinder_radius + 0.1
        for b1_idx in range(num_branches):
            for b2_idx in range(b1_idx + 1, num_branches):
                n1, n2 = branches[b1_idx]
                n3, n4 = branches[b2_idx]

                # Skip if branches share a node
                if n1 in (n3, n4) or n2 in (n3, n4):
                    continue

                dist, closest_p1, closest_p2 = segment_segment_distance(
                    positions[n1], positions[n2], positions[n3], positions[n4]
                )

                if dist < min_branch_dist:
                    overlap = min_branch_dist - dist
                    if dist < 1e-6:
                        dist = 1e-6
                        direction = np.random.rand(3)
                    else:
                        direction = (closest_p1 - closest_p2) / dist

                    total_force = (
                        learning_rate * repulsion_strength * overlap * direction
                    )

                    # Distribute this force to the 4 nodes
                    # branch 1
                    force_b1 = total_force / 2.0
                    vec_b1 = positions[n2] - positions[n1]
                    len_sq_b1 = np.dot(vec_b1, vec_b1)
                    s = (
                        np.dot(closest_p1 - positions[n1], vec_b1) / len_sq_b1
                        if len_sq_b1 > 1e-12
                        else 0.5
                    )
                    forces[n1] += force_b1 * (1.0 - s)
                    forces[n2] += force_b1 * s

                    # Force on branch 2
                    force_b2 = -total_force / 2.0
                    vec_b2 = positions[n4] - positions[n3]
                    len_sq_b2 = np.dot(vec_b2, vec_b2)
                    t = (
                        np.dot(closest_p2 - positions[n3], vec_b2) / len_sq_b2
                        if len_sq_b2 > 1e-12
                        else 0.5
                    )
                    forces[n3] += force_b2 * (1.0 - t)
                    forces[n4] += force_b2 * t

        # Anchor the first node and update positions
        forces[0] = 0.0
        positions += forces

        # Check for convergence
        max_movement = np.max(np.linalg.norm(forces, axis=1))
        if max_movement < force_stop_threshold:
            print(f"\nConvergence reached at iteration {i + 1}.")
            break
        if (i + 1) % 20 == 0:
            print(
                f"\rIteration {i + 1}/{iterations}, Max Movement: {max_movement:.6f}",
                end="",
            )

    print("\nRelaxation complete.")
    return positions


def relax_network_positions(
    initial_positions: np.ndarray,
    graph: dict,
    branch_to_length: dict,
    node_radii: np.ndarray,
    cylinder_radius: float,
    iterations: int = 2000,
    learning_rate: float = 0.05,
    repulsion_strength: float = 2.5,
    force_stop_threshold: float = 1e-5,
) -> np.ndarray:
    positions = np.copy(initial_positions)
    num_nodes = len(positions)

    branches = list(branch_to_length.keys())
    num_branches = len(branches)

    print("Relaxing network layout with collision mitigation")
    for i in range(iterations):
        forces = np.zeros_like(positions)

        # Spring Forces
        for node1, node2 in branches:
            target_length = branch_to_length[(node1, node2)]
            vec = positions[node2] - positions[node1]
            dist = np.linalg.norm(vec)

            # randomized emergency repulsion
            # otherwise it will explode
            if dist < 1e-6:
                dist = 1e-6
                vec = np.random.rand(3) * 1e-6

            error = dist - target_length
            direction = vec / dist
            # total force should be double this, but we apply it to both
            # F = k dx, k = learning_rate and dx = error
            force_vec = learning_rate * error * direction / 2.0
            forces[node1] += force_vec
            forces[node2] -= force_vec

        # Node-Node Repulsion
        for n1 in range(num_nodes):
            for n2 in range(n1 + 1, num_nodes):
                # some breathing room
                min_dist = node_radii[n1] + node_radii[n2] + 0.1
                vec = positions[n2] - positions[n1]
                dist = np.linalg.norm(vec)
                if dist < 1e-6:
                    dist = 1e-6
                    vec = np.random.rand(3) * 1e-6
                if dist < min_dist:
                    overlap = min_dist - dist
                    direction = vec / dist
                    repulsion = (
                        learning_rate * repulsion_strength * overlap * direction / 2.0
                    )
                    forces[n1] -= repulsion
                    forces[n2] += repulsion

        # Node-Branch Repulsion
        for node_k in range(num_nodes):
            for branch_i, branch_j in branches:
                # don't repel if it is the node's own branch
                if node_k == branch_i or node_k == branch_j:
                    continue
                dist, closest_pt = point_segment_distance(
                    positions[node_k], positions[branch_i], positions[branch_j]
                )
                min_allowed = node_radii[node_k] + cylinder_radius + 0.1
                if dist < min_allowed:
                    overlap = min_allowed - dist
                    direction = (
                        (positions[node_k] - closest_pt) / dist
                        if dist > 1e-6
                        else np.random.rand(3)
                    )
                    force_on_node = (
                        learning_rate * repulsion_strength * overlap * direction
                    )
                    forces[node_k] += force_on_node
                    vec_branch = positions[branch_j] - positions[branch_i]
                    len_sq = np.dot(vec_branch, vec_branch)
                    t = (
                        np.dot(closest_pt - positions[branch_i], vec_branch) / len_sq
                        if len_sq > 1e-12
                        else 0.5
                    )
                    forces[branch_i] -= force_on_node * (1.0 - t)
                    forces[branch_j] -= force_on_node * t

        # Branch-Branch
        min_branch_dist = 2 * cylinder_radius + 0.1
        for b1_idx in range(num_branches):
            for b2_idx in range(b1_idx + 1, num_branches):
                n1, n2 = branches[b1_idx]
                n3, n4 = branches[b2_idx]

                # Skip if branches share a node
                if n1 in (n3, n4) or n2 in (n3, n4):
                    continue

                dist, closest_p1, closest_p2 = segment_segment_distance(
                    positions[n1], positions[n2], positions[n3], positions[n4]
                )

                if dist < min_branch_dist:
                    overlap = min_branch_dist - dist
                    if dist < 1e-6:
                        dist = 1e-6
                        direction = np.random.rand(3)
                    else:
                        direction = (closest_p1 - closest_p2) / dist

                    total_force = (
                        learning_rate * repulsion_strength * overlap * direction
                    )

                    # Distribute this force to the 4 nodes
                    # branch 1
                    force_b1 = total_force / 2.0
                    vec_b1 = positions[n2] - positions[n1]
                    len_sq_b1 = np.dot(vec_b1, vec_b1)
                    s = (
                        np.dot(closest_p1 - positions[n1], vec_b1) / len_sq_b1
                        if len_sq_b1 > 1e-12
                        else 0.5
                    )
                    forces[n1] += force_b1 * (1.0 - s)
                    forces[n2] += force_b1 * s

                    # Force on branch 2
                    force_b2 = -total_force / 2.0
                    vec_b2 = positions[n4] - positions[n3]
                    len_sq_b2 = np.dot(vec_b2, vec_b2)
                    t = (
                        np.dot(closest_p2 - positions[n3], vec_b2) / len_sq_b2
                        if len_sq_b2 > 1e-12
                        else 0.5
                    )
                    forces[n3] += force_b2 * (1.0 - t)
                    forces[n4] += force_b2 * t

        # Anchor the first node and update positions
        forces[0] = 0.0
        positions += forces

        # Check for convergence
        max_movement = np.max(np.linalg.norm(forces, axis=1))
        if max_movement < force_stop_threshold:
            print(f"\nConvergence reached at iteration {i + 1}.")
            break
        if (i + 1) % 20 == 0:
            print(
                f"\rIteration {i + 1}/{iterations}, Max Movement: {max_movement:.6f}",
                end="",
            )

    print("\nRelaxation complete.")
    return positions


def segment_segment_distance(
    p1: np.ndarray, q1: np.ndarray, p2: np.ndarray, q2: np.ndarray
) -> tuple[float, np.ndarray, np.ndarray]:
    """
    Calculates the shortest distance between two line segments (p1,q1) and (p2,q2).

    Args:
        p1, q1 (np.ndarray): Endpoints of the first segment.
        p2, q2 (np.ndarray): Endpoints of the second segment.

    Returns:
        tuple[float, np.ndarray, np.ndarray]:
            - The shortest distance between the segments.
            - The closest point on the first segment.
            - The closest point on the second segment.
    """
    u = q1 - p1
    v = q2 - p2
    w = p1 - p2

    a = np.dot(u, u)  # >= 0
    b = np.dot(u, v)
    c = np.dot(v, v)  # >= 0
    d = np.dot(u, w)
    e = np.dot(v, w)

    D = a * c - b * b

    if D < 1e-7:
        s_c = 0.0
    else:
        s_c = b * e - c * d

    s = np.clip(s_c / D, 0.0, 1.0) if D > 1e-7 else 0.0

    # Recalculate t for the clamped s
    t_nom = b * s + e
    if t_nom < 0.0:
        t = 0.0
        s_nom = -d
        if s_nom < 0.0:
            s = 0.0
        elif s_nom > a:
            s = 1.0
        else:
            s = s_nom / a if a > 1e-7 else 0.0
    elif t_nom > c:
        t = 1.0
        s_nom = b - d
        if s_nom < 0.0:
            s = 0.0
        elif s_nom > a:
            s = 1.0
        else:
            s = s_nom / a if a > 1e-7 else 0.0
    else:
        t = t_nom / c if c > 1e-7 else 0.0

    closest_point1 = p1 + s * u
    closest_point2 = p2 + t * v
    distance = np.linalg.norm(closest_point1 - closest_point2)

    return float(distance), closest_point1, closest_point2


def point_segment_distance(
    p: np.ndarray, a: np.ndarray, b: np.ndarray
) -> tuple[float, np.ndarray]:
    """
    Calculates the shortest distance between a point p and a line defined by a and b.

    Args:
        p (np.ndarray): The 3D coordinates of the point.
        a (np.ndarray): The 3D coordinates of the start of the segment.
        b (np.ndarray): The 3D coordinates of the end of the segment.

    Returns:
        tuple[float, np.ndarray]:
            - The shortest distance.
            - The coordinates of the closest point on the segment to p.
    """
    # line segment
    ab = b - a

    ap = p - a

    len_sq_ab = np.dot(ab, ab)

    # If the segment is just a point (a and b are the same)
    if len_sq_ab < 1e-12:
        return float(np.linalg.norm(ap)), a

    t = np.dot(ap, ab) / len_sq_ab

    if t < 0.0:  # behind point a
        closest_point = a
    elif t > 1.0:  # ahead of point b
        closest_point = b
    else:  # within the segement, just perpendicular
        closest_point = a + t * ab

    distance = np.linalg.norm(p - closest_point)
    return float(distance), closest_point


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
            f"ITEM: BOX BOUNDS pp pp pp\n{-box_len // 2} {box_len // 2}\n{-box_len // 2} {box_len // 2}\n{-box_len // 2} {box_len // 2}\n"
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


def create_network_graph(N: int, M: int) -> dict[int, list[int]] | None:
    """
    Generates a connected graph with N nodes where each node has approximately M branches.

    Args:
        N (int): The number of nodes in the graph.
        M (int): The desired number of branches (degree) for each node.

    Returns:
        dict: An adjacency list representation of the graph, or None if
              the graph cannot be created.
    """
    if N <= 0:
        return {}
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
    if N > 2 and M < 2:
        print("Warning: For a connected graph with N > 2, M should be at least 2.")

    adj_list = {i: [] for i in range(N)}
    degrees = {i: 0 for i in range(N)}

    # 1. Create a Hamiltonian cycle to guarantee connectivity
    for i in range(N):
        neighbor = (i + 1) % N
        if neighbor not in adj_list[i]:
            adj_list[i].append(neighbor)
            adj_list[neighbor].append(i)
            degrees[i] += 1
            degrees[neighbor] += 1

    # 2. Add remaining edges randomly
    potential_edges = []
    for i in range(N):
        for j in range(i + 1, N):
            # Add edge if it doesn't exist yet
            if j not in adj_list[i]:
                potential_edges.append((i, j))

    np.random.shuffle(potential_edges)

    for node1, node2 in potential_edges:
        if degrees[node1] < M and degrees[node2] < M:
            adj_list[node1].append(node2)
            adj_list[node2].append(node1)
            degrees[node1] += 1
            degrees[node2] += 1

    return adj_list
