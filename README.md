# MCOverlay
*A blazing fast overlay to never get sniped again!*

# Task Checklist

## General tasks
- [ ] Table view
- [ ] Levelhead view

## Specific tasks
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
- [ ] Selectable statistics in table
	- [ ] Index score
	- [ ] Dynamic system showing all
- [ ] GUI
- [ ] Mistake "/who" detection and marking
- [ ] Autowho
	- [ ] Don't use when first player in lobby
	- [ ] Maybe with party size
	- [ ] Alarm when not all party members in lobby (detect amount)
- [ ] Lobby playername toggle (semi-command?)
	- [ ] Chat
	- [ ] Joined lobby
	- [ ] All
- [ ] Autoleave+pwarp after game
	- [ ] Toggle
- [ ] Detection and marking system (join & leave)
	- [ ] Player detection
	- [ ] Player already in list (do not request API again)
	- [ ] Rank detection
	- [ ] Party detection
	- [ ] Guild detection
	- [ ] Staff detection
	- [ ] Party list detection
		- [ ] Party promotion detection (who is leader, moderator, GUI option)
	- [ ] Who-command detection
- [ ] Error and warning system
	- [ ] Timeout
	- [ ] API overload (diff MCAPI / HyAPI)
- [ ] Dynamic game type selection system
	- [ ] Multiple games
- [ ] Version in title of program
- [ ] Improve request getting
	- [Postman](https://learning.postman.com/docs/getting-started/introduction/)
- [ ] Autoinvite
	- [ ] Toggle
	- [ ] Check stats
		- [ ] Configurable
	- [ ] Name mention