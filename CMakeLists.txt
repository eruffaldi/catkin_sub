cmake_minimum_required(VERSION 2.8)
project(catkin_sub)

find_package(catkin REQUIRED)
catkin_package()

catkin_python_setup()

catkin_install_python(PROGRAMS scripts/catkin_sub.py
                      DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})

