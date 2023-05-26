import plotly.express as px
import streamlit as st
import pandas as pd
import json


st.header("สหภาพแพทย์ผู้ปฏิบัติงาน")
st.subheader("Thai Frontline Physician Union (TFPU)")
df = pd.read_csv('data/test.csv')
df = df.dropna(subset = ['Timestamp'])
df['สถานพยาบาลที่ท่านทำงานอยู่ในสังกัดใด'][~df['สถานพยาบาลที่ท่านทำงานอยู่ในสังกัดใด'].isin(['ทั้งสองที่', 'รัฐ', 'เอกชน'])] = 'อื่นๆ'
df['ตำแหน่งงานในปัจจุบัน'][~df['ตำแหน่งงานในปัจจุบัน'].isin(
    ['นักศึกษา/นิสิตแพทย์', 'แพทย์เวชปฏิบัติทั่วไป (intern/GP)', 'แพทย์ประจำบ้านต่อยอด (resident)',
    'แพทย์เฉพาะทางต่อยอด (fellow)','แพทย์เฉพาะทาง (specialist)','แพทย์เฉพาะทาง (subspecialist)']
    )] = 'อื่นๆ'

with open("data/provinces.geojson", encoding='utf-8') as response:
    geo = json.load(response)
all_provinces = [name['properties']['pro_th'] for name in geo['features']]
all_provinces_en = [name['properties']['pro_en'] for name in geo['features']]
all_provinces = pd.DataFrame(columns=['name'], data = all_provinces)
all_provinces['eng_name'] = all_provinces_en
count_provinces = pd.DataFrame(df.groupby(by = ['จังหวัดที่ทำงานปัจจุบัน']).size())
count_provinces.reset_index(inplace=True)
count_provinces.columns = ['name', 'count']


all_provinces = all_provinces.merge(count_provinces, how = 'left', left_on= ['name'], right_on=['name'])
all_provinces.fillna(0, inplace=True)


fig = px.choropleth(all_provinces, geojson=geo, 
                    locations='name', color='count',
                           color_continuous_scale="Reds",
                           featureidkey = 'properties.pro_th',
                           # range_color=(0, 12),
                           # fitbounds = 'geojson',
                           scope="asia",
                           projection="mercator",
                           labels={'count':'number of worker'},
                          )
fig.update_geos(fitbounds = 'locations', visible =False)

hos_type_fig = px.histogram(df, x="สถานพยาบาลที่ท่านทำงานอยู่ในสังกัดใด",
                   labels={
                     "สถานพยาบาลที่ท่านทำงานอยู่ในสังกัดใด": "สังกัด"
                 },template = 'plotly_dark', color_discrete_sequence=['indianred'])
hos_type_fig.update_layout( 
    yaxis_title="จำนวนคน", 
    title = "โรงพยาบาลที่สังกัด", 
    xaxis_fixedrange = True,
    yaxis_fixedrange = True)

# Here we use a column with categorical data
job_fig = px.histogram(df, x="ตำแหน่งงานในปัจจุบัน",
                   labels={
                     "ตำแหน่งงานในปัจจุบัน": "ตำแหน่งงาน"
                 },template = 'plotly_dark', color_discrete_sequence=['indianred'])
job_fig.update_layout( 
    yaxis_title="จำนวนคน", 
    title = "ตำแหน้งงาน", 
    xaxis_fixedrange = True,
    yaxis_fixedrange = True)

tab1, tab2 = st.tabs(["โรงพยาบาลที่สังกัด", "ตำแหน่งงานในปัจจุบัน"])
with tab1:
    st.plotly_chart(hos_type_fig, theme="streamlit", use_container_width=True)
with tab2:
    st.plotly_chart(job_fig, theme="streamlit", use_container_width=True)

