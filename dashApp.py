from dash import Dash, html, dcc, callback, Output, Input, State, dash_table

import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
from sentiment import analyze_sentiment  # Import the sentiment analysis method

dbengine = create_engine('postgresql://postgres:1234@localhost/movie')
dt = pd.read_sql('SELECT * FROM title_basics WHERE primary_title = \'Top Gun\'', dbengine)

app = Dash("MovieDash", external_stylesheets=['./assets/navbar.css',dbc.themes.BOOTSTRAP])


searchBar = html.Div(
    [
        dbc.Input(id="input", placeholder="Search...", type="text", style={"width": "75%"}),
        html.P(id="output"),
    ],
    style={"flex-grow": "1", "display": "flex", "justify-content": "center", "align-items": "center", "background-color": "#dedede"}
)

staffImage = html.Div(
    html.Img(src=r'https://placehold.co/280x414', alt='image'),
    style={"flex-grow": "3", "display": "flex", "justify-content": "center", "align-items": "center"}
)

staffBio = html.Div(
    "Bio info you know whats up",
    style={"flex-grow": "8", "display": "flex", "justify-content": "center", "background-color": "#dedede"}
)


pageB = html.Div(children=[
    dbc.Row(
        [
            dbc.Col(
                [
                    searchBar,
                    staffImage,
                    staffBio
                ],
                style={'display': 'flex',  'flex-direction': 'column'},
                width=4
            ),
            dbc.Col(
                "",
                style={'background-color': '#dedede', "margin-left": "12px"}
            ),
        ],
        style={'height': '100%'}
    ),

    # html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
    # dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    # html.Div(id='output-container', style={'display': 'flex'}, children=[
    #     dcc.Graph(id='graph-content', style={'width': '50%', 'height': '500px'}),
    #     html.Div(children=[dash_table.DataTable(dt.to_dict('records'), page_size=300)], style={'width': '50%'}),
    # ])
    ],
    style={'height': '100%'}
)

pageC = dbc.Container(
    [
        dbc.Row(
            [
                html.H1(children='Title of Dash App', style={'textAlign': 'center'})
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("row1 col1", style={'border': '1px solid black', 'padding': '10px'}), width=4),
                dbc.Col(html.Div("row1 col2", style={'border': '1px solid black', 'padding': '10px'}), width=4),
                dbc.Col(html.Div("row1 col3", style={'border': '1px solid black', 'padding': '10px'}), width=4),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("row2 col1", style={'border': '1px solid black', 'padding': '10px'}), width=4),
                dbc.Col(html.Div([
                    html.Div([
                        dcc.Input(id='keyword-input', type='text', placeholder='Enter keyword'),
                        html.Button('Analyze Sentiment', id='analyze-button', n_clicks=0)
                    ]),
                    html.Div(id='sentiment-results'),  # Placeholder for sentiment analysis results
                    html.Div(id='wordcloud-container')  # Placeholder for word cloud image
                ]), width=8, style={'border': '1px solid black', 'padding': '10px'}),
                
            ]
        )
    ],
    fluid=True
)


pages = {
    '/': {'name': 'Home', 'content': html.Div(children="Dit is de homepagina")},
    '/page1': {'name': 'PageA', 'content': html.Div(children="Dit is pagina A")},
    '/page2': {'name': 'PageB', 'content': pageB},
    '/page3': {'name': 'PageC', 'content': pageC},
}

# Define app layout
app.layout = html.Div(children=[
    dcc.Location(id='url'),
    html.Div(
        [
            html.Div(className='navbar', children=[html.A(href=path, children=page['name']) for path, page in pages.items()]),
            html.Div(
                id='page-content',
                style={"flex-grow": "1", "margin-top": "24px"}
            )
        ],
        style={'height': '100%', "width": "100%", "display": "flex", "flex-direction": "column"}
    )
],
style={'height': '100%', "width": "100%", "display": "flex"}
)

# Callback to display page based on URL pathname
@app.callback(
    Output(component_id='page-content', component_property='children'),
    Input(component_id='url', component_property='pathname')
)
def display_page(pathname):
    return pages.get(pathname, {'content': html.Div(children="404")})['content']

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value'))
def update_graph(value):
    dff = df[df.country == value]
    return px.line(dff, x='year', y='pop')

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
        # Define CSS styles based on sentiment score
        if sentiment_results >= 6.5:
            sentiment_style = {'background-color': 'lime', 'padding': '5px','margin': '5px', 'display': 'inline-block', 'border': '1px solid black'}
        elif sentiment_results < 6.5 and sentiment_results >= 5.5:
            sentiment_style = {'background-color': 'yellow', 'padding': '5px','margin': '5px', 'display': 'inline-block', 'border': '1px solid black'}
        else:
            sentiment_style = {'background-color': 'red', 'padding': '5px','margin': '5px', 'display': 'inline-block', 'border': '1px solid black'}
        
        # Convert newline characters to <br> tags within a <pre> tag
        sentiment_results_html = html.Div(html.Pre(sentiment_results), style=sentiment_style)
        
        wordcloud_img = html.Img(src='data:image/png;base64,{}'.format(wordcloud_base64), style={'width': '50%', 'height': 'auto','border': '1px solid black','margin': '5px'})  # Create image element for word cloud with adjusted size
        
        # Return sentiment analysis results and word cloud image
        return (
            html.Div([
                html.H3(f"Sentiment Analysis Results for '{keyword}'"),
                sentiment_results_html
            ]),
            wordcloud_img
        )
        
    return None, None




if __name__ == '__main__':
    app.run(debug=False)