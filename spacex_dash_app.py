# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
sites = spacex_df['Launch Site'].unique()
site_options = [{'label': 'All Sites', 'value': 'ALL'}]
site_options.extend({'label': site, 'value': site} for site in sites)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={
                'textAlign': 'center',
                'color': '#503D36',
                'font-size': 40}
        ),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(
            id='site-dropdown',
            options = site_options,
            placeholder='Select a Launch Site',
            searchable=True
        ),
        html.Br(),

        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id='success-pie-chart')),
        html.Br(),

        html.P("Payload range (Kg):"),
        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            value=[min_payload, max_payload]
        ),

        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ]
)

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
   prevent_initial_call=True
)
def get_pie_chart(site):
    groups = spacex_df[['Launch Site', 'class']].groupby('Launch Site')
    df = groups.sum()
    if site == 'ALL':
        df.reset_index(inplace=True)
        df.columns = ['Launch Site', 'Total Success']
        fig = px.pie(
            df,
            names='Launch Site',
            values='Total Success',
            title='Total Success Launches by Site'
        )
    else:
        success = df.loc[site, 'class']
        failure = groups.count().loc[site, 'class'] - success
        fig = px.pie(
            names=['Success', 'Failure'],
            values=[success, failure],
            color=['blue', 'red'],
            title=f'Total Success Launches for Site {site}'
        )
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(
        component_id='success-payload-scatter-chart',
        component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value'),
    ],
    prevent_initial_call=True
)
def get_scatter(site, payload_range):
    min_mass, max_mass = payload_range
    mass = spacex_df['Payload Mass (kg)']
    df = spacex_df[(mass >= min_mass) & (mass <= max_mass)]
    if site == 'ALL':
        fig = px.scatter(
            df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites'
        )
    else:
        fig = px.scatter(
            df[df['Launch Site'] == site],
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites'
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
