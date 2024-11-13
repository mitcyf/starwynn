import requests, csv

verbose = True

def get_terr(n = 10):
    if verbose:
        print("requesting territory information...")
    request = requests.get("https://api.wynncraft.com/v3/guild/list/territory")
    try:
        assert request.status_code == 200
        if verbose:
            print("request successful!")
        return request.json()
    except AssertionError:
        if verbose:
            print("unsuccessful request")
        return None


def list_to_csv(data, file):
    with open(file, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        for item in data:
            writer.writerow([item])

def define_claim_from_guild(prefix, file=""):
    try:
        assert file[-4:] == ".csv"
    except AssertionError:
        file += ".csv"
    territories = get_terr()

    claim_list = []

    for terr, info in territories.items():
        if info["guild"]["prefix"] == prefix:
            claim_list.append(terr)
    if file != ".csv":
        list_to_csv(claim_list, file)

    return claim_list

def define_claim_from_csv(file):
    try:
        assert file[-4:] == ".csv"
    except AssertionError:
        file += ".csv"
    with open(file, mode='r') as file:
        reader = csv.reader(file)

        territories = [row[0] for row in reader]
    
    return territories

def find_claim_owners(territories):
    live = get_terr()
    return {terr: live[terr]["guild"]["prefix"] for terr in territories}

if __name__ == "__main__":
    sky = define_claim_from_csv("sky")
    print(find_claim_owners(sky))


# define_claim_from_guild("RATC", "sky")