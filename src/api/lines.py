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

# commented out for now because I need it to deploy

# @router.get("/lines/{conversation_id}", tags=["lines"])
# def get_conversation_info(conversation_id: int):
#     """
#     This endpoint returns a conversation by its identifier. For each conversation it returns:
#     * `conversation_id`: the internal id of the conversation.
#     * `movie`: the name of the movie the conversation occurred in
#     * `lines`: the lines of the conversation.

#     Each line is represented by a dictionary with the following keys:
#     * `character`: the name of the character who said the line.
#     * `character_id`: the id of the character
#     * `gender`: the gender of the character, `null` if not present
#     * `line_text`: the text of the line

#     """
#     json = []
#     conv = None
#     for line in db.lines:
#         if line["conversation_id"] == str(conversation_id):
#             temp = copy.deepcopy(line)
#             json.append({
#                 "character": db.char_id_to_name[temp["character_id"]],
#                 "character_id": int(temp["character_id"]),
#                 "gender": db.char_id_to_gender[temp["character_id"]] or None,
#                 "line_text": temp["line_text"]
#             })
#     for conversation in db.conversations:
#         if conversation["conversation_id"] == str(conversation_id):
#             conv = {
#                 "conversation_id": conversation_id,
#                 "movie": db.movie_id_to_title[conversation["movie_id"]],
#                 "lines": json
#             }
#             break
    
#     if len(json) == 0 or conv is None:
#         raise HTTPException(status_code=404, detail="conversation not found.")
#     else:
#         return conv


@router.get("/conversations/{conversation_id}", tags=["conversations"])
def list_conversations_by_id(conversation_id: int):
    """
    This endpoint returns the the content of lines present in a conversation by an id. 
    For each conversation it returns:
    `conversation_id`: the ID of the conversation
    `movie_title`: the title of the movie the conversation occurred in
    `num_lines`: the number of lines in the conversation
    `line_info`: information on the lines present in the conversation

    Each line in line_info is represented as a dictionary with the following keys
    `character`: the character speaking the line
    `line_id`: the ID of the line
    `line_text`: the text present in the line
    """
    json = {}
    with engine.begin() as conn:
        convs = conn.execute(
            sqlalchemy.text(
            f'''
            SELECT c.conversation_id, m.title, COUNT(l.conversation_id) n_lines FROM conversations AS c
            JOIN movies AS m ON c.movie_id = m.movie_id
            JOIN lines AS l ON l.conversation_id = c.conversation_id
            WHERE c.conversation_id = {conversation_id}
            GROUP BY l.conversation_id, m.title, c.conversation_id
            '''
            )
        )
        counter = 0
        for conv in convs:
            json = {
                "conversation_id": conv.conversation_id,
                "movie_title": conv.title,
                "num_lines": conv.n_lines
            }
            counter += 1
        if counter == 0:
            raise HTTPException(status_code=404, detail="conversation not found.")
        temp = []
        conv_tot = conn.execute(
            sqlalchemy.text(
            f'''
            SELECT l.line_id, l.line_text, c.name FROM lines AS l
            JOIN characters AS c ON c.character_id = l.character_id
            WHERE l.conversation_id = {conversation_id}
            '''
            )
        )
        temp = []
        for cn in conv_tot:
            temp.append(
                {
                "character": cn.name,
                "line_id": cn.line_id,
                "text": cn.line_text
                }
            )
        json["line_info"] = temp
    return json

class lines_sort_options(str, Enum):
    movie_title = "movie_title"
    character_name = "character_name"
    length = "length"

@router.get("/lines/", tags=["lines"])
def list_lines(
    text: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: lines_sort_options = lines_sort_options.movie_title
):
    """
    This endpoint returns a list of lines. For each line it returns:
    * `line_id`: the internal id of the line.
    * `character`: the name of the individual who said the line
    * `movie`: the movie the line featured in
    * `line_sort`: the provided line_sort parameter
    * `line_text`: what the line consists of

    You can filter for lines whose text contain a string by using the
    `text` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `character_name` - Sort by the characters who stated the line alphabetically.
    * `length` - Sort by line length, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    json = []
    sort_text = ""

    if "drop" in text:
        assert False

    if sort is lines_sort_options.length:
        sort_text = "LENGTH(l.line_text) DESC"
    elif sort is lines_sort_options.movie_title:
        sort_text = "m.title ASC"
    elif sort is lines_sort_options.character_name:
        sort_text is "c.name ASC"

    with engine.begin() as conn:
        lines = conn.execute(
            sqlalchemy.text(
            f'''
            SELECT l.line_id, c.name, m.title, l.line_sort, l.line_text FROM lines AS l
            JOIN movies AS m ON l.movie_id = m.movie_id
            JOIN characters as c on c.character_id = l.character_id
            WHERE l.line_text LIKE '%{text}%'
            ORDER BY {sort_text}
            '''
            )
        )
        for line in lines:
            json.append(
                {
                "line_id": line.line_id,
                "character": line.name,
                "movie": line.title,
                "line_sort": line.line_sort, 
                "line_text": line.line_text
                }
            )
    return json[offset:limit+offset]