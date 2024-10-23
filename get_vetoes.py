import os
import time
import json

############## UPDATE THESE ##############
faceit_api_key = os.environ['FACEIT_API_KEY']

# can get this from the url when looking at a team's league season matches
faceit_team_id = "30dd56ee-d645-4cd7-a7ca-e2ce5b7eddd8"

season_0 = ['foo']
seasons =[season_0]
# season_0 = ["1-36319026-c496-40ac-bc25-b5aa10b16467","1-303bcfc7-ff80-4028-bf06-69f1adebd748","1-72f723b8-93c1-429a-95b5-7d365b4dcb2e","1-cb00a42b-a8d9-4e95-b8bc-c653a4353a38","1-c6d34ede-c0ae-4e6a-bf74-aa6e72a00faf","1-b283347f-f4fb-4065-bd1c-b439721b152c","1-d72d75ea-3bad-41ff-a8cf-03ed34844ea0","1-00ac9367-3d17-4c67-a049-e8ad46e779d7"]
# season_1 = ["1-2478503e-5930-437b-bbcf-be8ecf94b8a5","1-f9e980d0-58ce-4818-b239-6137c774a7d9","1-9f687800-8019-4820-ab73-ea0a8b72983d","1-3e6f2355-ed02-43f5-8a48-609bb2a33485","1-3f842f5e-df10-4b3d-9c5e-c37dbd6bd99b","1-4edcbfa1-1d94-431c-8a22-5a8878ac6874","1-833254c1-5471-4f17-a0b4-37f014bd74e9","1-05447b17-1686-4b1e-a968-461cbb91437d","1-f636a7d0-ebf7-45ed-b018-1bf8bf3d5ce3","1-942f1d12-2f0f-478b-95bf-14eada868ff3","1-42408bde-2429-4520-845d-208360dce93d","1-c11048c7-19fd-40ad-87cf-151a464a0ecc","1-77c08a28-da17-4a24-a0ca-396df72aa4af","1-6fbb2ce1-a3a1-4101-97cd-aa695fa6d085"]

# seasons = [season_0, season_1]

# update if faceit cuts you off for too many requests.
TIME_BETWEEN_REQUESTS = 1
##########################################

FACTION_1_NAME = 'faction1'
FACTION_2_NAME = 'faction2'
MAP_ENTITY_TYPE = 'map'
BAN_STATUS = 'drop'
PICK_STATUS = 'pick'
FINISHED_STATUS = 'FINISHED'

team_data = {
    'team': '',
    'team_id': faceit_team_id,
    'maps':{}
}

def get_map_object():
    return {
            # how many times played
            'played':0,
            # how many times this team picked the map
            'picked':0,
            # how many times this team banned the map
            'banned':0,
            # how many time this team let the time run out and a random ban was introduced
            'random_ban':0,
            # number of wins this team has on the map
            'wins':0,
            # shows that there is a match still in progress.
            'unfinished':0
        }

def update_map_play_data(map, picked=0, banned=0, random_ban=0, wins=0, unfinished=0, played=0):
    if map not in team_data['maps']:
        team_data['maps'][map] = get_map_object()
    
    map_object = team_data['maps'][map]
    map_object['picked'] += picked
    map_object['banned'] += banned
    map_object['random_ban'] += random_ban
    map_object['wins'] += wins
    map_object['unfinished'] += unfinished
    map_object['played'] += played

def get_match_vetoes(match_id):
    # Open and read the JSON file
    with open('example_bo3_vetoes.json', 'r') as file:
        data = json.load(file)

    # Print the data
    # print(data)
    return data

def get_match(match_id):
    # Open and read the JSON file
    with open('example_bo3_match.json', 'r') as file:
        data = json.load(file)

    # Print the data
    # print(data)
    return data

def is_map_won(match, faction, map):
    # the pick list and detailed_results list are parallel lists.
    # given the index of the map in pick we can discern the detailed result.
    # allows handling bo1s and boXs.
    map_pick_index = match['voting']['map']['pick'].index(map)
    detailed_result = match['detailed_results'][map_pick_index]
    return detailed_result['winner'] == faction

def is_match_finished(match):
    return match['status'] == FINISHED_STATUS

def determine_faction(match):
    if match['teams']['faction1']['faction_id'] == faceit_team_id:
        team_data['team'] = match['teams']['faction1']['name']
        return FACTION_1_NAME
    elif match['teams']['faction2']['faction_id'] == faceit_team_id:
        team_data['team'] = match['teams']['faction2']['name']
        return FACTION_2_NAME
    else:
        raise Exception("Team does not match either faction, this should never happen.") 

def run():
    for season in seasons:
        for match_id in season:
            match = get_match(match_id)
            match_vetoes = get_match_vetoes(match_id)

            faction = determine_faction(match)
            print('faction: ' + faction)

            for ticket in match_vetoes['payload']['tickets']:
                if ticket['entity_type'] == MAP_ENTITY_TYPE:
                    for entity in ticket['entities']:
                        map_name = entity['guid']
                        # check if we're dealing with the team we're interested in and not their opponent.
                        if entity['selected_by'] == faction:
                            if entity['status'] == BAN_STATUS:
                                if entity['random'] == True:
                                    update_map_play_data(map_name, random_ban=1)
                                else:
                                    update_map_play_data(map_name, banned=1) 
                            elif entity['status'] == PICK_STATUS:
                                if is_match_finished(match):
                                    if is_map_won(match, faction, map_name):
                                        update_map_play_data(map_name, picked=1, played=1, wins=1) 
                                    else:
                                        update_map_play_data(map_name, picked=1, played=1)
                                else:
                                    update_map_play_data(map_name, picked=1, unfinished=1) 
                            else:
                                raise Exception("Unhandled veto status: " + entity['status']) 
                        else:
                            # see if enemy picked the map and determine if won
                            if entity['status'] == PICK_STATUS:
                                if is_match_finished(match):
                                    if is_map_won(match, faction, map_name):
                                        update_map_play_data(map_name, played=1, wins=1)
                                    else:
                                        update_map_play_data(map_name, played=1)
                                else:
                                    update_map_play_data(map_name, unfinished=1)
                            
            time.sleep(TIME_BETWEEN_REQUESTS)

run()

# Pretty print JSON with indentation
json_string = json.dumps(team_data, indent=4)

print(json_string)