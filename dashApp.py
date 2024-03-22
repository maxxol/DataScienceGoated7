from dash import Dash, html, dcc, callback, Output, Input, State, dash_table

import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
from sentiment import analyze_sentiment  # Import the sentiment analysis method


#dbengine = create_engine('postgresql://postgres:root@localhost/test')

#dt = pd.read_sql('SELECT * FROM stuff.stuff', dbengine)

app = Dash("MovieDash", external_stylesheets=['./assets/navbar.css'])

pageB = html.Div(children=[
    html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    html.Div(id='output-container', style={'display': 'flex'}, children=[
        dcc.Graph(id='graph-content', style={'width': '50%', 'height': '500px'}),
        #html.Div(children=[dash_table.DataTable(dt.to_dict('records'), page_size=300)], style={'width': '50%'}),
    ])
])

pageC = html.Div(children=[
    html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
    html.Div([
        dcc.Input(id='keyword-input', type='text', placeholder='Enter keyword'),
        html.Button('Analyze Sentiment', id='analyze-button', n_clicks=0)
    ]),
    html.Div(id='sentiment-results'),
    html.Div(id='keyword-input-previous', style={'display': 'none'})  # Hidden div to store previous keyword value
])

pages = {
    '/': {'name': 'Home', 'content': html.Div(children="Dit is de homepagina")},
    '/page1': {'name': 'PageA', 'content': html.Div(children="Dit is pagina A")},
    '/page2': {'name': 'PageB', 'content': pageB},
    '/page3': {'name': 'PageC', 'content': pageC},
}

# Define app layout
app.layout = html.Div(children=[
    dcc.Location(id='url'),
    html.Div(className='navbar', children=[html.A(href=path, children=page['name']) for path, page in pages.items()]),
    html.Div(id='page-content')
])

# Callback to display page based on URL pathname
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    return pages.get(pathname, {'content': html.Div(children="404")})['content']

# Callback to update sentiment results
@app.callback(
    Output('sentiment-results', 'children'),
    Output('keyword-input-previous', 'children'),
    Input('analyze-button', 'n_clicks'),
    State('keyword-input', 'value'),
    State('keyword-input-previous', 'children')
)
def update_sentiment(n_clicks, keyword, keyword_previous):
    keyword_previous = keyword_previous or ''  # Set default value if previous state is not defined
    # Check if button is clicked and keyword input value changes
    if n_clicks and keyword != keyword_previous:
        sentiment_results = analyze_sentiment(keyword)
        return (
            html.Div([
                html.H3(f"Sentiment Analysis Results for '{keyword}'"),
                html.P(sentiment_results)
            ]),
            keyword  # Update previous keyword value
        )
    return None, keyword_previous

if __name__ == '__main__':
    app.run(debug=False)