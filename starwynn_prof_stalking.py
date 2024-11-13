import requests, time, os, schedule
import pandas as pd

verbose = True
RATE_LIMIT = 180

request_delay = 60/RATE_LIMIT
GATHERING = ["fishing", "woodcutting", "mining", "farming"]
GATHERING_LEADERBOARD = [prof + "Level" for prof in GATHERING]

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

def add_players(file, players, reset = False): # ChatGPT
    try:
        assert file[-4:] == ".csv"
    except AssertionError:
        file += ".csv"
    new_df = pd.DataFrame(players, columns=['UUID', 'Player Name'])
    
    if os.path.exists(file) and not reset:
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


def get_prof_diff(player):
    player_data = requests.get(f"https://api.wynncraft.com/v3/player/{player}?fullResult").json()
    current_sum = sum([player_data["ranking"][prof] for prof in GATHERING_LEADERBOARD])
    previous_sum = sum([player_data["previousRanking"][prof] for prof in GATHERING_LEADERBOARD])

    return previous_sum - current_sum # positive means positive progress


def filter_active_profs(known_file, active_file):
    try:
        assert known_file[-4:] == ".csv"
    except AssertionError:
        known_file += ".csv"
    try:
        assert active_file[-4:] == ".csv"
    except AssertionError:
        active_file += ".csv"

    active_players = []

    count = 0
    actives = 0

    df = pd.read_csv(known_file)
    known_uuids = df['UUID'].tolist()
    known_players = len(known_uuids)
    
    for uuid in known_uuids:
        try:
            if get_prof_diff(uuid) > 0:
                print(uuid, get_name_from_uuid(uuid))
                active_players.append((uuid, get_name_from_uuid(uuid)))
                actives += 1

        except:
            pass
            # print(uuid)
            # print([char["professions"] for char in player_data["characters"].values()])

        count += 1
        if verbose:
            print("checked", count, "out of", known_players, "of which", actives, "are active")

        time.sleep(request_delay)
    
    add_players(active_file, active_players, reset = True)

class Stalker:
    def __init__(self, file, delay):
        self.file = file
        self.players = sum_worlds(find_active_prof(self.file))
        self.delay = delay
        print(f"initiated stalker for {self.file}")
    
    def update(self):
        current_players = sum_worlds(find_active_prof(self.file))
        print(dict_diff(current_players, self.players))
        self.current()
        self.players = current_players
    
    def start_stalking(self):
        schedule.every(self.delay).seconds.do(self.update)
    
    def current(self):
        print(self.players)
    
    # def wait(self):
    #     time.sleep(self.delay)





def get_total_prof(player, profs=GATHERING):
    pass # TODO

if __name__ == "__main__":
    # prof_stalker = Stalker("active_prof", 5)
    # prof_stalker.start_stalking()
    # while True:
    #     schedule.run_pending()
    find_prof(80, "known_prof")
    filter_active_profs("known_prof", "active_prof")

    # player = "starfaiien"
    # player_data = requests.get(f"https://api.wynncraft.com/v3/player/{player}?fullResult").json()
    # print(player_data["ranking"])

    # print(get_prof_diff(player))
    #print(sum_worlds(find_active_prof("known_prof")))