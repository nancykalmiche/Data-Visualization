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

# Defining a pastel color palette to be used in visualizations
pastel_palette = [
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

# Mapping general health categories to numeric values for easier processing
general_health_mapping = {'Poor': 0, 'Fair': 1, 'Good': 2, 'Very Good': 3, 'Excellent': 4}
df['GeneralHealthNumeric'] = df['GeneralHealth'].map(general_health_mapping)

# Defining a function to group health days into bins
def map_health_to_bins(value):
    return (value // 3) + 1  # Example: Converts continuous days to grouped ratings

# Applying the mapping function to mental and physical health days
df['MappedMentalHealth'] = df['MentalHealthDays'].apply(map_health_to_bins)
df['MappedPhysicalHealth'] = df['PhysicalHealthDays'].apply(map_health_to_bins)

# Helper function to convert matplotlib plots into base64-encoded images
def save_plot_to_base64(fig):
    buf = io.BytesIO()  # Create an in-memory byte stream
    fig.savefig(buf, format="png")  # Save the figure as a PNG into the stream
    buf.seek(0)  # Move the stream position to the beginning
    return base64.b64encode(buf.read()).decode("utf-8")  # Encode as base64 and decode to string

# Graph 1: Creating a choropleth map of average general health by state
state_health_mean = df.groupby('StateAbbr')['GeneralHealthNumeric'].mean().reset_index()  # Compute state-wise mean health
fig1 = px.choropleth(  # Create a choropleth map with Plotly
    state_health_mean,
    locations='StateAbbr',
    locationmode="USA-states",
    color='GeneralHealthNumeric',
    color_continuous_scale=pastel_palette,
    scope="usa",
    labels={'GeneralHealthNumeric': 'Avg General Health Score'}
)
fig1.update_layout(title_text='Avg General Health Score by State')  # Add title to the plot

# Graph 2: Creating a pie chart for general health distribution
general_health_distribution = df['GeneralHealth'].value_counts()  # Count occurrences of health ratings
plt.figure(figsize=(8, 8))  # Set figure size
plt.pie(
    general_health_distribution,
    labels=general_health_distribution.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=pastel_palette[:len(general_health_distribution)]  # Use palette colors
)
plt.title("Distribution of General Health Ratings")  # Add title to the pie chart
graph2_base64 = save_plot_to_base64(plt)  # Save the plot as a base64-encoded string

# Graph 3: Creating a bar chart for mental health distribution
mental_health_dist = df['MappedMentalHealth'].value_counts(normalize=True).sort_values(ascending=False) * 100  # Calculate percentages
plt.figure(figsize=(10, 6))  # Set figure size
plt.bar(
    mental_health_dist.index,
    mental_health_dist.values,
    color=pastel_palette[:len(mental_health_dist)]  # Use palette colors
)
plt.title('Percentage Distribution of Mental Health Ratings')  # Add title
plt.xlabel('Mental Health Rating')  # Add x-axis label
plt.ylabel('Percentage (%)')  # Add y-axis label
graph3_base64 = save_plot_to_base64(plt)  # Save the plot as a base64-encoded string

# Graph 4: Creating a scatter plot for mental vs. physical health
df_agg = df.groupby('MappedMentalHealth')['MappedPhysicalHealth'].mean().reset_index()  # Aggregate data by mental health ratings
plt.figure(figsize=(10, 6))  # Set figure size
sns.regplot(
    x='MappedMentalHealth',
    y='MappedPhysicalHealth',
    data=df_agg,
    scatter_kws={'color': pastel_palette[5]},  # Color for scatter points
    line_kws={'color': pastel_palette[-1]}  # Color for regression line
)
plt.title('Relationship Between Mental and Physical Health Ratings')  # Add title
plt.xlabel('Mental Health Rating')  # Add x-axis label
plt.ylabel('Physical Health Rating')  # Add y-axis label
graph4_base64 = save_plot_to_base64(plt)  # Save the plot as a base64-encoded string

# Creating the Dash app layout
layout = html.Div([
    html.H1("General Health Dashboard", style={'textAlign': 'center'}),  # Main heading centered

    # Grid layout for the plots
    html.Div([
        # Top-left: Choropleth Map
        html.Div([
            html.H2("Avg General Health by State"),
            dcc.Graph(figure=fig1)  # Display the Plotly choropleth map
        ], style={'grid-area': 'map', 'padding': '10px'}),  # Assign to grid area 'map'

        # Top-right: Pie Chart
        html.Div([
            html.H2("Distribution of General Health Ratings"),
            html.Img(src=f"data:image/png;base64,{graph2_base64}", style={'width': '100%'})  # Display pie chart image
        ], style={'grid-area': 'pie', 'padding': '10px'}),  # Assign to grid area 'pie'

        # Bottom-left: Bar Chart
        html.Div([
            html.H2("Percentage Distribution of Mental Health Data"),
            html.Img(src=f"data:image/png;base64,{graph3_base64}", style={'width': '100%'})  # Display bar chart image
        ], style={'grid-area': 'bar', 'padding': '10px'}),  # Assign to grid area 'bar'

        # Bottom-right: Scatter Plot
        html.Div([
            html.H2("Relationship Between Mental and Physical Health"),
            html.Img(src=f"data:image/png;base64,{graph4_base64}", style={'width': '100%'})  # Display scatter plot image
        ], style={'grid-area': 'scatter', 'padding': '10px'}),  # Assign to grid area 'scatter'

    ], style={  # Define grid layout properties
        'display': 'grid',
        'grid-template-areas': '''
            "map pie"
            "bar scatter"
        ''',
        'grid-template-columns': '1fr 1fr',  # Two equal-width columns
        'grid-template-rows': '1fr 1fr',  # Two equal-height rows
        'gap': '20px',  # Space between grid items
        'padding': '20px'  # Padding around the grid
    }),
])
