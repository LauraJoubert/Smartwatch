import dash
from dash.dependencies import Output, Input
from dash import dcc 
import dash_core_components as dcc
from dash import html 
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque

import serial     
import re         
import time       
import tkinter as tk
import sys
import csv
import numpy as np

import plotly.express as px

import dash_bootstrap_components as dbc
from datetime import datetime
import matplotlib.pyplot as plt


#Console installations
#!pip install pyserial
#!pip install dash
#!pip install dash-bootstrap-components


ser = serial.Serial()
ser.port = 'COM3'
ser.baudrate = 9600
ser.open()

X_bpm = deque(maxlen=20)
bpm_list = deque(maxlen=20) 

# Reading BPM's no sport
with open('no-sport.txt', 'r') as file:
    no_sport = [float(line.strip()) for line in file.readlines()]
    
# Reading BPM's sport
with open('sport.txt', 'r') as file:
    sport = [float(line.strip()) for line in file.readlines()]

# Reading steps given in a week
with open('steps_per_day.txt', 'r') as file:
    week = [float(line.strip()) for line in file.readlines()]
    
# Reading BPM of a day
with open('pulsaciones.txt', 'r') as file:
    pulsaciones = [float(line.strip()) for line in file.readlines()]

# Reading BPM while swimming
with open('swimming_bpm.txt', 'r') as file:
    bpm_swimming = [float(line.strip()) for line in file.readlines()]

# Reading BPM while running    
with open('running_bpm.txt', 'r') as file:
    bpm_running = [float(line.strip()) for line in file.readlines()]
 
# Reading BPM while cycling
with open('cycling_bpm.txt', 'r') as file:
    bpm_cycling = [float(line.strip()) for line in file.readlines()]
    
# Reading steps given day a day
with open('monday.txt', 'r') as file:
    monday_data = [float(line.strip()) for line in file.readlines()]
    
with open('tuesday.txt', 'r') as file:
    tuesday_data = [float(line.strip()) for line in file.readlines()]
    
with open('wednesday.txt', 'r') as file:
    wednesday_data = [float(line.strip()) for line in file.readlines()]

with open('thursday.txt', 'r') as file:
    thursday_data = [float(line.strip()) for line in file.readlines()]

with open('friday.txt', 'r') as file:
    friday_data = [float(line.strip()) for line in file.readlines()]

with open('saturday.txt', 'r') as file:
    saturday_data = [float(line.strip()) for line in file.readlines()]
    
with open('sunday.txt', 'r') as file:
    sunday_data = [float(line.strip()) for line in file.readlines()]

serial_read_state = True
def serialRead(ser, cmd):   
    global serial_read_state
    if (serial_read_state==True):
        serial_read_state=False
        read_command = (cmd+'\n')
        ser.write(read_command.encode("utf-8"))
        message = ser.readline() 
        data_string = message.decode("utf-8") 
        data = re.findall('[\d]+[.,\d]+', data_string) 
        data = float(data[0])
        
        serial_read_state=True
        
    else:
        time.sleep(0.1)
        data=serialRead(ser, cmd)
    return data

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ])

tab1 = dbc.Card(
    dbc.CardBody([ 
            html.Div([             
                html.H1(id='live-update-time', style={'textAlign': 'right', 'color': 'black', 'font-weight': 'bold', 'fontSize': 52}),
                dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
                html.H4(id='current-date'),
                    ]),
            html.H1('Actual BPM', style={'textAlign': 'center'}), 
            html.Div(id='live-update-text', style={'textAlign': 'center'}),        
            dbc.Row([
                    dbc.Col(dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(id='live-graph', animate=True),
                            dcc.Interval(id='graph-update', interval=2*1000),
                            ]),
                        inverse=True), 
                        width=9),
                    dbc.Col(dbc.Card(
                         dbc.CardBody([                                 
                             html.H4('Mean BPM', className='card-title',style={'textAlign': 'center'}),
                             html.H2(id='live-update-text',style={'textAlign': 'center','fontSize': 40}),
                             html.Img(src='https://media.idownloadblog.com/wp-content/uploads/2015/03/Apple-Watch-Wallpaper-i6-White.png', style={'width': '25vh', 'height': '38vh'}, className='align-self-center'),
                             ]),
                         inverse=True), 
                        width=3,className='mx-auto'),
                ]),     
            
            html.Br(),
            html.Br(),
            
            html.H1('Your usual values', style={'textAlign': 'center'}),
            html.P(id='live-update-no-sport'),
            html.P(id='live-update-sport'),

            dbc.Row([
                    dbc.Col(dbc.Card(
                         dbc.CardBody([
                             html.H4('Mean Sport', className='card-title',style={'textAlign': 'center'}),
                             html.H2(id='live-update-sport',style={'textAlign': 'center','fontSize': 20}),
                             ]),
                         color='lightblue', inverse=True), 
                        width=6,),
                    dbc.Col(dbc.Card(
                        dbc.CardBody([
                            html.H4('Mean No-Sport', className='card-title',style={'textAlign': 'center'}),
                            html.H2(id='live-update-no-sport',style={'textAlign': 'center','fontSize': 20}),
                            ]),
                        color='lightblue', inverse=True), 
                        width=6),
                    ]),

            html.Br(),

            dcc.Graph(id='sport-no-sport-graph', animate=True)
                ]),
         )

tab2 = dbc.Card(
    dbc.CardBody([         
            html.H1('Weekly analysis', style={'textAlign': 'center'}),
            
            html.Br(),
            
            html.H4('Steps per day in a week', style={'textAlign': 'center'}),
            dcc.Graph(id='week-steps'),
            
            html.Br(),

            dbc.Row([
                dbc.Col(dbc.Card(
                    dbc.CardBody([
                        html.H4('Max steps', className='card-title',style={'textAlign': 'center'}),
                        html.H2(id='max-steps-msg',style={'textAlign': 'center','fontSize': 20}),
                        ]),
                    
                        color='lightblue', inverse=True), 
                    width=4), 
                dbc.Col(dbc.Card(
                    dbc.CardBody([
                        html.H4('Min steps', className='card-title',style={'textAlign': 'center'}),
                        html.H2(id='min-steps-msg',style={'textAlign': 'center','fontSize': 20}),
                        ]),
                        color='lightblue', inverse=True), 
                    width=4),
                dbc.Col(dbc.Card(
                        dbc.CardBody([
                        html.H4('Sum steps', className='card-title',style={'textAlign': 'center'}),
                        html.H2(id='sum-steps-msg',style={'textAlign': 'center','fontSize': 20}),
                        ]),
                        color='lightblue', inverse=True), 
                    width=4),
                ]),

            html.Br(),
            html.Br(),
            
            html.H4('Day Steps', style={'textAlign': 'center'}),
            
            html.Br(),

            dcc.Dropdown(
                id='dropdown1',
                options=[
                    {'label': 'Monday', 'value': 'monday'},
                    {'label': 'Tuesday', 'value': 'tuesday'},
                    {'label': 'Wednesday', 'value': 'wednesday'},
                    {'label': 'Thursday', 'value': 'thursday'},
                    {'label': 'Friday', 'value': 'friday'},
                    {'label': 'Saturday', 'value': 'saturday'},
                    {'label': 'Sunday', 'value': 'sunday'},
                    ],
                value='friday',
                style={'color': 'black'}
                ), 
            
            html.Br(),
            
            dcc.Graph(id='day-steps'),
            
            html.Br(),            
 
            ])
        )
  
tab3 = dbc.Card(
    dbc.CardBody(
        [              
        html.H1('BPM by sport', style={'textAlign': 'center'}),
        html.P(id='bpm_swim'),
        html.P(id='bpm_run'),
        html.P(id='bpm_cycling'),
        dcc.Graph(id='different_sports_graph', animate=True),
        
        html.Br(),
        html.Br(),
        
        dbc.Row([
            dbc.Col(dbc.Card(
                dbc.CardBody([
                    dcc.Dropdown(id='dropdown2',options=[
                        {'label': 'Running', 'value': 'running'},
                        {'label': 'Swimming', 'value': 'swimming'},
                        {'label': 'Cycling', 'value': 'cycling'}
                        ],
                        value='running',
                        style={'color': 'black'}
                        ),  
                    html.Br(),
                    html.Img(src='https://www.farmacias1000.com/blog/wp-content/uploads/siluetas-colores-corredores_23-2147619177-e1545308005120.jpg', style={'width': '52vh', 'height': '48vh'}, className='align-self-center'),                             ]
                    ),
                    inverse=True
                    ), width=6),
                
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4('BPM distribution by Sport', className='card-title',style={'textAlign': 'center'}),
                            dcc.Graph(id='sport-box')
                            ]
                        ),
                    inverse=True
                    ), width=6),                
            ]),
            
        html.Br(),

            ]
    )
)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(tab1, label="Real time values"),
                dbc.Tab(tab2, label="Historical analysis"),
                dbc.Tab(tab3, label="Training analysis"),
            ])
        ])
    ])
]) 

#Hora
@app.callback(Output('live-update-time', 'children'),
              [Input('graph-update', 'n_intervals')])
def update_time(input_data):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return f"{current_time}"

#Fecha
def get_current_date():
    now = datetime.now()
    current_date = now.strftime("%d-%m-%Y")
    return html.Div([
        html.H1(current_date,style={'textAlign': 'right', 'color': 'black', 'fontSize': '75%'})
    ])

@app.callback(dash.dependencies.Output('current-date', 'children'),
              [dash.dependencies.Input('interval-component', 'n_intervals')])
def update_current_date(n):
    return get_current_date()

#Media bpm
@app.callback(Output('live-update-text', 'children'), 
              [Input('graph-update', 'n_intervals')])

def update_mean(input_data):  
    if len(bpm_list) > 0:
        mean_bpm = np.mean(bpm_list)
        return f"{mean_bpm:.2f}"   

@app.callback(Output('live-graph', 'figure'),    
              [Input('graph-update', 'n_intervals')])

def update_graph_scatter(input_data):  
    if len(X_bpm) == 0:
        X_bpm.append(1)
    else:
        X_bpm.append(X_bpm[-1]+1)
    bpm = serialRead(ser, 'bpm')
    bpm_list.append(bpm) 
    data = go.Scatter(
            x=list(X_bpm),
            y=list(bpm_list),
            name='Scatter',
            mode= 'lines+markers'
            )
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X_bpm),max(X_bpm)]),  
                                                yaxis=dict(range=[0,200]),
                                                xaxis_title='Time Step (2s)',
                                                yaxis_title='BPM',
                                                )} 

@app.callback(Output('live-update-sport', 'children'), 
              [Input('graph-update', 'n_intervals')])

def sport_mean(input_data):
    mean_sport = np.mean(sport)
    return f" {mean_sport:.2f} BPM"

@app.callback(Output('live-update-no-sport', 'children'), 
              [Input('graph-update', 'n_intervals')])

def no_sport_mean(input_data):
    mean_no_sport = np.mean(no_sport)
    return f" {mean_no_sport:.2f} BPM"

@app.callback(Output('sport-no-sport-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_data_graph_scatter(input_data):  
    sport_trace = go.Scatter(
        x=list(range(1, len(sport)+1)),
        y=sport,
        name='Sport',
        mode='lines+markers'
    )
    no_sport_trace = go.Scatter(
        x = list(range(1, len(no_sport)+1)),
        y = no_sport,
        name='No-Sport',
        mode='lines+markers'
    )
    
    return {'data': [no_sport_trace, sport_trace], 
            'layout': go.Layout(xaxis=dict(range=[0,20]),
                                 yaxis=dict(range=[0, 200]),
                                 xaxis_title='Time Step',
                                 yaxis_title='BPM',
                                 legend=dict(x=0, y=1),
                                 )}

@app.callback(Output('different_sports_graph', 'figure'),
              [Input('graph-update', 'n_intervals')])

def different_sport_graph(input_data):
    run_trace = go.Scatter(
        x=list(range(1, len(bpm_running)+1)),
        y=bpm_running,
        name='Running',
        mode='lines'
    )
    swim_trace = go.Scatter(
        x = list(range(1, len(bpm_swimming)+1)),
        y = bpm_swimming,
        name='Swimming',
        mode='lines'
    )
    cycling_trace = go.Scatter(
        x = list(range(1, len(bpm_cycling)+1)),
        y = bpm_cycling,
        name='Cycling',
        mode='lines'
    )
    
    max_value = []
    for i in range(103):
        max_value.append(160)

    max_trace = go.Scatter(
        x=list(range(1, len(bpm_cycling)+1)),
        y=max_value,
        name='Max',
        line=dict(dash='dash', width=2, color='red')
        )
    
    min_value = []
    for i in range(103):
        min_value.append(90)
    
    min_trace = go.Scatter(
        x=list(range(1, len(bpm_cycling)+1)),
        y=min_value,
        name='Min',
        line=dict(dash='dash', width=2, color='red')
        )
      
    return {'data': [run_trace, swim_trace, cycling_trace, max_trace, min_trace], 
            'layout': go.Layout(xaxis=dict(range=[0,len(bpm_running)]),
                                 yaxis=dict(range=[0, 200]),
                                 xaxis_title='Time Step',
                                 yaxis_title='BPM',
                                 legend=dict(x=1, y=1),
                                 )}

@app.callback(Output('week-steps', 'figure'),
              [Input('graph-update', 'n_intervals')])
def week_step(input_data):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        y=week,
        name='Steps'
    ))

    fig.update_layout(xaxis_title='Week days', yaxis_title='Steps')
    return fig   
 
@app.callback(Output('max-steps-msg', 'children'),
              [Input('graph-update', 'n_intervals')])
def max_steps_msg(input_data):
    max_steps = int(max(week))
    max_day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][week.index(max_steps)]
    return f' {max_day} {max_steps}'


@app.callback(Output('min-steps-msg', 'children'),
              [Input('graph-update', 'n_intervals')])
def min_steps_msg(input_data):
    min_steps = int(min(week))
    min_day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][week.index(min_steps)]
    return f' {min_day} {min_steps}'

@app.callback(Output('sum-steps-msg', 'children'),
              [Input('graph-update', 'n_intervals')])
def sum_steps(input_data):
    total_steps = int(sum(week))
    return f' {total_steps}'

@app.callback(Output('day-steps', 'figure'),
              [Input('dropdown1', 'value'),])

def day_steps(value):
    if value == 'monday':
        fig = go.Scatter(
            x=list(range(1, len(monday_data)+1)),
            y=monday_data,
            name='Monday',
            mode='lines+markers')
    elif value == 'tuesday':
        fig = go.Scatter(
            x=list(range(1, len(tuesday_data)+1)),
            y=tuesday_data,
            name='Tuesday',
            mode='lines+markers')
    elif value == 'wednesday':
        fig = go.Scatter(
            x=list(range(1, len(wednesday_data)+1)),
            y=wednesday_data,
            name='Wednesday',
            mode='lines+markers')
    elif value == 'thursday':
        fig = go.Scatter(
            x=list(range(1, len(thursday_data)+1)),
            y=thursday_data,
            name='Thursday',
            mode='lines+markers')
    elif value == 'friday':
        fig = go.Scatter(
            x=list(range(1, len(friday_data)+1)),
            y=friday_data,
            name='Friday',
            mode='lines+markers')
    elif value =='saturday':
        fig = go.Scatter(
            x=list(range(1, len(saturday_data)+1)),
            y=saturday_data,
            name='Saturday',
            mode='lines+markers')
    else:
        fig = go.Scatter(
            x=list(range(1, len(sunday_data)+1)),
            y=sunday_data,
            name='Sunday',
            mode='lines+markers')

    return {'data': [fig], 
            'layout': go.Layout(xaxis=dict(range=[0,24]),
                                 yaxis=dict(range=[0, 4000]),
                                 xaxis_title='Day hours',
                                 yaxis_title='Steps',
                                 )}
@app.callback(
    Output('sport-box', 'figure'),
    [Input('dropdown2', 'value')] 
    )
def update_box_plot(value):
    if value == 'running':
        data = [go.Box(y=bpm_running, name='Running')]
    elif value == 'swimming':
        data = [go.Box(y=bpm_swimming, name='Swimming')]
    else:
        data = [go.Box(y=bpm_cycling, name='Cycling')]
    return {
        'data': data,
        'layout': go.Layout(
            title='BPM',
            yaxis=dict(range=[0, 200]),
            xaxis_title='Type of activity',
            yaxis_title='BPM'
        )}

if __name__ == '__main__':
    app.run_server(port=8044, debug=False)