import requests, time, os
import pandas as pd

verbose = True
rate_limit = 180

request_delay = 60/rate_limit

def get_players():
    if verbose:
        print("requesting world information...")
    request = requests.get("https://api.wynncraft.com/v3/player?identifier=uuid")
    try:
        assert request.status_code == 200
        if verbose:
            print("request successful!")
        return request.json()
    except AssertionError:
        if verbose:
            print("unsuccessful request")
        return None

def get_name_from_uuid(uuid):
    return requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}").json()["name"]

def add_players(file, players): # ChatGPT
    try:
        assert file[-4:] == ".csv"
    except AssertionError:
        file += ".csv"
    new_df = pd.DataFrame(players, columns=['UUID', 'Player Name'])
    
    if os.path.exists(file):
        existing_df = pd.read_csv(file)
        new_df = new_df[~new_df['UUID'].isin(existing_df['UUID'])]

        if not new_df.empty:
            new_df.to_csv(file, mode='a', index=False, header=False)
            print(f"added {len(new_df)} new players to {file}")
        else:
            print("no new players to add")
    else:
        new_df.to_csv(file, mode='w', index=False)
    
    ###

    
        




def find_prof(level_min, file):
    data = get_players()
    online_players = data["total"]
    players = data['players'].keys()
    valid_players = []

    count = 0
    valids = 0
    
    for uuid in players:
        try:
            player_data = requests.get(f"https://api.wynncraft.com/v3/player/{uuid}?fullResult").json()
            profs = ["fishing", "woodcutting", "mining", "farming"]
            
            valid = any([any([char["professions"][profession]["level"] >= level_min for profession in profs]) for char in player_data["characters"].values() if char["professions"]])

            if valid:
                print(uuid, get_name_from_uuid(uuid))
                valid_players.append((uuid, get_name_from_uuid(uuid)))
                valids += 1

        except:
            pass
            # print(uuid)
            # print([char["professions"] for char in player_data["characters"].values()])

        count += 1
        if verbose:
            print("checked", count, "out of", online_players, "of which", valids, "are valid")

        time.sleep(request_delay)
    
    add_players(file, valid_players)

if __name__ == "__main__":

    find_prof(80, "known_prof")