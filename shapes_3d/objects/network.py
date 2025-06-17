import numpy as np

from shapes_3d.modules.cylinder import Cylinder
from shapes_3d.modules.ellipsoid import Ellipsoid
from ..modules.utils import (
    create_network_graph,
    save_dump,
    relax_network_positions,
)

# CONSTANTS
# NOTE: CHANGE THESE!!
RADIUS_MEAN = 4.0
RADIUS_STD = 0.5
NODE_AMOUNT = 6
BOX_LENGTH = 100
BRANCH_LENGTH_MEAN = 45.0
BRANCH_LENGTH_STD = 3.0
AMOUNT_PER_NODE = 3
CYLINDER_RADIUS = 1.7
DENSITY = 0.4
ITERATIONS = 80000
LEARNING_RATE = 0.01
REPULSION_STRENGTH = 7.6

radius_deviation_log = np.sqrt(np.log(1 + (RADIUS_STD / RADIUS_MEAN) ** 2))
radius_mean_log = np.log(RADIUS_MEAN) - radius_deviation_log**2 / 2

branch_length_deviation_log = np.sqrt(
    np.log(1 + (BRANCH_LENGTH_STD / BRANCH_LENGTH_MEAN) ** 2)
)
branch_length_mean_log = np.log(BRANCH_LENGTH_MEAN) - branch_length_deviation_log**2 / 2

radii: np.ndarray = np.random.lognormal(
    radius_mean_log, radius_deviation_log, NODE_AMOUNT
)

graph = create_network_graph(NODE_AMOUNT, AMOUNT_PER_NODE)
if graph is None:
    print("Error when creating graph. See previous messages")
    exit(1)

branches: list[tuple[int, int]] = []
visited_edges: set[tuple[int, int]] = set()
for node1 in range(NODE_AMOUNT):
    for node2 in graph.get(node1, []):
        edge: tuple[int, int] = (node1, node2) if node1 <= node2 else (node2, node1)
        if edge not in visited_edges:
            branches.append(edge)
            visited_edges.add(edge)

BRANCH_AMOUNT = len(branches)
target_lengths: np.ndarray = np.random.lognormal(
    branch_length_mean_log, branch_length_deviation_log, BRANCH_AMOUNT
)
branch_to_length = {branches[k]: target_lengths[k] for k in range(BRANCH_AMOUNT)}

# close to the origin
initial_node_centers = np.random.uniform(-20, 20, (NODE_AMOUNT, 3))

# node 0 (first node) always starts at origin for consistency
initial_node_centers[0] = np.array([0.0, 0.0, 0.0])

final_node_positions = relax_network_positions(
    initial_positions=initial_node_centers,
    graph=graph,
    branch_to_length=branch_to_length,
    node_radii=radii,
    cylinder_radius=CYLINDER_RADIUS,
    iterations=ITERATIONS,
    learning_rate=LEARNING_RATE,
    repulsion_strength=REPULSION_STRENGTH,
)

points_nodes: list = []
for i in range(NODE_AMOUNT):
    node = Ellipsoid(DENSITY, radii[i])
    node_points = node.make_obj() + final_node_positions[i]
    points_nodes.extend(node_points)

points_branches: list = []
for i, (node1, node2) in enumerate(branches):
    pos1 = final_node_positions[node1]
    pos2 = final_node_positions[node2]

    vec_diff = pos2 - pos1
    dist = np.linalg.norm(vec_diff)

    if dist < 1e-6:
        continue

    center_pos = (pos1 + pos2) / 2.0

    # tan(azi) = y/x
    azimuthal = np.arctan2(vec_diff[1], vec_diff[0])
    polar = np.arccos(vec_diff[2] / dist)

    branch = Cylinder(DENSITY, float(dist), CYLINDER_RADIUS, polar, azimuthal)
    branch_points = branch.make_obj() + center_pos
    points_branches.extend(branch_points)

points_arr: np.ndarray = np.array(points_nodes)
points_cylinder_arr: np.ndarray = np.array(points_branches)
save_dump([points_arr, points_cylinder_arr], "out/network.dump", BOX_LENGTH)

print("Done.")
