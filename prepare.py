import os
import json
import locale
import datetime
import requests
from pygooglenews import GoogleNews
from pylab import *
import numpy as np
import matplotlib.pyplot as plt

URL_ITALIA = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
URL_REGIONI = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv'
URL_PROVINCE = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv'
URL_RT = 'https://raw.githubusercontent.com/CloudItaly/Indice-RT/main/File-JSON.json'

STRINGS_KEYS_REGION = 'denominazione_regione'
STRINGS_KEYS_PROVINCIA = 'denominazione_provincia'
STRINGS_KEYS_DATA = 'data'
STRINGS_KEYS_STATO = 'stato'
STRINGS_KEYS_NUOVIPOSITIVI = 'nuovi_positivi'
STRINGS_KEYS_VARIAZIONEPOSITIVI = 'variazione_totale_positivi'
STRINGS_KEYS_TAMPONI = 'tamponi'
STRINGS_KEYS_NUOVITAMPONI = 'nuovi_tamponi'
STRINGS_KEYS_NUOVIPOSITIVIOVERNUOVITAMPONI = 'nuovipositivi_su_nuovitamponi'
STRINGS_FIELDS_PROVINCE = {
	'totale_casi': 'Totale casi'
}
STRINGS_FIELDS = {
	'ricoverati_con_sintomi': 'Ricoverati con sintomi',
	'terapia_intensiva': 'Terapia intensiva',
	'totale_ospedalizzati': 'Totale ospedalizzati',
	'totale_positivi': 'Totale positivi',
	'nuovi_positivi': 'Nuovi positivi',
	'nuovi_tamponi': 'Nuovi tamponi',
	'deceduti': 'Deceduti',
	'nuovipositivi_su_nuovitamponi': 'Rapporto nuovi positivi su nuovi tamponi'
}

NEWS_LANG = 'it'
NEWS_COUNTRY = 'IT'
NEWS_SEARCHES = ['covid', 'coronavirus']
NEWS_PERIOD = '1d'

ONDATE = [
	{'name': 1, 'to':'2020-06'},
	{'name': 2, 'from':'2020-10', 'to':'2020-12'},
	{'name': 3, 'from':'2021-02', 'to':'2021-06'},
	{'name': 4, 'from':'2021-07'}
]

# converts an input text t to simple lowercase text without special characters
def simpletext(t):
	l_empty = ['-', '\'', ' ', '.', '_bozen']
	l_underscore = ['/']
	t = t.lower()
	for c in l_empty: t = t.replace(c, '')
	for c in l_underscore: t = t.replace(c, '_')
	if '(' in t: t = t[:t.index('(')]
	return t

# converts an input text t to a latex-friendly text
def latexfriendlytext(t):
	l = ['&', '%', '_', '#', '/']
	for c in l: t = t.replace(c, '\\{}'.format(c))
	return t

# returns the list of dates found in l, considering the date as the property k
def getdates(l, k):
	r = []
	for ll in l:
		v = ll.get(k)
		if v is None: continue
		r.append(v)
	return r

# filters the list l by checking if the property k has value v (b=True to check only if k value starts with v, b=False to check if k value is equal to v; f=True to include all objects after a first match is found, f=False to always include only matching objects; r=True to include all objects until the match is found, r=False to include objects from the match to the end of the list)
def filter(l, k, v, b=False, f=False, r=False):
	new_l = l.copy()
	if r: new_l.reverse()
	res = []
	found = False
	for ll in new_l:
		if found or (b and ll.get(k).startswith(v)) or (not b and ll.get(k) == v):
			res.append(ll)
			found = f
	if r: res.reverse()
	return res

# returns the list of unique values on l, for the k property
def query(l, k):
	r = []
	for e in l:
		v = e.get(k)
		if v is None: continue
		if not v in r: r.append(v)
	return r

# takes a list of headers h and a list of (list of) values l and generates the list of objects having properties defined in h and values defined in l
def generateobjects(h, l):
	r = []
	for ll in l:
		o = {}
		if len(ll) != len(h): continue
		for i in range(0, len(h)):
			o[h[i]] = ll[i]
		r.append(o)
	return r

# for each record in r, it creates a new field key_new as the ratio between key1 over key2
def create_ratio_field(r, key1, key2, key_new):
	for i in range(0, len(r)):
		v = 0.0
		if float(r[i].get(key2)) == 0.0: v = 0.0
		else: v = float(r[i].get(key1)) * 100 / float(r[i].get(key2))
		r[i][key_new] = v
	return r

def create_incremental_field(r, key, key_new, filter_key=None):
	prev_vals = {}
	for i in range(0, len(r)):
		k = 'key'
		if filter_key != None: k = r[i].get(filter_key)
		if prev_vals.get(k) is None: prev_vals[k] = 0
		v = int(r[i].get(key))
		r[i][key_new] = (v - prev_vals.get(k))
		prev_vals[k] = v
	return r

def save_graph(x, y_l, t, filename, filter_x=True):
	x_i = []
	x_v = []
	filter_max_char = 10
	if filter_x: filter_max_char = 7
	for i in range(0, len(x)):
		if not filter_x or "01T" in str(x[i]):
			x_i.append(i)
			x_v.append(x[i].split('T')[0][2:filter_max_char])
	plt.style.use('ggplot')
	plt.figure()
	for y in y_l: plt.plot(y)
	plt.title(t)
	plt.xticks(x_i, x_v, rotation=90)
	#plt.ylabel("count")
	if len(y_l) > 1: plt.legend(t, loc="upper left")
	plt.grid(True)
	plt.savefig(filename)
	#plt.show()
	plt.close()

# downloads all data found in url u and generates the related list of objects
def download(u):
	r = requests.get(u)
	lines = r.text.split("\n")
	for i in range(0, len(lines)): lines[i] = lines[i].split(',')
	headers = lines[0]
	records = lines[1:]
	records = generateobjects(headers, records)
	return records

def generate_graph(records, date_key, field_key, field_title, where, filter_date=None):
	dates = getdates(records, date_key)
	y = []
	for i in range(0, len(records)):
		v = records[i].get(field_key)
		if v is None: v = 0
		y.append(int(v))
	filename = './out/img/{}-{}{}.png'.format(simpletext(where), field_key, ('' if filter_date is None else '_{}'.format(filter_date)))
	save_graph(dates, [y], '{} in {}'.format(field_title, where), filename)

def generate_graph_italia(records, date_key, field_key, field_title):
	generate_graph(records, date_key, field_key, field_title, 'Italia')
	for o in ONDATE:
		filtered_data = records
		if o.get('from') != None: filtered_data = filter(filtered_data, date_key, o.get('from'), b=True, f=True)
		if o.get('to') != None: filtered_data = filter(filtered_data, date_key, o.get('to'), b=True, f=True, r=True)
		generate_graph(filtered_data, date_key, field_key, field_title, 'Italia (ondata {})'.format(o.get('name')), o.get('name'))

def generate_graphs_regioni(records, date_key, region_key, field_key, field_title):
	regioni = query(records, region_key)
	for regione in regioni:
		r = filter(records, region_key, regione)
		generate_graph(r, date_key, field_key, field_title, regione)
		for o in ONDATE:
			filtered_data = r
			if o.get('from') != None: filtered_data = filter(filtered_data, date_key, o.get('from'), b=True, f=True)
			if o.get('to') != None: filtered_data = filter(filtered_data, date_key, o.get('to'), b=True, f=True, r=True)
			generate_graph(filtered_data, date_key, field_key, field_title, '{} (ondata {})'.format(regione, o.get('name')), o.get('name'))

def generate_graphs_province(records, date_key, provincia_key, field_key, field_title):
	province = query(records, provincia_key)
	for provincia in province:
		if '/' in provincia: continue
		r = filter(records, provincia_key, provincia)
		generate_graph(r, date_key, field_key, field_title, provincia)
		for o in ONDATE:
			filtered_data = r
			if o.get('from') != None: filtered_data = filter(filtered_data, date_key, o.get('from'), b=True, f=True)
			if o.get('to') != None: filtered_data = filter(filtered_data, date_key, o.get('to'), b=True, f=True, r=True)
			generate_graph(filtered_data, date_key, field_key, field_title, '{} (ondata {})'.format(provincia, o.get('name')), o.get('name'))

def generate_graph_rt(dates, records, region):
	filename = './out/img/{}-rt.png'.format(simpletext(region))
	save_graph(dates, [records], 'Indice Rt in {}'.format(region), filename, filter_x=False)

def getregiondata(d, v):
	r = []
	for e in d: r.append(e.get(v))
	return r

def save_tex_table(data, filename):
	f = open(filename, 'w')
	for e in {k: v for k, v in sorted(data.items(), key=lambda item: item[1])}:
		f.write('\t'+e+' & $'+str(data.get(e))+'$ \\\\ \\hline\n')
	f.close()

def save_tex_variables(array_map, filename):
	f = open(filename, 'w')
	for k in array_map:
		f.write('\\newcommand{\\'+str(k)+'}{'+str(array_map.get(k))+'}\n')
	f.close()

def save_tex_list(l, filename):
	f = open(filename, 'w')
	for e in l:
		f.write('\\item {}'.format(e))
	f.close()

def get_rt_data():
	r = requests.get(URL_RT)
	data = json.loads(r.text)
	latestdata = {}
	for e in data[-1]:
		if e[0].upper() == e[0]: latestdata[e] = data[-1].get(e)
	save_tex_table(latestdata, './out/italia-rt-table.tex')
	locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
	updatedate = data[-1].get('data')
	updatedate = datetime.datetime.strptime(updatedate, '%Y-%m-%dT%H:%M:%S').strftime('%d %B %Y')
	save_tex_variables({'italiaindicertdata': updatedate}, './out/italia-rt.tex')
	dates = getdates(data, STRINGS_KEYS_DATA)
	info = []
	for region in latestdata:
		d = getregiondata(data, region)
		generate_graph_rt(dates, d, region)

def get_news():
	r = []
	gn = GoogleNews(lang=NEWS_LANG, country=NEWS_COUNTRY)
	for s in NEWS_SEARCHES:
		search = gn.search(s, when=NEWS_PERIOD)
		r += search.get('entries')
		print(r[0])
		import time
		time.sleep(100)
	return r

# getting italian data
records_italia = download(URL_ITALIA)
records_italia = create_incremental_field(records_italia, STRINGS_KEYS_TAMPONI, STRINGS_KEYS_NUOVITAMPONI)
records_italia = create_ratio_field(records_italia, STRINGS_KEYS_NUOVIPOSITIVI, STRINGS_KEYS_NUOVITAMPONI, STRINGS_KEYS_NUOVIPOSITIVIOVERNUOVITAMPONI)
for f in STRINGS_FIELDS: generate_graph_italia(records_italia, STRINGS_KEYS_DATA, f, STRINGS_FIELDS.get(f))
# writing summary to tex
r = records_italia[-1]
array_map = {}
for k in r:
	if k in [STRINGS_KEYS_DATA, STRINGS_KEYS_STATO]: continue
	v = r.get(k)
	if v == '': v = 0
	array_map['italia'+k.replace('_', '')] = str(v)
save_tex_variables(array_map, './out/summary_italia.tex')
# getting italian news and writing it to tex
news = get_news()
news_list = []
for e in news:
	t = '\\href{{{LINK}}}{{{TITLE}}}\n'.replace('{{TITLE}}', latexfriendlytext(e.get('title'))).replace('{{LINK}}', e.get('links')[0].get('href'))
	news_list.append(t)
save_tex_list(news_list, './out/news_italia.tex')

# getting data for regions
records_regioni = download(URL_REGIONI)
records_regioni = create_incremental_field(records_regioni, STRINGS_KEYS_TAMPONI, STRINGS_KEYS_NUOVITAMPONI, STRINGS_KEYS_REGION)
records_regioni = create_ratio_field(records_regioni, STRINGS_KEYS_NUOVIPOSITIVI, STRINGS_KEYS_NUOVITAMPONI, STRINGS_KEYS_NUOVIPOSITIVIOVERNUOVITAMPONI)
for f in STRINGS_FIELDS: generate_graphs_regioni(records_regioni, STRINGS_KEYS_DATA, STRINGS_KEYS_REGION, f, STRINGS_FIELDS.get(f))
# getting r_t data
get_rt_data()
# writing summary to tex
regioni = query(records_regioni, STRINGS_KEYS_REGION)
for regione in regioni:
	r = filter(records_regioni, STRINGS_KEYS_REGION, regione)[-1]
	array_map = {}
	for k in r:
		if k in [STRINGS_KEYS_DATA, STRINGS_KEYS_STATO]: continue
		if 'nuts' in k: continue
		if r.get(k) == '': continue
		array_map['regione'+k.replace('_', '')] = r.get(k)
	save_tex_variables(array_map, './out/summary_regione_{}.tex'.format(simpletext(regione)))
# getting all latest nuovipositivi_su_nuovitamponi data
d = records_regioni[-1].get(STRINGS_KEYS_DATA)
records_latest = filter(records_regioni, STRINGS_KEYS_DATA, d)
data = {}
for e in records_latest: data[e.get(STRINGS_KEYS_REGION)] = e.get(STRINGS_KEYS_NUOVIPOSITIVIOVERNUOVITAMPONI)
save_tex_table(data, './out/italia-nuovipositivisunuovitamponi-table.tex')

# getting data for cities
records_province = download(URL_PROVINCE)
for f in STRINGS_FIELDS_PROVINCE: generate_graphs_province(records_province, STRINGS_KEYS_DATA, STRINGS_KEYS_PROVINCIA, f, STRINGS_FIELDS_PROVINCE.get(f))
# generating the list of (regione,provincia) couple
regioni_province = {}
for r in records_province:
	regione = r.get(STRINGS_KEYS_REGION)
	if regione is None: continue
	if regioni_province.get(regione) is None: regioni_province[regione] = []
	provincia = r.get(STRINGS_KEYS_PROVINCIA)
	if '/' in provincia: continue
	if provincia in regioni_province.get(regione): continue
	regioni_province[regione].append(provincia)
	regioni_province[regione].sort()
# writing to latex
for r in regioni_province:
	t = ''
	t_text = ''
	for p in regioni_province.get(r):
		if t != '':
			t += ','
			t_text += ','
		t += '{}'.format(simpletext(p))
		t_text += '{}'.format(p)
	array_map = {'regioniprovince':t, 'regioniprovincetext':t_text}
	save_tex_variables(array_map, 'out/province_{}.tex'.format(simpletext(r)))
