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
diamond_pearl_gym_leaders = ["Roark", "Gardenia", "Maylene", "Crasher Wake", "Fantina", "Byron", "Candice", "Volkner"]
diamond_pearl_elite4 = ["Aaron", "Bertha", "Flint", "Lucian", "Cynthia"]

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
    print(type_dict)

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
        game_name = df.iloc[ind,1]
        generation = df.iloc[ind,2]
        df_games[game_name] = generation
    print(df_games)
    
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
        df_pokemon[id] = [name, generation, type_1, type_2, pic]
    print(df_pokemon)

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
    print(df_stats)
    
def get_learn_csv():
    df = pd.read_csv("db/data/Learn.csv", header=None)
    for ind in df.index:
        id = df.iloc[ind,0]
        move_id = df.iloc[ind,1]
        df_can_learn[id] = [move_id]
    print(df_can_learn)
        
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
        move_name = df.iloc[ind,0]
        target = df.iloc[ind,1]
        mtype = df.iloc[ind,2]
        power = df.iloc[ind,3]
        acc = df.iloc[ind,4]
        crit_rate = df.iloc[ind,5]
        damage_class = df.iloc[ind,6]
        min_hits = df.iloc[ind,7]
        max_hits = df.iloc[ind,8]
        priority = df.iloc[ind,9]
        pp = df.iloc[ind,10]
        df_moves[move_name] = [move_name,target, mtype, power, acc, crit_rate, damage_class, min_hits, max_hits, priority,pp]
    print(df_moves)
    
def get_diamond_pearl_gym_leaders():
    pokemon = []
    for leader in diamond_pearl_gym_leaders:
        page = html_request_to_api(leader)
        soup = BeautifulSoup(page.content, "html.parser")
        text = soup.find("textarea", {"id": "wpTextbox1"})
        pokemon_data = text.string.split("===Pokémon===")[1].split("===={{game|")[1].split("{{Pokémon/4") # TODO: add loop to get platinum as well
        # TODO: ADD LOOP SOMWHERE TO GET BEFORE/AFTER IF APPLICABLE
        
        unnecessary_counter = 0
        for pokemon_section in pokemon_data[1:]:
            unnecessary_counter += 1
            print(unnecessary_counter)
            poke_name_regex = re.compile("\|pokemon.*\n")
            my_name = poke_name_regex.findall(pokemon_section)
            print(my_name)

            move_regex = re.compile("\|move[0-9]=[\w\s]+\|") #replace "\|" with "\n" and you can get the whole line
            my_moves = move_regex.findall(pokemon_section)
            for move in my_moves:
                move_name = move.replace("|","").strip().split("=")[1]
                move_id = movename_to_id[move_name]
                print(move_name, move_id)

            # ind = pokemon.split("\n")
            # ind = ind
            # for trait in ind:
                # print(trait)
        break




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
    #get_diamond_pearl_gym_leaders()
    get_games_csv()
    get_pokemon_csv()
    get_stats_csv()
    get_learn_csv()
    get_moves_csv()
    get_types_csv()
