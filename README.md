# catkin_sub

Tool for creating sub-repositories of catkin

## Usage

The tool is provided as ros package (catkin) or can be used as script:

	rosrun catkin_sub ...
	python catkin_sub.py ...
	catkin_sub.py

The main usage is:

	catkin_sub --full path-to-source pkg1 ... pkgN

The tool will analyze the sources and make a catkin workspace (in ./src) containing the packages and all the dependencies as found in the sources using symbolic links. It will also notify about unknown packages. Packages that are contained in folders are restored in a folder with the same name

# TODO

- inspect .rosinstall
- inspect rospack info 
