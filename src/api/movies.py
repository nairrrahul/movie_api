import copy
from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()


# include top 3 actors by number of lines
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

    json = None

    for movie in db.movies:
        if movie["movie_id"] == str(movie_id):
            json = copy.deepcopy(movie)

    if json is None:
        raise HTTPException(status_code=404, detail="movie not found.")
    else:
        chars_present = []
        for c_id in db.char_id_to_movie_id:
            if db.char_id_to_movie_id[c_id] == str(movie_id):
                chars_present.append(c_id)
        cs_list = [
            {
                "character_id": int(cid),
                "character": db.char_id_to_name[cid],
                "num_lines": db.characters_to_lines[cid]
            } for cid in chars_present
        ]
        cs_list.sort(key=lambda x: x["num_lines"], reverse=True)
        json['movie_id'] = int(json['movie_id'])
        json['top_characters'] = cs_list[:5]
        json.pop("year")
        json.pop("imdb_rating")
        json.pop("imdb_votes")
        json.pop("raw_script_url")
        #get chars from char_id_to_movie_name dict
        #get char name from char_id_to_name
        #figure out lines
    return json


class movie_sort_options(str, Enum):
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


# Add get parameters
@router.get("/movies/", tags=["movies"])
def list_movies(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
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
    json = copy.deepcopy(db.movies)
    for movie in json:
        movie.pop("raw_script_url")
        movie['movie_title'] = movie['title']
        movie.pop('title')
        movie['imdb_rating'] = float(movie['imdb_rating'])
        movie['imdb_votes'] = int(movie["imdb_votes"])
        movie['movie_id'] = int(movie['movie_id'])
    
    if sort == movie_sort_options.movie_title:
      json.sort(key=lambda x: x['movie_title'])
    elif sort ==  movie_sort_options.year:
      json.sort(key=lambda x: int(x['year']))
    else:
      json.sort(key=lambda x: x['imdb_rating'], reverse=True)
    return [j for j in json if name in j["movie_title"]][offset:limit]
