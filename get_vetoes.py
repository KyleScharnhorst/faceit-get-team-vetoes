import os
import datetime
import time
import json
import requests

############## UPDATE THESE ##############
faceit_api_key = os.environ['FACEIT_API_KEY']

# can get this from the url when looking at a team's league season matches
faceit_team_id = "73d28e6f-13a5-4d16-afef-4ba6572d5849"

# season_0 = ["1-81513758-e2be-453d-9444-60e782d8c99f"]
# seasons =[season_0]
season_0 = ["1-490e80f8-6d23-4014-80f9-b2e5280dabef","1-c49d7259-955d-4f8a-957d-794689d9bb99","1-e64f9ed4-c0a0-4a79-8636-5b8ec75533a6","1-340ca388-a930-4cbb-8f3a-33d5b69fa061","1-139a5e5a-715e-4c08-90ad-7dfd4cd797cd","1-e7c473fa-31df-464f-a25d-849cecfc7b63","1-dab4f737-ceb5-4b39-9b63-453120464e6e","1-def7ad65-4e13-40c3-a778-edde7b204306"]
season_1 = ["1-8d123f61-e982-4892-9bba-1164ccab6fe7","1-191be23e-4311-4dcc-83b1-483a744d1bd5","1-ce72d11b-d42c-4f59-b9a9-efd2edfdfcce","1-130b4c6e-8dc8-46a2-bcca-37089bf629ca","1-81513758-e2be-453d-9444-60e782d8c99f","1-cf4be1b3-beaf-404c-8733-7ad150e33e8b","1-65f5ed91-e0dc-4cda-ab71-4436e6625fb1","1-ef01719c-c0a5-4538-bf7f-cc302a0cbe94","1-dbe3522b-76d5-4803-a3fd-d3748400ebf2","1-8ab84471-9642-4fc4-92d6-37e0b10142c6","1-0b22c9df-b1ad-41c0-98a6-f469e3b50fbd","1-cb76a977-46c7-46ba-93cf-e98ef950d520","1-5137caf6-7bdb-469c-8304-1e5e69047903","1-f5d39d89-5576-4dbe-ad53-e34fb9c65aef"]

seasons = [season_0, season_1]

# update if faceit cuts you off for too many requests.
TIME_BETWEEN_REQUESTS = 0.1

# language, used for generating faceit url links.
DEFAULT_LANGUAGE = 'en'
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

def retrieve_faceit_api_get_match_url(match_id):
    # https://open.faceit.com/data/v4/matches/{{match_id}}
    return 'https://open.faceit.com/data/v4/matches/' + match_id

def retrieve_faceit_api_veto_url(match_id):
    # https://api.faceit.com/democracy/v1/match/{{match_id}}/history
    return 'https://api.faceit.com/democracy/v1/match/' + match_id + '/history'

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
            'unfinished':0,
            # shows if the map was chosen from either side, but didn't play it due to
            # something like bo3 going 2-0
            'not_played':0
        }

def update_map_play_data(map, picked=0, banned=0, random_ban=0, wins=0, unfinished=0, played=0, not_played=0):
    if map not in team_data['maps']:
        team_data['maps'][map] = get_map_object()
    
    map_object = team_data['maps'][map]
    map_object['picked'] += picked
    map_object['banned'] += banned
    map_object['random_ban'] += random_ban
    map_object['wins'] += wins
    map_object['unfinished'] += unfinished
    map_object['played'] += played
    map_object['not_played'] += not_played

def get_match_vetoes(match_id):
    url = retrieve_faceit_api_veto_url(match_id)
    # print('url: ' + url)
    response = requests.get(url)

    if response.status_code == 200:
        # print(response.text)
        return response.json()
    else:
        print(f"Get match vetoes request failed with status code {response.status_code}")

def get_match(match_id):
    
    url = retrieve_faceit_api_get_match_url(match_id)
    # print('url: ' + url)

    headers = {
        'Authorization': 'Bearer ' + faceit_api_key
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # print(response.text)
        return response.json()
    else:
        print(f"Get match request failed with status code {response.status_code}")

def was_map_played(match, map):  
    map_pick_index = match['voting']['map']['pick'].index(map)

    try:
        detailed_result = match['detailed_results'][map_pick_index]
        return True
    except:
        return False


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
        raise Exception("Team does not match either faction, this should never happen. Remember to update the faceit team id in the update section.") 

def get_faceit_url(match):
    result = None

    if match:
        faceit_url = match.get('faceit_url')
        if faceit_url:
            faceit_url = faceit_url.replace('{lang}', DEFAULT_LANGUAGE)
            result = faceit_url

    return result

def update_match_play_data(match, faction, map_name=None):

    if not match.get('voting'):
        print('missing voting entry for: ' + get_faceit_url(match))
        return
    maps = match['voting']['map']['pick']

    if map_name:
        maps = [map_name]

    for map in maps:
        if is_match_finished(match):
            if was_map_played(match, map_name):
                if is_map_won(match, faction, map_name):
                    update_map_play_data(map_name, played=1, wins=1)
                else:
                    update_map_play_data(map_name, played=1)
            else:
                update_map_play_data(map_name, not_played=1)
        else:
            update_map_play_data(map_name, unfinished=1)

def update_match_play_data_for_team_pick(match, faction, map_name=None):

    if not match.get('voting'):
        print('missing voting entry for: ' + get_faceit_url(match))
        return
    maps = match['voting']['map']['pick']

    if map_name:
        maps = [map_name]

    for map in maps:

        if is_match_finished(match):
            if was_map_played(match, map_name):
                if is_map_won(match, faction, map):
                    update_map_play_data(map, picked=1, played=1, wins=1) 
                else:
                    update_map_play_data(map, picked=1, played=1)
            else:
                update_map_play_data(map_name, picked=1, not_played=1)
        else:
            update_map_play_data(map, picked=1, unfinished=1)
    
def run():
    for season in seasons:
        # print('season match ids: ' + json.dumps(season))
        for match_id in season:
            # print('match_id: ' + match_id)
            match_url = 'https://www.faceit.com/en/cs2/room/' + match_id
            
            match = get_match(match_id)
            if match is None:
                print('Match was not provided, skipping')
                continue

            if match['status'] != 'FINISHED':
                print('Match is being played or has not been played yet, skipping. ' + match_url)
                continue

            faction = determine_faction(match)
            # print('faction: ' + faction)

            match_vetoes = get_match_vetoes(match_id)
            if match_vetoes is None:
                print('\tMatch vetoes not provided. Attempting to get played and win information.')
                # we have a match, but no vetoes, update played and whether won or not

                try:
                    update_match_play_data_for_team_pick(match, faction)
                except:
                    print('\tFAILED getting played and win infomation.')
                    print('\tYou can manually look at map and win information here: ' + match_url)
                continue

            for ticket in match_vetoes['payload']['tickets']:
                if ticket['entity_type'] == MAP_ENTITY_TYPE:
                    for index, entity in enumerate(ticket['entities']):
                        map_name = entity['guid']
                        # check if we're dealing with the team we're interested in and not their opponent.
                        if entity['selected_by'] == faction:
                            if entity['status'] == BAN_STATUS:
                                if entity['random'] == True:
                                    update_map_play_data(map_name, random_ban=1)
                                else:
                                    update_map_play_data(map_name, banned=1) 
                            elif entity['status'] == PICK_STATUS:
                                # determine if we're in the last index, because technically the team
                                # that performs the last ban is the team that "picks" a map.
                                # looking at the raw data, the pick goes to the team that didn't perform
                                # the last ban, which for us doesn't make sense.
                                if len(ticket['entities']) - 1 is index:
                                    # oppenent actually picked the map, update for that
                                    update_match_play_data(match, faction, map_name)
                                else:
                                    # team actually picked the map, update for them.
                                    update_match_play_data_for_team_pick(match, faction, map_name)
                            else:
                                raise Exception("Unhandled veto status: " + entity['status']) 
                        else:
                            # see if enemy picked the map and determine if won
                            if entity['status'] == PICK_STATUS:
                                if len(ticket['entities']) - 1 is index:
                                    # team actually picked the map update for them.
                                    update_match_play_data_for_team_pick(match, faction, map_name)
                                else:
                                    # oppenent actually picked the map update for that.
                                    update_match_play_data(match, faction, map_name)
              
            time.sleep(TIME_BETWEEN_REQUESTS)

run()

# Pretty print JSON with indentation
json_string = json.dumps(team_data, indent=4)

print ('writing to results dir')
print(json_string)

current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename=team_data['team'] + '_' + faceit_team_id + '_' + str(current_timestamp) + '.json'
with open('results/' + filename, 'w', encoding='utf-8') as f:
    json.dump(team_data, f, ensure_ascii=False, indent=4)