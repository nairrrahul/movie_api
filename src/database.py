import csv
import pandas as pd

# TODO: You will want to replace all of the code below. It is just to show you
# an example of reading the CSV files where you will get the data to complete
# the assignment.

print("reading movies")

with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    movies = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    ]

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    characters = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    ]

with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
    conversations = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    ]

with open("lines.csv", mode="r", encoding="utf8") as csv_file:
    lines = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    ]

char_final = pd.read_csv("characters.csv")
lines_final = pd.read_csv("lines.csv")
movie_final = pd.read_csv("movies.csv")

get_char_by_id = \
char_final.join(movie_final.loc[:,['movie_id', 'title']], on='movie_id', how='left', lsuffix='_left', rsuffix='_right').drop(columns=['movie_id_right', 'movie_id_left', 'age'])
get_char_by_id = list(get_char_by_id.T.to_dict().values())

get_chars_list = lines_final.groupby(by=['character_id', 'movie_id']) \
                    .count() \
                    .reset_index()[['character_id','movie_id','line_id']] \
                    .rename(columns={'line_id':'number_of_lines'}) \
                    .join(movie_final.loc[:,['movie_id', 'title']], on='movie_id', how='left', lsuffix='_left', rsuffix='_right') \
                    .join(char_final.loc[:,['character_id', 'name']], on='character_id', how='left', lsuffix='_left', rsuffix='_right') \
                    .rename(columns={'character_id_left':'character_id'})[['character_id','name', 'title', 'number_of_lines']].dropna()

get_chars_list = list(get_chars_list.T.to_dict().values())
print(get_chars_list)



