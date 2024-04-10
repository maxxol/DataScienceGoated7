import datetime
from sentiment import analyze_sentiment
import requests
from bs4 import BeautifulSoup
from dash import Output, Input, dash_table, html, State, ALL

import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from dash import dcc as dcc
from dash.exceptions import PreventUpdate


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
        [Input('select-genre', 'value'),
         Input('gross-overview', 'n_clicks')]
    )
    def update_graph3(selected_genre, n_clicks):
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
        if n_clicks % 2 == 0:
            query = f"""
            SELECT  count(f.revenue), round((f.revenue::numeric / f.budget::numeric), 1) as bucket
                FROM title t
                JOIN finance f ON t.title_id = f.title_id
                JOIN has_genre hg ON t.title_id = hg.title_id
                where hg.genre_id = 1
                and f.revenue is not null
                and f.revenue > 100
                and f.budget is not null
                and f.budget > 100
                group by bucket
                ORDER BY bucket asc
            """
        # SQL query with selected genre filter

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
        Input('select-genre', 'value'),
        Input('future-data-popularity', 'n_clicks')
    )
    def update_graph5(selected_genre, n_clicks):
        future_distance_years = 5
        now_year = datetime.datetime.now().year
        now_month = datetime.datetime.now().month

        future = False
        year_condition = "start_year <= DATE_PART('year', CURRENT_DATE)"
        time_range = [1950, now_year-1]
        if n_clicks % 2 == 1:
            future = True
            year_condition = "start_year >= DATE_PART('year', CURRENT_DATE)"
            time_range = [now_year+1, now_year+future_distance_years]

        # SQL query with selected genre filter
        query = f"""
    	SELECT start_year,count(title.title_id) AS film_count
    	FROM title
    	JOIN has_genre ON title.title_id = has_genre.title_id
    	JOIN genre ON has_genre.genre_id = genre.genre_id
    	WHERE genre.genre_name = '{selected_genre}' AND {year_condition}
    	group by start_year
        """
        tabel = pd.read_sql(query, dbengine)

        projects_this_year = tabel[tabel['start_year'] == 2024]['film_count'].values[0]
        predicted_projects_this_year = int(projects_this_year / now_month * 12)


        # create a line graph
        line_chart = go.Line(
            x=tabel['start_year'],
            y=tabel['film_count'],
            marker=dict(color='blue'),  # You can customize the color,
        )

        layout = go.Layout(
            title=f'Historical popularity:  {selected_genre}',
            xaxis=dict(title='year', range=time_range),
            yaxis=dict(title='films made'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )

        fig = go.Figure(data=[line_chart], layout=layout)

        return html.Div([dcc.Graph(figure=fig),
                         html.Span([f"{projects_this_year} {selected_genre} projecten tot dusver in {now_year}, "
                                    f"dit voorspeld voor {predicted_projects_this_year} projecten "
                                    f"aan het eind van het jaar"]),
                         ])

    @app.callback(
        Output('future-data-popularity', 'children'),
        Input('future-data-popularity', 'n_clicks'),
    )
    def update_future_button(n_clicks):
        output = "zie geplande projecten"
        if n_clicks % 2 == 1:
            output = "Zie afgeronde projecten"
        return output


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
        [Input('actor-id-store', 'value')]
    )
    def update_graph8(data):
        print("pi")
        if data is None:
            raise PreventUpdate
        data = data[0]
        actor_id = data["actor_id"]
        print(actor_id)
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
        WHERE person.person_id = '{actor_id}'
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
        marker=dict(colors=['blue', 'cyan', 'lime', 'green', 'yellow', 'orange', 'red', 'pink', 'purple'] * len(tabel))  # R A I N B O W
    )

        layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )

        fig = go.Figure(data=[pie_chart], layout=layout)

        return dcc.Graph(figure=fig)

    @app.callback(
        Output("actor-image", "children"),
        Input("actor-id-store", "value"),
    )
    def update_image(data):
        print("image")
        if data is None:
            raise PreventUpdate
        data = data[0]
        actor_id = data["actor_id"]
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'}

        url = f'https://www.imdb.com/name/{actor_id}/'

        result = requests.get(url, headers=headers)

        soup = BeautifulSoup(result.text, 'html.parser')

        try:
            container_div = soup.find("div", attrs={'class': "ipc-poster"})
            image = container_div.find("img")
            return html.Img(src=image["src"], alt='image', className="image"),

        except:
            print("oeps")

    @app.callback(
        [
            Output('graph-grossing-by-actor', 'children'),
            Output('sentiment-results', 'children'),
            Output('wordcloud-container', 'children'),
        ],
        [Input('actor-id-store', 'value'),],
    )
    def update_graph9(data):
        print('---update-graph9---')
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


        if data is None:
            raise PreventUpdate

        data = data[0]

        actor_id = data["actor_id"]
        actor_name = data["actor_name"]
        # SQL query with selected genre filter
        query = f"""
            SELECT t.primary_title as film, ROUND(AVG(f.revenue)) as revenue
            FROM title t
            JOIN finance f ON t.title_id = f.title_id
            JOIN works_on ON t.title_id = works_on.title_id
            JOIN person ON works_on.person_id = person.person_id
            WHERE person.person_id = '{actor_id}'
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

        actor_sentiment, actor_wordcloud = update_sentiment_and_wordcloud(1, actor_name)

        return table, actor_sentiment, actor_wordcloud




def callback_search_for_staff(app, dbengine):


    @app.callback(
        [
            Output("actor-id-store", "value"),
            Output('actor-header', 'children'),
            Output({"type": "actor-search-result", "actor_id": ALL, "actor_name": ALL}, "n_clicks"),
            Output('actor-search-button', 'n_clicks'),
        ],
        [
            State({"type": "actor-search-result", "actor_id": ALL, "actor_name": ALL}, "id"),
            Input({"type": "actor-search-result", "actor_id": ALL, "actor_name": ALL}, "n_clicks"),
        ]
    )
    def callback_func(data, n_clicks):
        print(n_clicks)
        n_clicks_array = []
        for i in range(len(n_clicks)):
            n_clicks_array.append(None)
        for i in range(len(n_clicks)):
            if (n_clicks[i] != None):
                return [data[i]], data[i]["actor_name"], n_clicks_array, None
        raise PreventUpdate

    @app.callback(
        [
            Output('actor-search-results', 'children')
        ],
        [Input('actor-search-button', 'n_clicks'),
         State('actor-search-input', 'value')]
    )
    def doe_dingen(n_clicks, selected_actor):
        print(n_clicks)
        if (n_clicks == None): return [[]]
        print(selected_actor)
        if (selected_actor != None):
            query = f"""
                SELECT person.person_id, person.primary_name, SUM(rating.num_votes) as votes
                    FROM person
                    INNER JOIN works_on
                            ON person.person_id = works_on.person_id
                    INNER JOIN rating
                            ON works_on.title_id = rating.title_id
                        WHERE
                            UPPER(person.primary_name) LIKE UPPER('{selected_actor}%%')
                            --AND (works_on.job_name = 'actor' OR works_on.job_name = 'actress')
                    GROUP BY person.person_id
                    ORDER BY votes DESC
                LIMIT 5
                """
            tabel = pd.read_sql(query, dbengine)

            result = []
            print(tabel)
            for _, row in tabel.iterrows():
                result.append(html.P(f"{row['primary_name']}",
                                     id={'type': 'actor-search-result', 'actor_id': row['person_id'],
                                         'actor_name': row['primary_name']}))
            print(result)
            return [result]
        else:
            return []

    # @app.callback(
    #     [
    #         Output('actor-search-results', 'style'),
    #     ],
    #     [
    #         Input("actor-id-store", "value")
    #     ]
    # )
    # def callback_func2(data):
    #     print(data)
    #     return [{'visibility': 'hidden'}]

    # @app.callback(
    #     [
    #         Output('actor-search-results', 'style'),
    #     ],
    #     [
    #         Input("visible", "value")
    #     ]
    # )
    # def callback_func3(data):
    #     print(data)
    #     if (data == True):
    #         return [{'visibility': 'visible'}]
    #     else:
    #         raise PreventUpdate
