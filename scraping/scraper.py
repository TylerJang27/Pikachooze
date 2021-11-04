#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 01:50:35 2021

@author: Pikachooze
"""
from os import P_PGID
import requests
import numpy as np
import pandas as pd
import re


from bs4 import BeautifulSoup
from sqlalchemy.sql.sqltypes import MatchType
# Database reference, only missing the Move-Pokemon connecting table (assume just a (poke_id, move_id)) relation.
# https://dbdiagram.io/d/6158de67825b5b01461dfd3f

# %% Constants
POKEAPI_HOSTNAME = "https://pokeapi.co/api/v2/"
POKEIMAGES_URL = "https://raw.githubusercontent.com/HybridShivam/Pokemon/master/assets/images/{:}"
SPECIES_LIST_EXT = "pokemon-species"
POKEMON_EXT = "pokemon/{:}"
MOVES = "move/{:}"
TYPES = "type"
POKEDEX = "pokedex/{:}"
GENERATION = "generation/{:}"
TRAINER_HOSTNAME = "https://bulbapedia.bulbagarden.net/w/index.php?title={:}&action=edit"
type_dict = {}
df_games = {}
df_moves = {}
df_pokemon = {}
df_stats = {}
df_can_learn = {}
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
diamond_pearl_gym_leaders = ["Roark", "Gardenia", "Maylene", "Crasher Wake", "Fantina", "Byron", "Candice", "Volkner"]
diamond_pearl_elite4 = ["Aaron_(Elite_Four)", "Bertha", "Flint_(Elite_Four)", "Lucian", "Cynthia"]
diamond_pearl_all_elite_trainers = diamond_pearl_gym_leaders + diamond_pearl_elite4
diamond_pearl_all_elite_trainers = diamond_pearl_elite4
gym_leader_url = "https://cdn2.bulbagarden.net/upload/2/2f/{:}"

# %% Helper Methods
def get_limit_and_offset(limit, offset):
    return "?limit={:d}&offset={:d}".format(limit, offset)

def request_to_api(extension):
    response = requests.get(POKEAPI_HOSTNAME + extension)
    if response.status_code == 200:
        return response.json()
    else:
        print("ERROR: STATUS CODE: {:}".format(response.status_code))

def html_request_to_api(trainer_name):
    response = requests.get(TRAINER_HOSTNAME.format(trainer_name))
    if response.status_code == 200:
        return response
    else:
        print("ERROR: STATUS CODE: {:}".format(response.status_code))

def get_types():
    count = 1
    typelist = []
    res = request_to_api(TYPES)
    for type in res["results"][:-2]:
        type_dict[type["name"]] = count
        typelist.append([count, type["name"]])
        count += 1
    print(type_dict)
    print(typelist)

    df_type = pd.DataFrame(typelist)
    df_type = df_type.to_csv('db/data/Types.csv', index = False, header = False)
    print(df_type)

    #print(type_dict)
   # print(typelist)

def get_types_csv():
    df = pd.read_csv("db/data/Types.csv", header=None)
    for ind in df.index:
        id = df.iloc[ind,0]
        name = df.iloc[ind,1]
        type_dict[name] = id
    #print(type_dict)

def get_generation():
    generation_list = [[4]] #expand to include all gens if needed
    df_generation = pd.DataFrame(generation_list)
    df_generation = df_generation.to_csv('db/data/Generations.csv', index = False, header = False)

    
def get_games():   
    res = request_to_api(GENERATION.format("4")) #expand this to include all generations if needed
    game_list =[]
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

def get_games_csv():
    df = pd.read_csv("db/data/Games.csv", header=None)
    for ind in df.index:
        game_id = df.iloc[ind,0]
        game_name = df.iloc[ind,1]
        generation = df.iloc[ind,2]
        df_games[game_name] = game_id
    #print(df_games)
    
def get_pokemon():
    res = request_to_api(POKEDEX.format("6"))
    for pokemon in res["pokemon_entries"]:
        name = pokemon["pokemon_species"]["name"]
    res = request_to_api(POKEDEX.format("6")) #change this, to be the pokedex for multiple generations
    for pokemon in res["pokemon_entries"]:
        #time.sleep(0.25)
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
            can_learn.append([uid, move_id])
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
    
def get_learn_csv():
    df = pd.read_csv("db/data/Learn.csv", header=None)
    for ind in df.index:
        id = df.iloc[ind,0]
        move_id = df.iloc[ind,1]
        df_can_learn[id] = [move_id]
    #print(df_can_learn)
        
def fill_moves(move_id):
    #time.sleep(0.25)
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
    moves[move_id] = [move_name,target, mtype, power, acc, crit_rate, damage_class, min_hits, max_hits, priority,pp]
    #print(moves[move_id])

def get_moves():
    for key in moves:
        m = [key]
        m += moves[key]
        move_list.append(m)
    df_moves = pd.DataFrame(move_list)
    df_moves = df_moves.convert_dtypes()
    df_moves = df_moves.to_csv('db/data/Moves.csv', index = False, header = False)

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
        df_moves[move_name] = [move_id,target, mtype, power, acc, crit_rate, damage_class, min_hits, max_hits, priority,pp]
    #print(df_moves)

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
    
def get_diamond_pearl_gym_leaders():
    for leader in diamond_pearl_all_elite_trainers:
        page = html_request_to_api(leader)
        soup = BeautifulSoup(page.content, "html.parser")
        text = soup.find("textarea", {"id": "wpTextbox1"})
        pokemon_game_data_list = text.string.split("===Pokémon===")[1].split("===={{game|")[1:]
        pokemon_scenarios = {}

        for game_data in pokemon_game_data_list:
            game_name_temp = game_data[:20]
            if not ("Diamond" in game_name_temp or "Pearl" in game_name_temp or "Platinum" in game_name_temp):
                continue

            if "=====" in game_data:
                #Platinum, before and after
                game_scenarios = game_data.split("\n=====")[1:]
                for game_scenario_data in game_scenarios:
                    if "Given away" in game_scenario_data:
                        break
                    if "Multi Battle" in game_scenario_data:
                        continue
                    scenario = game_scenario_data.split("=====")[0].replace("[", "").replace("]", "")
                    pokemon_scenarios[scenario] = game_scenario_data
                
            else:
                pokemon_scenarios[""] = game_data
                pokemon_data = game_data.split("{{Pokémon/4")

        for scenario in pokemon_scenarios:
            game_data = pokemon_scenarios[scenario]
            pokemon_data = game_data.split("{{Pokémon/4")

            trainer_section = pokemon_data[0]
            poke_trainer_name_regex = re.compile("\|name.*\n")
            poke_trainer_name = poke_trainer_name_regex.findall(trainer_section)
            poke_trainer_name = poke_trainer_name[0]
            poke_trainer_name = poke_trainer_name.split("=")[1]
            print(pokemon_scenarios.keys())
            poke_trainer_name = poke_trainer_name.strip() + (" " + scenario if len(scenario) > 0 and "{" not in scenario else "")
            print(poke_trainer_name)

            poke_sprite = re.compile("\|sprite.*\n")
            pic_url = poke_sprite.findall(trainer_section)
            pic_url = pic_url[0]
            pic_url = pic_url.split("=")[1]
            pic_url = pic_url.strip()
            pic_url = pic_url.replace(" ", "_")
            pic_url = gym_leader_url.format(pic_url)
            print(pic_url)

            game_name_regex = re.compile("\|game.*\n")
            game_name = game_name_regex.findall(trainer_section)
            game_name = game_name[0]
            game_name = game_name.split("=")[1]
            game_name = game_name.strip()
            print(game_name)

            location_name_regex = re.compile("\|locationname.*\n")
            location_name = location_name_regex.findall(trainer_section)
            if len(location_name) == 0:
                location_name_regex = re.compile("\|location.*\n")
                location_name = location_name_regex.findall(trainer_section)
            
            location_name = location_name[0]
            location_name = location_name.split("=")[1]
            location_name = location_name.strip()
            print(location_name)
            if location_name not in locations:
                locations[location_name] = len(locations)
                #TODO populate locations.csv
            location_id = locations[location_name]
            if game_name == "DP":
                game_ids = [df_games["diamond"],df_games["pearl"]]
            elif game_name == "Pt":
                game_ids = [df_games["platinum"]]
            else:
                print("NOT A GAME WE KNOW HOW TO PARSE")
                game_ids = []
            trainer_ids = []
            for game_id in game_ids:
                generation_id = 4
                trainer_id = len(trainer_list)
                trainer_ids.append(trainer_id)
                trainer_list.append([trainer_id,False,poke_trainer_name, pic_url,game_id,generation_id,location_id,None])

            for pokemon_section in pokemon_data[1:]:
                poke_name_regex = re.compile("\|pokemon.*\n")
                poke_name = poke_name_regex.findall(pokemon_section)
                poke_name = poke_name[0]
                poke_name = poke_name.split("=")[1]
                poke_name = poke_name.strip()
                if poke_name not in df_pokemon:
                    print("MISSING POKEMON FOR ", poke_name)
                    continue
                poke_id = df_pokemon[poke_name][0]
                # print(poke_name, poke_id)
                
                poke_level_regex = re.compile("\|level.*[\|\n]")
                poke_level = poke_level_regex.findall(pokemon_section)
                poke_level = poke_level[0]
                poke_level_temp = poke_level.split("=")[1]
                poke_level_temp = poke_level_temp.split("|")[0]
                poke_level_temp = poke_level_temp.strip()
                try:
                    poke_level = int(poke_level_temp)
                except:
                    poke_level_regex = re.compile("[0-9]+")
                    poke_level = poke_level_regex.findall(poke_level)
                    poke_level = poke_level[0]
                # print(poke_level)

                poke_gender_regex = re.compile("\|gender.*[\|\n]")
                poke_gender = poke_gender_regex.findall(pokemon_section)
                if len(poke_gender) > 0: 
                    poke_gender = poke_gender[0]
                    poke_gender = poke_gender.split("=")[1]
                    poke_gender = poke_gender.strip()
                else:
                    poke_gender = None
                # print(poke_gender)

                move_regex = re.compile("\|move[0-9]=[\w\s]+\|") #replace "\|" with "\n" and you can get the whole line
                my_moves_strings = move_regex.findall(pokemon_section)
                my_moves_list = []
                for move in my_moves_strings:
                    move_name = sanitize_move(move.replace("|","").strip().split("=")[1])
                    #move_id = movename_to_id[move_name]
                    move_id = df_moves[move_name][0]
                    # print(move_name, move_id)
                    my_moves_list.append(move_id)
                my_moves1 = my_moves_list[0] if len(my_moves_list) > 0 else None
                my_moves2 = my_moves_list[1] if len(my_moves_list) > 1 else None
                my_moves3 = my_moves_list[2] if len(my_moves_list) > 2 else None
                my_moves4 = my_moves_list[3] if len(my_moves_list) > 3 else None

                for trainer_id in trainer_ids:
                    trainer_pokemon_list.append([len(trainer_pokemon_list), trainer_id, poke_id, poke_name, poke_gender, poke_level, True, my_moves1,my_moves2,my_moves3,my_moves4])
                if "{{Party/Footer}}" in pokemon_section:
                    print("REACHED THE END")
                    break
    for trainer in trainer_list:
        print(trainer)
    for trainer_pokemon in trainer_pokemon_list:
        print(trainer_pokemon)

"""
    trainer_id = Column(Integer, primary_key = True) # trainer_id_seq, server_default=trainer_id_seq.next_value(), 
    is_user = Column(Boolean)
    name = Column(String(20))
    pic = Column(String)
    game_id = Column(Integer, ForeignKey('game.game_id'))
    generation_id = Column(Integer, ForeignKey('generation.generation'), default=4)
    location_id = Column(Integer, ForeignKey('location.location_id'), nullable=True)
    added_by_id = Column(Integer, ForeignKey('users.uid'), nullable=True)
                """

"""
    tp_id = Column(Integer, primary_key = True)
    trainer_id = Column(Integer, ForeignKey('trainer.trainer_id')) # TODO: ADD INDEXES
    poke_id = Column(Integer, ForeignKey('pokemon.poke_id'))
    nickname = Column(String(25))
    gender = Column(Enum(GenderClass), default=0) # TODO: MAKE ENUM
    level = Column(Integer, default=50)
    inParty = Column(Boolean, default=False)
    move1_id = Column(Integer, ForeignKey('move.move_id'), nullable=True)
    move2_id = Column(Integer, ForeignKey('move.move_id'), nullable=True)
    move3_id = Column(Integer, ForeignKey('move.move_id'), nullable=True)
    move4_id = Column(Integer, ForeignKey('move.move_id'), nullable=True)
                """
            #
            # ind = pokemon.split("\n")
            # ind = ind
            # for trait in ind:
                # print(trait)



# %% Scraping Methods
# %% Main
if __name__ == "__main__":
    #get_types()
    #get_generation()
    #get_games()
    #get_pokemon()
    #get_generation()
    #get_games()
    #get_moves()
    get_games_csv()
    get_pokemon_csv()
    get_stats_csv()
    get_learn_csv()
    get_moves_csv()
    get_types_csv()
    get_diamond_pearl_gym_leaders()
