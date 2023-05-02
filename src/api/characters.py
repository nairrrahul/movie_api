from fastapi import APIRouter, HTTPException
from fastapi.params import Query
import os
import dotenv
import sqlalchemy
import dotenv
from enum import Enum

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




@router.get("/characters/{id}", tags=["characters"])
def get_character(id: int):
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
    json = {}

    with engine.begin() as conn:
        lines_a = conn.execute(
            sqlalchemy.text(
            f'''
            SELECT ch.character_id, ch.name, ch.gender, m.title FROM characters as ch
            JOIN movies as m on m.movie_id = ch.movie_id
            WHERE ch.character_id = {id}
            '''
            )
        )
        for line_t in lines_a:
            json = {
                "character_id": line_t.character_id,
                "character": line_t.name,
                "movie": line_t.title,
                "gender": line_t.gender
            }
        lines_list = conn.execute(
            sqlalchemy.text(
            f'''
            WITH char_line_table as 
                (SELECT c.character1_id, c.character2_id, count(l.conversation_id) num_lines_with from lines as l
                 JOIN conversations as c on c.conversation_id = l.conversation_id
                 WHERE c.character1_id = {id} OR c.character2_id = {id}
                 GROUP BY l.conversation_id, c.conversation_id)
            SELECT ch.character_id, ch.name, ch.gender, sum(cl.num_lines_with) total_lines from char_line_table as cl
            JOIN characters as ch on (cl.character1_id = ch.character_id AND cl.character2_id = {id})
                                  or (cl.character2_id = ch.character_id AND cl.character1_id = {id})
            GROUP BY ch.character_id
            ORDER BY total_lines DESC
            '''
            )
        )
        temp = []
        for line in lines_list:
            temp.append(
                {
                "character_id": line.character_id,
                "character": line.name,
                "gender": line.gender,
                "number_of_lines_together": int(line.total_lines)
                }
            )
        json["top_conversations"] = temp
    return json


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
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
    sort_text = ""
    if sort is character_sort_options.character:
        sort_text = "name ASC"
    elif sort is character_sort_options.movie:
        sort_text = "title ASC"
    elif sort is character_sort_options.number_of_lines:
        sort_text = "num_lines DESC"
    else:
        assert False

    json = []

    if "drop" in name.lower():
        assert False

    with engine.begin() as conn:
        lines = conn.execute(
            sqlalchemy.text(
            f'''
            WITH char_list as
                (SELECT c.character_id, c.name, m.title, l.character_id, count(*) num_lines 
                 FROM characters as c 
                 JOIN movies as m ON m.movie_id = c.movie_id 
                 JOIN lines as l on l.character_id = c.character_id 
                 GROUP BY c.character_id, m.title, l.character_id) 
            SELECT * from char_list 
            WHERE name like '%{name.upper()}%' 
            ORDER BY {sort_text}
            '''))
        for line in lines:
            json.append({
                "character_id": line.character_id,
                "character": line.name,
                "movie": line.title,
                "number_of_lines": line.num_lines
            })
    return json[offset:limit+offset]
