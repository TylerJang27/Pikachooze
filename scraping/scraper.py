#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 01:50:35 2021

@author: Pikachooze
"""
import requests
import numpy as np
import pandas as pd

# Database reference, only missing the Move-Pokemon connecting table (assume just a (poke_id, move_id)) relation.
# https://dbdiagram.io/d/6158de67825b5b01461dfd3f

# %% Constants
POKEAPI_HOSTNAME = "https://pokeapi.co/api/v2/"
SPECIES_LIST_EXT = "pokemon-species"
POKEMON_EXT = "pokemon/{:}"
MOVES = "moves"
TYPES = "type"
POKEDEX = "pokedex/{:}"
GENERATION = "generation/{:}"
type_dict = {}
all_moves = set()
pokemon_list = []
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

def get_piplup():
    res = request_to_api(POKEMON_EXT.format("piplup"))
    moves = res[MOVES]
    for move in moves:
        print(move["move"]["name"])
    #print(res)

def get_types():
    count = 1
    typelist = []
    res = request_to_api(TYPES)
    for type in res["results"][:-2]:
        type_dict[type["name"]] = count
        typelist.append([count, type["name"]])
        count += 1
    #print(type_dict)
   # print(typelist)

    df_type = pd.DataFrame(typelist)
    df_type = df_type.to_csv('db/data/Types.csv', index = False, header = False)
    #print(df_type)

def get_generation():
    generation_list = [[4]]
    df_generation = pd.DataFrame(generation_list)
    df_generation = df_generation.to_csv('db/data/Generations.csv', index = False, header = False)

    
def get_games():   
    res = request_to_api(GENERATION.format("4"))
    game_list =[]
    version_group_list = []
    version_game = []
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
    print(version_game)

    
def get_pokemon():
    res = request_to_api(POKEDEX.format("6"))
    for pokemon in res["pokemon_entries"]:
        name = pokemon["pokemon_species"]["name"]
        pand = pokemon["pokemon_species"]["url"]
        ext = pand.split("https://pokeapi.co/api/v2/pokemon-species/")
        num = ext[1]
        res = request_to_api(POKEMON_EXT.format(num))
        expand = res
        uid = expand["id"]

        for items in expand["moves"]:
            for vers in items["version_group_details"]:
                if vers["version_group"]["name"] == "diamond-pearl" or "platinium":
                    all_moves.add(items["move"]["name"])
        if len(expand["types"]) == 1:
            typelist1 = []
            for type in expand["types"]:
                typelist1.append(type["type"]["name"])
            type1 = typelist1[0]
            type2 = ""
        else:
            typelist = []
            for type in expand["types"]:
                typelist.append(type["type"]["name"])
            type1 = typelist[0]
            type2 = typelist[1]
        pokemon_list.append([uid, name, 4, type1, type2, "pic"])
    #print(pokemon_list)
    print(all_moves)
        
        
        




    



# %% Scraping Methods



# %% Main
if __name__ == "__main__":
    #get_types()
    #get_generation()
    get_games()
    get_pokemon()
