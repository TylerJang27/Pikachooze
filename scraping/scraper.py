#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 01:50:35 2021

@author: Pikachooze
"""
from os import P_PGID
import requests
import pandas as pd
import re
import time

from bs4 import BeautifulSoup
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import MatchType
import shutil
# Database reference, only missing the Move-Pokemon connecting table (assume just a (poke_id, move_id)) relation.
# https://dbdiagram.io/d/6158de67825b5b01461dfd3f

# %% Constants
POKEAPI_HOSTNAME = "https://pokeapi.co/api/v2/{:}"
POKEIMAGES_URL = "https://raw.githubusercontent.com/HybridShivam/Pokemon/master/assets/images/{:}"
SPECIES_LIST_EXT = "pokemon-species/{:}"
POKEMON_EXT = "pokemon/{:}"
MOVES = "move/{:}"
TYPES = "type"
POKEDEX = "pokedex/{:}"
GENERATION = "generation/{:}"
TRAINER_HOSTNAME = "https://bulbapedia.bulbagarden.net/w/index.php?title={:}&action=edit"
GYM_LEADER_HOSTNAME = "https://pokemon.fandom.com/wiki/Gym_Leader#{:}"
ELITE_FOUR_HOSTNAME = "https://pokemon.fandom.com/wiki/Elite_Four#{:}"
ASSETS_FILEPATH = "app/static/assets/img/"

# dictionaries for preserved lookups
type_dict = {}
df_games = {}
df_moves = {}
df_pokemon = {}
df_stats = {}
df_can_learn = {}
leader_urls = {}

# collections for populating
all_moves = set()
pokemon_list = []
moves = {}
move_list = []
movename_to_id = {}
can_learn = []
pokemon_list = []
pokemon_stats = []
version_game = []
locations = {}
trainer_list = []
trainer_pokemon_list = []
evolutions = []

# trainers to scrape
diamond_pearl_gym_leaders = ["Roark", "Gardenia", "Maylene", "Crasher Wake", "Fantina", "Byron", "Candice", "Volkner"]
diamond_pearl_elite4 = ["Aaron_(Elite_Four)", "Bertha", "Flint_(Elite_Four)", "Lucian", "Cynthia"]
diamond_pearl_all_elite_trainers = diamond_pearl_gym_leaders + diamond_pearl_elite4

# %% Helper Methods
# deal with misformated names in source
def sanitize_move(move_name):
    if move_name == "Hi Jump Kick":
        return "High Jump Kick"
    if move_name == "Faint Attack":
        return "Feint Attack"
    if " " in move_name:
        return move_name
    for i, letter in enumerate(move_name):
        if letter.isupper() and i != 0:
            return move_name[:i] + " " + move_name[i:]
    return move_name

def sanitize_poke(poke_name):
    if poke_name == "Mr. Mime":
        return "Mr Mime"
    return poke_name
# extract a field from the trainer text
def extract_field(field_name, source_text, replace_spaces=False, manual_regex="\|{:}.*[\|\n]"):
    regex_pattern = re.compile(manual_regex.format(field_name))
    matching_fields = regex_pattern.findall(source_text)
    matching_fields = matching_fields[0]
    matching_text = matching_fields.split("=")[1].strip()
    if replace_spaces:
        matching_text = matching_text.replace(" ", "_")
    return matching_text

# get the extension for large queries
def get_limit_and_offset(limit, offset):
    return "?limit={:d}&offset={:d}".format(limit, offset)

# request to pokeapi for pokemon data
def request_to_api(extension):
    response = requests.get(POKEAPI_HOSTNAME.format(extension))
    if response.status_code == 200:
        return response.json()
    else:
        print("ERROR: STATUS CODE: {:}".format(response.status_code))

# request to bulbapedia for trainer data
def html_request_to_api(trainer_name):
    response = requests.get(TRAINER_HOSTNAME.format(trainer_name))
    if response.status_code == 200:
        return response
    else:
        print("ERROR: STATUS CODE: {:}".format(response.status_code))

# request to pokemon fandom for gym leader images
def html_request_to_fandom_api(region, leader=False):
    if leader:
        response = requests.get(ELITE_FOUR_HOSTNAME.format(region))
    else:
        response = requests.get(GYM_LEADER_HOSTNAME.format(region))
    if response.status_code == 200:
        return response
    else:
        print("ERROR: STATUS CODE: {:}".format(response.status_code))

# download a gym leader image
# based on code from https://towardsdatascience.com/how-to-download-an-image-using-python-38a75cfa21c
def download_image(image_url, filepath):
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(image_url, stream = True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
        
        # Open a local file with wb ( write binary ) permission.
        with open(filepath,'wb') as f:
            shutil.copyfileobj(r.raw, f)

# %% Scraping Methods
# populates Types.csv with [type_id, type_name]
def get_types():
    count = 1
    typelist = []
    res = request_to_api(TYPES)
    for type in res["results"][:-2]:
        type_dict[type["name"]] = count
        typelist.append([count, type["name"]])
        count += 1
    # print(type_dict)
    # print(typelist)

    df_type = pd.DataFrame(typelist)
    df_type = df_type.to_csv('db/data/Types.csv', index = False, header = False)
    # print(df_type)

# reads in from Types.csv to populate type_dict
def get_types_csv():
    df = pd.read_csv("db/data/Types.csv", header=None)
    for ind in df.index:
        id = df.iloc[ind,0]
        name = df.iloc[ind,1]
        type_dict[name] = id
    #print(type_dict)

# writes hard-coded generation to Generations.csv with [gen_number]
def get_generation():
    generation_list = [[4]] #expand to include all gens if needed
    df_generation = pd.DataFrame(generation_list)
    df_generation = df_generation.to_csv('db/data/Generations.csv', index = False, header = False)

# populates Games.csv with [game_id, game_name, gen_number]
def get_games():   
    res = request_to_api(GENERATION.format("4")) #expand this to include all generations if needed
    version_group_list = []
 
    for version_group in res["version_groups"][:-1]:
        vg = version_group["url"]
        ext = vg.split("https://pokeapi.co/api/v2/")
        version_group_list.append(ext[1])
    count = 1
    for version in version_group_list:
        res = request_to_api(version)
        for game in res["versions"]:
            game_name = game["name"]
            version_game.append([count,game_name,4])
            count +=1
    df_games = pd.DataFrame(version_game)
    df_games = df_games.to_csv('db/data/Games.csv', index = False, header = False)
    #print(version_game)

# reads in from Games.csv to populate df_games
def get_games_csv():
    df = pd.read_csv("db/data/Games.csv", header=None)
    for ind in df.index:
        game_id = df.iloc[ind,0]
        game_name = df.iloc[ind,1]
        generation = df.iloc[ind,2]
        df_games[game_name] = game_id
    #print(df_games)

# populates Pokemon.csv with [poke_id, name, generation_id, type1_id, type2_id, pic]
# populates Stats.csv with [poke_id, hp, attack_stat, defense_stat, special_attack_stat, special_defense_stat, speed]
# populates Learn.csv with [poke_id, move_id]
def get_pokemon():
    res = request_to_api(POKEDEX.format("1")) #change this, to be the pokedex for multiple generations
    for pokemon in res["pokemon_entries"]:
        time.sleep(0.25)
        name = pokemon["pokemon_species"]["name"]
        name = name.replace("-", " ")
        name = name.title()
        pand = pokemon["pokemon_species"]["url"]
        ext = pand.split("https://pokeapi.co/api/v2/pokemon-species/")
        num = ext[1]
        res = request_to_api(POKEMON_EXT.format(num))
        expand = res
        uid = expand["id"]
        lstat = []
        if len(str(uid)) == 1:
            pic = POKEIMAGES_URL.format("00" + str(uid)+".png")
        elif len(str(uid))==2:
             pic = POKEIMAGES_URL.format("0"+ str(uid)+".png")
        else:
             pic = POKEIMAGES_URL.format(str(uid)+".png")
        for move in expand["moves"]:
            move_url = ""
            move_id = 0
            for vers in move["version_group_details"]:
                if vers["version_group"]["name"] == "diamond-pearl" or "platinium":
                    move_url = move["move"]["url"]
                    move_id = move_url.split("https://pokeapi.co/api/v2/move/")[1].replace("/","")    
            can_learn.append([uid, move_id]) # LATER: CONSIDER DIFFERENT GENERATION CHANGES
            if not move_id in moves:
                fill_moves(move_id)   
        lstat.append(uid)
        for stat in expand["stats"]:
            lstat.append(stat["base_stat"])
        pokemon_stats.append(lstat)
        type = expand["types"]
        type1 =type[0]["type"]["name"]
        type1 = type_dict.get(type1)
        type2 =""
        if len(expand["types"]) > 1:
           type2 =type[1]["type"]["name"]
           type2 = type_dict.get(type2)
        pokemon_list.append([uid, name, 4, type1, type2, pic])
    
    df_pokemon = pd.DataFrame(pokemon_list)
    df_pokemon = df_pokemon.to_csv('db/data/Pokemon.csv', index = False, header = False)
   
    df_stats = pd.DataFrame(pokemon_stats)
    df_stats = df_stats.to_csv('db/data/Stats.csv', index = False, header = False)

    df_can_learn = pd.DataFrame(can_learn)
    df_can_learn = df_can_learn.to_csv('db/data/Learn.csv', index = False, header = False)

# reads in from Pokemon.csv to populate df_pokemon
def get_pokemon_csv():
    df = pd.read_csv("db/data/Pokemon.csv", header=None)
    for ind in df.index:
        id = df.iloc[ind,0]
        name = df.iloc[ind,1]
        generation = df.iloc[ind,2]
        type_1 = df.iloc[ind,3]
        type_2 = df.iloc[ind,4]
        pic = df.iloc[ind,5]
        df_pokemon[name] = [id, generation, type_1, type_2, pic]
    #print(df_pokemon)

# populates Evolution.csv with [poke1_id, poke2_id]
def get_evolutions():
    for pokemon in df_pokemon:
        res = request_to_api(SPECIES_LIST_EXT.format(pokemon.lower().replace(" ", "-")))
        prev = res["evolves_from_species"]
        post = df_pokemon[pokemon][0]
        if prev != None:
            pand = res["evolves_from_species"]["url"]
            ext = pand.split("https://pokeapi.co/api/v2/pokemon-species/")
            prev = ext[1].replace("/","")
           # print([prev,post])
            evolutions.append([prev, post])
    #print(evolutions)
    df_evolution = pd.DataFrame(evolutions)
    df_evolution = df_evolution.to_csv('db/data/Evolution.csv', index = False, header = False)
   

# reads in from Stats.csv to populate df_stats
def get_stats_csv():
    df = pd.read_csv("db/data/Stats.csv", header=None)
    for ind in df.index:
        id = df.iloc[ind,0]
        hp = df.iloc[ind,1]
        Attack = df.iloc[ind,2]
        Defense = df.iloc[ind,3]
        SP_attack = df.iloc[ind,4]
        SP_defense = df.iloc[ind,5]
        speed = df.iloc[ind,6]
        df_stats[id] = [hp, Attack, Defense, SP_attack, SP_defense, speed]
    #print(df_stats)

# reads in from Learn.csv to populate df_can_learn
def get_learn_csv():
    df = pd.read_csv("db/data/Learn.csv", header=None)
    for ind in df.index:
        id = df.iloc[ind,0]
        move_id = df.iloc[ind,1]
        df_can_learn[id] = [move_id]
    #print(df_can_learn)

# helper method to extract information about moves and add to moves dictionary
def fill_moves(move_id):
    time.sleep(0.25)
    res = request_to_api(MOVES.format(move_id))
    acc = res["accuracy"]
    if not acc is None:
        acc = int(acc)
    move_name = res["name"].replace("-", " ").title()
    power = res["power"]
    if not power is None:
        power = int(power)
    pp = res["pp"]
    priority = res["priority"]
    mtype = type_dict.get(res["type"]["name"])
    max_hits = res["meta"]["max_hits"]
    min_hits = res["meta"]["min_hits"]
    if max_hits is None:
        max_hits = ""
    if min_hits is None:
        min_hits = ""
    crit_rate = res["meta"]["crit_rate"]
    damage_class = res["damage_class"]["name"]
    target = res["target"]["name"].replace("-", "_")
    movename_to_id[move_name] = move_id
    moves[move_id] = [move_name, target, mtype, power, acc, crit_rate, damage_class, min_hits, max_hits, priority, pp]
    #print(moves[move_id])

# populates Moves.csv with [move_id, move_name, target, mtype, power, acc, crit_rate, damage_class, min_hits, max_hits, priority, pp]
def get_moves():
    for key in moves:
        m = [key]
        m += moves[key]
        move_list.append(m)
    df_moves = pd.DataFrame(move_list)
    df_moves = df_moves.convert_dtypes()
    df_moves = df_moves.to_csv('db/data/Moves.csv', index = False, header = False)

# reads in from Moves.csv to df_moves
def get_moves_csv():
    df = pd.read_csv("db/data/Moves.csv", header=None)
    for ind in df.index:
        move_id = df.iloc[ind,0]
        move_name = df.iloc[ind,1]
        target = df.iloc[ind,2]
        mtype = df.iloc[ind,3]
        power = df.iloc[ind,4]
        acc = df.iloc[ind,5]
        crit_rate = df.iloc[ind,6]
        damage_class = df.iloc[ind,7]
        min_hits = df.iloc[ind,8]
        max_hits = df.iloc[ind,9]
        priority = df.iloc[ind,10]
        pp = df.iloc[ind,11]
        df_moves[move_name] = [move_id, target, mtype, power, acc, crit_rate, damage_class, min_hits, max_hits, priority, pp]
    #print(df_moves)

# extracts a trainer image url from a soup
def get_url_for_trainer(trainer_name, soup):
    poke_trainer_name_for_img = trainer_name.split("_")[0].split(" ")[0]
    name_img_regex = re.compile(poke_trainer_name_for_img)
    print(trainer_name, name_img_regex)

    images = soup.find_all("img")
    for image in images:
        try:
            if name_img_regex.match(image['data-image-name']):
                url = image['data-src'].replace("100", "266").replace("82", "266").replace("81", "266")
                return url
                # print(image)
            if poke_trainer_name_for_img in image['data-image-name']:
                url = image['data-src'].replace("100", "266").replace("82", "266").replace("81", "266")
                return url
        except:
            # print("no alt tag")
            continue

# populates Leaders.csv with [trainer_id, is_user, name, pic, game_id, generation_id, location_id, added_by_id]
# populates LeaderPokemon.csv with [tp_id, trainer_id, poke_id, nickname, gender, level, inParty, move1_id, move2_id, move3_id, move4_id]
# populates Locations.csv with [location_id, location_name, is_route, is_gym, game_id]
def get_gym_leaders():
    # iterate through all desired trainers
    res = html_request_to_fandom_api("Sinnoh")
    image_soup = BeautifulSoup(res.content, "html.parser")
    res = html_request_to_fandom_api("Sinnoh", True)
    leader_soup = BeautifulSoup(res.content, "html.parser")

    for leader in diamond_pearl_all_elite_trainers:
        # retrieve trainer data
        page = html_request_to_api(leader)
        soup = BeautifulSoup(page.content, "html.parser")
        text = soup.find("textarea", {"id": "wpTextbox1"})

        # split trainer data by games
        pokemon_game_data_list = text.string.split("===Pokémon===")[1].split("===={{g")[1:]
        # print(leader, len(pokemon_game_data_list))
        pokemon_scenarios = {}

        # parse games for relevant games and their respective scenarios if multiple encounters
        for game_data in pokemon_game_data_list:
            game_name_temp = game_data[:25]
            if not ("Diamond" in game_name_temp or "Pearl" in game_name_temp or "Platinum" in game_name_temp):
                # print("SKIPPING BECAUSE IRRELEVANT GAME")
                continue

            if "=====" in game_data:
                #Platinum, before and after
                game_scenarios = game_data.split("\n=====")[1:]
                for game_scenario_data in game_scenarios:
                    if "Given away" in game_scenario_data:
                        break
                    if "Multi Battle" in game_scenario_data:
                        continue
                    scenario = game_scenario_data.split("=====")[0].replace("[", "").replace("]", "") # LATER: ADD BETTER EDGE CASE HANDLING
                    pokemon_scenarios[scenario] = game_scenario_data
                
            else:
                new_str = ""
                if "" in pokemon_scenarios:
                    new_str = " "
                pokemon_scenarios[new_str] = game_data
                pokemon_data = game_data.split("{{Pokémon/4")

        # iterate through game scenarios
        for scenario in pokemon_scenarios:
            game_data = pokemon_scenarios[scenario]
            scenario = scenario.strip()
            # split to separate trainer information from pokemon information
            pokemon_data = game_data.split("{{Pokémon/4")
            trainer_section = pokemon_data[0]
            
            # extract trainer name
            try:
                poke_trainer_name = extract_field("name", trainer_section)
            except:
                continue
            poke_trainer_name = poke_trainer_name + (" " + scenario if len(scenario) > 0 and "{" not in scenario else "")

            # extract trainer image
            pic_url = get_url_for_trainer(poke_trainer_name, image_soup)
            if pic_url is None:
                pic_url = get_url_for_trainer(poke_trainer_name, leader_soup)
            if pic_url is not None:
                if pic_url in leader_urls:
                    pic_url = leader_urls[pic_url]
                else:
                    new_url = poke_trainer_name.replace(" ", "_") + ".png"
                    leader_urls[pic_url] = new_url
                    download_image(pic_url, ASSETS_FILEPATH + new_url)
                    pic_url = new_url
            print(pic_url)
            # pic_name = extract_field("sprite", trainer_section, True)
            # pic_url = gym_leader_url.format(pic_name)

            # extract trainer game(s)
            game_name = extract_field("game", trainer_section)

            if game_name == "DP":
                game_ids = [df_games["diamond"],df_games["pearl"]]
            elif game_name == "Pt":
                game_ids = [df_games["platinum"]]
            else:
                print("NOT A GAME WE KNOW HOW TO PARSE", game_name)
                game_ids = []
            # print(poke_trainer_name, game_name, game_ids)

            # extract trainer location(s)
            try:
                location_name = extract_field("locationname", trainer_section)
            except:
                location_name = extract_field("location", trainer_section)

            for game_id in game_ids:
                if (location_name, game_id) not in locations:
                    locations[(location_name, game_id)] = len(locations)
            
            # make trainers for each game 
            trainer_ids = []
            for game_id in game_ids:
                print("adding for game_id: ", game_id)
                location_id = locations[(location_name, game_id)]
                trainer_id = len(trainer_list)
                trainer_ids.append(trainer_id)
                trainer_list.append([trainer_id, False, poke_trainer_name, pic_url, game_id, location_id, None])

            # iterate through a trainer's pokemon
            for pokemon_section in pokemon_data[1:]:

                # extract pokemon name
    
                poke_name = sanitize_poke(extract_field("pokemon", pokemon_section))
                # LATER: EXTRACT NICKNAME IF APPLICABLE
                if poke_name not in df_pokemon:
                    print("MISSING POKEMON FOR ", poke_name)
                    # TODO: ACCOUNT FOR MISSING POKEMON
                    continue

                # extract pokemon id
                poke_id = df_pokemon[poke_name][0]
                
                # extract pokemon level (use lowest if multiple)
                poke_level = extract_field("level", pokemon_section, False)
                try:
                    poke_level = int(poke_level)
                except:
                    poke_level_regex = re.compile("[0-9]+") # LATER: ACCOUNT FOR MULTIPLE ENCOUNTERS/LEVELS
                    poke_level = poke_level_regex.findall(poke_level)
                    poke_level = int(poke_level[0])

                try:
                    poke_gender = extract_field("gender", pokemon_section, False).split("|")[0].lower()
                except:
                    poke_gender = None

                # extract moves
                move_regex = re.compile("\|move[0-9]=[\w\s]+\|") #replace "\|" with "\n" and you can get the whole line
                my_moves_strings = move_regex.findall(pokemon_section)
                my_moves_list = []
                for move in my_moves_strings:
                    move_name = sanitize_move(move.replace("|","").strip().split("=")[1])
                    move_id = df_moves[move_name][0]
                    my_moves_list.append(int(move_id))
                my_moves1 = my_moves_list[0] if len(my_moves_list) > 0 else None
                my_moves2 = my_moves_list[1] if len(my_moves_list) > 1 else None
                my_moves3 = my_moves_list[2] if len(my_moves_list) > 2 else None
                my_moves4 = my_moves_list[3] if len(my_moves_list) > 3 else None

                # make trainer_pokemon for each pokemon in each encounter with a particular trainer
                for trainer_id in trainer_ids:
                    trainer_pokemon_list.append([len(trainer_pokemon_list), trainer_id, poke_id, poke_name, poke_gender, poke_level, True, my_moves1, my_moves2, my_moves3, my_moves4])
                if "{{Party/Footer}}" in pokemon_section:
                    # print("REACHED THE END")
                    break
            # end of a particular pokemon
        # end of a particular trainer scenario
    # end of a particular trainer

    # dump results to csv
    trainer_df = pd.DataFrame(trainer_list)
    trainer_df.to_csv('db/data/Leaders.csv', index = False, header = False)

    trainer_pokemon_df = pd.DataFrame(trainer_pokemon_list, dtype=object)
    print(trainer_pokemon_df)
    trainer_pokemon_df.to_csv('db/data/LeaderPokemon.csv', index = False, header = False)

    location_list = [[locations[location], location[0], False, False, location[1]] for location in locations]
    location_df = pd.DataFrame(location_list)
    location_df.to_csv('db/data/Locations.csv', index = False, header = False)

    # for trainer in trainer_list:
    #     print(trainer)
    # for trainer_pokemon in trainer_pokemon_list:
    #     print(trainer_pokemon)
    # for location in locations:
    #     print(location, locations[location])

# %% Main
if __name__ == "__main__":
    # Original parsing data
    #get_types()
    #get_generation()
    #get_games()
    #get_types_csv()
    #get_pokemon()
    #get_evolutions()
    #get_generation()
    #get_games()
    #get_moves()

    # Populate from csvs
    #get_games_csv()
    get_pokemon_csv()
    get_evolutions()
    # get_stats_csv()
    # get_learn_csv()
    # get_moves_csv()
    # get_types_csv()

<<<<<<< HEAD
    # get_gym_leaders()
=======
    get_gym_leaders()
    
>>>>>>> f622ded196590aad9261e2f655654b86e810822b
