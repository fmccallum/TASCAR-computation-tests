import xml.etree.ElementTree as ET
import sys
from os.path import exists
from testclasses import *

xml_file = sys.argv[1]
if not exists(xml_file):
	raise NameError('No XML file found')
tree = ET.parse(xml_file)
root = tree.getroot()
rchildren = list(root)


data = []
graphs = []

for rchild in rchildren:
	if rchild.tag == "data":
		for dchild in list(rchild):
			if dchild.tag == "tscene":
				data.append(Data(dchild.attrib))
	elif rchild.tag == "graphs":
		for gchild in list(rchild):
			graphs.append(createGraph(gchild))

for graph in graphs:
	graph.generate_data(data)
for graph in graphs:
	graph.plot(data)

		

		
