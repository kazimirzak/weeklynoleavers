import requests
from requests.auth import HTTPBasicAuth
from texttable import Texttable

BNET_CLIENT_ID = "<BNET_CLIENT_ID>"
BNET_CLIENT_SECRET = "<BNET_CLIENT_SECRET"
realmSlug = 'ravencrest'
nameSlug = 'desynced'


def get_bnet_auth_token():
    return requests.post('https://us.battle.net/oauth/token', data={'grant_type': 'client_credentials'}, auth=HTTPBasicAuth(BNET_CLIENT_ID, BNET_CLIENT_SECRET)).json()['access_token']


def get_chars():
    request = requests.get(f'https://eu.api.blizzard.com/data/wow/guild/{realmSlug}/{nameSlug}/roster', params={
        ':region': 'eu',
        'namespace': 'profile-eu',
        'locale': 'eu_US',
    }, headers={
        'Authorization': f'Bearer {get_bnet_auth_token()}'
    })
    characters = []
    for member in request.json()['members']:
        characters.append(member['character']['name'])
    return characters


def get_raiderio_weeklies(character):
    request = requests.get(f'https://raider.io/api/v1/characters/profile?region=eu&realm=ravencrest&name={character}&fields=mythic_plus_weekly_highest_level_runs')
    if not request.ok:
        return []
    dungeons_ = request.json()['mythic_plus_weekly_highest_level_runs']
    return dungeons_


chars = get_chars()
mapping = dict()
for character in chars:
    dungeons = get_raiderio_weeklies(character)
    for dungeon in dungeons:
        if character not in mapping:
            mapping[character] = []
        mapping[character].append(dungeon['mythic_level'])
mapping = [{'character': character, 'm15+': len([x for x in dungeons if x >= 15]), 'dungeons': dungeons} for character, dungeons in mapping.items()]
mapping = sorted(mapping, key= lambda x: (x['m15+'], x['character']), reverse=True)
table = Texttable()
table.set_cols_align(["l", "c", "c"])
table.set_cols_valign(['m', 'm', 'm'])
table.add_row(['Character', '15+s', 'Dungeon Levels'])
for x in mapping:
    table.add_row([x['character'], x['m15+'], x['dungeons']])
with open('output.txt', 'w') as file:
    file.write(table.draw())
