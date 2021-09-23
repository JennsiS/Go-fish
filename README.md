# Project 2 - CC3067 - 2021
A multiplayer implementation with rooms for Go Fish :fish: card game.<br>
Local `127.0.0.1`


## Requirements  :clipboard:
* Python 3.8.*

## How to Use  :rocket:
1. Download all python files.
2. Start server
```
python3 server.py -capacity [max capacity for rooms]
```
Default server capacity (if not provided) is `3`.

4. Connect Client(s)
```
python3 client.py
```
Each client is assigned a free slot in a room, when room capacity is filled, game begins.

## Components  :open_file_folder:
Component | Description |
:---: | :--- |
Server | Handles all rooms, client autojoins and overall comunication. |
Client | Handles user info, autojoin requests and user game interaction. |
Room | Handles room's game and room's players data. |
Game | Go Fish implementation. Handles: deck, hands, current turn, ocean and rules. |
Utils | Module for util functions. |

## Authors  :pencil2:
- *Luis Quezada* - [@Lfquezada](https://github.com/Lfquezada)
- *Jennifer Sandoval* - [@JennsiS](https://github.com/JennsiS)
- *Esteban del Valle* - [@Estdv](https://github.com/Estdv)

## References  :mag:
* https://realpython.com/python-sockets/
* https://bicyclecards.com/how-to-play/go-fish/
* https://www.ducksters.com/games/go_fish_rules.php
