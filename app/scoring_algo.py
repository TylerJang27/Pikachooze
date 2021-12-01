import json
import pandas
import math

pokemon_types = {"normal":0, "fire":1, "water":2, "electric":3, "grass":4, "ice":5,
                 "fighting":6, "poison":7, "ground":8, "flying":9, "psychic":10,
                 "bug":11, "rock":12, "ghost":13, "dragon":14, "dark":15, "steel":16, "fairy":17}

#row for attacking type, #column for defending type
damage_array =  [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1/2, 0, 1, 1, 1/2, 1],
                [1, 1/2, 1/2, 1, 2, 2, 1, 1, 1, 1, 1, 2, 1/2, 1, 1/2, 1, 2, 1],
                [1, 2, 1/2, 1, 1/2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1/2, 1, 1, 1],
                [1, 1, 2, 1/2, 1/2, 1, 1, 1, 0, 2, 1, 1, 1, 1, 1/2, 1, 1, 1],
                [1, 1/2, 2, 1, 1/2, 1, 1, 1/2, 2, 1/2, 1, 1/2, 2, 1, 1/2, 1, 1/2, 1],
                [1, 1/2, 1/2, 1, 2, 1/2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, 1/2, 1],
                [2, 1, 1, 1, 1, 2, 1, 1/2, 1, 1/2, 1/2, 1/2, 2, 0, 1, 2, 2, 1/2],
                [1, 1, 1, 1, 2, 1, 1, 1/2, 1/2, 1, 1, 1, 1/2, 1/2, 1, 1, 0, 2],
                [1, 2, 1, 2, 1/2, 1, 1, 2, 1, 0, 1, 1/2, 2, 1, 1, 1, 2, 1],
                [1, 1, 1, 1/2, 2, 1, 2, 1, 1, 1, 1, 2, 1/2, 1, 1, 1, 1/2, 1],
                [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1/2, 1, 1, 1, 1, 0, 1/2, 1],
                [1, 1/2, 1, 1, 2, 1, 1/2, 1/2, 1, 1/2, 2, 1, 1, 1/2, 1, 2, 1/2, 1/2],
                [1, 2, 1, 1, 1, 2, 1/2, 1, 1/2, 2, 1, 2, 1, 1, 1, 1, 1/2, 1],
                [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1/2, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1/2, 0],
                [1, 1, 1, 1, 1, 1, 1/2, 1, 1, 1, 2, 1, 1, 2, 1, 1/2, 1, 1/2],
                [1, 1/2, 1/2, 1/2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1/2, 2],
                [1, 1/2, 1, 1, 1, 1, 2, 1/2, 1, 1, 1, 1, 1, 1, 2, 2, 1/2, 1]]

#my_pkmn = [trainer_pokemon objects]
#opp_pkmn = [trainer_pokemon objects]

#returns a list of (trainer_pokemon object, (score, text)) tuples sorted by score (highest score comes first)
#currently includes all pokemon, can filter for first six pokemon by [0:5]
def score_teams(my_pkmn, opp_pkmn):
  score_list=[]
  for pk_1 in my_pkmn:
    score_list.append((pk_1, score(pk_1, opp_pkmn))) # (pikachu, (37, "Thunderbolt is great!"))
  print(sorted(score_list, key=lambda tup: tup[1][0]))
  return sorted(score_list, key=lambda tup: tup[1][0]) #could break ties through speed

#returns a list of (trainer_pokemon object, (score, text)) tuples sorted by score (highest comes first)
#fulfils a team with LP status
def score_team_6(my_pkmn, opp_pkmn):
  return

#returns a score for a single pokemon against a team of pokemon
def score(one_pkmn, team_pkmn):
  outgoing_dmg = [] #max outgoing damages
  incoming_dmg = [] #max incoming damages
  outgoing = [] #outgoing as a value (20, 25, 34, 50, 100)
  incoming = [] #incoming as a value (20, 25, 34, 50, 100)
  for pk_2 in team_pkmn:
    outgoing_dmg.append(max_damage_adjusted(one_pkmn, pk_2, True))
    incoming_dmg.append(max_damage_adjusted(pk_2, one_pkmn, False))
  for dmg_info in outgoing_dmg:
    dmg = dmg_info[0]*100
    val = 0
    if dmg >= 100:
      val = 100
    elif dmg >= 50:
      val = 50
    elif dmg >= 100/3:
      val = 100/3
    elif dmg >= 25:
      val = 25
    elif dmg >= 20:
      val = 20
    elif dmg >= 100/6:
      val = 100/6
    elif dmg >= 100/7:
      val = 100/7
    elif dmg >= 100/8:
      val = 100/8
    elif dmg >= 100/9:
      val = 100/9
    elif dmg >= 10:
      val = 10
    else:
      val = 0
    outgoing.append((val, dmg_info[1]))

  for dmg_info in incoming_dmg:
    dmg = dmg_info[0]*100
    val = 0
    if dmg >= 100:
      val = 100
    elif dmg >= 50:
      val = 50
    elif dmg >= 100/3:
      val = 100/3
    elif dmg >= 25:
      val = 25
    elif dmg >= 20:
      val = 20
    elif dmg >= 100/6:
      val = 100/6
    elif dmg >= 100/7:
      val = 100/7
    elif dmg >= 100/8:
      val = 100/8
    elif dmg >= 100/9:
      val = 100/9
    elif dmg >= 10:
      val = 10
    else:
      val = 0
    incoming.append((val, dmg_info[1]))
  
  #print(incoming_dmg, outgoing_dmg)
  #print(incoming, outgoing)
  difference = [(a_i[0] - b_i[0], 
                [a_i[1], b_i[1]][0 if a_i > b_i else 1]) 
                for a_i, b_i in zip(outgoing, incoming)]

  max_diff = max(difference, key = lambda i : abs(i[0]))
  move_text = max_diff[1]
  #calculation based on damages here
  #print(sum(difference)/len(difference))
  difference_nums = [k[0] for k in difference]

  return math.floor(sum(difference_nums)/len(difference_nums)), move_text

#calculate the max damage as percent of pokemon health out_pkmn and in_pkmn
def max_damage_adjusted(out_pkmn, in_pkmn, is_attacker):
  level = in_pkmn.level
  hp_IV = 0
  hp_EV = 0
  hp_base = in_pkmn.pokemon.pokemon_base_stats[0].hp
  HP = in_pkmn.custom_hp
  HP = HP if HP is not None else math.floor(0.01 * (2 * hp_base + hp_IV + math.floor(0.25 * hp_EV)) * level) + level + 10
  damage_perc = max_damage_perc(out_pkmn, in_pkmn, is_attacker, HP)
  if damage_perc[0] > 1.0:
    return (1.0, damage_perc[1])
  return damage_perc


#calculate the max damage that can be done by out_pkmn to in_pkmn
def max_damage_perc(out_pkmn, in_pkmn, is_attacker, hp):
  damage_list = []
  moves = [out_pkmn.move1, out_pkmn.move2, out_pkmn.move3, out_pkmn.move4]
  for move in moves:
    if move is not None:
      damage_val = damage_calc(out_pkmn, move, in_pkmn, is_attacker)
      damage_scaled = damage_val / hp
      
      move_text = ""
      if is_attacker:
        if damage_scaled >= 0.2 and damage_scaled < 0.4:
          move_text = "({:}) does high damage to ({:}). Good job!".format(move.move_name, in_pkmn.nickname)
        elif damage_scaled >= 0.4 and damage_scaled < 0.6:
          move_text = "({:}) does very high damage to ({:}). Great job!".format(move.move_name, in_pkmn.nickname)
        elif damage_scaled >= 0.6:
          move_text = "({:}) does massive damage to ({:}). Excellent job!".format(move.move_name, in_pkmn.nickname)
      else:
        if damage_scaled > 0.2 and damage_scaled < 0.5:
          if in_pkmn.level - out_pkmn.level > 10:
            move_text = "({:})'s move ({:}) does high damage to us. Consider leveling up your pokemon before retrying!".format(out_pkmn.nickname, move.move_name)
          else:
            move_text = "({:})'s move ({:}) does high damage to us. Ouch!".format(out_pkmn.nickname, move.move_name)
        if damage_scaled >= 0.5:
          if out_pkmn.level - in_pkmn.level > 10:
            move_text = "({:})'s move ({:}) does massive damage to us. Consider leveling up your pokemon before retrying!".format(out_pkmn.nickname, move.move_name)
          elif in_pkmn.level - out_pkmn.level > 5:
            move_text = "({:})'s move ({:}) does massive damage to us. Consider switching out this pokemon for a better match!".format(out_pkmn.nickname, move.move_name)
          else:
            move_text = "({:})'s move ({:}) does massive damage to us. Ouch!".format(out_pkmn.nickname, move.move_name)
        
      damage_list.append((damage_scaled, move_text))
  return max(damage_list, key = lambda i : i[0], default=0)

# calculate the raw damage that out_pkmn can do to in_pkmn using move
def damage_calc(out_pkmn, move, in_pkmn, is_attacker):
  if move.damage_class.value == 3:
    return 0
  
  level = out_pkmn.level
  power = move.power if move.power else 0 #if nullable=true, then do you check for None???
  
  #change this to calculate A from more than base stats
  A = 0
  D = 0
  A_base = 0
  D_base = 0
  A_Nature = 1
  D_Nature = 1
  A_IV = 0
  D_IV = 0
  A_EV = 0
  D_EV = 0
  #change these into data entered

  if move.damage_class.value == 1: #physical 
    A_base = out_pkmn.pokemon.pokemon_base_stats[0].attack_stat
    D_base = in_pkmn.pokemon.pokemon_base_stats[0].defense_stat
    A = out_pkmn.custom_attack_stat
    D = in_pkmn.custom_defense_stat
  if move.damage_class.value == 2: #special
    A_base = out_pkmn.pokemon.pokemon_base_stats[0].special_attack_stat
    D_base = in_pkmn.pokemon.pokemon_base_stats[0].special_defense_stat
    A = out_pkmn.custom_special_attack_stat
    D = in_pkmn.custom_special_defense_stat

  A = A if A is not None else math.floor(((0.01 * (2 * A_base + A_IV + math.floor(0.25 * A_EV)) * level) + 5) * A_Nature)
  D = D if D is not None else math.floor(((0.01 * (2 * D_base + D_IV + math.floor(0.25 * D_EV)) * level) + 5) * D_Nature)

  #targets = 1
  #weather = 1

  critical = 1 #(move.crit_rate*2)+(1-move.crit_rate*1)
  random_scale = 0.85 #0.85+0.05*.15 or 1
  STAB = 2 if ((move.move_type.type_name == out_pkmn.pokemon.type1.type_name) or (out_pkmn.pokemon.type2 and move.move_type.type_name == out_pkmn.pokemon.type2.type_name)) else 1
  Type1 = damage_array[pokemon_types[move.move_type.type_name.lower()]][pokemon_types[in_pkmn.pokemon.type1.type_name.lower()]]
  Type2 = damage_array[pokemon_types[move.move_type.type_name.lower()]][pokemon_types[in_pkmn.pokemon.type2.type_name.lower()]] if in_pkmn.pokemon.type2_id else 1
  accuracy = move.accuracy if move.accuracy else 100

  hits = 2 if (move.min_hits == 2) else 1
  #(2*0.375+3*0.375+4*0.125+5*0.125) if (move.min_hits == 2 and move.max_hits == 5) else 1

  #print(level, power, A, D, critical, random_scale, STAB, Type1, Type2, accuracy, hits)

  damage = ((2/5*level+2)*power*A/D/50+2)*critical*random_scale*STAB*Type1*Type2*accuracy/100*hits
  #print(damage)
  #*weather*targets*Burn*other
  return damage


#implement: when adding new pokemon to inventory, you can have default ivs/evs


#damage as a percent caculation of health
#multiple hits


