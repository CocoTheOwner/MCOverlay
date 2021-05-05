# MCOverlay
*A blazing fast overlay to never get sniped again!

# Task Checklist

## General tasks
- [ ] Table view
- [ ] Levelhead view

## Specific tasks
- [ ] Read `latest.log`
	- [ ] Detect changes, filter unimportant data
- [ ] Interpret `latest.log`
	- [ ] Lobby 1
		- [HH:MM:SS] [Client thread/INFO]: [CHAT] [STARS?] NAME: CHAT
		- [HH:MM:SS] [Client thread/INFO]: [CHAT] [RANK] NAME joined the lobby!
			- `RANK` can be MVP+ and MVP++
	- [ ] Game lobby ->
		- [HH:MM:SS] [Client thread/INFO]: [CHAT] NAME has joined (X/Y)!
			- `X` varies from 1 to `Y`
			- `Y` is 8 (solo or 4v4), 12 (3s) 16 (2s or 4s)
- [ ] Request UUID from Minecraft username API
- [ ] Get API token from file
- [ ] Use API token and UUID to retrieve player information from Hypixel API
- [ ] Teamcolors
- [ ] Selectable statistics in table
	- [ ] Index score
	- [ ] Dynamic system showing all
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
	- [ ] Staff detection
	- [ ] Party list detection
	- [ ] Who-command detection
- [ ] Error and warning system
	- [ ] Timeout
	- [ ] API overload (diff MCAPI / HyAPI)
- [ ] Dynamic game type selection system
	- [ ] Multiple games
- [ ] Version in title of program
