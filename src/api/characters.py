from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
import copy

router = APIRouter()


@router.get("/characters/{id}", tags=["characters"])
def get_character(id: str):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """

    json = None 

    #TODO: empty string to null
    for character in db.characters:
        if character["character_id"] == id:
            json = copy.deepcopy(character)
    
    if json is None:
        raise HTTPException(status_code=404, detail="movie not found.")
    else:
       json['movie'] = db.char_id_to_movie_name[id]
       json.pop('movie_id')
       c1_convs = db.query_for_chars(db.char_convs_pairs, 0, id)
       c2_convs = db.query_for_chars(db.char_convs_pairs, 1, id)
       c_list = c1_convs + c2_convs
       c_list.sort(key=lambda x: x["number_of_lines_together"], reverse=True)
       json['top_conversations'] = c_list
       json['character_id'] = int(json['character_id'])
       json.pop('age')

    return json


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """

    json = copy.deepcopy(db.characters)
    for char in json:
      char['movie'] = db.char_id_to_movie_name[char['character_id']]
      char.pop('movie_id')
      char['number_of_lines'] = db.characters_to_lines[char['character_id']]
      char['character_id'] = int(char['character_id'])
      char.pop('age')
      char.pop('gender')
    if sort == character_sort_options.character:
      json.sort(key=lambda x: x['name'])
    elif sort ==  character_sort_options.movie:
      json.sort(key=lambda x: x['movie'])
    else:
      json.sort(key=lambda x: x['number_of_lines'], reverse=True)
    return [j for j in json if name.upper() in j["name"]][offset:limit]
