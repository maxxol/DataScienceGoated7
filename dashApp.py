from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

dbengine = create_engine('postgresql://postgres:root@localhost/test')

dt = pd.read_sql('SELECT * FROM stuff.stuff', dbengine)

app = Dash("MovieDash", external_stylesheets=['./assets/navbar.css'])

pageB = html.Div(children=[
    html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    html.Div(id='output-container', style={'display': 'flex'}, children=[
        dcc.Graph(id='graph-content', style={'width': '50%', 'height': '500px'}),
        html.Div(children=[dash_table.DataTable(dt.to_dict('records'), page_size=300)], style={'width': '50%'}),
    ])
])

pages = {
    '/': {'name': 'Home', 'content': html.Div(children="Dit is de homepagina")},
    '/page1': {'name': 'PageA', 'content': html.Div(children="Dit is pagina A")},
    '/page2': {'name': 'PageB', 'content': pageB},
    '/page3': {'name': 'PageC', 'content': html.Div(children="Dit is pagina C")},
}

app.layout = html.Div(children=[
    dcc.Location(id='url'),
    html.Div(className='navbar', children=[html.A(href=path, children=page['name']) for path, page in pages.items()]),
    html.Div(id='page-content')
])


@app.callback(
    Output(component_id='page-content', component_property='children'),
    Input(component_id='url', component_property='pathname')
)
def display_page(pathname):
    return pages.get(pathname, {'content': html.Div(children="404")})['content']


@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country == value]
    return px.line(dff, x='year', y='pop')


if __name__ == '__main__':
    app.run(debug=False)
