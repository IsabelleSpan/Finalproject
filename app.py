#!/usr/bin/env python
# coding: utf-8

# In[ ]:



import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# Import the data
df = pd.read_csv("nama_10_gdp_1_Data.csv")
df = df.drop(["Flag and Footnotes","NA_ITEM"],axis=1)

# Clean the data 
lst = list()
df["Value"] = df["Value"].replace(":",np.NaN)
df = df.dropna()
for i in df["Value"]:
    i = str(i)
    i = i.replace("''","")
    i = i.replace(" ","0")
    float(i)
    lst.append(i)
df["Value"] = lst
df["Value"] = pd.to_numeric(df["Value"],errors='coerce')

available_indicators = df['UNIT'].unique()
available_countries = df["GEO"].unique()

# dash creates the webserver running the page
app = dash.Dash(__name__)
server = app.server
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
app.config['suppress_callback_exceptions'] = True

#             Main Frame
app.layout =  html.Div([
    
    # Dropdown Grid
    html.Div([

        # First dropdown
        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value=available_indicators[0]
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        # Second Dropdown
        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value=available_indicators[1]
            )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    html.Div([
    dcc.Graph(id='indicator-graphic',
              hoverData={'points': [{'customdata': 'Japan'}]})
            ],style={'padding': '0 155'}),

    dcc.Slider(
        id='year--slider',
        min=df['TIME'].min(),
        max=df['TIME'].max(),
        value=df['TIME'].max(),
        step=None,
        marks={str(year): str(year) for year in df['TIME'].unique()}
    ),
    html.Div([
        
        html.Div([dcc.Dropdown(
            id='yaxis-column_2',
            options=[{'label': i, 'value': i} for i in available_indicators],
            value = available_indicators[0]
            )
        ],style={'width': '48%', 'display': 'inline-block','marginBottom': 50, 'marginTop': 35}),
        
        html.Div([dcc.Dropdown(
            id='xaxis-column_2',
            options=[{'label': i, 'value': i} for i in available_countries],
            value = available_countries[0]
            )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block','marginBottom': 50, 'marginTop': 35})
    ]),
                  
    dcc.Graph(id='indicator-graphic_2')
        
])
# One output, which is the figure and many inputs
# It calls back everytime the inputs change
# app.callback is a creator, which is called inside the function
# Input is changed via the callback function and then the function update_graph is run
# put in the same name of the callback function into the update graph function
@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 year_value):
    dff = df[df['TIME'] == year_value]
# returns a scatter
    return {
        'data': [go.Scatter(
            x=dff[dff['UNIT'] == xaxis_column_name]['Value'],
            y=dff[dff['UNIT'] == yaxis_column_name]['Value'],
            text=dff[dff['UNIT'] == yaxis_column_name]['GEO'],
            customdata=dff[dff['UNIT'] == yaxis_column_name]['GEO'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear'
            },
            margin={'l': 120, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
            clickmode= 'event+select'
        )
    }

# Update the Dropdown
@app.callback(
    dash.dependencies.Output('yaxis-column_2', 'value'),
    [dash.dependencies.Input('xaxis-column', 'value')])
def update_dropdown(selection):
    dic = {"Chain linked volumes, index 2010=100":0,"Current prices, million euro":1,"Chain linked volumes (2010), million euro":2}
    selection = dic[selection]
    return available_indicators[selection]
        
    
# Update the Graph with Hovering
def create_time_series(dff,yaxis_column_name_2):
    return {
        'data': [dict(
            x=dff['TIME'],
            y=dff['Value'],
            mode='lines+markers'
        )],
        'layout': go.Layout(
            yaxis={
                'title': yaxis_column_name_2,
                'type': 'linear'
            },
            margin={'l': 120, 'b': 40, 't': 10, 'r': 0})
        }

# Update the Graph with Hovering
@app.callback(
    dash.dependencies.Output('indicator-graphic_2', 'figure'),
    [dash.dependencies.Input('indicator-graphic', 'hoverData'),
     dash.dependencies.Input('yaxis-column_2', 'value')])
def update_timeseries(hoverData, yaxis_column_name_2):
    country_name = hoverData['points'][0]['customdata']
    dff = df[df['GEO'] == country_name]
    dff = dff[dff['UNIT'] == yaxis_column_name_2]
    return create_time_series(dff,yaxis_column_name_2)

# Update the Dropdown countries
@app.callback(
    dash.dependencies.Output('xaxis-column_2', 'value'),
    [dash.dependencies.Input('indicator-graphic', 'hoverData')])
def update_dropdown(hoverData):
    country_name = hoverData['points'][0]['customdata']
    return country_name


if __name__ == '__main__':
    app.run_server()

