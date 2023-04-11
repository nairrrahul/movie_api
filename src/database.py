import csv

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

char_id_to_name = {char['character_id']: char['name'] for char in characters}
char_id_to_gender = {char['character_id']: char['gender'] for char in characters}
movie_id_to_title = {mv['movie_id']: mv['title'] for mv in movies}
char_id_to_movie_name = {char['character_id']: movie_id_to_title[char['movie_id']] for char in characters}
char_id_to_movie_id = {char['character_id']: char['movie_id'] for char in characters}

def conv_id_to_lines(lns):
    dct = {}
    for line in lns:
        if line["conversation_id"] not in dct:
            dct[line["conversation_id"]] = 1
        else:
            dct[line["conversation_id"]] += 1
    return dct

def convert_pairs(convs_list):
    p_dict = {}
    lns_dct = conv_id_to_lines(lines)
    pairs = []
    for conv in convs_list:
        key = str(conv['character1_id'])+"-"+str(conv['character2_id'])
        if key not in p_dict:
            p_dict[key] = lns_dct[conv["conversation_id"]]
        else:
            p_dict[key] += lns_dct[conv["conversation_id"]]
    for k in p_dict:
        c1id = k.split("-")[0]
        c2id = k.split("-")[1]
        pairs.append({
            "c1id": c1id,
            "c1name": char_id_to_name[c1id],
            "c2id": c2id,
            "c2name": char_id_to_name[c2id],
            "c2gender": char_id_to_gender[c2id],
            "c1gender": char_id_to_gender[c1id],
            "nlines": p_dict[k]
        })
    return pairs

def query_for_chars(pairs_list, char_number, char_id):
    if char_number == 0:
        #id is for 1st character
        return [
            {
                "character_id": int(p["c2id"]),
                "character": p["c2name"],
                "gender": p["c2gender"] if len(p["c2gender"]) > 0 else None,
                "number_of_lines_together": int(p["nlines"])
            } for p in pairs_list if p["c1id"] == char_id
        ]
    else:
        #id is for 2nd character
        return [
            {
                "character_id": int(p["c1id"]),
                "character": p["c1name"],
                "gender": p["c1gender"] if len(p["c1gender"]) > 0 else None,
                "number_of_lines_together": int(p["nlines"])
            } for p in pairs_list if p["c2id"] == char_id
        ]

def lines_per_c_id(lns):
    dct = {}
    for line in lns:
        if line["character_id"] not in dct:
            dct[line["character_id"]] = 1
        else:
            dct[line["character_id"]] += 1
    return dct

char_convs_pairs = convert_pairs(conversations)
characters_to_lines = lines_per_c_id(lines)