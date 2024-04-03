from dash import Dash, html, dcc, callback, Output, Input, State, dash_table, ALL

import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from sqlalchemy import create_engine
from dash import dcc as dcc
from dash import html as html
import dash_bootstrap_components as dbc
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
from sentiment import analyze_sentiment  # Import the sentiment analysis method

from graph_callbacks import *

dbengine = create_engine('postgresql://postgres:1234@localhost/movie')
dt = pd.read_sql('SELECT * FROM title_basics WHERE primary_title = \'Top Gun\'', dbengine)

app = Dash("MovieDash", external_stylesheets=['./assets/global.css','./assets/staffPage.css','./assets/genrePage.css'])

callback_rating_vs_runtime(app, dbengine)
callback_top_genre_pairs(app, dbengine)
callback_top_gross_movies(app, dbengine)
callback_bottom_gross_movies(app, dbengine)
callback_historical_popularity(app, dbengine)
callback_popular_actors(app, dbengine)
callback_popular_directors(app, dbengine)

genre_options = [
    {"label": "Action", "value": "Action"},
    # {"label": "Adult", "value": "Adult"},
    {"label": "Adventure", "value": "Adventure"},
    {"label": "Animation", "value": "Animation"},
    {"label": "Biography", "value": "Biography"},
    {"label": "Comedy", "value": "Comedy"},
    {"label": "Crime", "value": "Crime"},
    # {"label": "Documentary", "value": "Documentary"},
    {"label": "Drama", "value": "Drama"},
    {"label": "Family", "value": "Family"},
    {"label": "Fantasy", "value": "Fantasy"},
    {"label": "Film-Noir", "value": "Film-Noir"},
    # {"label": "Game-Show", "value": "Game-Show"},
    {"label": "History", "value": "History"},
    {"label": "Horror", "value": "Horror"},
    {"label": "Music", "value": "Music"},
    {"label": "Musical", "value": "Musical"},
    {"label": "Mystery", "value": "Mystery"},
    # {"label": "News", "value": "News"},
    # {"label": "Reality-TV", "value": "Reality-TV"},
    {"label": "Romance", "value": "Romance"},
    {"label": "Sci-Fi", "value": "Sci-Fi"},
    # {"label": "Short", "value": "Short"},
    {"label": "Sport", "value": "Sport"},
    # {"label": "Talk-Show", "value": "Talk-Show"},
    {"label": "Thriller", "value": "Thriller"},
    {"label": "War", "value": "War"},
    {"label": "Western", "value": "Western"}
]

dropdown = html.Div(className="container-dropdown", children=[
    dcc.Dropdown(options=genre_options, clearable=True, id="select-genre")
])

genreHeader = html.Div(className="header")

genreTopBar = html.Div(
    [
        dropdown,
        genreHeader,
    ],
    className="container-genre-top"
)


casting = html.Div([
    html.H1("Casting"),
    html.Div(id='graph-popular-actors', className="graph"),
    html.Div(id='graph-popular-directors', className="graph"),
    ],
    className="sub-container casting"
)

boxOffice = html.Div([
    html.H1("Box Office"),
    html.Div(id='graph-top-gross-movies', className="graph"),
    html.Div(id='graph-bottom-gross-movies', className="graph"),
    ],
    className="sub-container box-office"
)

technical = html.Div([
    html.H1("Technical"),
    html.Div(id='graph-rating-vs-runtime', className="graph"),
    html.Div(id='graph-top-genre-pairs', className="graph"),
    ],
    className="sub-container technical"
)

history = html.Div([
    html.H1("History"),
    html.Div(id='graph-historical-popularity', className="graph"),
    ],
    className="sub-container history"
)


genreContent = html.Div(
    [
        casting,
        boxOffice,
        technical,
        history,
    ],
    className="container-genre-bottom"
)

pageA = html.Div(
    [
        genreTopBar,
        genreContent,
    ],
    className="container-genre",
)


searchBar = html.Div(
    [
        dcc.Input(id="input", placeholder="Search...", type="text", className="search-bar"),
        html.P(id="output"),
    ],
    className="search-bar-container"
)

staffImage = html.Div(
    html.Img(src=r'https://placehold.co/280x414', alt='image', className="image"),
    className="container-image",
)

staffBio = html.Div(
    "Bio info you know whats up",
    className="container-bio",
)

header = html.H1(
    "Acteur Naam (of zo?)",
    className="header",
)

graph1 = html.Div(
    html.Img(src=r'https://placehold.co/400x400', alt='image', className="image"),
    className="graph-pi",
)

graph2 = html.Div(
    html.Img(src=r'https://placehold.co/750x400', alt='image', className="image"),
    className="graph-bar",
)

graphContainer = html.Div(
    [
        graph1,
        graph2,
    ],
    className="container-graph",
)

sentimentContainer = html.Div(
    "",
    className="container-sentiment",
)


pageB = html.Div([
        html.Div(
            [
                searchBar,
                staffImage,
                staffBio
            ],
            className="container-staff-left",
        ),
        html.Div(
            [
                header,
                graphContainer,
                sentimentContainer,
            ],
            className="container-staff-right",
        ),
    ],
    className="container-staff"
),

# html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
# dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
# html.Div(id='output-container', style={'display': 'flex'}, children=[
#     dcc.Graph(id='graph-content', style={'width': '50%', 'height': '500px'}),
#     html.Div(children=[dash_table.DataTable(dt.to_dict('records'), page_size=300)], style={'width': '50%'}),
# ])

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
    '/page1': {'name': 'PageA', 'content': pageA},
    '/page2': {'name': 'PageB', 'content': pageB},
    '/page3': {'name': 'PageC', 'content': pageC},
}

# Define app layout
app.layout = html.Div(children=[
    dcc.Location(id='url'),
    html.Div(
        [
            html.Div(id='navbar', className='navbar', children=[html.A(href=path, children=page['name'], id={"type":"link-navbar",
                "index": "/" if path == 0 else f"{path}"}) for path, page in pages.items()]),
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


@app.callback(Output({"type":"link-navbar", "index":ALL}, "className"),
[Input("url", "pathname"),Input({"type":"link-navbar", "index":ALL}, "id")])
def callback_func(pathname, link_elements):
    return ["active" if link["index"] == pathname else "" for link in link_elements]


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