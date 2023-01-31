# Food_issues 
import pandas as pd
import numpy as np
import datetime
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from streamlit_folium import folium_static
import folium
import json

from pandas import ExcelWriter
from pandas import ExcelFile

import geopandas as gpd
#mulitpages
import pickle as pkle
import os.path

#showWarningOnDirectExecution = false


# set page layout
st.set_page_config(
    page_title="Food Issues",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


#reducing space 
st.markdown("""
    <style>
    .css-1aumxhk {
        padding: 0em 1em;
    }
    </style>
""", unsafe_allow_html=True)


LINE = """<style>
.vl {
  border-left: 2px solid black;
  height: 400px;
  position: relative;
  left: 100%;
  margin-left: -3px;S
  top: 80px;
}
</style>
<div class="vl"></div>"""


#SIDEBAR
#IMAGE IN THE SIDEBAR
from PIL import Image
st.sidebar.image('images/logoPNG.png', width=110)
st.sidebar.title('''Food Issues''') 
st.sidebar.write (''' 📈 This App help you to explore the Food Issues from Farm to Fork.''')
st.sidebar.header('''Select the Issue''') 

#st.sidebar.header('''TESTING''') 
# MULTIPAGES SELECTOR 
# create a button in the side bar that will move to the next page/radio button choice
#next = st.sidebar.button('Next on list')

# will use this list and next button to increment page, MUST BE in the SAME order
# as the list passed to the radio button
new_choice = ['Home','Production','Consumption','Social','Climate change']

# This is what makes this work, check directory for a pickled file that contains
# the index of the page you want displayed, if it exists, then you pick up where the
#previous run through of your Streamlit Script left off,
# if it's the first go it's just set to 0----
#if os.path.isfile('next.p'):
    #next_clicked = pkle.load(open('next.p', 'rb'))
    # check if you are at the end of the list of pages
    #if next_clicked == len(new_choice):
     #   next_clicked = 0 # go back to the beginning i.e. homepage
#else:
 #   next_clicked = 0 #the start

# this is the second tricky bit, check to see if the person has clicked the
# next button and increment our index tracker (next_clicked)
#if next:
    #increment value to get to the next page
 #   next_clicked = next_clicked +1

    # check if you are at the end of the list of pages again
  #  if next_clicked == len(new_choice):
   #     next_clicked = 0 # go back to the beginning i.e. homepage

# create your radio button with the index that we loaded
choice = st.sidebar.radio(' ',('Home','Production','Consumption','Social','Climate change'))
#--choice = st.sidebar.radio("go to",('Home','Production','Consumption','Social','Climate change'), index=next_clicked)
# pickle the index associated with the value, to keep track if the radio button has been used
#pkle.dump(new_choice.index(choice), open('next.p', 'wb'))


#SIDEBAR INSTRUCTIONS
#st.sidebar.markdown ('---')
#st.sidebar.header('''Instructions''') 
#st.sidebar.write ('''1. Select the lever in the Food System''')
#st.sidebar.write ('''2. Select the COUNTRY or COUNTRIES, the METRIC to analyse and the interval''')
#st.sidebar.write('''3. You can print and download the data and charts''')


#SIDEBAR INFORMATION
st.sidebar.markdown ('---')
st.sidebar.header('''Information''') 
st.sidebar.write("💡 This app use open Datasets from different sources")
st.sidebar.write("💻 The code and sources are available here: [link](https://github.com/merlynjocol/FoodIssues_Interactive_Dashboards)")



new_template = dict(layout=go.Layout(plot_bgcolor="white",
                       hovermode="x unified",                      
                       title=dict(font=dict(
                                     size = 22)),
                        xaxis = dict(#title = 'Land Use', 
                                    showline=True,
                                    showgrid=False,
                                    linecolor='rgb(204, 204, 204)',
                                    linewidth=1,
                                    ticks='outside',
                                    tickmode="array",
                                    visible= True,
                                    tickfont = dict(family = 'Arial', 
                                                    size = 12, 
                                                    color = 'rgb(82, 82, 82)'),
                                    showticklabels=True), 
                        yaxis = dict(#title = 'Number of Hectares', 
                                    showgrid=True,
                                    gridcolor = 'rgb(204, 204, 204)',
                                    zeroline=False,
                                    showline=True,
                                    linecolor='rgb(204, 204, 204)',
                                    linewidth=0.5,
                                    tickmode="array",
                                    visible= True,
                                    ticks='outside',
                                    showticklabels=True), 
                        legend_title=dict(#text='<b>Land Use</b>',
                                     font=dict(
                                     size = 16))))




#Importing data
st.cache(persist=True)
def load_data():
    # DATA FOR BIG FARMS AND SMALL FARMS 
    skipcols = ['Most recent Gini index for land distribution  & tendency *','Sources', 'Unnamed: 10']
    all_df = pd.read_excel('data_production/Land_farmers_GRAIN_land-food-report-dataset.xls', sheet_name=['AFRICA','ASIA AND THE PACIFIC',
                                                                                              'LATIN AMERICA AND THE CARIBBEAN',
                                                                                              'NORTH AMERICA',
                                                                                              'EUROPE'], 
                                                                                               skiprows = 2, 
                                                                                               usecols=lambda x: x not in skipcols,   index_col=0 )
    
    
    all_df_concat = pd.concat(all_df[frame] for frame in all_df.keys())
    #removing rows without relevant information
    # clean the country names
    df_all2 = all_df_concat.copy()
    df_all = df_all2.reset_index()
    df_all['Country'] = df_all['Country'].str.replace('Afghanistan ', 'Afghanistan')
    df_all['Country'] = df_all['Country'].str.replace('Latvia ', 'Latvia')
    df_all['Country'] = df_all['Country'].str.replace('Hungary ', 'Hungary')


    #df_all = all_df_concat.drop( all_df_concat.index[[164,165,166,167,168,169,170,171,172]]).reset_index()
    
    # DATA total area from FAO STAT 2018Year
    total_area = pd.read_csv('data_production/FAOSTAT_data_land_use_country.csv')
    #removing columns
    total_area2 = total_area.drop(labels= ['Domain Code', 'Domain', 'Area Code (FAO)','Element Code',
       'Element', 'Item Code', 'Year Code', 'Year', 'Unit', 'Flag', 'Flag Description'], axis=1)
    total_area_land = total_area2.pivot(index="Area", columns= "Item", values="Value").reset_index()
    
    #merge df from GRAIN + FAOstats 
    total_area_land.rename(columns = {'Area' :'Country'}, inplace = True) #giving the same name key
    result = pd.merge(df_all,total_area_land, on=["Country"])
    #dataframe with columns organized
    all_farms = result[['Country', 'Country area', 'Agricultural land', 'Agricultural land (thousands of ha)',
       'Number of farms (thousands)', 'Criteria for small',
       ' Number of small farms \n(thousands)', 'small farms as % of all farms',
       'Agricultural land in the hands of small farmers\n(thousands of ha)',
       '% of agricultural land in the hands of small farmers',
       'Most recent Gini index for land distribution & tendency *']]
    
    #DATA FOR LAND USE-QUANTITIES
    skipcol_land = ['Domain Code', 'Domain', 'Area Code (FAO)', 'Element Code',
       'Element', 'Item Code', 'Year Code', 'Unit', 'Flag', 'Flag Description']
    land_use = pd.read_csv('data_production/FAOSTAT_data_aglandV1_1998_2018.csv',usecols=lambda x: x not in skipcol_land, index_col=0 ) 
    
    
    # DATA SHARE AGRICULTURE LAND
    skipcol_land = ['Domain Code', 'Domain', 'Area Code (FAO)', 'Element Code',
       'Element', 'Item Code', 'Year Code', 'Unit', 'Flag', 'Flag Description']
    land_share = pd.read_csv('data_production/FAOSTAT_data_share_agriland.csv', usecols=lambda x: x not in skipcol_land, index_col=0 ).reset_index()
    land_share.rename(columns = {'Area' :'Country'}, inplace = True)
    #DATA JSON COUNTRIES
    country_shapes = json.load(open('data_production/world-countries.json'))

    return all_farms, land_use, land_share, country_shapes, df_all
all_farms, land_use, land_share, country_shapes, df_all = load_data()




# finally get to whats on each page
if choice == 'Home':
    # TITLE AND HEADER

    # framework in columns
    col1, col2, col3 = st.beta_columns([3, 0.5, 5])

    with col1:
        st.title("Dashboards of Food Issues")
        #st.markdown ('<p style= "font-family:Verdana; color:Black; font-size: 20px;">Dashboards of Food Issues from farm to fork </p>', unsafe_allow_html=True)
        st.write(':chart_with_upwards_trend: This tool has dashboard to describe and diagnose food issues at global scale and national trends') 
        


    with col2:
        st.write(" ")

    with col3:
        st.image('images/planet&logo.JPG', width=300)
        
    st.header('''Instructions to Explore the Dashboards''')         
    st.image('images/persona_computer.JPG', width=200)
    st.write ('''1. Select the lever in the Food System''')
    st.write ('''2. Select the COUNTRY or COUNTRIES, and the METRIC to analyse and the interval''')
    st.write('''3. You can print and download the charts''')


elif choice == 'Production':
   
    #CONTAINER:HEADER
    st.markdown ('<h1 style= "font-family:Verdana; color:Black; font-size: 40px;">1. Issues in Food Production</h1>', unsafe_allow_html=True)
    #st.text('this is app')
    st.write (''' 
    This app present interactive dashboards to explore Open Data Sources at global level. You can choose the region and countries, select the analysis, compare between the variables and countries, and select the time period.''')

    st.markdown ('---')
    # CONTAINER 2
    st.title("* How much land are we using for agriculture?")

    #CREATING DATAFRAMES 
    #selecting data from Year=2018
    land_2018 = land_use[land_use['Year'] == 2018 ].groupby(['Area','Year','Item'])['Value'].sum().reset_index()
    all_2018= land_2018.groupby(['Item'])['Value'].sum().reset_index()
    all_2018  = all_2018.loc[all_2018["Item"] != "Country area"]
    #removing the variable are of the Country
    land_use2=land_use.reset_index()
    land_use2.rename(columns = {'Area' :'Country'}, inplace = True)
    land_use3  = land_use2.loc[land_use2["Item"] != "Country area"]

    #CHART PIE Year 2018
    fig_pie = px.pie(all_2018, values='Value', names='Item', color='Item',
                 color_discrete_map={'Agriculture':"#2a2b5a",
                                     'Forest land':'#0bca9b',
                                     'Other land':'#e51858'},
                                    width = 400)
    fig_pie.update_layout(title="<b>Land Use WorlWide in %<b>")
    fig_pie.update_layout(legend=dict(  yanchor="top",
                                        y=0.99,
                                        xanchor="left",
                                        x=0.01))



    col1, line, col2 = st.beta_columns([2,0.5,4])

    with col1:
        st.subheader("Agriculture land use at Worldwide")
        st.plotly_chart(fig_pie, unsafe_allow_html=True)
        st.text("Source: FAO STATS 2018. Land Use Inputs") #footer in the chart 
    with line: 

        line.markdown(LINE, unsafe_allow_html=True)

    with col2:
        #selecting country  
        st.subheader("Agriculture land use at Country Level")
        country = st.multiselect("SELECT A COUNTRY or COUNTRIES", land_share['Country'].unique())
        new_share = land_share[land_share['Country'].isin(country)]
        #STATE AN ERROR
        if not country:
            st.error(" ⚠️ Please select at least one country.")
    #CHART LINE 
        fig_line = px.line(new_share, x = 'Year', y =  'Value' , color = "Country")
        fig_line.update_layout(title="<b>Agriculture Land Use (%) by Country in 2018 <b>", plot_bgcolor="white")
        fig_line.update_layout(xaxis = dict(title = 'Year'), 
                               yaxis = dict(title = 'Share Agriculture Land %', range = (0,100)),
                               legend_title=dict(text='<b>Countries</b>'),
                               width = 600, height= 350)
        fig_line.update_layout(template = new_template)

        st.plotly_chart(fig_line, unsafe_allow_html=True)
        st.text("Source: FAO STATS 1998-2018. Land Use Inputs") #footer in the chart 



    
    # CONTAINER 3
    st.markdown ('---')


    # GEODATA
    #MAP
    #file with coordinates
    country_geo = gpd.read_file('data_production/world-countries.json')
    country_geo.rename(columns = {'id' :'ISO3'}, inplace = True)

    #oficial file with ISOCODE from FAO
    isocode = pd.read_excel('data_production/country_codes.xlsx')
    isocode.rename(columns = {'Short name' :'Country'}, inplace = True)

    #dataframe for map share agriculture landuse for Year 2018
    land_share2018  = land_share.loc[land_share["Year"] == 2018]

    # Merging DF to built geodata. In this method we lost 6 countries. ISOCODE have 195 countries, FAO file have 225 countries
    merged_iso_values = pd.merge(land_share2018, isocode, on=['Country'], how='inner')
    # in this method we lost some countries.Check shape
    landuse_geo= country_geo.merge(merged_iso_values,on="ISO3")


    # CONTAINER 2
    st.title("Agriculture land use in %, 2018 ")
    st.write("Check the countries, the land use in agriculture is in % or Hectares ")


    ag_map = folium.Map(location=[0,0], zoom_start=2,tiles=None)
    folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(ag_map)

    # Creating choropleth map

    ag_map.choropleth(geo_data= landuse_geo,
                 name='Choropleth',         
                 data=landuse_geo,
                 columns=['Country','Value'], 
                 key_on='feature.properties.Country', 
                 fill_color= 'YlGn', #YlOrRd',
                 fill_opacity=0.8, 
                 line_opacity=0.5,
                 legend_name='land use in hectares (Ha)', 
                 smooth_factor=0,     
                 highlight=True
                     )


    #Adding labels to map
    style_function = lambda x: {'fillColor': '#ffffff', 
                                'color':'#000000', 
                                'fillOpacity': 0.1, 
                                'weight': 0.1}

    landuse_value = folium.features.GeoJson(
        landuse_geo,
        style_function= style_function, 
        control=False,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Country','Value'],
            aliases=['Country: ','% Agriculture land use: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
        )
    )
    ag_map.add_child(landuse_value)
    ag_map.keep_in_front(landuse_value)
    folium.LayerControl().add_to(ag_map)

    folium_static(ag_map, width=1000, height=550)

    st.text("Source: Food and Agriculture Organization. FAOSTATS.2018. Land Use Inputs")

    st.markdown ('---')
    #CONTAINER 3
    st.title("How much is using the land by crops, livestocks and forests?")
    st.text("Livestock is the production of meat and products derivated from animal production")


    #DF CHART LINE FOREST vs LIVESTOCK vs CROPS vs MELLDOW
    # download data 
    skipcol_cropsEN = ['Domain Code', 'Domain', 'Area Code (FAO)', 'Element Code',
           'Element', 'Item Code', 'Year Code', 'Flag', 'Flag Description']
    crops_livestock= pd.read_csv('data_production/FAOSTAT_data_livestock_crops_1978_2019_EN.csv', usecols=lambda x: x not in skipcol_cropsEN, index_col=0 ).reset_index()

    #only the columns we need 
    options = ['Agricultural land', 'Land under temporary crops', 'Land with temporary fallow',
           'Land under permanent crops','Land under perm. meadows and pastures','Forest land','Land under temp. meadows and pastures' ]
    new_df= crops_livestock[crops_livestock["Item"].isin(options)]
    new_df.rename(columns = {'Area' :'Country'}, inplace = True)

    # selecting the country
    Country = st.multiselect("SELECT A COUNTRY", new_df['Country'].unique())
    #create the DF with the country
    new_df_country  = new_df[new_df['Country'].isin(Country)]
    df_year_country = new_df_country.groupby(['Year', 'Item'])['Value'].sum().reset_index()



     # LINECHART BY YEAR
    #create columns wiht the values
    df_year_landUse = df_year_country.pivot(index="Year", columns = "Item").reset_index()
    df_year_landUse.columns = [' '.join(x) for x in df_year_landUse.columns.values]

    #create new columns with values of crops and livestock
    #Need to write a condition, where the column is Zero or NaN 
    df_year_landUse['Land_crops']= df_year_landUse['Value Land under permanent crops'] + df_year_landUse['Value Land under temporary crops']
    df_year_landUse['Land_crops'].round()
    sumcols = df_year_landUse['Value Land under perm. meadows and pastures'] + df_year_landUse['Value Land under temp. meadows and pastures']
    df_year_landUse['Land_livestock'] = sumcols
    df_year_landUse['Land_livestock'].round()
    #remove columns
    df_year_land =  df_year_landUse.drop(['Value Land under perm. meadows and pastures',
                                           'Value Land under permanent crops',
                                            'Value Land under temp. meadows and pastures',
                                           'Value Land under temporary crops'], axis = 1)

    # CHART LINE, Forest vs Crops vs Livestoks per all the period 1998-2018
    df_year_land1 = df_year_land.melt(id_vars=['Year ']+list(df_year_land.keys()[6:]), var_name='landuse')
    df_year_land1 = df_year_land.melt(id_vars=['Year ']+list(df_year_land.keys()[6:]), var_name='landuse')

    # Chart line
    fig_livestock = px.line(df_year_land1, x='Year ', y= 'value', color = "landuse", color_discrete_map={'Value Agricultural land': 'rgb(51, 51, 51)',
                                                                                                'Land_crops':"#2a2b5a",
                                                                                                 'Value Forest land':'#0bca9b',
                                                                                                 'Land_livestock':'#e51858',
                                                                                              'Value Land with temporary fallow': '#F4B436' })

    fig_livestock.update_layout(title="<b>Land use by crops, livestock, forests and fallow. 1998-2019<b>", plot_bgcolor="white")
    fig_livestock.update_xaxes(categoryorder='category ascending')
    fig_livestock.update_layout(xaxis = dict(title = 'Year'), 
                    yaxis = dict(title = 'Number of Hectares'), 
                    legend_title=dict(text='<b>Land Use</b>'),
                    width = 650, height= 400)
    fig_livestock.update_layout(template = new_template)



    # CHARTBAR Forest vs Crops vs Livestoks per year
    #dataframe 
    data = df_year_country.loc[df_year_country['Item'] != "Agricultural land"]
    bar_year = data.loc[data['Year']== 2001].reset_index()
    bar_year.loc[bar_year['Item'] == 'Forest land', 'Type_land'] = 'Forest use'
    bar_year.loc[bar_year['Item'] == 'Land with temporary fallow', 'Type_land'] = 'Fallow use'
    bar_year.loc[(bar_year['Item'] == 'Land under permanent crops')
                 |(bar_year['Item'] == 'Land under temporary crops')
                 |(bar_year['Item'] == 'Land under perm. meadows and pastures')
                 |(bar_year['Item'] == 'Land under temp. meadows and pastures')
                 , 'Type_land']= 'Agriculture use'

    #setting the chart colors
    colors = {'Land under temporary crops': '#90be6d',
                                    'Land under permanent crops':"#43aa8b",
                                    'Forest land':'#2d6a4f', #'#4d908e',#0bca9b',
                                    'Land under perm. meadows and pastures':'#f8961e',
                                   'Land under temp. meadows and pastures': '#f94144',
                                    'Land with temporary fallow': '#f9c74f'}
    # plot the figure use groupby and a list comprehension to create data                                   
    databar = [go.Bar(name=group, x= bar['Type_land'], y= bar['Value'], marker={'color': colors[group]}) for group, bar in bar_year.groupby(by='Item') ]
    x = go.Figure(databar)
    x.update_layout(barmode='stack', title="<b>Land use by crops, livestock, forests and fallow<b>", xaxis_title='Name')
    x.update_xaxes(categoryorder='category ascending')
    x.update_layout(xaxis = dict(title = 'Land Use'), 
                    yaxis = dict(title = 'Number of Hectares'), 
                    legend_title=dict(text='<b>Land Use</b>'),
                    width = 650, height= 400)
    x.update_layout(template = new_template)

    # COLUMNS CONTAINER 3
    col1, col2, col3 = st.beta_columns([1,0.2, 1])

    with col1:
        st.plotly_chart(fig_livestock, unsafe_allow_html=True)
        st.text("Source: FAO STATS 1998-2018. Land Use Inputs") #footer in the chart 
        st.text("Data for all the variables are avaialable from 2001")
    with col2:
        st.text("  ")

    with col3:   
        st.plotly_chart(x, unsafe_allow_html=True)
        st.text("Source: FAO STATS 2018. Land Use Inputs") #footer in the chart 

    st.error('This is an error', icon="🚨")

        
        
# PAGE CONSUMPTION        
elif choice == 'Consumption':

    #st.markdown ('---')
    st.markdown ('<h1 style= "font-family:Verdana; color:Black; font-size: 40px;">2.Issues in Food Consumption</h1>', unsafe_allow_html=True)
    #st.text('this is app')
    st.write (''' 
    This app present interactive dashboards to explore Open Data Sources at global level. You can choose the region and countries, select the analysis, compare between the variables and countries, and select the time period.''')

    st.markdown ('---')
    # CONTAINER 2
    st.title("Prevalence of obesity in adult males")
    st.write (''' The share of adult men defined as obese, measured as the percentage of men with a body
    mass index (BMI) value >30.0. Body mass index is a person's weight in kilograms (kg) divided
    by his or her height in metres squared.''')

    #CREATING DATAFRAMES 
        #file with coordinates
    country_geo = gpd.read_file('data_production/world-countries.json')
    country_geo.rename(columns = {'id' :'ISO3'}, inplace = True)
    
    # DATA total area from NCDRisC
    obesity_adults = pd.read_csv('data_nutrition/prevalence-of-obesity-in-adult-males.csv')

    #mapping obesity 
    country = st.multiselect("SELECT A YEAR", obesity_adults ['Year'].unique(),key= "obesity" )
    new_obesity_adults = obesity_adults [obesity_adults ['Year'].isin(country)]
    obesity_geo = pd.merge(country_geo, new_obesity_adults,left_on='ISO3', right_on='Code', )

    obesity = folium.Map(location=[0,0], zoom_start=2,tiles=None)
    folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(obesity)

    # Creating choropleth map
    obesity.choropleth(geo_data= obesity_geo,
                     name='Choropleth',         
                     data= obesity_geo,
                     columns=['Entity','Obese (NCDRisC (2017))'], 
                     key_on='feature.properties.name', 
                     fill_color= 'YlOrBr', #YlGn', #YlOrRd',
                     fill_opacity=0.6, 
                     line_opacity=0.8,
                     nan_fill_color="white",
                     #bins= [0, 20, 40, 60, 80, 90],
                     legend_name='%', 
                     smooth_factor=0,     
                     highlight=True
                         )


    #Adding labels to map
    style_function = lambda x: {'fillColor': '#ffffff', 
                                    'color':'#000000', 
                                    'fillOpacity': 0.1, 
                                    'weight': 0.1}

    obesity_tooltip = folium.features.GeoJson(
           obesity_geo,
            style_function=style_function, 
            control=False,
            tooltip=folium.features.GeoJsonTooltip(
                fields=['Entity','Obese (NCDRisC (2017))'
                        ],
                aliases=['Country: '
                        ,'% prevalence Obesity: '
                        ],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
            )
        )
    obesity.add_child(obesity_tooltip)
    obesity.keep_in_front(obesity_tooltip)
    folium.LayerControl().add_to(obesity)
    folium_static(obesity, width=1000, height=550)
    st.write("Source: Obese NCDRisC. Dataset Available here: [link](https://www.ncdrisc.org/data-downloads.html)")             


    
# PAGE SOCIAL 
    
elif choice == 'Social':
   
    #CONTAINER:HEADER
    st.markdown ('<h1 style= "font-family:Verdana; color:Black; font-size: 40px;">3. Social Issues</h1>', unsafe_allow_html=True)
  
    st.markdown ('---')
    #CONTAINER 4
    st.title("The land is in the hands of big farms")
    st.write("This map the % of land own by small-farms and the total (%) of small farms in each country")

    #OPTION
    farm_option = st.radio("SELECT AN OPTION", ("Land in smallfarms % ", 'Total smallfarms %'))


    #GEO DATA MAP2 
    country_geo1 = gpd.read_file('data_production/world-countries.json')
    names = pd.read_csv('data_production/country names vs UNoficial_2021 - Sheet1.csv') #dataset with UN OFICIAL names
    #merging the list of names to get the ISOCODE
    names.rename(columns = {'land GRAIN ' :'Country'}, inplace = True)
    farms_iso = pd.merge(df_all, names, on=["Country"])
    farm_iso_d = farms_iso.round()
    # creating the geo file
    farms_geo = country_geo1.merge(farm_iso_d, how="left", left_on=["id"], right_on=['ISO3'])


    if farm_option == "Land in smallfarms % ":

        landfarm = folium.Map(location=[0,0], zoom_start=2,tiles=None)
        folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(landfarm)
        # Creating choropleth map

        landfarm.choropleth(geo_data= farms_geo,
                     name='Choropleth',         
                     data= farms_geo,
                     columns=['name','% of agricultural land in the hands of small farmers'], 
                     key_on='feature.properties.name', 
                     fill_color= 'RdBu', #YlGn', #YlOrRd',
                     fill_opacity=0.6, 
                     line_opacity=0.8,
                     nan_fill_color="white",
                     #bins=[0, 20, 40, 60, 80, 100],
                     legend_name='% small-Farms (%)', 
                     smooth_factor=0,     
                     highlight=True
                         )


        #Adding labels to map
        style_function = lambda x: {'fillColor': '#ffffff', 
                                    'color':'#000000', 
                                    'fillOpacity': 0.1, 
                                    'weight': 0.1}

        landfarm_tooltip = folium.features.GeoJson(
           farms_geo,
            style_function=style_function, 
            control=False,
            tooltip=folium.features.GeoJsonTooltip(
                fields=['name', '% of agricultural land in the hands of small farmers'
                        ],
                aliases=['Country: '
                        ,'% land in small-farms: '
                        ],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
            )
        )
        landfarm.add_child(landfarm_tooltip)
        landfarm.keep_in_front(landfarm_tooltip)
        folium.LayerControl().add_to(landfarm)

        folium_static(landfarm, width=1000, height=550)


    #map
    if farm_option == 'Total smallfarms %': 

        farm = folium.Map(location=[0,0], zoom_start=2,tiles=None)
        folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(farm)
        # Creating choropleth map

        farm.choropleth(geo_data= farms_geo,
                     name='Choropleth',         
                     data= farms_geo,
                     columns=['name','small farms as % of all farms'], 
                     key_on='feature.properties.name', 
                     fill_color= 'YlOrBr', #YlGn', #YlOrRd',
                     fill_opacity=0.6, 
                     line_opacity=0.8,
                     nan_fill_color="white",
                     #bins= [0, 20, 40, 60, 80, 90],
                     legend_name='% small-Farms (%)', 
                     smooth_factor=0,     
                     highlight=True
                         )


        #Adding labels to map
        style_function = lambda x: {'fillColor': '#ffffff', 
                                    'color':'#000000', 
                                    'fillOpacity': 0.1, 
                                    'weight': 0.1}

        farm_tooltip = folium.features.GeoJson(
           farms_geo,
            style_function=style_function, 
            control=False,
            tooltip=folium.features.GeoJsonTooltip(
                fields=['name', 'small farms as % of all farms'
                        ],
                aliases=['Country: '
                        ,'% small-farms: '
                        ],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
            )
        )
        farm.add_child(farm_tooltip)
        farm.keep_in_front(farm_tooltip)
        folium.LayerControl().add_to(farm)

        folium_static(farm, width=1000, height=550)

    st.write("2014, GRAIN. Dataset Available here: [link](https://grain.org/article/entries/4929-hungry-for-land-small-farmers-feed-the-world-with-less-than-a-quarter-of-all-farmland)")
    st.text("NOTE: Countries define 'small farmer'differently. Click in the bottom SMALLFARMS CRITERIA to download the data")
    # other questions



elif choice == 'Climate change':
    st.markdown ('<h1 style= "font-family:Verdana; color:Black; font-size: 40px;">4. Climate Change Issues</h1>', unsafe_allow_html=True)
  
    st.markdown ('---')
    st.title("Land use per kilogram of food product")
    st.write (''' Land use is measured in meters squared (m²) per kilogram of a given food product.''')

    # DATA total area from NCDRisC
    food_land = pd.read_csv('data_nutrition/land-use-protein-poore(1).csv')
    food_landsorted = food_land.sort_values(by= "Land use per 100g protein (Poore & Nemecek, 2018)", ascending=True)
    bar_foodland = px.bar(food_landsorted  , x="Land use per 100g protein (Poore & Nemecek, 2018)", y="Entity", width= 900, height = 800)
    bar_foodland.update_layout(plot_bgcolor= "white")
    bar_foodland.update_layout(title = "  ", title_font_size = 20)
    bar_foodland.update_traces(marker_color='#00aae6', opacity = 0.8)
    bar_foodland.update_yaxes(tickmode="array", title_text= " ")
    bar_foodland.update_xaxes(title_text = 'Land use per 100g protein',

                    title_font=dict( size=15, family='Verdana', color='Black'), 
                    tickfont=dict( size=15, family='Verdana', color='Black'),
                    tickmode="array",
                    visible= True,
                    color= 'black',
                    showgrid = True,
                    gridcolor = '#abd3df')
    st.plotly_chart(bar_foodland, unsafe_allow_html=True)
    st.write("Source: Poore & Nemecek, 2018. Dataset Available here: [link](https://science.sciencemag.org/content/360/6392/987)")             
    # CONTAINER FOOD CO2
    st.markdown ('---')

    st.title("GHG emissions per kilogram (Poore & Nemecek, 2018)")
    st.write ('''Greenhouse gas emissions are measured in kilograms of carbon dioxide equivalents (kgCO₂eq) per kilogram of food product. ''')


    # DATA total area from NCDRisC
    food_print = pd.read_csv('data_climate/food-footprints.csv')

    food_print_sorted = food_print.sort_values(by= "GHG emissions per kilogram (Poore & Nemecek, 2018)", ascending=True)
    bar_food_print = px.bar(food_print_sorted  , x="GHG emissions per kilogram (Poore & Nemecek, 2018)", y="Entity", width= 900, height = 800)
    bar_food_print.update_layout(plot_bgcolor= "white")
    bar_food_print.update_layout(title = "  ", title_font_size = 20)
    bar_food_print.update_traces(marker_color= '#B4C292', opacity = 0.8)
    bar_food_print.update_yaxes(tickmode="array", title_text= " ")
    bar_food_print.update_xaxes(title_text = 'GHG emissions per kilogram',

                    title_font=dict( size=15, family='Verdana', color='Black'), 
                    tickfont=dict( size=15, family='Verdana', color='Black'),
                    tickmode="array",
                    visible= True,
                    color= 'black',
                    showgrid = True,
                    gridcolor = '#abd3df')
    st.plotly_chart(bar_food_print, unsafe_allow_html=True)
    st.write("Source: Poore & Nemecek, 2018. Dataset Available here: [link](https://science.sciencemag.org/content/360/6392/987)")             

    st.markdown ('---')
    st.write('DASHBOARD RECOMENDATIONS')
    ''' 
    . what food we produce most?
    - who produced what?
    - % import food by country
    - % export food by country
    - how we can answer we produce for humans, animals and cars?

    '''



