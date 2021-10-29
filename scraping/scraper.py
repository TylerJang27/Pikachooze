#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 01:50:35 2021

@author: Pikachooze
"""
import requests
import numpy as np
import pandas as pd
import time

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
TRAINER_HOSTNAME = "https://bulbapedia.bulbagarden.net/w/index.php?title="
type_dict = {}
all_moves = set()
pokemon_list = []
moves = {}
can_learn = []
pokemon_list = []
pokemon_stats = []
version_game = []
trainers = ["Roark", "Gardenia", "Maylene", "Crasher Wake", "Fantina", "Byron", "Candice", "Volkner", "Aaron", "Bertha", "Flint", "Lucian", "Cynthia"]
# %% Global Variables
move_list = [] #could be a map, or use enumerate when you need to, in order to preserve foreign keys

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
    return requests.get(TRAINER_HOSTNAME + trainer_name + "&action=edit")
    # if response1.status_code == 200:
    #     return response1.json()
    # else:
    #     print("ERROR: STATUS CODE: {:}".format(response1.status_code))

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

    df_type = pd.DataFrame(typelist)
    df_type = df_type.to_csv('db/data/Types.csv', index = False, header = False)
   # print(df_type)

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

    
def get_pokemon():
    res = request_to_api(POKEDEX.format("6"))
    for pokemon in res["pokemon_entries"]:
        name = pokemon["pokemon_species"]["name"]
    res = request_to_api(POKEDEX.format("6")) #change this, to be the pokedex for multiple generations
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

from bs4 import BeautifulSoup

def get_trainers():
    for trainer in trainers:
        page = html_request_to_api(trainer)
        soup = BeautifulSoup(page.content, "html.parser")
        print(soup.head.title)






# %% Scraping Methods
# %% Main
if __name__ == "__main__":
    get_types()
    #get_types()
    #get_generation()
    #get_games()
    #get_pokemon()
    #get_generation()
    #get_games()
    #get_pokemon()
    #get_moves()
    get_trainers()
