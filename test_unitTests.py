from pyparsing import col
import pytest

import os
import numpy as np
from unitSphereModule import unitSpherePoint, unitSphere
import file_operations

def make_simple_sphere()->unitSphere:
    sphere = unitSphere(n=6)
    sphere.points[0].coords = np.array([1,0,0])
    sphere.points[1].coords = np.array([-1,0,0])
    sphere.points[2].coords = np.array([0,1,0])
    sphere.points[3].coords = np.array([0,-1,0])
    sphere.points[4].coords = np.array([0,0,1])
    sphere.points[5].coords = np.array([0,0,-1])
    return sphere

def get_new_unique_file_name(file_name=".temp_file")->str:
    i = 0
    true_file_name = file_name
    while True:
        if os.path.exists(true_file_name):
            true_file_name = file_name + str(i)
            i += 1
        else:
            return true_file_name

class TempFile:    
    def __enter__(self):
        self.file_name = get_new_unique_file_name()
        open(self.file_name, "w").close()
        return self.file_name

    def __exit__(self, exc_type, exc_value, traceback):
        if os.path.exists(self.file_name):
            os.remove(self.file_name)


def Vector3_str_format(Vec3:np.ndarray|list):
    """
    Creates data in x|y|z format as in Vector3.
    
    """
    return f"{Vec3[0]:.9f}|{Vec3[1]:.9f}|{Vec3[2]:.9f}"

def generate_row(time, num_of_probes=3, axis=3):
    """
    Generates 1 row of data for the CSV format
    """
    # Bee chamber specific
    outer_frame_speed = np.random.randint(1,20)
    bee_chamber_speed = np.random.randint(1,20)

    outer_frame_ang = np.random.uniform(0, 10)
    bee_chamber_ang = np.random.uniform(0, 10)

    bee_chamb_xyz = Vector3_str_format(np.random.uniform(-9.81, 9.81, size=3))

    if axis == 2:
        row = f"{time:.6f},{outer_frame_speed},{bee_chamber_speed},{outer_frame_ang},{bee_chamber_ang},{bee_chamb_xyz}"
    elif axis == 3:
        inner_frame_ang = np.random.uniform(-10,10)
        inner_frame_speed = np.random.uniform(-10,10)
        row = f"{time:.6f},{outer_frame_speed},{inner_frame_speed},{bee_chamber_speed},{outer_frame_ang},{inner_frame_ang},{bee_chamber_ang},{bee_chamb_xyz}"
    else:
        raise ValueError("too many axes required")
 
    # Probes
    for i in num_of_probes:
        pos3 = Vector3_str_format(np.random.uniform(-9.81,9.81,size=3))
        vel3 = Vector3_str_format(np.random.uniform(-9.81,9.81,size=3))
        acc3 = Vector3_str_format(np.random.uniform(-9.81,9.81,size=3))
        row += f",{pos3},{vel3},{acc3}"

    return row

def write_random_csv_data_file(file_name,point_num=10, axis=3, probe_num=3):
    HEADER = "Time[s],OuterFrameSpeed[deg/s],BeeChamberSpeed[deg/s],OuterFrameAng[deg],BeeChamberAng[deg],BeeChamb_XYZ[m]"
    for i in range(probe_num):
        probe_id = Vector3_str_format(np.random.uniform(-10,10,size=3))
        HEADER += f",{probe_id}_pos"
    with os.open(file_name, os.O_WRONLY):
        pass



class TestUnitSpherePoint_basic:
    def test_point_initialization(self):
        point = unitSpherePoint()
        assert np.all(np.isnan(point.coords))
        assert point.is_inUnitSphere() == False
        assert point.num_passed == 0
        assert point.max_neighbour_dist == np.Inf
        assert point.neighbours == {}

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

        # other types of data
        point2 = np.array([1,0,0])
        point3 = np.array([2,0,0])
        assert np.isclose(point1.distance_to(point2), 0.0)
        assert np.isclose(point1.distance_to(point3), 1.0)

        point2 = [1,0,0]
        point3 = [2,0,0]
        assert np.isclose(point1.distance_to(point2), 0.0)
        assert np.isclose(point1.distance_to(point3), 1.0)

        

    def test_neigbours(self):
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(0, 1, 0)

        # reference check
        point1.neighbours[point2] = 1.0
        point2.id = 7
        assert list(point1.neighbours.keys())[0].id == 7

        # uniqness check
        point3 = unitSpherePoint(0, 0, 1)
        point4 = unitSpherePoint(0, 0, 1)
        point5 = unitSpherePoint(0, 0, 1)
        point1.neighbours[point3] = 1.0
        point1.neighbours[point4] = 1.0
        nei_list = list(point1.neighbours.keys())
        assert point5 not in nei_list
        for nei in nei_list:
            how_many_same = 0
            for other_nei in nei_list:
                if nei == other_nei:
                    how_many_same += 1
            assert how_many_same == 1

    def test_mutables_not_shared_between_instances(self):
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(0, 1, 0)
        point3 = unitSpherePoint(0, 0, 1)

        # dict of neighbours should be unique to each instance
        point1.neighbours[point2] = 1.0
        assert len(point1.neighbours) == 1
        assert len(point2.neighbours) == 0
        assert len(point3.neighbours) == 0

        # coords should be unique to each instance
        assert np.all(point1.coords) == np.all(np.array([1, 0, 0]))
        assert np.all(point2.coords) == np.all(np.array([0, 1, 0]))
        assert np.all(point3.coords) == np.all(np.array([0, 0, 1]))

class TestUnitSphere_basic:
    def test_initialization(self):
        # random sampling
        sphere = unitSphere(n=100)
        assert len(sphere.points) == 100
        for i, point in enumerate(sphere.points):
            assert isinstance(point, unitSpherePoint)
            assert point.is_inUnitSphere() == True
            assert point.id == i
        assert sphere.neighbours_assigned == False

        # Polar Coordinates Subdivision
        sphere = unitSphere(n=30, method="polarCoordsSubdivision")
        for i, point in enumerate(sphere.points):
            assert isinstance(point, unitSpherePoint)
            assert point.is_inUnitSphere() == True
            assert point.id == i
        assert sphere.neighbours_assigned == False

        # IcoSphere Subdivision
        sphere = unitSphere(n=3, method="icoSphere")
        for i, point in enumerate(sphere.points):
            assert isinstance(point, unitSpherePoint)
            assert point.is_inUnitSphere() == True
            assert point.id == i
        assert sphere.neighbours_assigned == False

    def test_find_closest(self):
        # manual
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(0, 1, 0)
        point3 = unitSpherePoint(0, 0, 1)
        point4 = unitSpherePoint(1, 1, 0)
        point5 = unitSpherePoint(1, 0, 1)
        sphere = unitSphere(n=0)
        sphere.points = [point1,point2,point3,point4,point5]
        test_point = unitSpherePoint(1.1, 0.9, 0)
        assert sphere.find_closest(test_point)["point_ref"] == point4

    def test_assign_neighbours(self):
        # manual
        point1 = unitSpherePoint(1, 0, 0)
        point2 = unitSpherePoint(0, 1, 0)
        point3 = unitSpherePoint(0, 0, 1)
        point4 = unitSpherePoint(1, 1, 0)
        point5 = unitSpherePoint(1, 0, 1)
        sphere = unitSphere(n=0)
        sphere.points = [point1, point2, point3, point4, point5]
        sphere.assign_neighbours(neighbour_num=2)

        assert sphere.neighbours_assigned == True
        point1_neighbours = list(point1.neighbours.keys())
        assert point4 in point1_neighbours
        assert point5 in point1_neighbours
        assert point1.neighbours[point4] == 1.0
        assert point1.neighbours[point5] == 1.0
        assert point1.max_neighbour_dist == 1.0

        for point in sphere.points:
            assert len(point.neighbours) == 2
            for neighbour, distance in point.neighbours.items():
                assert isinstance(neighbour, unitSpherePoint)
                assert distance > 0

        sphere = make_simple_sphere()
        sphere.assign_neighbours(4)
        for p in sphere.points:
            not_nei = -p.coords
            not_nei = sphere.find_closest(not_nei)
            not_nei = not_nei["point_ref"]
            for other_p in sphere.points:
                if p == other_p:
                    continue
                if other_p == not_nei:
                    assert other_p not in list(p.neighbours.keys())
                else:
                    assert other_p in list(p.neighbours.keys())

        # random
        sphere = unitSphere(n=20)
        sphere.assign_neighbours(neighbour_num=5)
        assert sphere.neighbours_assigned == True
        for point in sphere.points:
            assert len(point.neighbours) == 5
            max_dist = 0.0
            for neighbour, distance in point.neighbours.items():
                if distance > max_dist:
                    max_dist = distance
                assert isinstance(neighbour, unitSpherePoint)
                assert distance > 0
            assert max_dist == point.max_neighbour_dist

    def test_mark_traj_same_point(self):
        sphere = make_simple_sphere()
        with pytest.raises(ValueError) : sphere.mark_trajectory(np.array([[1,0,0]])) 

        # staying in the same point
        sphere = make_simple_sphere()
        sphere.assign_neighbours(4) # all points expect the furthest one on the other side
        data_xyz = np.array([[1,0,0],[1.1, 0.1, 0], [0.9, 0.2, 0]])
        nei_skips = sphere.mark_trajectory(data_xyz)
        assert nei_skips == 0
        closest = sphere.find_closest([1,0,0])
        for p in sphere.points:
            if p == closest["point_ref"]:
                assert p.num_passed == 1
                assert p == sphere.last_marked_point
            else:
                assert p.num_passed == 0

    def test_make_traj_next_nei(self):
        # marking traj for next neigbours
        sphere = make_simple_sphere()
        sphere.assign_neighbours(4) # all points expect the furthest one on the other side
        data_xyz = np.array([[1.1,-0.1,0.2],[0.1, 1.1, 0], [0, -0.2, 0.9]])
        nei_skips = sphere.mark_trajectory(data_xyz)
        assert nei_skips == 0

        closest_list = []
        for data in data_xyz:
            closest = sphere.find_closest(data)
            closest_list.append(closest["point_ref"])

        for p in sphere.points:
            if p in closest_list:
                assert p.num_passed == 1
                if p == sphere.find_closest(data_xyz[-1])["point_ref"]:
                    assert p == sphere.last_marked_point
            else:
                assert p.num_passed == 0


    def test_make_traj_further_than_nei(self):
        # interpolate and go into circle
        sphere = make_simple_sphere()
        sphere.assign_neighbours(4) # all points expect the furthest one on the other side
        data_xyz = np.array([[1.1,-0.1,0.2],[-1, 0.1, 0], [1.1, 0, -0.2]])
        points_to_be_marked = [[1,0,0],[0,1,0],[-1,0,0],[0,0,-1]]
        nei_skips = sphere.mark_trajectory(data_xyz)
        assert nei_skips == 2

        passed_points = []
        for data_p in points_to_be_marked:
            closest = sphere.find_closest(data_p)
            passed_points.append( closest["point_ref"] )

        for p in sphere.points:
            if p in passed_points:
                assert p.num_passed >= 1
                if p == sphere.find_closest(data_xyz[-1])["point_ref"]:
                    assert p == sphere.last_marked_point
                    assert p.num_passed == 2
                else:
                    assert p.num_passed == 1
            else:
                assert p.num_passed == 0

class TestCSVReader:
    def test_data_type_parse(self):
        with TempFile() as fileName:
            # create file with rand data
            csv_header_list = ["one","two","three","four"]
            with open(fileName, "w") as fd:
                # header
                row = f"{csv_header_list[0]}"
                for col_name in csv_header_list[1:]:
                    row += f",{col_name}"
                row += '\n'
                fd.write(row)
                # data rows
                for i in range(5):
                    tmp_int1 = -5
                    tmp_int2 = np.random.randint(2000)
                    tmp_float32 = np.random.uniform()
                    tmp_Vec3 = Vector3_str_format(np.random.uniform(size=3))
                    row = f"{tmp_int1},{tmp_int2},{tmp_float32},{tmp_Vec3}\n"
                    fd.write(row)
            # parse using csv reader
            CSV_Parser = file_operations.CSV_DataParser(fileName, maxBuffCnt=50)
            for (col_names,buffers,buff_row_cnt) in CSV_Parser.gen_get_data():
                # buffer cnt check
                assert buff_row_cnt == 5
                # header check
                for i,col_name in enumerate(col_names):
                    assert col_name == csv_header_list[i]
                # type check
                assert buffers[0].dtype == np.int32
                assert buffers[1].dtype == np.int32
                assert buffers[2].dtype == np.float32
                assert buffers[3].dtype == np.float32
                assert buffers[3].shape[1] == 3
                for buff in buffers:
                    assert buff.shape[0] == 5

    def test_buffer_spliting(self):
        # no split (MAX_BUFF_SIZE > ROW_CNT)
        ROW_CNT = 20
        MAX_BUFF_SIZE = 50
        with TempFile() as fileName:
            # prepare file
            with open(fileName, "w") as fd:
                # header
                row = "awawka\n"
                fd.write(row)
                # data rows
                for i in range(ROW_CNT):
                    row = f"{i}\n"
                    fd.write(row)

            # parse using csv reader
            CSV_Parser = file_operations.CSV_DataParser(fileName, maxBuffCnt=MAX_BUFF_SIZE)
            for i,(col_names,buffers,buff_row_cnt) in enumerate(CSV_Parser.gen_get_data()):
                assert i == 0
                assert len(col_names) == 1
                assert buffers[0].shape[0] == ROW_CNT
                assert buff_row_cnt == ROW_CNT
                for iter in range(ROW_CNT):
                    assert iter == buffers[0][iter]

        # one split (MAX_BUFF_SIZE < ROW_CNT)
        ROW_CNT = 70
        MAX_BUFF_SIZE = 50
        with TempFile() as fileName:
            # prepare file
            with open(fileName, "w") as fd:
                # header
                row = "awawka,floatawaw\n"
                fd.write(row)
                # data rows
                for i in range(ROW_CNT):
                    row = f"{i},{i*0.5}\n"
                    fd.write(row)

            # parse using csv reader
            CSV_Parser = file_operations.CSV_DataParser(fileName, maxBuffCnt=MAX_BUFF_SIZE)
            for i,(col_names,buffers,buff_row_cnt) in enumerate(CSV_Parser.gen_get_data()):
                assert i < 2
                assert len(col_names) == 2
                if i == 0:
                    assert buffers[0].shape[0] == MAX_BUFF_SIZE
                    assert buff_row_cnt == MAX_BUFF_SIZE
                    for iter in range(MAX_BUFF_SIZE):
                        assert iter+i*MAX_BUFF_SIZE == buffers[0][iter]
                        assert (iter+i*MAX_BUFF_SIZE)*0.5 == buffers[1][iter]
                elif i == 1:
                    assert buffers[0].shape[0] == ROW_CNT-MAX_BUFF_SIZE
                    assert buff_row_cnt == ROW_CNT-MAX_BUFF_SIZE
                    for iter in range(ROW_CNT-MAX_BUFF_SIZE):
                        assert iter+i*MAX_BUFF_SIZE == buffers[0][iter]
                        assert (iter+i*MAX_BUFF_SIZE)*0.5 == buffers[1][iter]
                
            





            