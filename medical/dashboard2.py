# Importing necessary modules for building the dashboard, data manipulation, and plotting
from dash import html, dcc  # Dash components for creating web apps
import pandas as pd  # For data manipulation
import plotly.express as px  # For creating Plotly visualizations
import matplotlib.pyplot as plt  # For creating matplotlib visualizations
import seaborn as sns  # For enhanced data visualization with matplotlib
import io  # For in-memory binary streams
import base64  # For encoding images in base64 format

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

# Helper function to convert matplotlib plots into base64-encoded images
def save_plot_to_base64(fig):
    buf = io.BytesIO()  # Create an in-memory byte stream
    fig.savefig(buf, format="png")  # Save the figure as a PNG into the stream
    buf.seek(0)  # Move the stream position to the beginning
    return base64.b64encode(buf.read()).decode("utf-8")  # Encode as base64 and decode to string

# Graph 1: Creating a choropleth map of population count by state
state_counts = df['StateAbbr'].value_counts().reset_index()  # Count the number of people per state
state_counts.columns = ['StateAbbr', 'PopulationCount']  # Rename columns for clarity
fig1 = px.choropleth(  # Create a choropleth map with Plotly
    state_counts,
    locations='StateAbbr',
    locationmode="USA-states",
    color='PopulationCount',
    hover_name='StateAbbr',
    color_continuous_scale=pastel_purple_palette,
    scope="usa",
    labels={'PopulationCount': 'Number of People'}
)
fig1.update_layout(title_text='Number of People by State')  # Add title to the plot

# Graph 2: Creating a pie chart for race distribution
race_counts = df['RaceEthnicityCategory'].value_counts()  # Count occurrences of each race/ethnicity
plt.figure(figsize=(8, 8))  # Set figure size
plt.pie(
    race_counts,
    labels=race_counts.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=pastel_purple_palette[:len(race_counts)]  # Use palette colors
)
plt.title('Race Distribution')  # Add title to the pie chart
plt.axis('equal')  # Ensure the pie chart is circular
race_chart_base64 = save_plot_to_base64(plt)  # Save the plot as a base64-encoded string

# Graph 3: Creating a bar chart for age distribution
age_counts = df['AgeCategory'].value_counts().reset_index()  # Count occurrences of each age category
age_counts.columns = ['AgeCategory', 'Count']  # Rename columns for clarity
plt.figure(figsize=(8, 6))  # Set figure size
sns.set(style="whitegrid")  # Set seaborn style
sns.barplot(x='AgeCategory', y='Count', data=age_counts, palette=pastel_purple_palette[:len(age_counts)])  # Create bar chart
plt.xlabel('Age Category')  # Add x-axis label
plt.ylabel('Count')  # Add y-axis label
plt.title('Age Distribution by Category')  # Add title
plt.xticks(rotation=45)  # Rotate x-axis labels for readability
age_chart_base64 = save_plot_to_base64(plt)  # Save the plot as a base64-encoded string

# Graph 4: Creating a donut chart for gender distribution
gender_counts = df['Sex'].value_counts()  # Count occurrences of each gender
plt.figure(figsize=(8, 8))  # Set figure size
plt.pie(
    gender_counts,
    labels=gender_counts.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=[pastel_purple_palette[2], pastel_purple_palette[5]],  # Use specific colors from the palette
    wedgeprops={'width': 0.4}  # Create a donut chart by reducing the width of wedges
)
plt.title('Gender Distribution')  # Add title to the chart
plt.axis('equal')  # Ensure the chart is circular
gender_chart_base64 = save_plot_to_base64(plt)  # Save the plot as a base64-encoded string

# Creating the Dash app layout
layout = html.Div([
    html.H1("Demographics Dashboard", style={'textAlign': 'center'}),  # Add main heading

    html.Div([
        # Top row: Choropleth map and race distribution pie chart
        html.Div([
            html.Div([
                html.H2("Number of People by State"),  # Add heading for the map
                dcc.Graph(figure=fig1)  # Display the Plotly choropleth map
            ], style={'flex': '1', 'margin': '10px'}),  # Define flexbox layout for the map
            
            html.Div([
                html.H2("Race Distribution"),  # Add heading for the pie chart
                html.Img(src=f"data:image/png;base64,{race_chart_base64}", style={'width': '100%'})  # Display pie chart image
            ], style={'flex': '1', 'margin': '10px'})  # Define flexbox layout for the pie chart
        ], style={'display': 'flex', 'justify-content': 'space-between'}),  # Set up a row with flexbox

        # Bottom row: Age distribution bar chart and gender distribution donut chart
        html.Div([
            html.Div([
                html.H2("Age Distribution by Category"),  # Add heading for the bar chart
                html.Img(src=f"data:image/png;base64,{age_chart_base64}", style={'width': '100%'})  # Display bar chart image
            ], style={'flex': '1', 'margin': '10px'}),  # Define flexbox layout for the bar chart
            
            html.Div([
                html.H2("Gender Distribution"),  # Add heading for the donut chart
                html.Img(src=f"data:image/png;base64,{gender_chart_base64}", style={'width': '100%'})  # Display donut chart image
            ], style={'flex': '1', 'margin': '10px'})  # Define flexbox layout for the donut chart
        ], style={'display': 'flex', 'justify-content': 'space-between'})  # Set up another row with flexbox
    ], style={'padding': '20px'}),  # Add padding around the grid layout
])
