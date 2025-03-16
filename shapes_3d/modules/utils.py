from pathlib import Path
import numpy as np


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
        # random point
        R: np.ndarray = np.random.uniform(min_pt, max_pt, 3)
        point_within_distance = True
        for pt in points:
            if np.linalg.norm(R - pt) <= min_dist:
                point_within_distance = False
                break
        if point_within_distance:
            points[current_num_of_pts] = R
            current_num_of_pts += 1
            print("Made center n = ", current_num_of_pts, " out of ", num_pts)

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
    num = sum(pt.shape[0] for pt in points)
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w") as f:
        f.write("ITEM: TIMESTEP\n0\n")
        f.write(f"ITEM: NUMBER OF ATOMS\n{num}\n")
        f.write(
            f"ITEM: BOX BOUNDS pp pp pp\n{-box_len // 2} {box_len // 2}\n{-box_len // 2} {box_len // 2}\n{-box_len//2} {box_len//2}\n"
        )
        f.write("ITEM: ATOMS id type x y z\n")
        max_type = 0
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
