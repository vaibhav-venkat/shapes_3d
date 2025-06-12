import numpy as np

from shapes_3d.modules.cylinder import Cylinder
from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import (
    create_network_graph,
    save_dump,
    get_intersection_circle,
    get_cartesian_relative,
)

ERROR = 0.1
RADIUS_MEAN = 6.0
RADIUS_STD = 0.5
NODE_AMOUNT = 3
BOX_LENGTH = 200
BRANCH_LENGTH_MEAN = 30.0
BRANCH_LENGTH_STD = 0.0
AMOUNT_PER_NODE = 2
BRANCH_AMOUNT = NODE_AMOUNT
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
    branch_length_mean_log, branch_length_deviation_log, BRANCH_AMOUNT
)

# (x_a, y_a, z_a, R, polar, azimuthal, i)
centers_nodes: np.ndarray = np.zeros((NODE_AMOUNT, 7))
# (x_a, y_a, z_a, R, polar, azimuthal)
centers_branches: np.ndarray = np.zeros((BRANCH_AMOUNT, 6))
angles_branches: np.ndarray = np.zeros((BRANCH_AMOUNT, 2))


graph = create_network_graph(NODE_AMOUNT, AMOUNT_PER_NODE)

visited_node: np.ndarray = np.full(NODE_AMOUNT, False)
visited_node[0] = True
if graph is None:
    print("error when creating graph")
    exit(1)

branch_index: int = 0


for primary_node in range(NODE_AMOUNT):
    branches_in_node = graph.get(primary_node)
    if branches_in_node is None:
        continue
    for secondary_node in branches_in_node:
        if secondary_node <= primary_node:
            continue
        primary_cartesian_coordinates: np.ndarray = get_cartesian_relative(
            centers_nodes[primary_node]
        )
        branch_effective_radius: float = radii[primary_node] + length[branch_index] / 2
        if not visited_node[secondary_node]:
            polar: float = np.random.uniform(0, np.pi)
            azimuthal: float = np.random.uniform(0, np.pi)

            angles_branches[branch_index] = np.array([polar, azimuthal])
            node_effective_radius: float = radii[primary_node] + length[branch_index]
            centers_nodes[secondary_node] = np.concatenate(
                (
                    primary_cartesian_coordinates,
                    np.array([node_effective_radius, polar, azimuthal, branch_index]),
                )
            )
            centers_branches[branch_index] = np.concatenate(
                (
                    primary_cartesian_coordinates,
                    np.array([branch_effective_radius, polar, azimuthal]),
                )
            )
        else:
            bound_sphere_radius = centers_nodes[primary_node][3]
            fictitious_sphere_radius = radii[secondary_node] + length[branch_index]

            secondary_center: np.ndarray = centers_nodes[secondary_node]
            secondary_radius = secondary_center[3]
            secondary_polar_angle = secondary_center[4]
            secondary_azimuthal_angle = secondary_center[5]

            secondary_cartesian: np.ndarray = get_cartesian_relative(
                centers_nodes[secondary_node]
            )
            primary_cartesian = np.array(centers_nodes[primary_node][:3])
            dist = np.linalg.norm(primary_cartesian - secondary_cartesian)
            if np.abs(dist - fictitious_sphere_radius) > ERROR:
                circle_spherical_coordinates = get_intersection_circle(
                    np.pi / 2,
                    bound_sphere_radius,
                    fictitious_sphere_radius,
                    primary_cartesian,
                    secondary_cartesian,
                )
                if circle_spherical_coordinates is not None:
                    _, circle_polar_angle, circle_azimuthal_angle = (
                        circle_spherical_coordinates
                    )
                    centers_nodes[primary_node][4] = circle_polar_angle
                    centers_nodes[primary_node][5] = circle_azimuthal_angle

                    primary_cartesian_coordinates: np.ndarray = get_cartesian_relative(
                        centers_nodes[primary_node]
                    )
                    difference_between = (
                        secondary_cartesian - primary_cartesian_coordinates
                    )  # (dx, dy, dz)

                    dist = np.linalg.norm(difference_between)

                    azimuthal = np.arctan2(difference_between[1], difference_between[0])
                    polar = np.arccos(difference_between[2] / dist)

                    centers_branches[branch_index] = np.concatenate(
                        (
                            primary_cartesian_coordinates,
                            np.array([branch_effective_radius, polar, azimuthal]),
                        )
                    )
                    angles_branches[branch_index] = np.array([polar, azimuthal])

                    difference_between_adjusted = (
                        primary_cartesian_coordinates - centers_nodes[primary_node][:3]
                    )
                    dist_adjusted = np.linalg.norm(difference_between_adjusted)
                    azimuthal = np.arctan2(
                        difference_between_adjusted[1], difference_between_adjusted[0]
                    )
                    polar = np.arccos(difference_between_adjusted[2] / dist_adjusted)
                    associated_branch_idx = int(centers_nodes[primary_node][6])
                    centers_branches[associated_branch_idx][4] = polar
                    centers_branches[associated_branch_idx][5] = azimuthal
                    angles_branches[associated_branch_idx][0] = polar
                    angles_branches[associated_branch_idx][1] = azimuthal
        visited_node[secondary_node] = True
        branch_index += 1

points_nodes: list = []
points_cylinder: list = []
for primary_node in range(NODE_AMOUNT):
    node = Ellipsoid(DENSITY, radii[primary_node])
    primary_cartesian_coordinates: np.ndarray = get_cartesian_relative(
        centers_nodes[primary_node]
    )
    node_shift = node.make_obj() + primary_cartesian_coordinates
    for point in node_shift:
        points_nodes.append(point)
for primary_node in range(BRANCH_AMOUNT):
    branch = Cylinder(
        DENSITY,
        length[primary_node],
        CYLINDER_RADIUS,
        angles_branches[primary_node][0],
        angles_branches[primary_node][1],
    )
    primary_cartesian_coordinates: np.ndarray = get_cartesian_relative(
        centers_branches[primary_node]
    )
    branch_shift = branch.make_obj() + primary_cartesian_coordinates
    for point in branch_shift:
        points_cylinder.append(point)


points_arr: np.ndarray = np.array(points_nodes)
points_cylinder_arr: np.ndarray = np.array(points_cylinder)
save_dump([points_arr, points_cylinder_arr], "out/network.dump", BOX_LENGTH)
