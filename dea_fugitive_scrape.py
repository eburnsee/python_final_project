import requests, time, csv, re
from bs4 import BeautifulSoup
from fugitive import Fugitive
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def extract_data(soup_obj):
	"""extracts HTML data from ><"""
	split_left=str(soup_obj).split(">")
	split_right=split_left[1].split("<")
	return split_right[0]

def extract_ncic(soup_ele):
	"""extracts HTML data from <br/><br/>"""
	split=str(soup_ele).split("<br/>")
	return split[1]

def get_base_fugs():
	"""using selenium to iterate through the pages of DEA fugitives to get the links to each fugitives profile"""
	for numb in range(0,65):
		fug_iter_page = "https://www.dea.gov/fugitives/all?keywords=&page=" + str(numb)
		browser.get(fug_iter_page)
		page_source=browser.page_source
		soup_sel = BeautifulSoup(page_source, 'html.parser')
		link_soup = soup_sel.find_all(class_="teaser__heading")
		for ele in link_soup:
			link_split_0 = str(ele).split('href="')
			link_split_1 = link_split_0[1].split('">')
			url ="https://www.dea.gov" + link_split_1[0]
			name_split = link_split_1[1].split('<')
			name= name_split[0].split(" ")
			if len(name) == 2:
				f_name = name[0]
				l_name = name[1]
				m_name = "null"
			elif len(name) == 3:
				if name[1] == '':
					f_name = name[0]
					m_name = "null"
					l_name = name[2]
				else:
					f_name = name[0]
					m_name = name[1]
					l_name = name[2]
			elif len(name) >3:
				f_name = name[0]
				m_name = name[1]
				l_name = name[2] + name[3]
			wanted_by = "DEA"
			this_fugitive = Fugitive(name, l_name, f_name, m_name, wanted_by, url)
			fugitive_list.append(this_fugitive)

def get_fug_info(fugitive):
	'''Gets profile information from a fugitive's profile'''
	fug_page = fugitive.url
	browser.get(fug_page)
	page_source=browser.page_source
	soup_sel = BeautifulSoup(page_source, 'html.parser')
	# aliases, allegations
	al_al_res = soup_sel.find_all(class_="meta__value")
	for ele in al_al_res:
		if ele == al_al_res[0]:
			aliases=extract_data(ele)
			if (aliases == '') or (aliases == "None") or (aliases == "-") or (aliases == "N/A") or (aliases == "--") or (aliases == "NA"):
				fugitive.alias_1 = "null"
				fugitive.alias_2 = "null"
				fugitive.alias_3 = "null"
			else:
				alias_semi_colon = str(aliases).split(";")
				if len(alias_semi_colon) == 1:
					alias_commas = str(aliases).split(",")
					if len(alias_commas) == 1:
						fugitive.alias_1 = re.sub('[^a-zA-Z]', '', aliases)
						fugitive.alias_2 = "null"
						fugitive.alias_3 = "null"
					if len(alias_commas) == 2:
						fugitive.alias_1 = re.sub('[^a-zA-Z]', '', alias_commas[0])
						fugitive.alias_2 = re.sub('[^a-zA-Z]', '', alias_commas[1])
						fugitive.alias_3 = "null"
					elif len(alias_commas) >= 3:
						fugitive.alias_1 = re.sub('[^a-zA-Z]', '', alias_commas[0])
						fugitive.alias_2 = re.sub('[^a-zA-Z]', '', alias_commas[1].strip())
						fugitive.alias_3 = re.sub('[^a-zA-Z]', '', alias_commas[2].strip())
				elif len(alias_semi_colon) == 2:
					fugitive.alias_1 = re.sub('[^a-zA-Z]', '', alias_semi_colon[0])
					fugitive.alias_2 = re.sub('[^a-zA-Z]', '', alias_semi_colon[1].strip())
					fugitive.alias_3 = "null"
				elif len(alias_semi_colon) >= 3:
					fugitive.alias_1 = re.sub('[^a-zA-Z]', '', alias_semi_colon[0].strip())
					fugitive.alias_2 = re.sub('[^a-zA-Z]', '', alias_semi_colon[1].strip())
					fugitive.alias_3 = re.sub('[^a-zA-Z]', '', alias_semi_colon[2].strip())
		elif ele == al_al_res[1]:
			allegations = extract_data(ele)
			fugitive.allegation_1 = allegations
			fugitive.allegation_2 = "null"
			fugitive.allegation_3 = "null"
	# table data
	table_res = soup_sel.find('table').find_all('td')
	temp_list=[]
	for ele in table_res:
		new_ele=extract_data(ele)
		temp_list.append(new_ele)
	title = temp_list[::2]
	data = temp_list[1::2]
	info_dict = dict(zip(title, data))
	for title, data in info_dict.items():
		if title == 'Race':
			if data == "":
				fugitive.race = "null"
			else:
				fugitive.race = data
		if title == 'Height':
			if (data == "'") or (data == "0'0\"") or (data == '\' "') or (data == "0'0") or (data == "0' 0") or (data == "' "):
				fugitive.height = 'null'
			else:
				height_0 =re.sub('[^0-9]', '', data)
				height_1 = list(height_0)
				try:
					height_2 = (int(height_1[0])*12) + int(height_1[1])
					fugitive.height = height_2
				except IndexError:
					height_2 = (int(height_1[0])*12)
					fugitive.height = height_2
		if title == 'Weight':
			if (data == '') or (data == '0'):
				fugitive.weight = "null"
			else:
				fugitive.weight = data
		if title == 'Hair Color':
			if data == 'Unknown':
				fugitive.hair = 'null'
			else:
				fugitive.hair = data
		if title == 'Eye Color':
			if data == 'Unknown':
				fugitive.eyes = 'null'
			else:
				fugitive.eyes = data
		if title == 'NCIC #':
			if data == "":
				ncic_0 = extract_ncic(table_res[17])
				ncic_1 = ncic_0.strip()
				ncic_2 = ncic_1.split("/")
				ncic_3 = ncic_2[0]
				ncic_4 = re.sub('[^0-9]', '', ncic_3)
				fugitive.ncic = ncic_4
			else:
				ncic_0 = re.sub('[^0-9]', '', data)
				fugitive.ncic = ncic_0
		if title == "Notes":
			if (data == '') or (data =="--"):
				fugitive.note_1 = "null"
				fugitive.note_2 = "null"
				fugitive.note_3 = "null"
			else:
				fugitive.note_1 = data
				fugitive.note_2 = "null"
				fugitive.note_3 = "null"
	# yob
	yob_res = soup_sel.find("time")
	if (yob_res == None) or (yob_res == ""):
		fugitive.yob = 'null'
	else:
		yob = extract_data(yob_res)
		fugitive.yob = yob
	fugitive_list_2.append(fugitive)

def get_male_list():
	for numb in range(0,60):
		male_fugs_url = "https://www.dea.gov/fugitives/all?f%5B0%5D=fugitive_sex%3A2566&keywords=&page=" + str(numb)
		browser.get(male_fugs_url)
		page_source=browser.page_source
		soup_male = BeautifulSoup(page_source, 'html.parser')
		link_soup = soup_male.find_all(class_="teaser__heading")
		for ele in link_soup:
			link_split_0 = str(ele).split('href="')
			link_split_1 = link_split_0[1].split('">')
			name_split = link_split_1[1].split('<')
			name= name_split[0].split(" ")
			male_list.append(name)

def get_female_list():
	for numb in range(0,5):
		female_fugs_url = "https://www.dea.gov/fugitives/all?keywords=&f%5B0%5D=fugitive_sex%3A2561&page=" + str(numb)
		browser.get(female_fugs_url)
		page_source=browser.page_source
		soup_fem = BeautifulSoup(page_source, 'html.parser')
		link_soup = soup_fem.find_all(class_="teaser__heading")
		for ele in link_soup:
			link_split_0 = str(ele).split('href="')
			link_split_1 = link_split_0[1].split('">')
			name_split = link_split_1[1].split('<')
			name= name_split[0].split(" ")
			female_list.append(name)

def get_unknown_list():
	unknown_fugs_url ="https://www.dea.gov/fugitives/all?keywords=&f%5B0%5D=fugitive_sex%3A2560&f%5B1%5D=fugitive_sex%3A2571"
	browser.get(unknown_fugs_url)
	page_source=browser.page_source
	soup_unk = BeautifulSoup(page_source, 'html.parser')
	link_soup = soup_unk.find_all(class_="teaser__heading")
	for ele in link_soup:
		link_split_0 = str(ele).split('href="')
		link_split_1 = link_split_0[1].split('">')
		name_split = link_split_1[1].split('<')
		name= name_split[0].split(" ")
		unknown_list.append(name)

def get_lists():
	get_male_list()
	get_female_list()
	get_unknown_list()

def get_sex(fugitive):
	if fugitive.name in male_list:
		fugitive.sex="Male"
	elif fugitive.name in female_list:
		fugitive.sex="Female"
	elif fugitive.name in unknown_list:
		fugitive.sex = "Unknown"
	fugitive_list_3.append(fugitive)

def append_fug_csv():
	"""writes a csv with information from each fugitive object"""
	with open('fugitives_file.csv', mode='a', encoding="utf-8") as fugitives:
		fields=("ncic", "last_name", "first_name", "middle_name","wanted_by", "url", 
					"allegation_1", "allegation_2", "allegation_3", "alias_1", "alias_2", 
					"alias_3", "year_of_birth", "hair_color", "eye_color", "height",
					"weight", "sex", "race", "note_1", "note_2", "note_3")
		wr = csv.DictWriter(fugitives, fieldnames=fields, lineterminator="\n")
		for fugitive in fugitive_list_3:
			if (fugitive.ncic == ''):
				continue
			else:
				wr.writerow({"ncic": fugitive.ncic, "last_name": fugitive.l_name, "first_name": fugitive.f_name, "middle_name": fugitive.m_name,
								"wanted_by": fugitive.wanted_by, "url": fugitive.url, "allegation_1": fugitive.allegation_1, "allegation_2": fugitive.allegation_2,
								"allegation_3": fugitive.allegation_3, "alias_1": fugitive.alias_1, "alias_2": fugitive.alias_2, "alias_3": fugitive.alias_3,
								"year_of_birth": fugitive.yob, "hair_color": fugitive.hair, "eye_color": fugitive.eyes, "height": fugitive.height, 
								"weight": fugitive.weight, "sex": fugitive.sex, "race": fugitive.race, "note_1": fugitive.note_1, "note_2": fugitive.note_2, 
								"note_3": fugitive.note_3})
		fugitives.close()

############################################################
start = time.time()

s=requests.session()
fug_link_list=[]
fugitive_list = []
fugitive_list_2 = []
fugitive_list_3 = []
male_list = []
female_list = []
unknown_list=[]
# creates selenium environment
options = Options()
options.headless = False
browser = webdriver.Firefox(options=options)
get_lists()
get_base_fugs()
for fugitive in fugitive_list:
	get_fug_info(fugitive)
browser.quit()
for fugitive in fugitive_list_2:
	get_sex(fugitive)
append_fug_csv()

end = time.time()
print(f'\nRUNTIME: {end-start}\n')