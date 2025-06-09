import numpy as np

from shapes_3d.modules.cylinder import Cylinder
from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import save_dump, make_centers_iter

RADIUS_MEAN = 5.0
RADIUS_STD = 0.5
NODE_AMOUNT = 5
BOX_LENGTH = 200
BRANCH_LENGTH_MEAN = 30.0
BRANCH_LENGTH_STD = 0.0
AMOUNT_PER_NODE = 3


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
    branch_length_mean_log, branch_length_deviation_log, NODE_AMOUNT * AMOUNT_PER_NODE
)


centers_nodes: np.ndarray = make_centers_iter(
    NODE_AMOUNT, -BOX_LENGTH / 2, BOX_LENGTH / 2, radii
)
centers_branches: np.ndarray = make_centers_iter(
    NODE_AMOUNT * AMOUNT_PER_NODE, -BOX_LENGTH / 2, BOX_LENGTH / 2, length
)
points_nodes: list = []
points_cylinder: list = []
for i in range(NODE_AMOUNT):
    node = Ellipsoid(0.4, radii[i])
    node_shift = node.make_obj() + centers_nodes[i]
    for point in node_shift:
        points_nodes.append(point)
for i in range(NODE_AMOUNT):
    branch = Cylinder(0.4, length[i], 3.0, np.pi / 3, np.pi / 3)
    branch_shift = branch.make_obj() + centers_branches[i]
    for point in branch_shift:
        points_cylinder.append(point)

points_arr: np.ndarray = np.array(points_nodes)
points_cylinder_arr: np.ndarray = np.array(points_cylinder)
save_dump([points_arr, points_cylinder_arr], "out/network.dump", BOX_LENGTH)
