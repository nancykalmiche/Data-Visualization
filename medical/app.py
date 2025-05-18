from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dashboard1
import dashboard2
import dashboard3
import dashboard4

app = Dash(__name__)
server = app.server

# App layout with enhanced styling
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # Navigation bar
    html.Nav([
        dcc.Link("General", href="/dashboard1", className='nav-link'),
        dcc.Link("Demographic", href="/dashboard2", className='nav-link'),
        dcc.Link("COVID-19", href="/dashboard3", className='nav-link'),
        dcc.Link("Obesity and Health", href="/dashboard4", className='nav-link')
    ], className='navbar'),

    # Main content area
    html.Div(id='page-content', className='content')
])

# Route handling
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dashboard2':
        return dashboard2.layout
    elif pathname == '/dashboard3':
        return dashboard3.layout
    elif pathname == '/dashboard4':
        return dashboard4.layout
    else:
        return dashboard1.layout

# External CSS via Dash for styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Multi Dashboard App</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', sans-serif;
                background-color: #f5f7fa;
                margin: 0;
                padding: 0;
            }
            .navbar {
                display: flex;
                justify-content: center;
                background-color: #2c3e50;
                padding: 15px 0;
            }
            .nav-link {
                color: white;
                text-decoration: none;
                margin: 0 20px;
                font-size: 18px;
                transition: color 0.3s;
            }
            .nav-link:hover {
                color: #1abc9c;
            }
            .content {
                max-width: 1300px;
                margin: 30px auto;
                padding: 20px;
                background: white;
                box-shadow: 0 4px 8px rgba(0,0,0,0.05);
                border-radius: 12px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True)
