import numpy as np


RADIUS_MEAN = 5.0
RADIUS_STD = 0.0
NODE_AMOUNT = 12

BRANCH_LENGTH_MEAN = 2.0
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

edges_connected: np.ndarray = np.zeros(NODE_AMOUNT)

adj_list: np.ndarray = np.full((NODE_AMOUNT, NODE_AMOUNT), False)

start = 0
for i in range(NODE_AMOUNT):
    for j in range(start, NODE_AMOUNT):
        if i == j:
            continue
        if edges_connected[i] >= AMOUNT_PER_NODE:
            break
        if edges_connected[j] < AMOUNT_PER_NODE:
            adj_list[i][j] = True
            edges_connected[i] += 1
            edges_connected[j] += 1
        start = (start + 1) % NODE_AMOUNT
# points: np.ndarray = np.full((NODE_AMOUNT, 3), None)
# points[0] = np.zeros(3)
#
# for i in range(NODE_AMOUNT):
#     for j in range(1, NODE_AMOUNT):
#         if adj_list[i][j] and points[j][0] is None:
#             theta: float = np.random.uniform(0, np.pi)
#             phi: float = np.random.uniform(0, 2 * np.pi)
#             point = (length[i] + radii[j] + radii[i]) * np.array(
#                 [
#                     np.sin(theta) * np.cos(phi),
#                     np.sin(theta) * np.sin(phi),
#                     np.cos(theta),
#                 ]
#             )
#             points[j] = point
#             print(np.linalg.norm(points[j] - points[i]))
