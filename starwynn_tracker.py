import starwynn_utils as utils
import time

verbose = False
utils.verbose = False

class Tracker:
    def __init__(self, claim, guild):
        self.territories = utils.define_claim_from_csv(claim)
        self.current_territories = utils.find_claim_owners(self.territories)
        self.guild = guild
        if verbose:
            print("tracker started on", claim)
    
    def update_territories(self):
        if verbose:
            print("updating territories")
        new_territories = utils.find_claim_owners(self.territories)
        updated_teritories = []

        for terr in self.territories:
            if new_territories[terr] != self.current_territories[terr]:
                print(terr, "has been captured by", new_territories[terr], "from", self.current_territories[terr]) # this would be 
                updated_teritories.append((terr, new_territories[terr], self.current_territories[terr]))

        self.current_territories = new_territories
        return updated_teritories


if __name__ == "__main__":
    tracker = Tracker("desert")
    while True:
        time.sleep(2)
        print(tracker.update_territories())
