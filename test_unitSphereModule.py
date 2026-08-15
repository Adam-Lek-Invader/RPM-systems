import pytest

import numpy as np
from unitSphereModule import unitSpherePoint

class TestUnitSpherePoint_basic:
    def test_point_initialization(self):
        point = unitSpherePoint()
        assert np.all(np.isnan(point.coords))
        assert point.is_inUnitSphere() == False
        assert point.num_passed == 0
        assert point.is_selected == False
        assert point.max_neighbor_dist == np.Inf
        assert point.neighbors == {}

    def test_is_in_unit_sphere(self):
        # manual
        point = unitSpherePoint(1, 0, 0)
        assert point.is_inUnitSphere() == True

        point = unitSpherePoint(0, 1, 0)
        assert point.is_inUnitSphere() == True

        point = unitSpherePoint(0, 0, 1)
        assert point.is_inUnitSphere() == True

        point = unitSpherePoint(1, 1, 1)
        assert point.is_inUnitSphere() == False

        # random
        for _ in range(50):
            x,y,z = np.random.normal(0, 1, 3)
            mag = np.sqrt(x**2 + y**2 + z**2)
            x,y,z = x/mag, y/mag, z/mag  # normalize to unit sphere
            point = unitSpherePoint(x, y, z)
            assert point.is_inUnitSphere() == True

        for _ in range(50):
            x,y,z = np.random.normal(0, 1, 3)
            mag = np.sqrt(x**2 + y**2 + z**2)
            x,y,z = x/mag, y/mag, z/mag  # normalize to unit sphere
            pert_x,pert_y,pert_z = np.random.normal(0, 1, 3)  # perturb the point
            x += pert_x
            y += pert_y
            z += pert_z
            mag = np.sqrt(x**2 + y**2 + z**2)
            if mag == 1:
                continue  # skip if it accidentally ends up on the unit sphere
            point = unitSpherePoint(x, y, z)
            assert point.is_inUnitSphere() == False

    def test_point_creation(self):
        point = unitSpherePoint()
        for _ in range(50):
            point.create_new_point()
            assert point.is_inUnitSphere() == True

    def test_distance_to(self):
        # manual
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(2, 0, 0)
        distance = point1.distance_to(point2)
        assert np.isclose(distance, 1.0)

        point3 = unitSpherePoint(0, 0, 1)
        distance = point1.distance_to(point3)
        assert np.isclose(distance, np.sqrt(2.0))

        point4 = unitSpherePoint(0, 1, 1)
        distance = point1.distance_to(point4)
        assert np.isclose(distance, np.sqrt(3.0))

        for _ in range(50):
            point2.create_new_point()
            distance = point1.distance_to(point2)
            expected_distance = np.linalg.norm(point1.coords - point2.coords)
            assert np.isclose(distance, expected_distance)
