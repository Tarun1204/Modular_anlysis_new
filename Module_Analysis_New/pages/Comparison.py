# Import required libraries
from dash import html, dcc
# from Data_cleaning_SQL import df_raw
from callbacks_new import df_raw

colors = {
    # For black background
    # 'background': 'rgb(50, 50, 50)',
    # 'text':  'white'      # '#7FDBFF'
    'background': 'white',
    'text':  'black'      # '#7FDBFF'

}
layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div([
        html.Div([
            html.H1('Data Comparison', style={'color': colors['text']},
                    className='title'), ], className='logo_title'),
        html.Div([
            html.P('Select Product',
                   style={'color': colors['text']},
                   className='drop_down_list_title'
                   ),
            dcc.Dropdown(id='Product_comparison',
                         # options=[{'label': i, 'value': i}for i in df_raw['PRODUCT_NAME'].unique()],
                         clearable=True,
                         value=None,
                         placeholder='Select a product here',
                         searchable=True,
                         className='drop_down_list'),
        ], className='title_drop_down_list'),
        ], className='title_and_drop_down_list'),
    html.Div([
        # html.H3('Comparison'),
        html.Div([
            html.P('Select Month',
                   style={'color': colors['text']},
                   className='drop_down_month_title'
                   ),
            dcc.Dropdown(id='Month1',
                         # options=[{'label': i, 'value': i}for i in df_raw['MONTH'].unique()] +
                         #         [{'label': 'Select all', 'value': 'all_values'}],
                         # options=[{'label': i, 'value': i} for i in final_month_list] +
                         #         [{'label': 'Select all', 'value': 'all_values'}],
                         clearable=True,
                         value='all_values',
                         # multi=True,
                         placeholder='Select a month here',
                         searchable=True,
                         className='drop_down_month'),
        ], className='month_drop_down_list'),
        html.Div([
            html.P('Select  second Month',
                   style={'color': colors['text']},
                   className='drop_down_month_title'
                   ),
            dcc.Dropdown(id='Month2',
                         # options=[{'label': i, 'value': i}for i in df_raw['MONTH'].unique()],
                         # options=[{'label': i, 'value': i} for i in final_month_list],
                         clearable=True,
                         value=None,
                         placeholder='Select a  second month here',
                         searchable=True,
                         className='drop_down_month'),
        ], className='month_drop_down_list'),
    ], className='title_and_drop_down_list'),

    # dcc.Dropdown(id='List of Faults',
    #              value=None,
    #              placeholder='Select a Fault here',
    #              searchable=True),
    html.Br(),
    html.Br(),
    html.Div(id='comparison'),
    html.Br(),
    html.Div([dcc.Graph(id='bar_comparison')]),
    # html.Div([
    #     html.Div(id='comparison', style={'width': '40%'}),
    #     html.Div([dcc.Graph(id='bar_comparison')], style={'width': '60%'})
    #                              ], style={'display': 'flex'}),

])
