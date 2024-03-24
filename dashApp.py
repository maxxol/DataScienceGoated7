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
    ])
])

pageC = html.Div(children=[
    html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
    html.Div([
        dcc.Input(id='keyword-input', type='text', placeholder='Enter keyword'),
        html.Button('Analyze Sentiment', id='analyze-button', n_clicks=0)
    ]),
    html.Div(id='sentiment-results'),  # Placeholder for sentiment analysis results
    html.Div(id='wordcloud-container')  # Placeholder for word cloud image
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

# Callback to update sentiment results and word cloud
@app.callback(
    Output('sentiment-results', 'children'),
    Output('wordcloud-container', 'children'),
    Input('analyze-button', 'n_clicks'),
    State('keyword-input', 'value')
)
def update_sentiment_and_wordcloud(n_clicks, keyword):
    if n_clicks and keyword:  # Check if button is clicked and keyword is provided
        sentiment_results, wordcloud_base64 = analyze_sentiment(keyword)  # Call analyze_sentiment function
        wordcloud_img = html.Img(src='data:image/png;base64,{}'.format(wordcloud_base64))  # Create image element for word cloud
        
        # Return sentiment analysis results and word cloud image
        return (
            html.Div([
                html.H3(f"Sentiment Analysis Results for '{keyword}'"),
                html.P(sentiment_results)
            ]),
            wordcloud_img
        )
    return None, None  # Return None if button is not clicked or keyword is not provided

if __name__ == '__main__':
    app.run(debug=False)