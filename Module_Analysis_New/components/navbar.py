# Import necessary libraries
from dash import html
import dash_bootstrap_components as dbc
# from dash import html, dcc
from app import app


# Define the navbar structure
def navbar_input():

    layout = html.Div([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("SUMMARY", href="/page1"),
                            style={'margin-left': '20px', 'verticalAlign': 'top'}),
                dbc.NavItem(dbc.NavLink("F1_DATA", href="/page2"),
                            style={'margin-left': '20px', 'verticalAlign': 'top'}),
                dbc.NavItem(dbc.NavLink("F2_DATA", href="/page3"),
                            style={'margin-left': '20px', 'verticalAlign': 'top'}),
                dbc.NavItem(dbc.NavLink("Analysis", href="/page4"),
                            style={'margin-left': '20px', 'verticalAlign': 'top'}),
                dbc.NavItem(dbc.NavLink("COMPARISON", href="/Comparison"),
                            style={'margin-left': '20px', 'verticalAlign': 'top'}),
                dbc.NavItem(dbc.NavLink("DATA_TABLE", href="/table"),
                            style={'margin-left': '20px', 'verticalAlign': 'top'}),
                # Button in navbar
                dbc.NavItem(
                    dbc.Button('Cache_clear', id='navbar-button', color='primary', className='button')
                ),
                # Output div in navbar
                dbc.NavItem(
                    html.Div(id='navbar-output')
                ),
                html.Img(src=app.get_asset_url('logo.png'), style={'height': '40px', 'margin-left': '50px'})
            ],
            brand="FAULT ANALYSIS APP",
            brand_href="/page1",
            color="dark",
            dark=True,
            brand_style={'fontWeight': 'bold', 'fontSize': '25px'}
        ),
    ])

    return layout
