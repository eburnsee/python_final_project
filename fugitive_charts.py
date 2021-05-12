import csv, math
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib import cm

def read_csv_make_lists():
	with open('fugitives_file.csv', mode='r', encoding="utf-8") as fugitives:
		dreader = csv.DictReader(fugitives)
		for row in dreader:
			# get each value from race column into a list
			if row['race'] != 'null':
				all_races.append(row['race'])
			# get each value from allegations columns into a list
			if row['allegation_1'] != 'null':
				all_allegations.append(row['allegation_1'])
			if row['allegation_2'] != 'null':
				all_allegations.append(row['allegation_2'])
			if row['allegation_3'] != 'null':
				all_allegations.append(row['allegation_3'])
			if row['year_of_birth'] != 'null':
				yob_list.append(row['year_of_birth'])
			if row['sex'] != 'null':
				all_sex_vals.append(row['sex'])

def make_bar_chart_png(labels, values, title, file_title):
	plt.bar(labels, values)
	plt.xticks(rotation='vertical')
	axes=plt.gca()
	axes.set_title(title, fontsize=14, pad=10.0)
	plt.savefig(f'{file_title}.png', bbox_inches='tight')

def make_gauge_chart(percent, group):
	title =f'Proportion of {group} Fugitives'
	deal =f'{percent}%'
	dial_colors = np.linspace(0,1,1000)
	figname = 'myDial_' + str(group)
	arrow_index = int(percent)*10
	labels = [' ']*len(dial_colors)*2
	labels[25] = '100%'
	labels[250] = '75%'
	labels[500] = '50%'
	labels[750] = '25%'
	labels[975] = '0%'
	fig, ax = plt.subplots()
	size_of_groups=np.ones(len(dial_colors)*2)
	# Create a pieplot, half white, half colored by your color array
	white_half = np.ones(len(dial_colors))*.5
	color_half = dial_colors
	color_pallet = np.concatenate([color_half, white_half])	 
	cs=cm.RdYlBu(color_pallet)
	pie_wedge_collection = ax.pie(size_of_groups, colors=cs, labels=labels)
	i=0
	for pie_wedge in pie_wedge_collection[0]:
		pie_wedge.set_edgecolor(cm.RdYlBu(color_pallet[i]))
		i=i+1
	# create a white circle to make the pie chart a dial
	my_circle=plt.Circle( (0,0), 0.3, color='white')
	ax.add_artist(my_circle)
	# create the arrow, pointing at specified index
	arrow_angle = (arrow_index/float(len(dial_colors)))*3.14159
	arrow_x = math.cos(arrow_angle)
	arrow_y = math.sin(arrow_angle)
	ax.arrow(0,0,-arrow_x,arrow_y, width=.02, head_width=.05,
				head_length=.1, fc='k', ec='k')
	ax.set_aspect('equal')
	plt.text(-1.07, 1.2,title, weight='bold', size=14)
	plt.text(-.1,.1,deal, weight='bold', size=14)
	plt.savefig(figname + '.png', bbox_inches='tight')
	im = Image.open(figname + '.png')
	width, height = im.size
	im = im.crop((0, 0, width, int(height/2.0))).save(figname + '.png')

def make_race_gauges():
	make_gauge_chart(race_percent_dict['White'], 'White')
	make_gauge_chart(race_percent_dict['Hispanic'], 'Hispanic')
	make_gauge_chart(race_percent_dict['Black'], 'Black')
	make_gauge_chart(race_percent_dict['Asian'], 'Asian')

#LISTS
# allegations lists
unique_allegations = []
all_allegations = []
count_per_all = []
# race lists
unique_race_list = []
all_races = []
count_per_race =[]
# sex lists
unique_sexes = []
all_sex_vals=[]
count_per_sex=[]
# yob lists
yob_list=[]
age_list = []

# read in relevant CSV data
read_csv_make_lists()

#ALLEGATION
# get each unique allegation
for allegation in all_allegations:
	if allegation not in unique_allegations:
		unique_allegations.append(allegation)
for all_cat in unique_allegations:
	counter = 0
	for allegation in all_allegations:
		if allegation == all_cat:
			counter += 1
	count_per_all.append(counter)
# find allegations with highest counts
alls_dict=dict(zip(unique_allegations, count_per_all))
high_counts_dict={}
for cat, count in alls_dict.items():
	if int(count)>10:
		high_counts_dict[cat] = count
# create bar chart for allegations
# make_bar_chart_png(high_counts_dict.keys(), high_counts_dict.values(), "Most Frequent Allegations of Federal Fugitives", "allegations")

# YOB/AGE
for yob in yob_list:
	age=2021-int(yob)
	age_list.append(age)
age_group_dict = {"Under 20":[],
					"20s":[],
					"30s":[],
					"40s":[],
					"50s":[],
					"60s":[],
					"70s":[],
					"80s":[],
					"Over 89":[]}
age_group_totals={}
for age in age_list:
	if age < 20:
		age_group_dict["Under 20"].append(age)
	if (age >= 20) and (age <=29):
		age_group_dict["20s"].append(age)
	if (age >= 30) and (age <=39):
		age_group_dict["30s"].append(age)
	if (age >= 40) and (age <=49):
		age_group_dict["40s"].append(age)
	if (age >= 50) and (age <=59):
		age_group_dict["50s"].append(age)
	if (age >= 60) and (age <=99):
		age_group_dict["60s"].append(age)
	if (age >= 70) and (age <=79):
		age_group_dict["70s"].append(age)
	if (age >= 80) and (age <=89):
		age_group_dict["80s"].append(age)
	if age > 89:
		age_group_dict["Over_89"].append(age)
for group, ages in age_group_dict.items():
	age_group_totals[group] = len(ages)
# make_bar_chart_png(age_group_totals.keys(), age_group_totals.values(), "Federal Fugitives by Age", "ages")

# SEX
for sex in all_sex_vals:
	if sex not in unique_sexes:
		unique_sexes.append(sex)
for group in unique_sexes:
	counter=0
	for sex in all_sex_vals:
		if sex == group:
			counter += 1
	count_per_sex.append(counter)
sex_totals = dict(zip(unique_sexes, count_per_sex))
# make_bar_chart_png(sex_totals.keys(), sex_totals.values(), "Federal Fugitives by Sex", 'sex')

# RACE
# get each unique value represented in races 
for race in all_races:
	if race not in unique_race_list:
		unique_race_list.append(race)
# get a count for each race category
for race_cat in unique_race_list:
	counter = 0
	for race in all_races:
		if race == race_cat:
			counter += 1
	count_per_race.append(counter)
# make_bar_chart_png(unique_race_list, count_per_race, "Federal Fugitives by Race", "race")
# create dictionary with races and their percentages of the whole
total = len(all_races)
percentages_list = []
for counter in count_per_race:
	per_cent=(int(counter)/total)*100
	percentages_list.append(int(per_cent))
race_percent_dict=dict(zip(unique_race_list, percentages_list))
make_race_gauges()