import plotly.express as px
import streamlit as st
import pandas as pd
from PIL import Image
import json

import bokeh
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool
from bokeh.palettes import brewer
import geopandas as gp


df = pd.read_csv('data/test.csv')
df = df.dropna(subset = ['Timestamp'])
df['สถานพยาบาลที่ท่านทำงานอยู่ในสังกัดใด'][~df['สถานพยาบาลที่ท่านทำงานอยู่ในสังกัดใด'].isin(['ทั้งสองที่', 'รัฐ', 'เอกชน'])] = 'อื่นๆ'
df['ตำแหน่งงานในปัจจุบัน'][~df['ตำแหน่งงานในปัจจุบัน'].isin(
    ['นักศึกษา/นิสิตแพทย์', 'แพทย์เวชปฏิบัติทั่วไป (intern/GP)', 'แพทย์ประจำบ้านต่อยอด (resident)',
     'แพทย์เฉพาะทางต่อยอด (fellow)','แพทย์เฉพาะทาง (specialist)','แพทย์เฉพาะทาง (subspecialist)']
    )] = 'อื่นๆ'

gdf = gp.read_file("data/provinces.geojson")

count_provinces = pd.DataFrame(df.groupby(by = ['จังหวัดที่ทำงานปัจจุบัน']).size())
count_provinces.reset_index(inplace=True)
count_provinces.columns = ['name', 'count']


gdf = gdf.merge(count_provinces, how = 'left', left_on= ['pro_th'], right_on=['name'])
gdf.fillna(0, inplace=True)

merged_json = json.loads(gdf.to_json())

#Convert to str like object
json_data = json.dumps(merged_json)
geosource = GeoJSONDataSource(geojson = json_data)

def get_map(gdf, geosource):
    palette =  bokeh.palettes.Reds[256]
    #Reverse color order so that dark blue is highest obesity.
    palette = palette[::-1]

    color_mapper = LinearColorMapper(palette = palette, low=gdf['count'].min(), high = gdf['count'].max(), nan_color = '#d9d9d9')
    hover = HoverTool(tooltips = [ ('จังหวัด','@pro_th'),('คนทำงาน','@count')])
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                border_line_color=None,location = (0,0), orientation = 'horizontal')
    p = figure( height = 1200 , toolbar_location = None, tools = [hover])
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False
    p.patches('xs','ys', source = geosource, fill_color = {'field' :'count', 'transform' : color_mapper},
            line_color = 'black', line_width = 0.1, fill_alpha = 1)

    p.add_layout(color_bar, 'below')
    return p

p = get_map(gdf, geosource)

# fig = px.choropleth(all_provinces, geojson=geo, 
#                     locations='name', color='count',
#                            color_continuous_scale="Reds",
#                            featureidkey = 'properties.pro_th',
#                            # range_color=(0, 12),
#                            # fitbounds = 'geojson',
#                            scope="asia",
#                            projection="mercator",
#                            labels={'count':'number of worker'},
#                     template = 'plotly_dark'
#                           )
# fig.update_geos(fitbounds = 'locations', visible =False)
# fig.update_layout( 
#     xaxis_fixedrange = True,
#     yaxis_fixedrange = True,dragmode=False , coloraxis_showscale=False)

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
    title = "ตำแหน่งงาน", 
    xaxis_fixedrange = True,
    yaxis_fixedrange = True)

special_fig = px.histogram(df, x="ความเฉพาะทาง (วุฒิบัตร)",
                   labels={
                     "ความเฉพาะทาง (วุฒิบัตร)": "ความเฉพาะทาง (วุฒิบัตร)"
                 },template = 'plotly_dark', color_discrete_sequence=['indianred'])
special_fig.update_layout( 
    yaxis_title="จำนวนคน", 
    title = "ความเฉพาะทาง (วุฒิบัตร)", 
    xaxis_fixedrange = True,
    yaxis_fixedrange = True)

t1, t2 = st.columns((1,8))

title_image = Image.open("data/logo.png")
t1.image(title_image, width = 75)

t2.header("สหภาพแพทย์ผู้ปฏิบัติงาน")
st.subheader("Thai Frontline Physician Union (TFPU)")
tabs = st.tabs(["โรงพยาบาลที่สังกัด", "ตำแหน่งงานในปัจจุบัน", "ความเฉพาะทาง", "จังหวัด"])
with tabs[0]:
    st.plotly_chart(hos_type_fig, theme="streamlit", use_container_width=True)
with tabs[1]:
    st.plotly_chart(job_fig, theme="streamlit", use_container_width=True)

with tabs[2]:
    st.plotly_chart(special_fig, theme="streamlit", use_container_width=True)

with tabs[3]:
    st.bokeh_chart(p, use_container_width=False)

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
        """
st.metric(label = 'สมาชิกคนทำงาน', value = f"{int(gdf['count'].sum())} คน")

st.markdown(hide_menu_style, unsafe_allow_html=True)
st.markdown("---")

st.markdown(
    """<font size='2'>Facebook page: [สหภาพแพทย์ผู้ปฏิบัติงาน](https://www.facebook.com/ThaiFrontlinePhysicianUnion)</font>""",
    unsafe_allow_html=True
)

st.markdown(
    """<font size='2'>Twitter: [สหภาพแพทย์ผู้ปฏิบัติงาน](https://twitter.com/TFPU_official)</font>""",
    unsafe_allow_html=True
)
