import requests, csv, time, re
from bs4 import BeautifulSoup
from fugitive import Fugitive


def find_fugs(url):
	"""opens a page on the fbi's website, iterates through fugitive reocrds, and
	 instantiates fugitive objects with names, urls"""
	# open the link
	fbi_fugs = s.get(url)
	# make the soup
	soup = BeautifulSoup(fbi_fugs.text, 'html.parser')
	# scrape the soup for fugitive record
	name_soup = soup.find_all(class_="name")
	for res in name_soup:
		res_1 = str(res).split('href="')
		res_2 = res_1[1].split('"')
		url = res_2[0]
		# fullname
		name = extract_data(res_2[1])
		name_split = name.split(" ")
		# split the name up; make conditional approach to lack of middle name
		if len(name_split) == 2:
			f_name = name_split[0]
			l_name = name_split[1]
			m_name = "null"
		elif len(name_split) == 3:
			f_name = name_split[0]
			m_name = name_split[1]
			l_name = name_split[2]
		elif len(name_split) > 3:
			f_name = name_split[0]
			m_name = name_split[1]
			l_name = name_split[2] + name_split[3]			
		wanted_by = "FBI"
		# instantiate the fugitive object
		this_fugitive = Fugitive(name, l_name, f_name, m_name, wanted_by, url)
		# add the fugitive to the list of fugitive objects
		fugitive_list.append(this_fugitive)

def get_next_page_links(url):
	"""adds the url for the next page to a list so they can be iterated through"""
	fbi_fugs = s.get(url)
	soup = BeautifulSoup(fbi_fugs.text, 'html.parser')
	link_soup = soup.find_all(class_='load-more')
	link_next_1 = str(link_soup).split('href="')
	link_next_2 = link_next_1[1].split('"')
	next_link = link_next_2[0]
	next_page_link_list.append(next_link)

def find_all_fugs():
	"""iterates through all pages and fugitives to give the complete list of fugitive objects"""
	find_fugs(fbi_fugs_url)
	get_next_page_links(fbi_fugs_url)
	for link in next_page_link_list:
		try:
			find_fugs(link)
			get_next_page_links(link)
		except IndexError:
			break

def extract_data(soup_obj):
	"""extracts HTML data from > <"""
	split_left=str(soup_obj).split(">")
	split_right=split_left[1].split("<")
	return split_right[0]

def get_page_data(fugitive):
	"""scrapes additional data from each fugitive's page"""
	this_fug_page = s.get(fugitive.url)
	fug_soup = BeautifulSoup(this_fug_page.text, 'html.parser')
	# summary
	sum_res = fug_soup.find(class_="summary")
	summary=extract_data(sum_res)
	summary_split = summary.split(";")
	if len(summary_split) == 1:
		if summary_split[0] == '':
			fugitive.allegation_1 = "null"
			fugitive.allegation_2 = "null"
			fugitive.allegation_3 = "null"
		else:
			fugitive.allegation_1 = summary_split[0].lower()
			fugitive.allegation_2 = "null"
			fugitive.allegation_3 = "null"
	if len(summary_split) == 2:
		fugitive.allegation_1 = summary_split[0].lower()
		fugitive.allegation_2 = summary_split[1].lower()
		fugitive.allegation_3 = "null"
	if len(summary_split) >= 3:
		fugitive.allegation_1 = summary_split[0].lower()
		fugitive.allegation_2 = summary_split[1].lower()
		fugitive.allegation_3 = summary_split[2].lower()
	# aliases
	try:
		ali_res = fug_soup.find(class_="wanted-person-aliases").find('p')
		aliases =extract_data(ali_res)
		alias_split=aliases.split(",")
		if len(alias_split) == 1:
			if alias_split[0] == '':
				fugitive.alias_1 ="null"
				fugitive.alias_2 ="null"
				fugitive.alias_3 ="null"
			else:
				fugitive.alias_1 = alias_split[0]
				fugitive.alias_2 = "null"
				fugitive.alias_3 = "null"
		if len(alias_split) == 2:
			fugitive.alias_1 = alias_split[0]
			fugitive.alias_2 = alias_split[1]
			fugitive.alias_3 = "null"
		if len(alias_split) >= 3:
			fugitive.alias_1 = alias_split[0]
			fugitive.alias_2 = alias_split[1]
			fugitive.alias_3 = alias_split[2]
	except AttributeError:
		fugitive.alias_1 ="null"
		fugitive.alias_2 ="null"
		fugitive.alias_3 ="null"
	# table of data
	try:
		table_res = fug_soup.find(class_="table table-striped wanted-person-description").find_all("td")
		temp_list=[]
		for ele in table_res:
			new_ele=extract_data(ele)
			temp_list.append(new_ele)
		title = temp_list[::2]
		data = temp_list[1::2]
		info_dict = dict(zip(title, data))
		for title, data in info_dict.items():
			if title == 'Date(s) of Birth Used':
				y_split = str(data).split(",")
				try:
					y_split_0 =y_split[1].split(" ")
					fugitive.yob = y_split_0[1]
				except IndexError:
					fugitive.yob=y_split[1]
			if title == 'Hair':
				if data == 'Unknown':
					fugitive.hair = 'null'
				else:
					fugitive.hair = data
			if title == 'Eyes':
				if data == 'Unknown':
					fugitive.eyes = 'null'
				else:
					fugitive.eyes = data
			if title == 'Height':
				height_0 = data.split(" ")
				if height_0[0] == 'Approximately':
					height_1 = re.sub('[^0-9]', '', height_0[1])
					height_2 = list(height_1)
					try:
						height_3 = (int(height_2[0])*12) + int(height_2[1])
						fugitive.height = height_3
					except IndexError:
						height_3 = (int(height_2[0])*12)
						fugitive.height = height_3
				else:
					height_1 = re.sub('[^0-9]', '', height_0[0])
					height_2 = list(height_1)
					try:
						height_3 = (int(height_2[0])*12) + int(height_2[1])
						fugitive.height = height_3
					except IndexError:
						height_3 = (int(height_2[0])*12)
						fugitive.height = height_3
			if title == 'Weight':
				weight = data.split(" ")
				if weight[0] == 'Approximately':
					fugitive.weight = weight[1]
				else:
					fugitive.weight = weight[0]
			if title == 'Sex':
				fugitive.sex = data
			if title == 'Race':
				if data == "White (Hispanic)":
					fugitive.race = "Hispanic"
				else:
					fugitive.race = data
			if title == 'NCIC':
				ncic_0 = data.split(";")
				ncic_1 = ncic_0[0]
				ncic =re.sub('[^0-9]', '', ncic_1) 
				fugitive.ncic = ncic
	except AttributeError:
		fugitive.yob = "null"
		fugitive.hair = "null"
		fugitive.eyes = "null"
		fugitive.height = "null"
		fugitive.weight = "null"
		fugitive.sex = "null"
		fugitive.race = "null"
		fugitive.ncic = "null"
	if fugitive.hair == None:
		fugitive.hair = "null"
	if fugitive.eyes == None:
		fugitive.eyes = "null"
	if fugitive.height == None:
		fugitive.height = "null"
	if fugitive.weight == None:
		fugitive.weight = "null"
	if fugitive.sex == None:
		fugitive.sex = "null"
	if fugitive.race == None:
		fugitive.race = "null"
	# reward
	try:
		reward_res = fug_soup.find(class_="wanted-person-reward").find("p")
		note_1 = extract_data(reward_res)
		fugitive.note_1 = note_1
	except AttributeError:
		fugitive.note_1 ="null"
	# remarks
	try:
		remarks_res = fug_soup.find(class_="wanted-person-remarks").find("p")
		note_2 = extract_data(remarks_res)
		fugitive.note_2=note_2
	except AttributeError:
		fugitive.note_2 = "null"
	# caution
	try:
		caution_res = fug_soup.find(class_="wanted-person-caution").find("p")
		note_3 = extract_data(caution_res)
		fugitive.note_3 = note_3
	except AttributeError:
		fugitive.note_3 = "null"
	fugs_w_page_data.append(fugitive)

def write_fug_csv():
	"""writes a csv with information from each fugitive object"""
	with open('fugitives_file.csv', mode='w', encoding="utf-8") as fugitives:
		fields=("ncic", "last_name", "first_name", "middle_name","wanted_by", "url", 
					"allegation_1", "allegation_2", "allegation_3", "alias_1", "alias_2", 
					"alias_3", "year_of_birth", "hair_color", "eye_color", "height",
					"weight", "sex", "race", "note_1", "note_2", "note_3")
		wr = csv.DictWriter(fugitives, fieldnames=fields, lineterminator="\n")
		wr.writeheader()
		for fugitive in fugs_w_page_data:
			if (fugitive.ncic == None) or (fugitive.ncic == "null"):
				continue
			else:
				wr.writerow({"ncic": fugitive.ncic, "last_name": fugitive.l_name, "first_name": fugitive.f_name, "middle_name": fugitive.m_name,
								"wanted_by": fugitive.wanted_by, "url": fugitive.url, "allegation_1": fugitive.allegation_1, "allegation_2": fugitive.allegation_2,
								"allegation_3": fugitive.allegation_3, "alias_1": fugitive.alias_1, "alias_2": fugitive.alias_2, "alias_3": fugitive.alias_3,
								"year_of_birth": fugitive.yob, "hair_color": fugitive.hair, "eye_color": fugitive.eyes, "height": fugitive.height, 
								"weight": fugitive.weight, "sex": fugitive.sex, "race": fugitive.race, "note_1": fugitive.note_1, "note_2": fugitive.note_2, 
								"note_3": fugitive.note_3})
		fugitives.close()

#####################################################################################################################
start = time.time()

s=requests.session()
fbi_fugs_url = "https://www.fbi.gov/wanted/fugitives"
fugitive_list = []
next_page_link_list=[]
find_all_fugs()
fugs_w_page_data=[]
for fugitive in fugitive_list:
	get_page_data(fugitive)
write_fug_csv()

end = time.time()
print(f'\nRUNTIME: {end-start}\n')