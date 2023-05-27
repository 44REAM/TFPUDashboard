import pandas as pd
import json
import plotly.graph_objects  as go
import plotly.express as px
import bokeh
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, LogColorMapper
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

palette =  bokeh.palettes.Reds[256]
#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]

color_mapper = LinearColorMapper(palette = palette, low=gdf['count'].min(), high = gdf['count'].max(), nan_color = '#d9d9d9')

color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
            border_line_color=None,location = (0,0), orientation = 'horizontal')

hover = HoverTool(tooltips = [ ('จังหวัด','@pro_th'),('คนทำงาน','@count')])

p = figure( height = 1000 , toolbar_location = None, tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.axis.visible = False
p.patches('xs','ys', source = geosource, fill_color = {'field' :'count', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.1, fill_alpha = 1)

p.add_layout(color_bar, 'below')
output_notebook()
show(p)