from os.path import exists
import os
import signal
import subprocess
import time
import psutil
import numpy as np
import math
import datetime
import pickle
import statistics
import matplotlib.pyplot as plt

import xml.etree.cElementTree as cET
import xml.etree.ElementTree as ET
import sys

def createGraph(graph):
	if graph.tag =="renderFile":
		return renderFile(graph.attrib)
		
	elif graph.tag =="jackPercentage":
		return jackPerc(graph.attrib)
	else:
		raise AttributeError('Please define valid metric for graph')

class Data:
	label =""
	path = ""
	data_option ="nothing"
	data_options = ["missing","overwrite","collate","nothing"]
	filetype=".txt"
	reference =None
	ref_option = ""
	def __init__(self,attrib):
		for key in attrib:
			if key=="path":
				self.path = attrib[key]
			elif key=="label":
				self.label = attrib[key]
			elif key=="data_option":
				option = attrib[key] 
				if option not in self.data_options:
					raise AttributeError(option + ' not a valid data saving option')
				else:
					self.data_option = option
			elif key=="reference":
				refattrib = {"path":attrib[key],"data_option":"collate"}
				self.reference = Data(refattrib)
			elif key=="ref_option":
				option = attrib[key] 
				if option not in self.data_options:
					raise AttributeError(option + ' not a valid data saving option')
				else:
					self.ref_option = option
		if self.reference is not None:
			if self.ref_option == "":
				self.ref_option = self.data_option
			self.reference.data_option = self.ref_option
			
			
			
	#check data takes list of files and returns list of files that need to be generated
	
	def check_exists(self,fileN):
		if exists(self.path+fileN):
			return True
		else:
			print("File "+self.path+fileN+ " not found")
			return False
	def check_prefix(self,prefix,path):
		for file in os.listdir(self.path+path):
			if file.startswith(prefix+"_"):
				return True
		return False
			
	
	def check_generate(self,prefix,path):
		if self.data_option == "nothing":
			return False
		elif self.data_option == "overwrite" or self.data_option == "collate":
			return True
		elif(self.check_prefix(prefix,path)):
			return False
		else:
			return True
	def save_data(self,prefix,path,results):
		if not os.path.exists(self.path+path):
			os.makedirs(self.path+path)
		if self.check_generate(prefix,path):
			if self.data_option == "overwrite":
				for file in os.listdir(self.path+path):
					if file.startswith(prefix+"_"):
						os.remove(self.path+path+file)
			fName = self.path+path+prefix+"_"+time.strftime("%Y%m%d-%H%M%S")+self.filetype
			with open(fName,'w')as f:
				for r in results:
					f.write(str(r)+'\n')
	def load_data(self,path):
		results = []
		x_axis = []
		if not os.path.exists(self.path+path):	
			return x_axis,results
		for file in os.listdir(self.path+path):
			prefix = file.split('_')[0]
			try:
				float(prefix)
			except ValueError:
				continue
			result =[]
			with open(self.path+path+file,'r')as f:
				content = f.read()
				result = [float(r) for r in (content.split())]
			x = float(prefix)
			if  x in x_axis:
				index = x_axis.index(x)
				results[index] = results[index] + result
			else:
				x_axis.append(x)
				results.append(list(result))
			
			
			
		return x_axis,results

class ContinueI(Exception):
	pass

class Graph:
	name = "Abstract graph"
	metrics =["renderFile","jackpercentage"]
	save_file = ""
	req_files = []
	tests = []
	xlabel=""
	ylabel=""
	refstring=" with reference subtracted"
	bars='none'
	path = ""
	repeats = 1
	plot_type = "mean"
	ref = False
	#option for saving metric data to file!! So it can be plotted separately
	#option for varying number of repeats based on length of test
	def __init__(self,attrib):
		for key in attrib:
			if key=="save_file":
				self.save_file = attrib[key]
			if key=="bars":
				self.bars = attrib[key]
			if key=="plot":
				self.plot_type = attrib[key]
			if key=="repeats":
				self.repeats = int(attrib[key])
			if key=="ref":
				if attrib[key].lower() == "true":
					self.ref = True
	
	def generate_data(self,data_arr):
		for d in data_arr:
			#don't try to generate anything if any of the required files don't exist
			try:
			#should put something in for reference?
				for rfile in self.req_files:
					if not d.check_exists(rfile):
						raise ContinueI
			except ContinueI:
				continue
			print("Getting data for "+ d.label)
			for i in range(self.repeats):
				print("Repeat " +str(i+1) +" out of "+str(self.repeats))
			#note: repeats only really make sense when using collate data option
				nT = 0	
				for t in self.tests:
					nT +=1
					print("Test "+str(nT) +" out of "+ str(len(self.tests))) 
					if d.check_generate(str(t),self.path):
						print("Generating data")
						result = self.run_test(t,d)
						d.save_data(str(t),self.path,result)
					if d.reference is not None:
						if d.reference.check_generate(str(t),self.path):
							print("Generating reference data")
							result = self.run_test(t,d.reference)
							d.reference.save_data(str(t),self.path,result)
		
	def runTest(t,d):
		pass		

	def plotmean(self,data_arr):
		labels=[]

		for d in data_arr:
			x_axis,results = d.load_data(self.path)
			zipped=zip(x_axis,results)
			zipped=sorted(zipped)
			x_axis=[x for x,_ in zipped]
			results=[result for _,result in zipped]
			
			means = [statistics.mean(result) for result in results]
			stdevs = [statistics.stdev(result) for result in results]
			brange =[]
			brange.append( [means[count]-min(result) for count,result in enumerate(results)])
			brange.append( [max(result)-means[count] for count,result in enumerate(results)])
			#if subtracting reference mean, can oly use data in both datasets
			if self.ref == True:
				if d.reference is None:
					continue
					#raise AttributeError("No reference data provided")
				xref,refresults = d.reference.load_data(self.path)
				results = [rlist for i,rlist in enumerate(results) if x_axis[i] in xref]
				x_axis = [xval for i,xval in enumerate(x_axis) if x_axis[i] in xref]
				refresults = [rlist for i,rlist in enumerate(refresults) if xref[i] in x_axis]
				refmeans = [statistics.mean(result) for result in refresults]
				means = [statistics.mean(result) -refmeans[xref.index(x_axis[i])] for i,result in enumerate(results)]
				

			if means:
				if self.bars =="std":
					plt.errorbar(x_axis,means,stdevs,marker='x', capsize=8,label=d.label)
				elif self.bars =="range":
					plt.errorbar(x_axis,means,brange,marker='x', capsize=8,label=d.label)
				else:
					plt.plot(x_axis,means, label=d.label)
		plt.xlabel(self.xlabel)
		plt.ylabel(self.ylabel)
		if self.ref ==True:
			plt.title(self.name+self.refstring)
		else:
			plt.title(self.name)
		plt.legend()
		plt.show()
	
	def plotall(self,data_arr):
		labels=[]

		for d in data_arr:
			x_axis,results = d.load_data(self.path)
			for count,a in enumerate(x_axis):
				plt.plot(results[count])
				plt.xlabel('sample')
				plt.ylabel(self.name)
				plt.title('All results for '+self.name+' '+d.label+ ' test '+ str(a))
				plt.show()
			if self.ref == True:
				if d.reference is None:
					continue
					#raise AttributeError("No reference data provided")
				xref,refresults = d.reference.load_data(self.path)
				for count,a in enumerate(xref):
					plt.plot(refresults[count])
					plt.xlabel('sample')
					plt.ylabel(self.name)
					plt.title('All reference results for '+self.name+' '+d.label+ ' test '+ str(a))
					plt.show()

					
	def plot(self,data_arr):
		if self.plot_type.lower() == "mean":
			self.plotmean(data_arr)
		elif self.plot_type.lower() == "all":
			self.plotall(data_arr)
					
		
	def file_sources_circle(self,N,path,sourceT = "pink",fileName="sources.tsc"):
		source_string=""
		if sourceT=="pink":
			source_string ="<source name=\"target\"><position>0 1 0 0</position><sound><plugins><pink 	level=\"90\" fmax=\"16000\"/></plugins></sound></source>"
		elif sourceT == "none":
			source_string ="<source name=\"target\"><position>0 1 0 0</position><sound></sound></source>"
		elif sourceT=="file":
			source_string ="<source name=\"target\"><position>0 1 0 0</position><sound><plugins><sndfile name=\"demo_04_data/footsteps.wav\" level=\"65\" loop=\"0\"/></plugins></sound></source>"
		      
	
		et = ET.parse(path+fileName)
		root = et.getroot()
		scene = root[0]
		for i in range(N):
			angle_deg = i*2*math.pi/N
			z = "0"
			x = str(math.cos(angle_deg))
			y = str(math.sin(angle_deg))
			position = "0 "+x+" "+y+" 0"
			name = "target" + str(i)
		
			source_el = ET.fromstring(source_string)
			source_el.find("position").text = position
			source_el.set('name',name)

			scene.append(source_el)
		et.write(path+'tempsources.tsc')

class renderFile(Graph):
	name = "TASCAR Renderfile time"
	req_files = ["sources.tsc"]
	path = "data/render-file/"
	sourceT="pink"
	samples = 1
	xlabel= 'sources'
	ylabel=name
	def __init__(self,attrib):
		super().__init__(attrib)
		for key in attrib:
			if key=="sources":
				self.tests = [int(x) for x in attrib[key].split()]
			if key=="samples":
				self.samples = int(attrib[key])

	
	def run_test(self,sourceN,data):
		self.file_sources_circle(sourceN,data.path,self.sourceT)
		results = []
		for i in range(self.samples):
			cmd = ["tascar_renderfile","-o outfile.wav",data.path+"tempsources.tsc"]
			start = time.time()
			pro = subprocess.run(cmd,stdout=subprocess.PIPE)
			results.append(time.time()-start)
		return results
		




class jackPerc(Graph):
	name = "Jack load percentage"
	req_files = ["sources.tsc"]
	path ="data/jack-percentage/"
	sourceT="pink"
	run_time = 10
	source_time = 0.1
	gui=False
	xlabel= 'sources'
	ylabel=name
	
	def __init__(self,attrib):
		super().__init__(attrib)
		
		for key in attrib:
			if key=="sources":
				self.tests = [int(x) for x in attrib[key].split()]
			if key =="gui":
				if attrib[key].lower() == "true":
					self.gui = True
			if key=="source_time":
				self.source_time = float(attrib[key])
			if key=="run_time":
				self.run_time = float(attrib[key])
	
	def run_test(self,sourceN,data):
		self.file_sources_circle(sourceN,data.path,self.sourceT)
		wait_time = self.source_time*sourceN+2
		jackFile = "jackcpu.txt"
		endcmd = ["killall", "jmatconvol"]
		jackcmd = "timeout --kill-after=1 "+str(self.run_time)+" jack_cpu_load >> "+jackFile
		
		cmd = ["tascar",data.path+"tempsources.tsc"]
		if not self.gui:
			cmd = ["tascar_cli",data.path+"tempsources.tsc"]
			

		if exists(jackFile):
			os.remove(jackFile)
		print("Starting TASCAR")
		pro = subprocess.Popen(cmd,stdout=subprocess.PIPE, preexec_fn=os.setsid)
		ps = psutil.Process(pro.pid)
		print("waiting for "+str(wait_time)+ " seconds")
		time.sleep(wait_time)
		#start measuring jack percentage usage over runtime
		print("Now measuring jack usage for "+str(self.run_time)+" seconds")
		os.system(jackcmd)
		
		print("Finished, now closing TASCAR")
		os.killpg(os.getpgid(pro.pid),signal.SIGKILL)
	
	

		print("Closing jconvolver if not already closed")
		pro = subprocess.Popen(endcmd,stdout=subprocess.PIPE, preexec_fn=os.setsid)
	
		results = []
		if exists(jackFile):
			with open(jackFile) as f:
				for line in f:
					results.append(float(line.split()[-1]))
			os.remove(jackFile)
		else:
			raise ValueError("Expected log file")
		time.sleep(2)
		return results




