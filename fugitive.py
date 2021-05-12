class Fugitive:
	def __init__(self, name, l_name, f_name, m_name, wanted_by, url, allegation_1=None, allegation_2=None, 
					allegation_3=None, alias_1=None, alias_2=None, alias_3=None,
					yob=None, hair=None, eyes=None, height=None, weight=None, sex=None, race=None,
					ncic=None, note_1=None, note_2=None, note_3=None):
		self.name=name
		self.l_name=l_name
		self.f_name=f_name
		self.m_name=m_name
		self.wanted_by=wanted_by
		self.url=url
		self.allegation_1=allegation_1
		self.allegation_2=allegation_2
		self.allegation_3=allegation_3
		self.alias_1=alias_1
		self.alias_2=alias_2
		self.alias_3=alias_3
		self.yob=yob
		self.hair=hair
		self.eyes=eyes
		self.height=height
		self.weight=weight
		self.sex=sex
		self.race=race
		self.ncic=ncic
		self.note_1=note_1
		self.note_2=note_2
		self.note_3=note_3


	def __str__(self):
		return f'Name: {self.name} URL: {self.url}'

	__repr__=__str__
