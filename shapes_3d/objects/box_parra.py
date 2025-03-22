import sys
import numpy as np
from shapes_3d.modules.parallelepiped import Parallelepiped
from ..modules.utils import make_centers_iter, save_dump

VOLUME_FRACTION = 0.05
BOX_LEN = 1000


density: np.ndarray = np.full(2, 0.1)


length_x_mean: np.ndarray = np.array([30.0, 20.0])
length_y_mean: np.ndarray = np.array([10.0, 30.0])
length_z_mean: np.ndarray = np.array([20.0, 10.0])
length_mean: np.ndarray = np.array([length_x_mean, length_y_mean, length_z_mean])

length_x_std: np.ndarray = np.array([3.0, 2.0])
length_y_std: np.ndarray = np.array([1.0, 3.0])
length_z_std: np.ndarray = np.array([2.0, 1.0])
length_std: np.ndarray = np.array([length_x_std, length_y_std, length_z_std])

theta_mean: float = np.pi / 6
phi_mean: float = np.pi / 6

theta_std: float = np.pi / 12
phi_std: float = np.pi / 11


log_length_std: np.ndarray = np.sqrt(np.log(1 + (length_std / length_mean) ** 2))
log_length_mean: np.ndarray = np.log(length_mean) - log_length_std**2 / 2
log_theta_std: float = np.sqrt(np.log(1 + (theta_std / theta_mean) ** 2))
log_theta_mean: float = np.log(theta_mean) - log_theta_std**2 / 2
log_phi_std: float = np.sqrt(np.log(1 + (phi_std / phi_mean) ** 2))
log_phi_mean: float = np.log(phi_mean) - log_phi_std**2 / 2

length_list: list = []
theta_list: list[float] = []
phi_list: list[float] = []

target = (BOX_LEN**3) * VOLUME_FRACTION
current_volume: float = 0
while current_volume < target:
    curr_length = np.random.lognormal(log_length_mean, log_length_std)
    curr_theta: float = min(np.pi / 2, np.random.lognormal(theta_mean, theta_std))
    curr_phi: float = min(np.pi / 2, np.random.lognormal(phi_mean, phi_std))
    current_volume += (
        np.prod(np.sum(curr_length, axis=1)) * np.sin(curr_theta) * np.sin(curr_phi)
    )
    if current_volume > target:
        break
    length_list.append(curr_length.T)
    theta_list.append(curr_theta)
    phi_list.append(curr_phi)

length: np.ndarray = np.array(length_list)
theta: np.ndarray = np.array(theta_list)
phi: np.ndarray = np.array(phi_list)
N: int = length.shape[0]
print(f"N = {N} points")

max_length_sum: np.ndarray = np.sum(length, axis=1).T
max_x, max_y, max_z = (max_length_sum[0], max_length_sum[1], max_length_sum[2])
max_height = max_z * np.sin(theta) * np.sin(phi)
min_dist = 0.5 * np.sqrt(max_x**2 + max_height**2 + max_y**2)

centers = make_centers_iter(N, -BOX_LEN / 2, BOX_LEN / 2, min_dist)
print("")

points = []
for i in range(N):
    print(f"\rcreated {i+1} out of {N}", end="")
    sys.stdout.flush()
    shell = Parallelepiped(length[i], density, theta[i], phi[i], center=centers[i])
    points.extend(shell.make_obj())
points = np.array(points)
print("")

save_dump(points=[points], box_len=BOX_LEN, filename="out/box_par.dump")
points = np.array(points)
