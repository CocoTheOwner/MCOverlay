import json
from Enums import Bedwars

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

def getStats(data: dict):
    bw = getGame(data, "Bedwars")

    useless = []
    resources = {}
    stats = {}

    stats["Overall"] = {}
    stats["Overall"]["stars"] = get(get(data, "achievements"), "bedwars_level")
    stats["Overall"]["coins"] = get(bw, "coins")
    stats["Overall"]["isPartyChat"] = get(data, "channel") == "PARTY"
    stats["Overall"]["rank"] = getRank(data)
    stats["Overall"]["name"] = get(data, "playername")
    if get(data, "playername") != get(data, "displayname"):
        stats["Overall"]["displayName"] = get(data, "displayname")

    ult = get(bw, "selected_ultimate")
    if ult != None:
        stats["Overall"]["ult"] = ult



    for st in bw.keys():
        if st in Bedwars.stats.keys():
            stats["Overall"][Bedwars.stats[st]] = get(bw, st)
        elif st.endswith("_bedwars") or st.endswith("_winstreak"):
            if st in stats["Overall"].keys():
                continue
            path = st.split("_")
            if len(path) > 2 and path[-3] == "resources" and path[-2] == "collected":
                resources[st] = get(bw, st)
            elif path[0] in ["castle", "eight", "four", "two"]:
                for mode in Bedwars.modes.keys():
                    if st.startswith(mode):
                        if st.removeprefix(mode).removeprefix("_") in Bedwars.stats.keys():
                            if not Bedwars.modes[mode] in stats:
                                stats[Bedwars.modes[mode]] = {}
                            statistic = Bedwars.stats[st.removeprefix(mode).removeprefix("_")]
                            value = get(bw, st)
                            stats[Bedwars.modes[mode]][statistic] = value
                            break
        useless.append(st)
    #for key in stats.keys():
        # You can add statistics that depend on others here.

    return stats

if __name__=="__main__":
    stats = getStats(json.loads(open("./statistics/cocodef9.json", "r").read())["player"])
    for key in stats:
        print("{}: {}".format(key, stats[key]))