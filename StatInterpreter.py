import json
from Enums import Bedwars
from pandas import DataFrame

def getRank(data: dict):
    if "levelUp_MVP_PLUS" in data:
        return "MVP+"
    elif "levelUp_MVP" in data:
        return "MVP"
    elif "levelUp_VIP_PLUS" in data:
        return "VIP+"
    elif "levelUp_VIP" in data:
        return "VIP"
    else:
        return "NON"

def getGame(data: dict, game: str):
    x = get(data, "stats")
    if x != None: return get(x, game)

def get(data: dict, key: str):
    if data != None and key in data: return data[key]

class Statistics:

    name = None
    stats = {}
    general_stats = {}
    resources = {}
    ignored = []
    round = 2 #Decimals

    def __init__(self, data: dict):

        bw = getGame(data, "Bedwars")

        self.general_stats["Stars"] = get(get(data, "achievements"), "bedwars_level")
        self.general_stats["Coins"] = get(bw, "coins")
        self.general_stats["IsPartyChat"] = get(data, "channel") == "PARTY"
        self.general_stats["Rank"] = getRank(data)
        self.general_stats["Name"] = get(data, "playername")
        if get(data, "playername") != get(data, "displayname"):
            self.general_stats["DisplayName"] = get(data, "displayname")

        ult = get(bw, "selected_ultimate")
        if ult != None:
            self.general_stats["ult"] = ult

        for st in bw.keys():
            if st in Bedwars.stats.keys():
                if not "Overall" in self.stats:
                    self.stats["Overall"] = {}
                self.stats["Overall"][Bedwars.stats[st]] = get(bw, st)
            elif st.endswith("_bedwars") or st.endswith("_winstreak"):
                if st in self.general_stats.keys():
                    continue
                path = st.split("_")
                if len(path) > 2 and path[-3] == "resources" and path[-2] == "collected":
                    self.resources[st] = get(bw, st)
                elif path[0] in ["castle", "eight", "four", "two"]:
                    for mode in Bedwars.modes.keys():
                        if st.startswith(mode):
                            if st.removeprefix(mode).removeprefix("_") in Bedwars.stats.keys():
                                if not Bedwars.modes[mode] in self.stats:
                                    self.stats[Bedwars.modes[mode]] = {}
                                statistic = Bedwars.stats[st.removeprefix(mode).removeprefix("_")]
                                value = get(bw, st)
                                self.stats[Bedwars.modes[mode]][statistic] = value
                                break
            self.ignored.append(st)
        for key in self.stats.keys():
            #print(str(type(self.stats[key])) + "m" + str(key))
            self.stats[key]["FKDR"] = round(get(self.stats[key],    "FinalKs") / get(self.stats[key], "FinalDs"), self.round)
            self.stats[key]["WLR"]  = round(get(self.stats[key],    "Wins")    / get(self.stats[key], "Losses"), self.round)
            self.stats[key]["KDR"]  = round(get(self.stats[key],    "Kills")   / get(self.stats[key], "Deaths"), self.round)
            self.stats[key]["BBBL"] = round(get(self.stats[key],    "BedsB")   / get(self.stats[key], "BedsL"), self.round)
            self.stats[key]["FK/G"] = round(get(self.stats[key],    "FinalKs") / get(self.stats[key], "Games"), self.round)
            self.stats[key]["Index"]= round(get(self.general_stats, "Stars")   * get(self.stats[key], "FKDR")**2, self.round) / 10

if __name__=="__main__":
    s = Statistics(json.loads(open("./statistics/cocodef9.json", "r").read())["player"])
    k = DataFrame(s.stats)
    for key in s.stats.keys():
        print(str(k[key][["KDR", "FKDR", "Index"]][[0, 1, 2]]) + " <- " + key)
    print("Overall: " + str(s.general_stats))