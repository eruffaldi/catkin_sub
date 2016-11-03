#!/usr/bin/python
#
# Catking Subfolders 
# Emanuele Ruffaldi @ SSSA 2016
#
#
import argparse
import xml.etree.ElementTree as ET
import os,sys
from collections import defaultdict 

known = set("pkg-config,pluginlib,boost,actionlib_msgs,visualization_msgs,sensor_msgs,rospy,roslibs,catkin,roscpp,cmake_modules,geometry_msgs,tf,message_generation,urdf,xacro,message_runtime,std_msgs,std_srvs".split(","))
known = known | set("twist_mux,gazebo_ros,interactive_marker_twist_server,actionlib,kdl_parser,trajectory_msgs,control_msgs,orocos_kdl,tf_conversions,cv_bridge".split(","))
known = known | set("fh_config,fh_description".split(","))

def commonpath(path1,path2):
	p1 = path1.split(os.sep)
	p2 = path2.split(os.sep)
	same = True
	for i in range(0,min(len(p1),len(p2))):
		if p1[i] != p2[i]:
			same = False
			break
	if same:
		# different length
		if len(p1) == len(p2):
			return common,".","."
		elif len(p1) > len(p2):
			i+=1
			common = os.sep.join(p2)
			a2b = os.sep.join([".." for j in range(0,len(p1)-i)])
			b2a = os.sep.join([".." for j in range(0,len(p2)-i)]+p1[i:])
		else:
			i+=1
			common = os.sep.join(p1)
			a2b = os.sep.join([".." for j in range(0,len(p1)-i)]+p2[i:])
			b2a = os.sep.join([".." for j in range(0,len(p2)-i)])
	else:
		common = os.sep.join(p1[0:i])
		a2b = os.sep.join([".." for j in range(0,len(p1)-i)]+p2[i:])
		b2a = os.sep.join([".." for j in range(0,len(p2)-i)]+p1[i:])
	return common,a2b,b2a

def getpackdeps(path):
	# look into package.xml
	#		buildtool_depend
	#		build_depend
	#		run_depend
	tree = ET.parse(path)
	root = tree.getroot()
	r = set()
	for x in root.iter('buildtool_depend'):
		r.add(x.text)
	for x in root.iter('build_depend'):
		r.add(x.text)
	for x in root.iter('run_depend'):
		r.add(x.text)
	return r

def getpacks(root,relroot):
	# direct if contains package.xml
	z ={}
	pf = os.path.join(root,"package.xml")
	if os.path.isfile(pf):
		z[os.path.split(root)[1]] = dict(type="pack",deps=getpackdeps(pf),path=relroot,children=[])
	else:
		for l in os.listdir(root):
			fp = os.path.join(root,l)
			if os.path.isdir(fp):
				rp = os.path.join(relroot,l)
				zz = getpacks(fp,rp) # ignore conflicts
				S = dict(type="meta",deps=set(),path=rp,children=zz)
				z[l] = S	
				z.update(zz)


	return z

#if __name__ == '__main__':
#	import sys
#	print commonpath(os.path.abspath(sys.argv[1]),os.path.abspath(sys.argv[2]))
if __name__ == '__main__':
	
	#TODO: support multiple full paths	
	parser = argparse.ArgumentParser(description='Catkin Partial Tree')
	parser.add_argument('package',nargs='*',help='needed packages')
	parser.add_argument('--full',required=True,help='full source base with all packages')
	parser.add_argument('--dest',default="src",help='destination path')
	parser.add_argument('--simulate',action="store_true")
	parser.add_argument('--abs',action="store_true",help="abs paths")
	parser.add_argument('--stats',action="store_true",help="stats only")
	parser.add_argument('--list',action="store_true",help="stats only")

	args = parser.parse_args()
	args.full = os.path.abspath(args.full)
	args.dest = os.path.abspath(args.dest)
	common,a2b,b2a = commonpath(args.full,args.dest)
	allpacks = getpacks(args.full,"")

	if args.stats:
		sknown = set(known.split(","))
		inp = set(allpacks.keys())
		allp = reduce(lambda x,y: x|y,[v["deps"] for v in allpacks.values()],set())
		ext = allp-inp-sknown
		print "total packages",len(allpacks)
		print "external packages",len(ext)
		if args.list:
			print "\n".join(sorted(list(ext)))
		sys.exit(0)
	elif args.list:
		print "\n".join(sorted(allpacks.keys()))

	if not os.path.isdir(args.full):
		os.mkdir(args.full)

	done = set()
	ds = set()
	todo = set(args.package)
	originator = defaultdict(set)
	while len(todo) > 0:
		p = todo.pop()
		done.add(p)
		pi = allpacks.get(p)

		if pi is None:
			if p not in known:
				print "unknown package",p,"from",originator[p]
			continue

		if pi["type"] != "meta":
			if not args.abs:				
				sp = os.path.join(b2a,pi["path"])
			else:
				sp = os.path.join(args.full,pi["path"])
			dp = os.path.join(args.dest,pi["path"])

			if args.simulate:
				print "symlink",sp,dp
			elif not os.path.islink(dp) and not os.path.isdir(dp):
				pdp = os.path.split(dp)[0]
				if not os.path.isdir(pdp):
					os.makedirs(pdp)
				os.symlink(sp,dp)

		# dependencies are all full packages
		deps = pi["deps"]
		for d in deps:
			originator[d].add(p)
		todo = todo | (deps-done)

	for p in done:
		pi = allpacks.get(p)
		if pi is not None:
			missing = pi["deps"]-done
			if len(missing) > 0:
				print p,"externals: ",",".join(list(missing))



