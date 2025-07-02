import numpy as np

from shapes_3d.modules.cylinder import Cylinder
from shapes_3d.modules.ellipsoid import Ellipsoid
from ..modules.utils import (
    create_network_graph,
    relax_network_positions_alt,
    save_dump,
)

# CONSTANTS
# NOTE: CHANGE CONSTANTS
RADIUS_MEAN = 5.0
RADIUS_STD = 0.5
NODE_AMOUNT = 10
BOX_LENGTH = 200
AMOUNT_PER_NODE = 3
CYLINDER_RADIUS = 3
DENSITY = 0.4
ITERATIONS = (
    290000  # As high as you can tolerate. It will terminate if it converges before.
)
LEARNING_RATE = 0.005
REPULSION_STRENGTH = 7.6  # 5.0 < REPULSION_STRENGTH < 10.0

radius_deviation_log = np.sqrt(np.log(1 + (RADIUS_STD / RADIUS_MEAN) ** 2))
radius_mean_log = np.log(RADIUS_MEAN) - radius_deviation_log**2 / 2


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

# close to the origin
initial_node_centers = np.random.uniform(
    -BOX_LENGTH / 2, BOX_LENGTH / 2, (NODE_AMOUNT, 3)
)


final_node_positions = relax_network_positions_alt(
    initial_positions=initial_node_centers,
    graph=graph,
    box_length=BOX_LENGTH,
    branches=branches,
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
    diff_y = vec_diff[1]
    diff_x = vec_diff[0]
    diff_z = vec_diff[2]

    if dist < 1e-6:
        continue

    center_pos = (pos1 + pos2) / 2.0

    azimuthal = np.arctan2(diff_y, diff_x)
    polar = np.arccos(diff_z / dist)

    branch = Cylinder(DENSITY, float(dist), CYLINDER_RADIUS, polar, azimuthal)
    branch_points = branch.make_obj() + center_pos
    points_branches.extend(branch_points)

points_arr: np.ndarray = np.array(points_nodes)
points_cylinder_arr: np.ndarray = np.array(points_branches)
save_dump([points_arr, points_cylinder_arr], "out/network.dump", BOX_LENGTH)
branch_lengths = np.zeros(len(branches))
for i in range(len(branches)):
    branch_lengths[i] = np.linalg.norm(
        final_node_positions[branches[i][0]] - final_node_positions[branches[i][1]]
    )
print("Branch lengths: ", branch_lengths)
print("Done.")
