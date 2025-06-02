# Import required libraries
import pandas as pd
import dash
from dash import html  # Updated import
from dash import dcc    # Updated import
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
# Make sure "spacex_launch_dash.csv" is in the same directory as your script,
# or provide the full path to the CSV file.
try:
    spacex_df = pd.read_csv("spacex_launch_dash.csv")
except FileNotFoundError:
    print("Error: 'spacex_launch_dash.csv' not found. Please ensure the file is in the correct directory.")
    # Create an empty DataFrame with expected columns to prevent further errors during layout creation
    spacex_df = pd.DataFrame({
        'Payload Mass (kg)': [0],
        'Launch Site': ['Default'],
        'class': [0], # Assuming 'class' column is used for success/failure
        'Booster Version Category': ['Default'] # Assuming this column exists for scatter plot color
    })

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    # Wrap Dropdown in a Div for centering
    html.Div([
        dcc.Dropdown(id='site-dropdown',
                     options=[
                         {'label': 'All Sites', 'value': 'ALL'},
                         # Dynamically populate other options from the dataframe
                         *[{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]
                     ],
                     value='ALL', # Default value
                     placeholder="Select a Launch Site",
                     searchable=True,
                     style={'width': '100%', 'padding': '3px', 'font-size': '20px', 'textAlignLast': 'center'} # Dropdown takes full width of its container
                     )
    ], style={'width': '80%', 'margin': '0 auto'}), # Center the Div container

    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'textAlign': 'center'}),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0,
                    max=10000, 
                    step=1000,
                    marks={i: str(i) for i in range(0, 10001, 1000)},
                    value=[min_payload if pd.notna(min_payload) else 0, 
                           max_payload if pd.notna(max_payload) else 10000]
                   ),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        # Filter for successful launches to sum them up per site
        # This assumes 'class' == 1 means success.
        successful_launches_df = filtered_df[filtered_df['class'] == 1]
        fig = px.pie(successful_launches_df, 
                     names='Launch Site', 
                     title='Total Successful Launches by Site')
        return fig
    else:
        # Filter for the selected site
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        # Calculate success (class=1) vs. failed (class=0) for the site
        # Create a DataFrame suitable for px.pie where names are 'Success' and 'Failure'
        status_counts = site_filtered_df['class'].map({1: 'Success', 0: 'Failure'}).value_counts().reset_index()
        status_counts.columns = ['status', 'count'] # Rename columns 
        
        fig = px.pie(status_counts, 
                     values='count', 
                     names='status',
                     title=f'Successful vs. Failed Launches for site {entered_site}')
        return fig

# TASK 4: Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Filter by payload range first
    # Ensure 'Payload Mass (kg)' column exists and is numeric
    if 'Payload Mass (kg)' not in spacex_df.columns:
        # Return an empty figure or a message if the column is missing
        return px.scatter(title='Payload Mass (kg) column missing')

    # Make sure payload_range values are valid numbers before filtering
    if not (isinstance(low, (int, float)) and isinstance(high, (int, float))):
         # If payload_range is not valid, perhaps use the full range or return an empty chart
        current_filtered_df = spacex_df.copy() # Or handle error appropriately
    else:
        current_filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                                        (spacex_df['Payload Mass (kg)'] <= high)]

    if entered_site == 'ALL':
        # Scatter plot for all sites
        fig = px.scatter(current_filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', # Assuming 'class' is 0 or 1 for failure/success
                         color='Booster Version Category', 
                         title='Payload vs. Launch Outcome for All Sites')
        return fig
    else:
        # Further filter for the selected site
        site_filtered_df = current_filtered_df[current_filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(site_filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title=f'Payload vs. Launch Outcome for site {entered_site}')
        return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True) # Changed from app.run_server
