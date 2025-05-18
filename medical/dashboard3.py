# Importing necessary modules for building the dashboard, data manipulation, and plotting
from dash import html, dcc  # Dash components for creating web apps
import pandas as pd  # For data manipulation
import plotly.express as px  # For creating Plotly visualizations
import plotly.graph_objects as go  # For creating advanced Plotly visualizations

# Loading the dataset into a Pandas DataFrame
df = pd.read_csv(r"medical.csv")

# Defining a pastel purple color palette for visualizations
pastel_purple_palette = [
    "#D9C4F2", "#C6A8EB", "#B28EE4", "#9D73DC",
    "#8958D4", "#7342C7", "#5F32B2", "#49259E"
]

# Mapping state names to abbreviations
state_abbreviation_mapping = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL',
    'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
    'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
    'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR',
    'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
    'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}
df['StateAbbr'] = df['State'].map(state_abbreviation_mapping)

# Defining a function to group health days into bins
def map_health_to_bins(value):
    return (value // 3) + 1  # Converts continuous days into grouped ratings

# Applying the binning function to mental and physical health days
df['MappedMentalHealth'] = df['MentalHealthDays'].apply(map_health_to_bins)
df['MappedPhysicalHealth'] = df['PhysicalHealthDays'].apply(map_health_to_bins)

# Graph 1: Creating a choropleth map for COVID cases by state
covid_hits_state = df[df['CovidPos'] == 'Yes'].groupby('StateAbbr').size().reset_index(name='COVIDCount')  # Count COVID cases per state
total_covid_cases = covid_hits_state['COVIDCount'].sum()  # Calculate total COVID cases
covid_hits_state['Percentage'] = (covid_hits_state['COVIDCount'] / total_covid_cases) * 100  # Calculate percentage of cases per state
fig1 = px.choropleth(  # Create a choropleth map
    covid_hits_state,
    locations='StateAbbr',
    locationmode="USA-states",
    color='Percentage',
    hover_name='StateAbbr',
    color_continuous_scale=pastel_purple_palette,
    scope="usa",
    labels={'Percentage': 'Percentage of COVID Cases'}
)
fig1.update_layout(  # Customize layout
    title_text='Distribution of COVID Cases by State (Percentage)',
    geo=dict(showframe=False, showcoastlines=False)
)

# Graph 2: Creating a time series for COVID cases and mental health ratings
df['YearMonth'] = pd.to_datetime(df[['Year', 'Month']].assign(Day=1))  # Combine Year and Month into a datetime column
covid_time_series = (
    df[(df['CovidPos'] == 'Yes') & (df['Year'] == 2020)]
    .groupby(df['YearMonth'])['CovidPos']
    .count()
    .reset_index(name='CovidCount')
)  # Count monthly COVID cases in 2020
mapped_mental_health = (
    df[(df['Year'] == 2020)]
    .groupby(df['YearMonth'])['MappedMentalHealth']
    .mean()
    .reset_index(name='AvgMappedMentalHealth')
)  # Calculate average mental health rating by month in 2020
time_series = pd.merge(covid_time_series, mapped_mental_health, on='YearMonth', how='outer').fillna(0)  # Merge dataframes
fig2 = go.Figure()  # Create a new figure
fig2.add_trace(go.Scatter(  # Add line for COVID cases
    x=time_series['YearMonth'],
    y=time_series['CovidCount'],
    mode='lines+markers',
    name='COVID-19 Cases',
    line=dict(color=pastel_purple_palette[5])
))
fig2.add_trace(go.Scatter(  # Add line for mental health ratings
    x=time_series['YearMonth'],
    y=time_series['AvgMappedMentalHealth'],
    mode='lines+markers',
    name='Mental Health Score',
    line=dict(color='black'),
    yaxis="y2"
))
fig2.update_layout(  # Customize layout
    title='COVID-19 Cases and Mental Health Rating',
    xaxis=dict(title='Month (2020)', tickformat='%b', tickangle=45),
    yaxis=dict(title='COVID-19 Cases', titlefont=dict(color=pastel_purple_palette[5])),
    yaxis2=dict(
        title='Mental Health Rating',
        titlefont=dict(color=pastel_purple_palette[3]),
        overlaying='y',
        side='right'
    ),
    legend=dict(x=0.1, y=1.1, orientation="h"),
    template="plotly_white"
)

# Graph 3: Creating a bar chart for depressive disorder cases
df_depressive_disorder_yes = df[(df['HadDepressiveDisorder'] == 'Yes') & (df['Year'].isin([2019, 2020, 2021]))]  # Filter depressive disorder cases
df_depressive_disorder_yes_grouped = (
    df_depressive_disorder_yes.groupby('Year')['HadDepressiveDisorder']
    .count()
    .reset_index(name='Count')
)  # Count cases by year
df_depressive_disorder_yes_grouped['Percentage'] = (
    df_depressive_disorder_yes_grouped['Count'] / df_depressive_disorder_yes_grouped['Count'].sum() * 100
)  # Calculate percentage of cases by year
fig3 = px.bar(  # Create a horizontal bar chart
    df_depressive_disorder_yes_grouped,
    x='Percentage',
    y='Year',
    orientation='h',
    title='Percentage of Depressive Disorder Cases in 2019, 2020, and 2021',
    labels={'Percentage': 'Percentage (%)', 'Year': 'Year'},
    color='Percentage',
    color_continuous_scale=pastel_purple_palette
)

# Graph 4: Creating a bar chart for COVID distribution by age
covid_age_data = df[df['CovidPos'] == 'Yes'].groupby('AgeCategory').size().reset_index(name='COVIDCount')  # Count cases by age category
fig4 = px.bar(  # Create a bar chart
    covid_age_data,
    x='AgeCategory',
    y='COVIDCount',
    title='COVID Distribution by Age',
    labels={'AgeCategory': 'Age Category', 'COVIDCount': 'Number of COVID Cases'},
    color='COVIDCount',
    color_continuous_scale=pastel_purple_palette
)
fig4.update_layout(  # Customize layout
    xaxis=dict(tickangle=45),
    title_font_size=16,
    xaxis_title_font_size=14,
    yaxis_title_font_size=14
)

# Creating the Dash app layout
layout = html.Div([
    html.H1("COVID-19 Dashboard", style={'textAlign': 'center'}),  # Add main heading

    # Top row: Map and time series
    html.Div([
        html.Div([
            html.H2("COVID Cases by State"),  # Add heading for the map
            dcc.Graph(figure=fig1)  # Display the choropleth map
        ], style={'flex': '1', 'margin': '10px'}),  # Define layout for the map
        
        html.Div([
            html.H2("COVID Cases vs Mental Health"),  # Add heading for the time series
            dcc.Graph(figure=fig2)  # Display the time series chart
        ], style={'flex': '1', 'margin': '10px'})  # Define layout for the time series
    ], style={'display': 'flex', 'justify-content': 'space-between'}),  # Set up a row with flexbox

    # Bottom row: Bar charts
    html.Div([
        html.Div([
            html.H2("Depressive Disorder Cases (2019-2021)"),  # Add heading for the bar chart
            dcc.Graph(figure=fig3)  # Display the bar chart
        ], style={'flex': '1', 'margin': '10px'}),  # Define layout for the bar chart
        
        html.Div([
            html.H2("COVID Distribution by Age"),  # Add heading for the age distribution
            dcc.Graph(figure=fig4)  # Display the age distribution chart
        ], style={'flex': '1', 'margin': '10px'})  # Define layout for the age distribution
    ], style={'display': 'flex', 'justify-content': 'space-between'}),  # Set up another row with flexbox
])
