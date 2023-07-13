# Import required libraries
from dash import html, dcc
# from Data_cleaning_SQL import df_raw
from callbacks_new import df_raw


filtered_df = df_raw.loc[df_raw['STAGE'] == 'ATE']

colors = {
    # For black background
    # 'background': 'rgb(50, 50, 50)',
    # 'text':  'white'      # '#7FDBFF'
    'background': 'white',
    'text':  'black'      # '#7FDBFF'
}
# Create an app layout instead of app.layout we are using layout for multiple pages
layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div([html.Div([
        # html.Img(src = app.get_asset_url('logo.png'),style = {'height': '50px'},className = 'title_image'),
              html.H1('Data Analysis', style={'color': colors['text']},
                      className='title'), ], className='logo_title'),
              html.Div([
                  html.P('Select Product',
                         style={'color': colors['text']},
                         className='drop_down_list_title'),
                  dcc.Dropdown(id='Products',
                               # options=[{'label': i, 'value': i}
                               #          for i in df_card['PRODUCT'].unique()],
                               # for i in df_raw['PRODUCT_NAME'].unique()],
                               # need to change the reference from raw to card total
                               clearable=True,
                               value=None,
                               placeholder='Select a product here',
                               searchable=True,
                               className='drop_down_list'),
              ], className='title_drop_down_list'),
              html.Div([
                  html.P('Select Month',
                         style={'color': colors['text']},
                         className='drop_down_month_title'),
                  dcc.Dropdown(id='Month',
                               # options=[{'label': i, 'value': i}for i in df_raw['MONTH'].unique()],
                               # options=[{'label': i, 'value': i} for i in final_month_list],
                               #  need to check the reference of raw and total
                               clearable=True,
                               value=None,
                               multi=True,
                               placeholder='Select a month here',
                               searchable=True,
                               className='drop_down_month'),
              ], className='month_drop_down_list'),
              html.Div([
                  html.P('Select Part no.',
                         style={'color': colors['text']},
                         className='drop_down_list_title'),
                  dcc.Dropdown(id='Part_no',
                               # options=[{'label': i, 'value': i}for i in df_raw['PART_CODE'].unique()],
                               clearable=False,
                               value='all_values',
                               placeholder='Select a part no here',
                               searchable=True,
                               className='drop_down_list'),
              ], className='title_drop_down_list'), ], className='title_and_drop_down_list'),
    html.Div([
        html.Div([html.H6(children='Tested',
                          style={'textAlign': 'center', 'color': 'white', 'fontSize': 20}),
                  html.P(id='tested_value',
                         style={
                             'textAlign': 'center', 'color': 'orange', 'fontSize': 40,
                             'margin-top': '-18px'})], className="card_container two columns",),
        html.Div([
            html.H6(children='Pass',
                    style={
                        'textAlign': 'center',
                        'color': 'white', 'fontSize': 20}
                    ),

            html.P(id='pass_value',
                   style={
                       'textAlign': 'center',
                       'color': 'lime', 'margin-top': '-18px',
                       'fontSize': 40}
                   )], className="card_container two columns",),
        html.Div([
            html.H6(children='Fail',
                    style={
                        'textAlign': 'center',
                        'color': 'white', 'fontSize': 20}
                    ),

            html.P(id='fail_value',
                   style={
                       'textAlign': 'center',
                       'color': 'red', 'margin-top': '-18px',
                       'fontSize': 40}
                   )], className="card_container two columns",),
        html.Div([
            html.H6(children='FTY',
                    style={
                        'textAlign': 'center',
                        'color': 'white', 'fontSize': 20}
                    ),

            html.P(id='fty_value',
                   # style={
                   #     'textAlign': 'center', 'margin-top': '-18px', 'fontSize': 40,
                   #     'color': 'lime' if 'fty_value' > '98' else 'red'},
                   )], className="card_container two columns",),
        html.Div([
            html.H6(children='DPT',
                    style={
                        'textAlign': 'center',
                        'color': 'white', 'fontSize': 20}
                    ),

            html.P(id='dpt_value',
                   style={
                       'textAlign': 'center',
                       'color': 'aqua', 'margin-top': '-18px',
                       'fontSize': 40}
                   )], className="card_container two columns")

    ], className="row flex-display"),
    html.Br(),
    html.Div([
        html.Div(id='summary_table', style={'width': '50%'}),  # , className="create_container six columns"
        # html.Br(),
        html.Div([dcc.Graph(id='Sunburst')], style={'width': '50%'}, className='plotOptions'),  # className="create_container five columns"
    ], style={'display': 'flex'}),  # className="row flex-display"
    # html.Div([dcc.Graph(id='Faults')]),
    # html.Br(),

    html.Div([
        html.Div([dcc.Graph(id='Pie_chart')], style={'width': '50%'}),
        html.Br(),
        html.Div([dcc.Graph(id='Bar')], style={'width': '50%'})
                                 ], style={'display': 'flex'}),
    html.Br(),

    html.Div([
            html.Div([dcc.Graph(id='Category_bar')])
                                     ]),
    html.Br(),
    # html.Div(id='output-div')
                                ])
