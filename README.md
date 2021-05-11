# MCOverlay
*A blazing fast overlay to never get sniped again!*

# Task Checklist
## Backend
- [ ] Mistake "/who" detection and marking
- [ ] Autoinvite
	- [X] Toggle
	- [ ] Check stats
		- [ ] Configurable
	- [X] Name mention
## Frontend
- [ ] GUI Layout
- [ ] Selectable statistics in table
	- [ ] Index score
	- [ ] Dynamic system showing all
	- [ ] Party detection
	- [ ] Guild detection
- [ ] Alarm when not all party members in lobby (detect amount)
- [ ] Navigate to log file
	- Perhaps navigate to C:/Users, let the user pick a folder.
	- Then see if there's a .minecraft folder in */AppData/
	- If there is, just pick that, go into */logs/latest.log
	- If there is not, let the user select a minecraft game folder manually
	- Then check if there exists a logs folder, if not, return to previous step ^
- [ ] Dynamic game type selection system
	- [ ] Multiple games
- [ ] Version in title of program
## Completed tasks
- [X] Upon open, disregard all entries before that timestamp (set linenumber)
	- Improved by only discarding certain elements 
		- lobbyname, among other things, is maintained. 
		- Downloads are completely ignored. /who will autodownload again.
- [X] Autowho
	- [X] Don't use when first player in lobby
	- ~~[X] Maybe with party size~~
- [X] Autoleave+pwarp after game
	- [X] Toggle (both leave & pwarp)
- [X] Improve request getting (now less than 100ms! (based on your connection!))
- [x] Read `latest.log`
	- [x] Detect changes, filter unimportant data
- [x] Interpret `latest.log`
	- [x] Lobby 1
		- [HH:MM:SS] [Client thread/INFO]: [CHAT] [STARS?] NAME: CHAT
		- [HH:MM:SS] [Client thread/INFO]: [CHAT] [STARS?] [RANK] NAME: CHAT
		- [HH:MM:SS] [Client thread/INFO]: [CHAT] [RANK] NAME joined the lobby!
			- `RANK` can be MVP+ and MVP++
	- [x] Game lobby ->
		- [HH:MM:SS] [Client thread/INFO]: [CHAT] NAME has joined (X/Y)!
			- `X` varies from 1 to `Y`
			- `Y` is 8 (solo or 4v4), 12 (3s) 16 (2s or 4s)
- [x] Request UUID from Minecraft username API
	- [x] Save uuid->player and player->uuid tables between runs
- [x] Get API token from file
- [x] Use API token and UUID to retrieve player information from Hypixel API
- [X] Upkeep list of party members
	- [X] On party member disconnect leave lobby etc
	- [X] On party disconnect write message in party chat (?) (toggleable)
	- [X] If party size = 1 (only self), don't /p warp after autoLeave
- [X] ~~Suppress keyboard input when sending a command~~ Not possible within python
- [X] Lobby playername toggle (semi-command?)
	- [X] Chat
	- [X] Joined lobby
	- [X] All
	- [X] Added more
- [X] Error and warning system for API
	- ~~[ ] Timeout~~ Scrapped due to default integration. Adding would need threads inside threads so will not.
	- [X] API overload (diff MCAPI / HyAPI)
- [X] Detection and marking system (join & leave)
	- [X] Player detection
	- [X] Player already in list (do not request API again)
	- [X] Rank detection
	- [X] Staff detection
	- [X] Party list detection
		- [X] Party promotion detection (who is leader, moderator, GUI option)
	- [X] Who-command detection
- [X] Refresh player statistics at the end of the game
- [X] Party alarm
	- [X] Leave gamelobby if party member disconnects or leaves