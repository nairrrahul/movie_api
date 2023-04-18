from fastapi import APIRouter, HTTPException
from fastapi.params import Query
from enum import Enum
from src import database as db
import copy

router = APIRouter()

@router.get("/lines/{conversation_id}", tags=["lines"])
def get_conversation_info(conversation_id: int):
    """
    This endpoint returns a conversation by its identifier. For each conversation it returns:
    * `conversation_id`: the internal id of the conversation.
    * `movie`: the name of the movie the conversation occurred in
    * `lines`: the lines of the conversation.

    Each line is represented by a dictionary with the following keys:
    * `character`: the name of the character who said the line.
    * `character_id`: the id of the character
    * `gender`: the gender of the character, `null` if not present
    * `line_text`: the text of the line

    """
    json = []
    conv = None
    for line in db.lines:
        if line["conversation_id"] == str(conversation_id):
            temp = copy.deepcopy(line)
            json.append({
                "character": db.char_id_to_name[temp["character_id"]],
                "character_id": int(temp["character_id"]),
                "gender": db.char_id_to_gender[temp["character_id"]] or None,
                "line_text": temp["line_text"]
            })
    for conversation in db.conversations:
        if conversation["conversation_id"] == str(conversation_id):
            conv = {
                "conversation_id": conversation_id,
                "movie": db.movie_id_to_title[conversation["movie_id"]],
                "lines": json
            }
            break
    
    if len(json) == 0 or conv is None:
        raise HTTPException(status_code=404, detail="conversation not found.")
    else:
        return conv


@router.get("/conversations/{movie_id}", tags=["conversations"])
def list_movie_conversations(movie_id: int):
    """
    This endpoint returns the conversations present in a movie. For each movie it returns:
    * `movie_id`: the internal id of the movie.
    * `movie`: the name of the movie the conversations occurred in
    * `conversations`: the lines of the conversation.

    Each conversation is represented by a dictionary with the following keys:
    * `conversation_id`: the internal id of the conversation
    * `first_character`: the name of the first character speaking
    * `second_character`: the name of the second character speaking
    * `num_lines`: the number of lines in the conversation

    """
    temp = []
    for conv in db.conversations:
        if conv["movie_id"] == str(movie_id):
            temp.append({
                "conversation_id": int(conv["conversation_id"]),
                "first_character": db.char_id_to_name[conv["character1_id"]],
                "second_character": db.char_id_to_name[conv["character2_id"]],
                "num_lines": db.conv_id_lines[conv["conversation_id"]]
            })

    if len(temp) == 0:
        raise HTTPException(status_code=404, detail="conversation not found.")
    else:
        return {
            "movie_id": movie_id,
            "movie": db.movie_id_to_title[str(movie_id)],
            "conversations": temp
        }

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
    json = copy.deepcopy(db.lines)
    for line in json:
        line["line_id"] = int(line["line_id"])
        line["line_sort"] = int(line["line_sort"])
        line["character"] = db.char_id_to_name[line["character_id"]]
        line["movie"] = db.movie_id_to_title[line["movie_id"]]
        line.pop("movie_id")
        line.pop("character_id")
        line.pop("conversation_id")
    if sort == lines_sort_options.movie_title:
        json.sort(key=lambda x: x["movie"])
    elif sort == lines_sort_options.character_name:
        json.sort(key=lambda x: x["character"])
    else:
        json.sort(key=lambda x: len(x["line_text"]), reverse=True)
    return [j for j in json if text.lower() in j["line_text"].lower()][offset: offset+limit]