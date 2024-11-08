#!/usr/bin/env python
import rospy
import yaml
import copy
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Pose, PoseArray
from typing import List
from math import pi
from practica_1.msg import Floor

# Definir función para extraer configuración inicial y usarla después.
def get_initial_conf(archivo="/home/laboratorio/ros_workspace/src/actividad_1/src/practica_1/confs_y_poses/configuraciones.yaml") -> JointState:
    with open(archivo, "r") as f:
        conf_data = yaml.safe_load(f)
        conf_position = conf_data["configuracion_inicial"]

        conf = JointState()
        conf.header.stamp = rospy.Time.now()
        conf.position = conf_position

    return conf

# Del mismo modo extraer pose incial.
def get_initial_pose(archivo="/home/laboratorio/ros_workspace/src/actividad_1/src/practica_1/confs_y_poses/poses.yaml") -> Pose:
    with open(archivo, "r") as f:
        pose_data = yaml.safe_load(f)
        
    x_position = pose_data["pose_inicial"]["position"]["x"]
    y_position = pose_data["pose_inicial"]["position"]["y"]
    z_position = pose_data["pose_inicial"]["position"]["z"]
    w_orientation = pose_data["pose_inicial"]["orientation"]["w"]
    x_orientation = pose_data["pose_inicial"]["orientation"]["x"]
    y_orientation = pose_data["pose_inicial"]["orientation"]["y"]
    z_orientation = pose_data["pose_inicial"]["orientation"]["z"]

    # Pasar a tipo Pose
    pose = Pose()
    pose.position.x = x_position
    pose.position.y = y_position
    pose.position.z = z_position
    pose.orientation.w = w_orientation
    pose.orientation.x = x_orientation
    pose.orientation.y = y_orientation
    pose.orientation.z = z_orientation

    return pose

# Creamos una nueva pose a partir de la actual.
def create_pose(pose_init: Pose) -> Pose:
    new_pose = copy.deepcopy(pose_init)
    new_pose.position.x -= 0.1

    return new_pose

# Lo mismo con una conf.
def create_conf(conf_init: JointState) -> JointState:
    new_conf = copy.deepcopy(conf_init)
    new_conf.position[5] += 45 * pi / 180

    return new_conf

# Creamos una trayectoria.
def create_trajectory(pose: Pose) -> PoseArray:
    waypoints = [pose]
    
    pose.position.x += 0.1
    waypoints.append(copy.deepcopy(pose))

    pose.position.y += 0.1
    waypoints.append(copy.deepcopy(pose))

    pose.position.z-= 0.1
    waypoints.append(copy.deepcopy(pose))

    trajectory = PoseArray()
    trajectory.header.stamp = rospy.Time.now()
    trajectory.header.frame_id = "base_link"
    trajectory.poses = waypoints

    return trajectory

# Se añade el suelo.
def create_floor() -> Floor:
    pose_suelo = Pose()
    pose_suelo.position.x = 0.0
    pose_suelo.position.y = 0.0
    pose_suelo.position.z = -0.026

    floor = Floor()
    floor.pose_caja = pose_suelo
    floor.name = 'suelo'
    floor.tamaño = [2, 2, .05]

    return floor

# En función de lo que se quiera enviar se teclea un número.
def publish():
    rospy.init_node('basic_publisher', anonymous=True)
    pub_pose = rospy.Publisher("/mover_pose", Pose, queue_size=10)
    pub_conf = rospy.Publisher("/mover_configuracion", JointState, queue_size=10)
    pub_trajectory = rospy.Publisher("/trayectoria_cartesiana", PoseArray, queue_size=10)
    pub_obstacle = rospy.Publisher("/añadir_obstaculo", Floor, queue_size=10)
    rate = rospy.Rate(1)

    # Creamos variables para la configuración inicial, pose y el suelo.
    conf_init = get_initial_conf()
    pose_init = get_initial_pose()
    floor = create_floor()

    print("===============================================")
    print('0 -> Enviar obstáculo para crear suelo.')
    print('1 -> Enviar configuración inicial de yaml.\n2 -> Enviar segunda configuración.')
    print('3 -> Enviar pose de yaml.\n4 -> Enviar segunda pose.')
    print('5 -> Enviar trayectoria cartesiana.')
    print("===============================================")

    while not rospy.is_shutdown():

        # Pedir al usuario qué enviar.
        order = int(input("Ingrese la orden: "))

        if order == 0:
            pub_obstacle.publish(floor)

        elif order == 1:
            pub_conf.publish(conf_init)

        elif order == 2:
            conf_msg = create_conf(conf_init)
            pub_conf.publish(conf_msg)

        elif order == 3:
            pub_pose.publish(pose_init)

        elif order == 4:
            pose_msg = create_pose(pose_init)
            pub_pose.publish(pose_msg)

        elif order == 5:
            pose = create_pose(pose_init)
            trajectory_msg = create_trajectory(pose)
            pub_trajectory.publish(trajectory_msg)

        else:
            break

        rate.sleep() 

if __name__ == "__main__":
    try:
        publish()
    except rospy.ROSInterruptException:
        pass
