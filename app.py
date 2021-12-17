import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import json
import plotly.express as px

plt.style.use('seaborn')

st.title('Production Data Viewer')
st.write('Oleh Muhammad Naufal Aurora (12220081)')

# load data
@st.cache
def load_data(json_data):
	df = pd.read_csv('produksi_minyak_mentah.csv')
	df = df[df.columns[:3]]

	# dict nama negara internal
	list_kode_negara = df.kode_negara.unique()
	dict_nama_negara = dict()
	for negara in json_data:
	    if negara['alpha-3'] in list_kode_negara:
	        dict_nama_negara.update({negara['alpha-3']: negara['name']})

	# update df
	for kode_negara in df.kode_negara.unique():
	    if kode_negara not in dict_nama_negara:
	        df.drop(df[df.kode_negara == kode_negara].index, inplace=True)
	return df

# load json data
@st.cache
def load_json():
	file_json = open('./kode_negara_lengkap.json')
	json_data = json.load(file_json)
	return json_data

# buat list kode negara utk filter kode negara yg avalilable
@st.cache
def dict_nama_negara_generator():
	list_kode_negara = df.kode_negara.unique()
	dict_nama_negara = dict()
	for negara in json_data:
	    if negara['alpha-3'] in list_kode_negara:
	        dict_nama_negara.update({negara['alpha-3']: negara['name']})
	return dict_nama_negara

# setup function untuk mengconvert kode negara
def convert_kode_negara(kode):
    try:
        return dict_nama_negara[kode]
    except:
        return kode

def search_in_json(kode):
    for negara in json_data:
        if negara['alpha-3'] == kode:
            return negara



# setup dan load data
json_data = load_json()
df = load_data(json_data)
dict_nama_negara = dict_nama_negara_generator()


# sidebar
sidebar = st.sidebar.selectbox('Select Modes', 
	('Production by Country', 'Top Countries by Yearly Production', 'Top Countries by Cummulative Production', 'Country with Most/Least/None Yearly Production', 'Geomap Yearly Production'))

# main window
if sidebar == 'Production by Country':
	#========
	# no 1) line chart produksi per negara (produksi vs tahun)
	negara_options = df.kode_negara.unique()
	st.subheader('Production by country')
	negara = st.selectbox(label="Negara", options=negara_options, key='negara_1')

	line_chart_data = df[df['kode_negara'] == negara][['tahun', 'produksi']]
	line_chart_x = df[df['kode_negara'] == negara].tahun
	line_chart_y = df[df['kode_negara'] == negara].produksi
	fig_1, ax1 = plt.subplots()
	ax1.plot(line_chart_x, line_chart_y)
	ax1.set_title(f'Produksi {convert_kode_negara(negara)}')
	st.pyplot(fig_1)


elif sidebar == 'Top Countries by Yearly Production':
	#===========
	# no 2) bar chart n negara terbesar pada tahun tertentu
	st.subheader('Top Countries by Yearly Production')
	number_2 = st.slider(label='Banyak negara', min_value=1, max_value=142, key='number_2') # buat slider streamlit
	tahun = st.slider(label='Tahun', min_value=1970, max_value=2015, key='tahun_2')
	# algo
	max_prod = df[df.tahun == tahun].produksi.sort_values(ascending=False)[:number_2].values
	fig_2, ax2 = plt.subplots()
	for prod in max_prod:
		# find kode negara
		kode_negara_prod_max = df[(df.tahun == tahun) & (df.produksi == prod)].kode_negara.item() # dah dalam string
		# convert ke nama negara
		nama_negara_prod_max = convert_kode_negara(kode_negara_prod_max)
		# buat plot
		ax2.barh(nama_negara_prod_max, prod)
	    
	plt.title(f'{number_2} Negara dengan Produksi Terbesar Tahun {tahun}')
	st.pyplot(fig_2)


elif sidebar == 'Top Countries by Cummulative Production':
	#========
	# no 3) barh chart n negara dengan produksi kumulatif terbesar
	st.subheader('Top Countries by Cummulative Production')
	number_3 = st.slider(label='Banyak negara', min_value=1, max_value=142, key='number_3')

	xs = df.groupby(['kode_negara']).sum().sort_values(by='produksi', ascending=False).produksi[:number_3].index
	ys = df.groupby(['kode_negara']).sum().sort_values(by='produksi', ascending=False).produksi[:number_3]
	fig3, ax3 = plt.subplots()

	for x, y in zip(xs, ys):
		x = convert_kode_negara(x)
		ax3.barh(x, y)

	plt.title(f'{number_3} Negara dengan Produksi Kumulatif Terbesar')
	st.pyplot(fig3)


elif sidebar == 'Country with Most/Least/None Yearly Production':
		#==========
	# no 4)
	st.subheader('Country with Most/Least/None Yearly Production')
	tahun4 = st.slider(label='Tahun', min_value=1970, max_value=2015, key='tahun4')

	# tunjukkin yang terbesar
	kode_negara_terbesar = df[df.tahun == tahun4].sort_values(by='produksi', ascending=False).kode_negara[:1].values[0]
	kode_negara_terkecil = df[(df.tahun == tahun4) & (df.produksi != 0)].sort_values(by='produksi').kode_negara[:1].values[0]
	kode_negara_nol = df[(df.tahun == tahun4) & (df.produksi == 0)].kode_negara.values

	col_big, col_small = st.columns(2)
	# ambil data json lewt kode
	# terbesar
	with col_big:
		negara = search_in_json(kode_negara_terbesar)
		st.metric(label='Most Production', value=negara['name'])
		st.write('Code: ' , negara['alpha-3'])
		st.write('Sub-Region: ', negara['sub-region'])
		st.write('Production: ',df[(df.kode_negara == kode_negara_terbesar) & (df.tahun == tahun4)].produksi.values[0])
		

	# terkecil
	with col_small:
		negara = search_in_json(kode_negara_terkecil)
		st.metric(label='Least Production', value=negara['name'])
		st.write('Code: ' , negara['alpha-3'])
		st.write('Sub-Region: ', negara['sub-region'])
		st.write('Production: ',df[(df.kode_negara == kode_negara_terkecil) & (df.tahun == tahun4)].produksi.values[0])
	    
	# yg 0
	st.write('**0 Production**')

	tabel = pd.DataFrame()
	country_list = list()
	code_list = list()
	region_list = list()
	subregion_list = list()
	prod_list = list()

	for kode in kode_negara_nol:
		negara = search_in_json(kode)
		country_list.append(negara['name'])
		code_list.append(negara['alpha-3'])
		region_list.append(negara['region'])
		subregion_list.append(negara['sub-region'])
		prod_list.append(df[(df.kode_negara == kode) & (df.tahun == tahun4)].produksi.values[0])
            
	tabel['Country'] = country_list
	tabel['Code'] = code_list
	tabel['Region'] = region_list
	tabel['Sub-Region'] = subregion_list
	tabel['Production'] = prod_list

	st.table(tabel)

elif sidebar == 'Geomap Yearly Production':
	st.subheader('Geomap Yearly Production')
	tahun = st.slider('Tahun', 1970, 2015)

	prod_list = df[df.tahun == tahun].produksi
	kode_list = df[df.tahun == tahun].kode_negara

	geo_df = pd.DataFrame()
	geo_df['produksi'] = prod_list
	geo_df['kode_negara'] = kode_list
	
	fig = px.scatter_geo(geo_df, locations="kode_negara",
                     hover_name="kode_negara", size="produksi",
                     projection="natural earth")

	st.plotly_chart(fig)












