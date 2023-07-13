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
    html.Div([
        html.Div([
              html.H1('Module Level Analysis', style={'color': colors['text']},
                      className='title'), ], className='logo_title'),
        html.Div([
            html.P('Select Product',
                   style={'color': colors['text']},
                   className='drop_down_list_title'
                   ),
            dcc.Dropdown(id='Product_f2',
                         # options=[{'label': i, 'value': i}for i in filtered_df['PRODUCT_NAME'].unique()],
                         clearable=True,
                         value=None,
                         placeholder='Select a product here',
                         searchable=True,
                         className='drop_down_list'),
        ], className='title_drop_down_list'),
        html.Div([
            html.P('Select Month',
                   style={'color': colors['text']},
                   className='drop_down_month_title'
                   ),
            dcc.Dropdown(id='Month_f2',
                         # options=[{'label': i, 'value': i}for i in df_raw['MONTH'].unique()],
                         # options=[{'label': i, 'value': i} for i in final_month_list],
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
                  dcc.Dropdown(id='Part_no_f2',
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
                  html.P(id='tested_value_f2',
                         style={
                             'textAlign': 'center', 'color': 'orange', 'fontSize': 40,
                             'margin-top': '-18px'})], className="card_container two columns",),
        html.Div([
            html.H6(children='Pass',
                    style={
                        'textAlign': 'center',
                        'color': 'white', 'fontSize': 20}
                    ),
            html.P(id='pass_value_f2',
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
            html.P(id='fail_value_f2',  # f"{covid_data_1['recovered'].iloc[-1]:,.0f}"
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
            html.P(id='fty_value_f2',  # f"{covid_data_1['active'].iloc[-1]:,.0f}"
                   style={
                       'textAlign': 'center',
                       'color': '#e55467', 'margin-top': '-18px',
                       'fontSize': 40}
                   )], className="card_container two columns",),
        html.Div([
            html.H6(children='DPT',
                    style={
                        'textAlign': 'center',
                        'color': 'white', 'fontSize': 20}
                    ),
            html.P(id='dpt_value_f2',  # f"{covid_data_1['active'].iloc[-1]:,.0f}"
                   style={
                       'textAlign': 'center',
                       'color': 'aqua', 'margin-top': '-18px',
                       'fontSize': 40}
                   )], className="card_container two columns")
    ], className="row flex-display"),
    html.Div([
        html.Div([html.P('Select Stage:', className='fix_label',  style={'color': 'white'}),
                  dcc.Dropdown(id='stages',
                                  multi=False,
                                  clearable=True,
                                  placeholder='Select Stage',
                                  className='drop_down_stage1'),
                  dcc.Graph(id='Tested', config={'displayModeBar': False}, className='dcc_compon',
                            style={'margin-top': '20px'},
                            ),

                  dcc.Graph(id='Pass1', config={'displayModeBar': False}, className='dcc_compon',
                            style={'margin-top': '20px'},
                            ),

                  dcc.Graph(id='Fail', config={'displayModeBar': False}, className='dcc_compon',
                            style={'margin-top': '20px'},
                            ),

                  dcc.Graph(id='%Fail', config={'displayModeBar': False}, className='dcc_compon',
                            style={'margin-top': '20px'},
                            ),
                  dcc.Graph(id='DPT', config={'displayModeBar': False}, className='dcc_compon',
                            style={'margin-top': '20px'},
                            ),
                  ], className="create_container one-half columns", id="cross-filter-options"),
        html.Div([
                      dcc.Graph(id='pie_chart1',
                                config={'displayModeBar': 'hover'}),
                              ], className="create_container four columns"),
        html.Div([
            dcc.Graph(id="Bar1")
                    ], className="create_container five-half columns"),
        ], className="row flex-display"),
                                ])
