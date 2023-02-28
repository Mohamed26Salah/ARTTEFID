import pyvista as pv
import numpy as np
from typing import Tuple

def contains(point_in_world: Tuple[float, float, float], extent: Tuple[float, float, float]) -> bool:
    # local_min = tuple(-ex / 2 for ex in extent)
    # local_max = tuple(ex / 2 for ex in extent)
    local_min = [0 ,extent[1]-1,extent[2]*-1 ]
    local_max = [extent[0] ,extent[1],0]

    # The bounding box is in local coordinates, so convert point to local, too.
    local_point = tuple(point_in_world[i] for i in range(3))

    return (local_min[0] <= local_point[0] <= local_max[0]) and \
           (local_min[1] <= local_point[1] <= local_max[1]) and \
           (local_min[2] <= local_point[2] <= local_max[2])

# Load the 3D model
mesh = pv.read('scaned.obj')
bbox = [0.57728195, 1.1623952, 0.5555216]
result = list(map(lambda x: x * 2.1, bbox))
contained = [contains(mesh.points[i], result) for i in range(mesh.n_points)]
# Print the number of contained points
print(f'{sum(contained)} out of {mesh.n_points} points are contained within the bounding box')
reduced_mesh, ridx = mesh.remove_points(np.logical_not(contained))
reduced_mesh.plot()
        
# filtered_points = mesh.points[contained]
# filtered_mesh = pv.PolyData(filtered_points)

# # filtered_mesh.save('filtered.obj')
# filtered_mesh.plot()
# reduced_mesh.plot()



