# Importing necessary modules for building the dashboard, data manipulation, and plotting
from dash import html, dcc  # Dash components for creating web apps
import pandas as pd  # For data manipulation
import plotly.express as px  # For creating Plotly visualizations
import plotly.graph_objects as go  # For creating advanced Plotly visualizations
from plotly.subplots import make_subplots  # For creating subplots

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

# Mapping health bins for mental and physical health ratings
def map_health_to_bins(value):
    return (value // 3) + 1  # Converts continuous days into grouped ratings

df['MappedMentalHealth'] = df['MentalHealthDays'].apply(map_health_to_bins)  # Apply binning for mental health
df['MappedPhysicalHealth'] = df['PhysicalHealthDays'].apply(map_health_to_bins)  # Apply binning for physical health
df['Obese'] = df['BMI'] >= 30  # Define obesity based on BMI threshold (BMI >= 30)

# Subplots: Obesity-related trends over time
grouped_time = df.groupby('Year').agg({
    'BMI': 'mean',  # Calculate average BMI
    'MappedMentalHealth': 'mean',  # Calculate average mental health rating
    'PhysicalActivities': lambda x: (x == 'Yes').mean() * 100,  # Calculate percentage of physically active individuals
    'HadDiabetes': lambda x: (x == 'Yes').mean() * 100  # Calculate percentage of diabetics
}).reset_index()

fig1 = make_subplots(  # Create a 2x2 subplot layout
    rows=2, cols=2,
    subplot_titles=(
        "Average BMI",
        "Average Mental Health Rating",
        "Percentage of Physically Active",
        "Percentage of Diabetics"
    )
)

# Adding traces for each subplot
fig1.add_trace(
    go.Scatter(x=grouped_time['Year'], y=grouped_time['BMI'], mode='lines+markers', name='BMI', line=dict(color="#29259e")),
    row=1, col=1
)
fig1.add_trace(
    go.Scatter(x=grouped_time['Year'], y=grouped_time['MappedMentalHealth'], mode='lines+markers', name='Mental Health', line=dict(color='#8e259e')),
    row=1, col=2
)
fig1.add_trace(
    go.Scatter(x=grouped_time['Year'], y=grouped_time['PhysicalActivities'], mode='lines+markers', name='Physically Active', line=dict(color='#9e257e')),
    row=2, col=1
)
fig1.add_trace(
    go.Scatter(x=grouped_time['Year'], y=grouped_time['HadDiabetes'], mode='lines+markers', name='Diabetics', line=dict(color='#49259e')),
    row=2, col=2
)
fig1.update_layout(title="Obesity-Related Trends Over Time", height=700, width=700)

# Horizontal bar chart: Obesity percentage by race/ethnicity
race_grouped = df.groupby('RaceEthnicityCategory').agg({
    'Obese': lambda x: x.mean() * 100  # Calculate obesity percentage
}).reset_index()

fig2 = px.bar(
    race_grouped,
    x='Obese',
    y='RaceEthnicityCategory',
    orientation='h',  # Horizontal bar chart
    title='Percentage of Obesity by Race/Ethnicity',
    labels={'RaceEthnicityCategory': 'Race/Ethnicity', 'Obese': 'Percentage (%)'},
    color='Obese',
    color_continuous_scale=pastel_purple_palette
)

# Vertical bar chart: Percentage of obese individuals
obesity_percentage = df['Obese'].mean() * 100  # Calculate overall obesity percentage
obesity_data = pd.DataFrame({
    'Category': ['Obese', 'Not Obese'],
    'Percentage': [obesity_percentage, 100 - obesity_percentage]  # Calculate percentages for obese vs. not obese
})
fig3 = px.bar(
    obesity_data,
    x='Category',
    y='Percentage',
    title='Percentage of Obese Individuals',
    labels={'Category': 'Category', 'Percentage': 'Percentage (%)'},
    color='Category',
    color_discrete_sequence=[pastel_purple_palette[1], pastel_purple_palette[6]]
)

# Donut chart: Gender distribution among obese individuals
gender_distribution_obese = (
    df[df['Obese']].groupby('Sex').size() / df[df['Obese']].shape[0] * 100  # Calculate gender distribution percentages
)
fig4 = go.Figure(data=[go.Pie(
    labels=gender_distribution_obese.index,
    values=gender_distribution_obese.values,
    textinfo='label+percent',  # Display labels and percentages
    hole=0.4,  # Create a donut chart
    marker=dict(colors=[pastel_purple_palette[2], pastel_purple_palette[5]])  # Use palette colors
)])
fig4.update_layout(title='Gender Distribution Among Obese Individuals')

# Dashboard 4 Layout
layout = html.Div([
    html.H1("Obesity and Health Dashboard", style={'textAlign': 'center'}),  # Add main heading

    # Top row: Obesity trends and obesity by race/ethnicity
    html.Div([
        html.Div([
            html.H2("Obesity-Related Trends Over Time"),  # Add heading for the trends plot
            dcc.Graph(figure=fig1)  # Display the subplot figure
        ], style={'flex': '1', 'margin': '10px'}),  # Define layout for the trends plot
        
        html.Div([
            html.H2("Obesity by Race/Ethnicity"),  # Add heading for the bar chart
            dcc.Graph(figure=fig2)  # Display the horizontal bar chart
        ], style={'flex': '1', 'margin': '10px'})  # Define layout for the bar chart
    ], style={'display': 'flex', 'justify-content': 'space-between'}),  # Set up a row with flexbox

    # Bottom row: Obesity percentage and gender distribution
    html.Div([
        html.Div([
            html.H2("Percentage of Obese Individuals"),  # Add heading for the vertical bar chart
            dcc.Graph(figure=fig3)  # Display the vertical bar chart
        ], style={'flex': '1', 'margin': '10px'}),  # Define layout for the vertical bar chart
        
        html.Div([
            html.H2("Gender Distribution Among Obese Individuals"),  # Add heading for the donut chart
            dcc.Graph(figure=fig4)  # Display the donut chart
        ], style={'flex': '1', 'margin': '10px'})  # Define layout for the donut chart
    ], style={'display': 'flex', 'justify-content': 'space-between'}),  # Set up another row with flexbox
])
