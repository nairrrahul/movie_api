from fastapi import APIRouter
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime


# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]


router = APIRouter()


@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """

    # TODO: Remove the following two lines. This is just a placeholder to show
    # how you could implement persistent storage.

    conv_lines = conversation.lines
    last_conv_id = int(db.convs_log[-1]['conversation_id'])
    last_line_id = int(db.lines_log[-1]['line_id'])
    temp = 1
    for line in conv_lines:
        db.lines_log.append({"line_id": last_line_id + 1, "character_id": line.character_id, "movie_id": movie_id, "line_sort": temp, "line_text": line.line_text})
        last_line_id += 1
        temp += 1
    db.convs_log.append({"conversation_id": last_conv_id + 1, "character1_id": conversation.character_1_id, "character2_id": conversation.character_2_id, "movie_id": movie_id})
    db.upload_new_conv()
    db.upload_new_line()
    db.update_convs()
    db.update_lines()