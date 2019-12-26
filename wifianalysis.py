#!/usr/bin/env python
# coding: utf-8

import sys
from datetime import datetime
import numpy as np
import pandas as pd
import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go

csv_content = '/home/juan/scans/dataframes/content.csv'
df = pd.read_csv(csv_content)
print('-'*160)
print("Starting @ {}".format(datetime.now()))
# print("Original size of df is {}".format(df.shape))
# df = df[df['timeSeenTotal'] >= 2 * 60 * 60]
# print("Filtered df size is {}".format(df.shape))


# normalized_power = (df['powerAvg']-df['powerAvg'].mean())/df['powerAvg'].std()
normalized_power = (df['powerAvg']-df['powerAvg'].min())/(df['powerAvg'].max()-df['powerAvg'].min())
power_bins = pd.cut(df['power'], 4)
packets_bins = pd.cut(df['packets'], 4)


def clean_manufacturer(x):
    if isinstance(x, str):
        if 'apple' in x.lower():
            return 'Apple'
        elif 'samsung' in x.lower():
            return 'Samsung'
    return x

df.insert(0, 'inc', range(1, len(df)+1))
df['lastTimeSeen'] = pd.to_datetime(df['lastTimeSeen'], format='%Y-%m-%d %H:%M:%S')
df['firstTimeSeen'] = pd.to_datetime(df['firstTimeSeen'], format='%Y-%m-%d %H:%M:%S')
df['stationMacVendor'] = df['stationMacVendor'].map(clean_manufacturer)
df['date'] = df['firstTimeSeen'].map(lambda x: datetime.strftime(x, '%d-%m-%Y'))
df['time'] = df['firstTimeSeen'].map(lambda x: datetime.strftime(x, '%H:%M:%S'))

tbins = pd.timedelta_range(0, periods=25, freq='H')
tslots = pd.cut(pd.to_timedelta(df['time']), bins=tbins)
dfheatmap = df.replace(0, np.nan).groupby([tslots, pd.cut(df['packets'], 1)]).packets.mean().unstack()

df['power'] = df['power'].map(lambda x: '{0:,.0f}'.format(x))
df['packets'] = df['packets'].map(lambda x: '{0:,.0f}'.format(x))
df['packetsAvg'] = df['packetsAvg'].map(lambda x: '{0:,.1f}'.format(x))
df['powerAvg'] = df['powerAvg'].apply(lambda x: '{0:,.1f}'.format(x))
df['packetsTotal'] = df['packetsTotal'].map(lambda x: '{0:,.0f}'.format(x))
df['timeSeen'] = df['timeSeen'].map(lambda x: '{0:,.0f}'.format(x))
#df['timeSeenTotal'] = df['timeSeenTotal'].map(lambda x: '{0:,}'.format(x))

df.set_index('lastTimeSeen', inplace=True)

config_toolbar = {'editable': True, 'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'hoverClosestCartesian', 'hoverCompareCartesian']}

datepicker = html.Div(children=[
        dcc.DatePickerSingle(
            id='my-date-picker-single',
            min_date_allowed=df.index.min(),
            max_date_allowed=df.index.max(),
            display_format='DD/MM/YYYY',
            clearable=True,
            # with_portal=True,
            placeholder='Pick a date'
        ),
    ])


navbar = dbc.NavbarSimple(
    children=[
        datepicker,
    ],
    brand="Wifi scans",
    brand_href="#",
    dark=True,
    color='dark',
    #sticky="top",
)

power_graph = {
    'data': [
        go.Scatterpolar(
            r=normalized_power,
            theta=np.random.randint(0, 180, df.shape[0]),
            mode='markers',
            marker={'color': 'peru'}
        )
    ],
    'layout': go.Layout(
        showlegend=False,
        radialaxis={'range': [0, 180]},
        direction='counterclockwise',
        title='Location'
    )
}

packets_hour = html.Div([
    dcc.Graph(
        id='packetshour',
        figure={
            'data': [{
                'x': list(range(9, 19)),
                'y': dfheatmap.loc['09:00:00':'18:59:59'].values.flatten(),
                'type': 'bar',
            }],
            'layout': {
                'showline': True,
                'title': "Mobile usage per hour"
            }
        },
    ),
])

manufacturers = html.Div([
    dcc.Graph(
        id='manufacturers',
        figure={
            'data': [{
                'x': df['stationMacVendor'].unique(),
                'y': df['stationMacVendor'].value_counts(normalize=True),
                'type': 'bar',
            }],
            'layout': {
                'showline': True,
                'title': "List of manufacturers"
            }
        },
    ),
])



dftable = df

table_columns = [
    {'name': '#', 'id': 'inc', 'hideable': False},
    {'name': 'Date', 'id': 'date', 'hideable': False},
    {'name': 'Time', 'id': 'time', 'hideable': False},
    {'name': 'ID', 'id': 'stationMac', 'hideable': False},
    {'name': 'Manufacturer', 'id': 'stationMacVendor', 'hideable': False},
    {'name': 'Wifi', 'id': 'essids', 'hideable': False},
    {'name': 'Signal', 'id': 'power', 'hideable': False},
    {'name': 'Traffic', 'id': 'packets', 'hideable': False},
    # {'name': 'id2', 'id': 'id', 'hideable': True},
    # {'name': 'tick', 'id': 'tick', 'hideable': True},
    # {'name': 'packetsTotal', 'id': 'packetsTotal', 'hideable': True},
    # {'name': 'packetsAvg', 'id': 'packetsAvg', 'hideable': True},
    # {'name': 'timeSeen', 'id': 'timeSeen', 'hideable': True},
    # {'name': 'timeSeenTotal', 'id': 'timeSeenTotal', 'hideable': True},
    # {'name': 'bssidVendor', 'id': 'bssidVendor', 'hideable': True},
    # {'name': 'powerAvg', 'id': 'powerAvg', 'hideable': True},
    # {'name': 'bssid', 'id': 'bssid', 'hideable': True},
]

scanstable = dash_table.DataTable(
    id='table-scans',
    data=dftable.to_dict('records'),
    columns=table_columns,
    editable=False,
    sort_action="native",
    row_deletable=False,
    selected_rows=[],
    page_action='none',
    fixed_rows={'headers': True, 'data': 0},
    style_table={
        'overflowX': 'scroll',
    },
    style_cell={
        'whiteSpace': 'normal',
        #'overflowX': 'scroll',
        #'textOverflow': 'ellipsis',
        'minWidth': '100px',
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
    },
    style_data_conditional=[
        {'if': {'column_id': 'inc'}, 'textAlign': 'center'},
        {'if': {'column_id': 'date'}, 'textAlign': 'center'},
        {'if': {'column_id': 'time'}, 'textAlign': 'center'},
    ],
    virtualization=True,
    style_as_list_view=True,
    style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'fontWeight': 'bold',
        'textAlign': 'center',
        'color': 'white'
    },
    #row_selectable='multi',
    #sort_mode='multi',
    #page_action='native', # 'none'
    #page_current= 0,
    #page_size= 10,
    #hidden_columns=['id'],
)


body = dbc.Container(
    [
        html.Br(),
        dbc.Row([dbc.Col(scanstable, md=12)]),
        html.Br(),
        dbc.Row([dbc.Col(manufacturers,  md=12)]),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(html.Div(children=[
                    dcc.Graph(id='packets-graph', config=config_toolbar),
                    ], style={'width': '100%'})
                ),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(html.Div(children=[
                    dcc.Graph(figure=power_graph, id='power-graph', config=config_toolbar),
                    ])
                ),
            ],
        ),
        html.Br(),
        dbc.Row([dbc.Col(packets_hour,  md=12)]),
    ],
    className="mt-6",
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([navbar, body])


####################
# Callbacks
###################
@app.callback(
    [
        Output(component_id='packets-graph', component_property='figure')
    ], [
        Input('my-date-picker-single', 'date'),
        Input('table-scans', 'selected_row_ids'),
        Input('table-scans', 'active_cell'),
    ]
)
def update_graph(selecteddate_start_str, selected_row_ids, active_cell):

    active_row_id = active_cell['row_id'] if active_cell else None
    if active_row_id:
        df = dftable[dftable['id'] == active_row_id]
    else:
        df = dftable[dftable['id'] == 1]

    if selecteddate_start_str:
        selecteddate_start_dt = datetime.strptime(selecteddate_start_str.split(' ')[0], '%Y-%m-%d')
        selecteddate_end_dt = datetime(selecteddate_start_dt.year, selecteddate_start_dt.month, selecteddate_start_dt.day, 23, 59, 59)
        selecteddate_end_str = selecteddate_end_dt.strftime('%Y-%m-%d')
        df = df[selecteddate_start_str:selecteddate_end_str]

    df.sort_index(ascending=True)

    if df.shape[0] > 0:

        packets_graph = {
            'data': [
                {'x': df.index, 'y': df['packets'], 'type': 'bar', 'name': 'Traffic'},
                {'x': df.index, 'y': df['packetsAvg'], 'name':'Avg. Traffic', 'line': dict(color='firebrick', width=2, dash='dash')},
            ],
            'layout': go.Layout(
                xaxis={'title': 'Dates', 'range': [df.index.min(), df.index.max()]},
                yaxis={'type': 'log', 'title': 'Packets'},
                margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                title='Packets',
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                transition={'duration': 500},
            )
        }

        # output must be a tuple or list
        return packets_graph,


if __name__ == '__main__':
    app.run_server(debug=True)
