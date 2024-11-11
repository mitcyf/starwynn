import requests, time, os
import pandas as pd

verbose = True
rate_limit = 180

request_delay = 60/rate_limit
GATHERING = ["fishing", "woodcutting", "mining", "farming"]

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
            profs = GATHERING
            
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



def find_active_prof(file):
    try:
        assert file[-4:] == ".csv"
    except AssertionError:
        file += ".csv"
    assert os.path.exists(file)

    df = pd.read_csv(file)
    uuids = df['UUID'].tolist()
    players = get_players()["players"]

    player_world = []
    for uuid in uuids:
        if uuid in players.keys():
            player_world.append((uuid, players[uuid]))
    return player_world

def sum_worlds(player_world):
    worlds = {}
    for pair in player_world:
        if pair[1] not in worlds.keys():
            worlds[pair[1]] = 1
        else:
            worlds[pair[1]] += 1
    
    return worlds

def dict_diff(dict1, dict2):
    out_dict = {key: value for key, value in dict1.items()}
    for key, value in dict2.items():
        if key not in out_dict.keys():
            out_dict[key] = -value
        else:
            out_dict[key] -= value
    out_dict = {key: value for key, value in out_dict.items() if value != 0}
    return out_dict
    
class Stalker:
    def __init__(self, file, delay):
        self.file = file
        self.players = sum_worlds(find_active_prof(self.file))
        self.delay = delay
        print(f"initiated stalker for {self.file}")
    
    def update(self):
        current_players = sum_worlds(find_active_prof(self.file))
        print(dict_diff(current_players, self.players))
        self.players = current_players
    
    def current(self):
        print(self.players)
    
    def wait(self):
        time.sleep(self.delay)





def get_total_prof(player, profs=GATHERING):
    pass # TODO

if __name__ == "__main__":
    # prof_stalker = Stalker("known_prof", 5)
    # while True:
    #     prof_stalker.update()
    #     prof_stalker.current()
    #     prof_stalker.wait()

    # recheck_timer = 60
    # recheck_count = 5
    # last_players = []
    # for i in range(recheck_count):
    #     data = get_players()
    #     current_players = list(data["players"].keys())
        
    #     if last_players:
    #         log_off = []
    #         log_on = []

    #         # for old in last_players:
    #         #     if old not in current_players:
    #         #         log_off.append(old)

    #         # for new in current_players:
    #         #     if new not in last_players:
    #         #         log_on.append(new)
        
    #         for old_index in range(len(last_players)):
    #             if last_players[old_index] not in current_players:
    #                 log_off.append(old_index)

    #         for new_index in range(len(current_players)):
    #             if current_players[new_index] not in last_players:
    #                 log_on.append(new_index)
                    
    #         print("log off", log_off)
    #         print("log on", log_on)
    #         print("------")
        
    #     last_players = current_players
    #     time.sleep(recheck_timer)


    find_prof(80, "known_prof")
    #print(sum_worlds(find_active_prof("known_prof")))