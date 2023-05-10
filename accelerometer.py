
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

import serial     # library used to communicate with serial port
import re         # library used to extract data from string
import time       # library used to create periodic reading event
 

#X_humd=deque(maxlen=20)         #En nuestro dash, si tenemos por ejemplo una gráfica que va actualizando los 
                                #valores en tiempo real, no vana poder salir todos los datos que hemos obtenido
                                #desde el principio. Definimos que como máximo veremos 20 datos
#X_humd.append(1)
#X_temp=deque(maxlen=20)
#X_temp.append(1)
#temp_list = deque(maxlen=20)
#temp_list.append(1)
#humd_list = deque(maxlen=20)
#humd_list.append(1)

X_step=deque(maxlen=30)
step_list = deque(maxlen=30)


#arduinoData = []       # list to save data from Arduino
ser = serial.Serial()  # create a serial instance
ser.port = 'COM3'      # set the port number
ser.baudrate = 9600    # set the baudrate of the port


ser.open()

serial_read_state = True
def serialRead(ser, cmd):   #Serial read function
    global serial_read_state
    if (serial_read_state==True):   # Avoid reading serial port at the same time -> conflict
        serial_read_state=False
        read_command = (cmd+'\n')
        ser.write(read_command.encode("utf-8"))
        message = ser.readline() # read a line of data from serial port
        print('msg' + str(message))
        data_string = message.decode("utf-8") # decode the received message to string
        print(data_string)
        valor = re.findall('[\d]+', data_string) # extract values from string in a list
        #data=[int(s) for s in valor]
        data = int(valor[0])
        print('data ' + str(data))
        serial_read_state=True
    else:
        time.sleep(0.1)
        data=serialRead(ser, cmd)
    return data 

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.Div([
        html.H1('Steps'),
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=300    # update every 5 seconds 
        ),
    ]),
    #html.Div([
       #dcc.Graph(id='live-graph2', animate=True),
       #dcc.Interval(
            #id='graph-update2',
            #interval=2*1000    # update every 5 seconds
        #),
    #])
  ]
)

@app.callback(Output('live-graph', 'figure'),    # callback to update live-graph
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(input_data):  #function to update data of live-graph
    if len(X_step)==0:
        X_step.append(1)
    else:
        X_step.append(X_step[-1]+1)
    step = serialRead(ser, 'step')
    step_list.append(step)   # display the first Arduino data from the list
    data = go.Scatter(
            x=list(X_step),
            y=list(step_list),
            name='Scatter',
            mode= 'lines+markers'
            )
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X_step),max(X_step)]),   # x-> time step range
                                                yaxis=dict(range=[0,1050]),
                                                xaxis_title='Time Step (2s)',
                                                yaxis_title='STEP')} # y-> temp range

# @app.callback(Output('live-graph2', 'figure'),  #callback to update live-graph2
#               [Input('graph-update2', 'n_intervals')])
# def update_graph_scatter_temp(input_data): #function to update data of live-graph2
#     #X_temp.append(X_temp[-1]+1)
    
#     if len(X_temp)==0:
#         X_temp.append(1)
#     else:
#         X_temp.append(X_temp[-1]+1)
    
#     temp = serialRead(ser,'temp')
#     temp_list.append(temp)
#     data = go.Scatter(
#             x=list(X_temp),
#             y=list(temp_list),
#             name='Scatter',
#             mode= 'lines+markers'
#             )
#     return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X_temp),max(X_temp)]),   # x-> time step range
#                                                 yaxis=dict(range=[15,20]),
#                                                 xaxis_title='Time Step (2s)',
#                                                 yaxis_title='Temperature (℃)',)} # y-> temp range


if __name__ == '__main__':
    app.run_server(port=8044, debug=False) 