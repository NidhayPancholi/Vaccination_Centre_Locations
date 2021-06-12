import requests
import folium
import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input,Output
from cowin_api import CoWinAPI
api=CoWinAPI()


def get_district_names():
    state=api.get_states()
    districts={}
    for x in state['states']:
        districts[x['state_name']]=[]
        temp=api.get_districts(x['state_id'])
        for y in temp['districts']:
            districts[x['state_name']].append([y['district_name'],y['district_id']])
    return districts


m=folium.Map(
    location=[25,80],
    zoom_start=10
)
m.save('Location.html')
app=dash.Dash(__name__)
districts=get_district_names()
app.layout=html.Div(
    children=[
        dcc.Dropdown(id='state',value='Gujarat',options=[{'label':x,'value':x} for x in districts.keys()]),
        dcc.Dropdown(id='district',value='Ahmedabad',options=[]),
        html.Iframe(id='folium_map',srcDoc=open('Location.html','r').read(),width='100%',height='600')
    ])


@app.callback(
    Output('district','options'),
    [Input('state','value')]
)
def dropdown_vals(state):
    temp=districts[state]
    o=[]
    for x in temp:
        o.append({'label':x[0],'value':x[0]})
    return o


@app.callback(
    Output('folium_map','srcDoc'),
    [Input('district','value'),Input('state','value')]
)
def update_map(district,state):
    temp=districts[state]
    code=None
    for x in temp:
        if x[0]==district:
            code=x[1]
    if code is None:
        m = folium.Map(
            location=[25, 80],
            zoom_start=10
        )
        m.save('Location.html')
        return open('Location.html','r').read()
    else :
        URL='https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict'
        centers=requests.get(URL,params={'district_id':code,'date':'12-06-2021'}).json()
        print(centers)
        map=folium.Map(location=[25,80],zoom_start=6)
        for x in centers['centers']:
            folium.Marker(location=[x['lat'],x['long']],
                          popup=folium.Popup(x['name'],parse_html=True)
                          ).add_to(map)
        map.save("Location.html")
        return open('Location.html','r').read()


app.run_server(debug=True)

