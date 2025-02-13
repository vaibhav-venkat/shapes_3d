from patch_shell import PatchShell
from onion import Onion
from pathlib import Path
import numpy as np

sphere = Onion(np.array([50, 20]), np.array([[0, 0, 0]]), np.array([1])).pts
patches = PatchShell(50, np.array([300.0, 200.0, 900.0, 1500.0, 200.0, 3000.0]), 6)
pts = patches.make_patches()


def save_dump(points, filename="out/patches.dump", box_len=1000):
    """
    Save coordinates to a dump file, for use with OVITO
    """
    num = sum(pt.shape[0] for pt in points)
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w") as f:
        f.write("ITEM: TIMESTEP\n0\n")
        f.write(f"ITEM: NUMBER OF ATOMS\n{num}\n")
        f.write(
            f"ITEM: BOX BOUNDS pp pp pp\n{-box_len // 2} {box_len // 2}\n{-box_len // 2} {box_len // 2}\n{-box_len//2} {box_len//2}\n"
        )
        f.write("ITEM: ATOMS id type x y z\n")
        for i in range(0, len(points)):
            if points[i].shape[1] == 4:
                for j in range(points[i].shape[0]):
                    f.write(
                        f"{j + 1} {int(points[i][j][3] + i)} {points[i][j][0]:.6f} {points[i][j][1]:.6f} {points[i][j][2]:.6f}\n"
                    )
            else:
                for j, (x, y, z) in enumerate(points[i], start=1):
                    f.write(f"{j} {i + 1} {x:.6f} {y:.6f} {z:.6f}\n")
        print("dumped to", filename)


save_dump([sphere, pts], box_len=2 * 50)
