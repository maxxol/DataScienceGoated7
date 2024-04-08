import requests
from bs4 import BeautifulSoup
from dash import Output, Input, dash_table, html

import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from dash import dcc as dcc


def callback_rating_vs_runtime(app, dbengine):
    @app.callback(
        Output('graph-rating-vs-runtime', 'children'),
        [Input('select-genre', 'value')]
    )
    def update_graph_rating_vs_runtime(selected_genre):
        #SQL query with selected genre filter
        query = f"""
        SELECT t.run_time_minutes, AVG(r.average_rating) AS avg_rating
        FROM title t
        JOIN rating r ON t.title_id = r.title_id
        JOIN has_genre hg ON t.title_id = hg.title_id
        JOIN genre g ON hg.genre_id = g.genre_id
        WHERE g.genre_name = '{selected_genre}'
        GROUP BY t.run_time_minutes;
        """
        tabel = pd.read_sql(query, dbengine)

        #create line graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tabel['run_time_minutes'], y=tabel['avg_rating'],
                                  mode='lines',
                                  name='Rating vs Runtime'))
        fig.update_layout(title='Rating vs Runtime',
                          xaxis_title='Runtime (minutes)',
                          yaxis_title='Average Rating',
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          )
        fig.update_xaxes(range=[0, 200])  # Set the y-axis upper bound to 30

        return dcc.Graph(figure=fig)


def callback_top_genre_pairs(app, dbengine):
    @app.callback(
        Output('graph-top-genre-pairs', 'children'),
        [Input('select-genre', 'value')]
    )
    def update_graph2(selected_genre):
        #SQL query with selected genre filter
        query = f"""
        WITH genre_pairs AS (
            SELECT 
                g1.genre_name AS genre1,
                g2.genre_name AS genre2,
                COUNT(*) AS frequency,
                ROW_NUMBER() OVER(PARTITION BY g1.genre_name ORDER BY COUNT(*) DESC) AS rank
            FROM 
                has_genre hr1
            JOIN 
                genre g1 ON hr1.genre_id = g1.genre_id
            JOIN 
                has_genre hr2 ON hr1.title_id = hr2.title_id
            JOIN 
                genre g2 ON hr2.genre_id = g2.genre_id
            WHERE 
                g1.genre_id < g2.genre_id -- Ensures that we only get unique pairs of genre
                AND g1.genre_name = '{selected_genre}'  -- Filter by selected genre
            GROUP BY 
                genre1, genre2
            HAVING 
                g1.genre_name <> g2.genre_name -- Exclude pairs of the same genre
        )
        SELECT 
            genre1,
            genre2,
            frequency
        FROM 
            genre_pairs
        WHERE 
            rank <= 5;
        """
        tabel = pd.read_sql(query, dbengine)

        #create a bar graph
        bar_chart = go.Bar(
            x=tabel['genre2'],
            y=tabel['frequency'],
            marker=dict(color='blue')
        )

        layout = go.Layout(
            title=f'Top 5 genre Paired with {selected_genre}',
            xaxis=dict(title='Genre'),
            yaxis=dict(title='Frequency'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )

        fig = go.Figure(data=[bar_chart], layout=layout)

        return dcc.Graph(figure=fig)


def callback_top_gross_movies(app, dbengine):
    @app.callback(
        Output('graph-top-gross-movies', 'children'),
        [Input('select-genre', 'value')]
    )
    def update_graph3(selected_genre):
        # SQL query with selected genre filter
        query = f"""
    	SELECT t.primary_title, ROUND(AVG(f.revenue))as revenue
        FROM title t
        JOIN finance f ON t.title_id = f.title_id
        JOIN has_genre hg ON t.title_id = hg.title_id
        JOIN genre g ON hg.genre_id = g.genre_id
        WHERE g.genre_name = '{selected_genre}'
    	and revenue is not null
        and revenue >100
    	group by t.primary_title
    	ORDER BY revenue desc

        LIMIT 10
        """
        tabel = pd.read_sql(query, dbengine)

        # create a bar graph
        bar_chart = go.Bar(
            x=tabel['primary_title'],
            y=tabel['revenue'],
            marker=dict(color='blue')
        )

        layout = go.Layout(
            title=f'Top 10 earning film with genre:  {selected_genre}',
            xaxis=dict(title='Genre'),
            yaxis=dict(title='earnings'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )

        fig = go.Figure(data=[bar_chart], layout=layout)

        return dcc.Graph(figure=fig)


def callback_bottom_gross_movies(app, dbengine):
    @app.callback(
        Output('graph-bottom-gross-movies', 'children'),
        [Input('select-genre', 'value')]
    )
    def update_graph4(selected_genre):
        # SQL query with selected genre filter
        query = f"""
    	SELECT t.primary_title, ROUND(AVG(f.revenue))as revenue
        FROM title t
        JOIN finance f ON t.title_id = f.title_id
        JOIN has_genre hg ON t.title_id = hg.title_id
        JOIN genre g ON hg.genre_id = g.genre_id
        WHERE g.genre_name = '{selected_genre}'
    	and revenue is not null
        and revenue >100
    	group by t.primary_title
    	ORDER BY revenue asc

        LIMIT 10
        """
        tabel = pd.read_sql(query, dbengine)

        # create a bar graph
        bar_chart = go.Bar(
            x=tabel['primary_title'],
            y=tabel['revenue'],
            marker=dict(color='blue')
        )

        layout = go.Layout(
            title=f'Bottom 10 earning film with genre:  {selected_genre}',
            xaxis=dict(title='Genre'),
            yaxis=dict(title='earnings'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )

        fig = go.Figure(data=[bar_chart], layout=layout)

        return dcc.Graph(figure=fig)


def callback_historical_popularity(app, dbengine):
    @app.callback(
        Output('graph-historical-popularity', 'children'),
        [Input('select-genre', 'value')]
    )
    def update_graph5(selected_genre):
        # SQL query with selected genre filter
        query = f"""
    	SELECT start_year,count(title.title_id) AS film_count
    	FROM title
    	JOIN has_genre ON title.title_id = has_genre.title_id
    	JOIN genre ON has_genre.genre_id = genre.genre_id
    	WHERE genre.genre_name = '{selected_genre}'
    	group by start_year
        """
        tabel = pd.read_sql(query, dbengine)

        # create a line graph
        line_chart = go.Line(
            x=tabel['start_year'],
            y=tabel['film_count'],
            marker=dict(color='blue')  # You can customize the color
        )

        layout = go.Layout(
            title=f'Historical popularity:  {selected_genre}',
            xaxis=dict(title='year', range=[1950, 2026]),
            yaxis=dict(title='films made'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )

        fig = go.Figure(data=[line_chart], layout=layout)

        return dcc.Graph(figure=fig)


def callback_popular_actors(app, dbengine):
    @app.callback(
        Output('graph-popular-actors', 'children'),
        [Input('select-genre', 'value')]
    )
    def update_graph6(selected_genre):
        # SQL query with selected genre filter
        query = f"""
    	SELECT 
        AVG(rating.average_rating) AS rating, 
        AVG(f.revenue) AS revenue, 
        person.primary_name AS name, 
        COUNT(directed_films.title_id) AS film_count
    FROM rating 
    JOIN (SELECT 
            works_on.person_id,
            works_on.title_id
        FROM works_on 
        WHERE works_on.job_name = 'actor' or works_on.job_name = 'actress'
    ) AS directed_films ON rating.title_id = directed_films.title_id
    JOIN person ON directed_films.person_id = person.person_id
    JOIN has_genre ON rating.title_id = has_genre.title_id
    JOIN genre g ON has_genre.genre_id = g.genre_id
    full outer JOIN finance f ON rating.title_id = f.title_id 
    WHERE 
        g.genre_name = '{selected_genre}' and revenue is not null
    GROUP BY 
        person.primary_name
    ORDER BY 
        film_count DESC
    LIMIT 30;


        """
        tabel = pd.read_sql(query, dbengine)
        bubble_scale = 1
        # create a bubble plot
        scatter = go.Scatter(
            x=tabel['revenue'],
            y=tabel['rating'],
            mode='markers',
            marker=dict(
                size=tabel['film_count'] * bubble_scale,  # Adjusting the bubble size
                color='blue',
                opacity=0.5,
                line=dict(width=0.5, color='DarkSlateGrey')
            ),
            text=tabel[['name', 'film_count', 'rating']].apply(
                lambda x: f"Name: {x['name']}<br>Film Count: {x['film_count']}<br>Rating: {x['rating']}", axis=1)

        )

        layout = go.Layout(
            title=f'Popular Genre actors:  {selected_genre}',
            xaxis=dict(title='Average box office', range=[0, max(tabel['revenue'])]),
            yaxis=dict(title='Average Rating', range=[0, 10]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        fig = go.Figure(data=[scatter], layout=layout)
        return dcc.Graph(figure=fig)


def callback_popular_directors(app, dbengine):
    @app.callback(
        Output('graph-popular-directors', 'children'),
        [Input('select-genre', 'value')]
    )
    def update_graph7(selected_genre):
        # SQL query with selected genre filter
        query = f"""
    	SELECT 
        AVG(rating.average_rating) AS rating, 
        AVG(f.revenue) AS revenue, 
        person.primary_name AS name, 
        COUNT(directed_films.title_id) AS film_count
    FROM rating 
    JOIN (SELECT 
            works_on.person_id,
            works_on.title_id
        FROM works_on 
        WHERE works_on.job_name = 'director'
    ) AS directed_films ON rating.title_id = directed_films.title_id
    JOIN person ON directed_films.person_id = person.person_id
    JOIN has_genre ON rating.title_id = has_genre.title_id
    JOIN genre g ON has_genre.genre_id = g.genre_id
    full outer JOIN finance f ON rating.title_id = f.title_id 
    WHERE 
        g.genre_name = '{selected_genre}' and revenue is not null
    GROUP BY 
        person.primary_name
    ORDER BY 
        film_count DESC
    LIMIT 30;

        """
        tabel = pd.read_sql(query, dbengine)
        bubble_scale = 1
        # create a bubble plot
        scatter = go.Scatter(
            x=tabel['revenue'],
            y=tabel['rating'],
            mode='markers',
            marker=dict(
                size=tabel['film_count'] * bubble_scale,  # adjusting the bubble size
                color='blue',
                opacity=0.5,
                line=dict(width=0.5, color='DarkSlateGrey')
            ),
            text=tabel[['name', 'film_count', 'rating']].apply(
                lambda x: f"Name: {x['name']}<br>Film Count: {x['film_count']}<br>Rating: {x['rating']}", axis=1)

        )

        layout = go.Layout(
            title=f'Popular Genre Directors:  {selected_genre}',
            xaxis=dict(title='Average box office', range=[0, max(tabel['revenue'])]),
            yaxis=dict(title='Average Rating', range=[0, 10]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        fig = go.Figure(data=[scatter], layout=layout)
        return dcc.Graph(figure=fig)


def callback_genres_by_actor(app, dbengine):
    @app.callback(
        Output('graph-genres-by-actor', 'children'),
        Output("actor-input-store", "data"),
        [Input('actor-input-box', 'value')]
    )
    def update_graph8(selected_actor):
        #SQL query with selected genre filter
        query = f"""
        SELECT 
        person.person_id, 
        person.primary_name AS name, 
        genre.genre_name AS genre,
        COUNT(DISTINCT rating.title_id) AS film_count
        FROM rating 
        JOIN has_genre ON rating.title_id = has_genre.title_id
        JOIN genre  ON has_genre.genre_id = genre.genre_id
        JOIN works_on ON rating.title_id = works_on.title_id
        JOIN person ON works_on.person_id = person.person_id
        WHERE person.primary_name = '{selected_actor}'
        GROUP BY person.person_id, person.primary_name, genre
        ORDER BY film_count DESC;
        """

        # Originele code
        # tabel = pd.read_sql(query, dbengine)
        tabel = pd.read_sql(query, dbengine).head(8) # Aangepast om alleen de eerste 8 te pakken

        person_id = tabel['person_id'].values[0]
        person_name = tabel['name'].values[0]
        #print(person_id)
        #print(person_name)

        #create a pie chart
        pie_chart = go.Pie(
        labels=tabel['genre'],
        values=tabel['film_count'],
        marker=dict(colors=['blue', 'cyan' ,'lime', 'green', 'yellow', 'orange', 'red', 'pink', 'purple'] * len(tabel))  # R A I N B O W
    )

        layout = go.Layout(
            title=f'Film distribution by Genre for {selected_actor}',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )

        fig = go.Figure(data=[pie_chart], layout=layout)

        return dcc.Graph(figure=fig), {'actor_id': person_id, 'actor_name': person_name}

    @app.callback(
        Output("actor-header", "children"),
        Output("actor-id-store", "data"),
        Input("actor-input-store", "data")
    )
    def update_header(data):
        return data['actor_name'], {'actor_id': data['actor_id']}

    @app.callback(
        Output("actor-image", "children"),
        Input("actor-id-store", "data"),
    )
    def update_image(data):
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'}

        actor_id = data['actor_id']
        url = f'https://www.imdb.com/name/{actor_id}/'
        print(url)

        result = requests.get(url, headers=headers)

        soup = BeautifulSoup(result.text, 'html.parser')

        try:
            container_div = soup.find("div", attrs={'class': "ipc-poster"})
            image = container_div.find("img")
            return html.Img(src=image["src"], alt='image', className="image"),

        except:
            print("oeps")


def callback_most_grossing_by_actor(app, dbengine):
    @app.callback(
        Output('graph-grossing-by-actor', 'children'),
        [Input('actor-input-box', 'value')]
    )
    def update_graph9(selected_actor):
        # SQL query with selected genre filter
        query = f"""
        SELECT t.primary_title as film, ROUND(AVG(f.revenue)) as revenue
        FROM title t
        JOIN finance f ON t.title_id = f.title_id
        JOIN works_on ON t.title_id = works_on.title_id
        JOIN person ON works_on.person_id = person.person_id
        WHERE person.primary_name = '{selected_actor}'
        and revenue is not null
        group by t.primary_title
        ORDER BY revenue desc
        LIMIT 10
        """
        tabel = pd.read_sql(query, dbengine)

        # create a Dash DataTable component to display the query result
        table = dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in tabel.columns],
            data=tabel.to_dict('records'),
            style_table={'overflowX': 'scroll'},
            style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
            style_data={'whiteSpace': 'normal', 'height': 'auto'}
        )

        return table