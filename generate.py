import os
import csv
import json
from shutil import copyfile
from statistics import mean, median

walkpath = "_data/"
lwalkpath = len(walkpath)

stats = {}
odata = {}
groups = []

with open("_templates/group.html", 'r') as file:
	grptemplate = file.read()
with open("_templates/homework.html", 'r') as file:
	hwtemplate = file.read()

with open(os.path.join(walkpath, 'homeworklist.json'), 'r') as file:
	hwlist = json.load(file)

for hw in hwlist:
	ndir = os.path.join(walkpath, hw['dirname'])
	if not os.path.exists(ndir):
		os.makedirs(ndir)

def process_files(dir, filename):
	# print((dir, filename))
	f, e = os.path.splitext(filename)
	if e == '.csv' and f != "overall":
		path = os.path.join(dir, filename)
		promo = f.replace('s', '#')
		groups.append(promo)
		
		print("Processing " + promo + "...")
		
		data = [None]
		n = 1 # Dynamic length of data.
		
		with open(path, 'r', newline='') as file:
			header = file.readline().rstrip().split(',') # Header (first row)
			lheader = len(header)
			for i in range(1, lheader):
				hw = hwlist[i - 1]['dirname']
				npath = os.path.join(walkpath, hw, filename)  # walkpath/hw/promo.csv
				with open(npath, 'w', newline='') as nfile:
					wr = csv.writer(nfile)
					wr.writerow(['Login', header[i]])
			
			for line in file:
				parts = line.rstrip().split(',')
				lparts = len(parts)
				
				for i in range(n, lparts): # Increase size of data, as needed.
					data.append([])
					n += 1
				
				for i in range(1, lparts): # Skip login column.
					hw = hwlist[i - 1]['dirname']
					npath = os.path.join(walkpath, hw, filename)  # walkpath/hw/promo.csv
					with open(npath, 'a', newline='') as file:
						wr = csv.writer(file)
						wr.writerow([parts[0], parts[i]])
					
					if parts[i] != "":
						try: data[i].append(float(parts[i]))
						except: pass
		
		for i in range(1, n): # Skip login data (None)
			dataset = data[i]
			if not dataset: continue
			hw = hwlist[i - 1]['dirname']
			
			count = len(dataset)
			avg = round(mean(dataset), 2)
			med = round(median(dataset), 2)
			mini = min(dataset)
			maxi = max(dataset)
			
			if hw not in stats:
				stats[hw] = [["Promotion", "Count", "Average", "Median", "Minimum", "Maximum"]]
			
			stats[hw].append([promo, count, avg, med, mini, maxi])
			
			if promo not in odata:
				odata[promo] = [[], [], [], [], []]
			
			odata[promo][0].append(count)
			odata[promo][1].append(avg)
			odata[promo][2].append(med)
			odata[promo][3].append(mini)
			odata[promo][4].append(maxi)

for root, dirs, files in os.walk(walkpath):
	# print((root, dirs, files))
	dirname = root[lwalkpath:]
	if dirname == "":
		for filename in files:
			process_files(root, filename)
		break

print("Finishing touches...")

stats[""] = [["Promotion", "Number of Homework", "Average Count", "Global Average", "Average Median", "Average Minimum", "Average Maximum"]]

for promo in sorted(odata):
	final = odata[promo]
	
	count = len(final[0])
	avgcount = round(mean(final[0]), 2)
	avgavg = round(mean(final[1]), 2)
	avgmed = round(mean(final[2]), 2)
	avgmini = round(mean(final[3]), 2)
	avgmaxi = round(mean(final[4]), 2)
	
	stats[""].append([promo, count, avgcount, avgavg, avgmed, avgmini, avgmaxi])

print("Listing groups...")

npath = os.path.join(walkpath, 'groupslist.json')
with open(npath, 'w', newline='') as file:
	json.dump(groups, file)

print("Creating data files...")

for hw in stats:
	npath = os.path.join(walkpath, hw, 'overall.csv')
	with open(npath, 'w', newline='') as file:
		wr = csv.writer(file)
		for row in stats[hw]:
			wr.writerow(row)

print("Creating web pages for groups...")

for group in groups:
	with open(group + '.html', 'w') as file:
		content = grptemplate
		content = content.replace('##GROUP##', group)
		
		file.write(content)

print("Creating web pages for stats...")

for hw in hwlist:
	with open(hw['dirname'] + '.html', 'w') as file:
		content = hwtemplate
		content = content.replace('##DIRNAME##', hw['dirname'])
		content = content.replace('##NAME##', hw['name'])
		content = content.replace('##DESCRIPTION##', hw['description'])
		
		file.write(content)

print("Done.")
