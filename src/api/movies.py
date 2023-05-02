from fastapi import APIRouter, HTTPException
from fastapi.params import Query
import os
import dotenv
import sqlalchemy
import dotenv
from enum import Enum
import database as db

router = APIRouter()

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url())


@router.get("/movies/{movie_id}", tags=["movies"])
def get_movie(movie_id: int):
    """
    This endpoint returns a single movie by its identifier. For each movie it returns:
    * `movie_id`: the internal id of the movie.
    * `title`: The title of the movie.
    * `top_characters`: A list of characters that are in the movie. The characters
      are ordered by the number of lines they have in the movie. The top five
      characters are listed.

    Each character is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `num_lines`: The number of lines the character has in the movie.

    """

    json = {}
    with engine.begin() as conn:
        movies_init = conn.execute(
            sqlalchemy.text(
            f'''
            SELECT title, movie_id FROM movies
            WHERE movie_id = {movie_id}
            '''
            )
        )
        counter = 0
        for mov in movies_init:
            json = {
                "movie_id": mov.movie_id,
                "title": mov.title
            }
            counter+=1
        if counter == 0:
            raise HTTPException(status_code=404, detail="movie not found.")
        movies_2 = conn.execute(
            sqlalchemy.text(
            f'''
            SELECT c.name, l.character_id, count(l.character_id) num_lines FROM lines AS l
            JOIN characters AS c ON c.character_id = l.character_id
            WHERE l.movie_id = {movie_id}
            GROUP BY l.character_id,c.name
            ORDER BY num_lines DESC
            '''
            ))
        temp = []
        for mov_t in movies_2:
            temp.append(
                {
                "character_id": mov_t.character_id,
                "character": mov_t.name,
                "num_lines": mov_t.num_lines
                }
            )
        json["top_characters"] = temp[:5]
    return json


class movie_sort_options(str, Enum):
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


# Add get parameters
@router.get("/movies/", tags=["movies"])
def list_movies(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: movie_sort_options = movie_sort_options.movie_title,
):
    """
    This endpoint returns a list of movies. For each movie it returns:
    * `movie_id`: the internal id of the movie. Can be used to query the
      `/movies/{movie_id}` endpoint.
    * `movie_title`: The title of the movie.
    * `year`: The year the movie was released.
    * `imdb_rating`: The IMDB rating of the movie.
    * `imdb_votes`: The number of IMDB votes for the movie.

    You can filter for movies whose titles contain a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `year` - Sort by year of release, earliest to latest.
    * `rating` - Sort by rating, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    sort_text = ""
    if sort is movie_sort_options.movie_title:
        sort_text = "title ASC"
    elif sort is movie_sort_options.year:
        sort_text = "year ASC"
    elif sort is movie_sort_options.rating:
        sort_text = "imdb_rating DESC"
    else:
        assert False

    if "drop" in name.lower():
        assert False

    json = []
    with engine.begin() as conn:
        movies_t = conn.execute(
            sqlalchemy.text(
            f'''
            SELECT movie_id, title, year, imdb_rating, imdb_votes FROM movies
            WHERE title LIKE '%{name.lower()}%'
            ORDER BY year {sort_text}
            '''
            )
        )
        for t in movies_t:
            json.append(
                {
                "movie_id": t.movie_id,
                "movie_title": t.movie_title,
                "year": str(t.year),
                "imdb_rating": t.imdb_rating,
                "imdb_votes": t.imdb_votes
                }
            )

    return json[offset:limit+offset]
