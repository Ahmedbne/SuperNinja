# **🎮 SUPER NINJA** - A MULTIPLAYER SIDE-SCROLLING VIDEO GAME 🥷🏻

## DESCRIPTION
Welcome to Super Ninja, the ultimate side-scrolling multiplayer adventure! You’re a daring ninja armed with nothing but your wits and unmatched skills. Your mission? Survive waves of gun-toting enemies in a chaotic world where every second counts. Rally your ninja crew for cooperative gameplay and prove that together, no challenge is insurmountable!

A _multiplayer_, _co-op_ game made with __Pygame__, networking was made possible with __Socket__.

🕹️ Pygame: For smooth and responsive gameplay.

🌐 Socket Networking: To enable seamless multiplayer co-op.


## **🎮 Game Controls**

### **Gameplay**

| Action          | Key(s)                        |
| --------------- | ----------------------------- |
| **Move Left**   | `A` or `Left Arrow`           |
| **Move Right**  | `D` or `Right Arrow`          |
| **Jump**        | `Space` or `Up Arrow`         |
| **Dash/Attack** | `Left Shift` or `Right Shift` |
| **Pause/Exit**  | `ESC`                         |

### **Map Editor**

| Action                  | Key(s)                           |
| ----------------------- | -------------------------------- |
| **Pan Camera**          | `W`, `A`, `S`, `D` or Arrow Keys |
| **Place Tiles**         | `Left Click`                     |
| **Delete Tiles**        | `Right Click`                    |
| **Toggle Snap-to-Grid** | `G`                              |
| **Cycle Tile Groups**   | `Scroll Wheel`                   |
| **Cycle Tile Variants** | `Shift + Scroll Wheel`           |
| **Save Map**            | `Ctrl + S`                       |
| **Auto-Format Tiles**   | `Ctrl + R`                       |
| **Exit Edit Mode**      | `ESC`                            |

---

## REQUIRED EXTERNAL MODULES
Install modules by the command `python -m pip install [module_name]` or `python3 -m pip install [module_name]`.
- pygame
- PyInstaller
- pyperclip
- gtk (Linux only)
- PyQt4 (Linux only)

## INSTALLATION
- Clone the repo with `git clone https://github.com/Ahmedbne/SuperNinja.git`.
- Install all required modules from the above section.
- Navigate to `Super_Ninja\assets\fonts` and install all required fonts.
- Run these following commands:
```
cd Super_Ninja
For Windows: python silly_ninja.py
For Linux: python3 silly_ninja.py
```
 
## MULTIPLAYER INSTRUCTION
Because the game only supports multiplayer through Local Area Network (LAN), there're couple of ways to establish connections and play with your friends:
- You and your friends must be on the same network or Wifi, so that the host's IP can be discovered by other clients.
- Using third party software that provide the ability to create your own virtual networks, such as _Hamachi_, _RadminVPN_ or _ZeroTier_,... just to name a few. Then you and your friend can join the same network and establish connection. This is actually the prefer method because y'all can connect to each other from anywhere on the globe, as long as your device remain in that said virtual network.

After that, open the game and press the `Join` or `Host` button, depends on your situation:
- For the host, enter local IP on your network to the `IP` field, and enter a port number to the `Port` field (must be greater than 1000). After that, choose a nickname and press `Start`, you'll be in the lobby if the server starts successfully.
- For the client, enter the Host's IP and port to both fields. After that, pick a nickname and press `Join`, you'll be in the lobby if the connection establishes successfully.
- After all clients have joined the lobby and ready, indicates by their slots borders turn green, the Host then can start the game by pressing the `Launch` button.

## KNOWN ISSUES
- Levels are currently be order by ID as an integer. So when you create a new level using the Map Editor, its ID must be an integer that goes after the last level in the `assets/maps` folder, otherwise the game will crashes on level transitions.
- Levels are __NOT__ synced between machines on multiplayer mode, so if you make a new level or delete an existing one using the Map Editor. Then those new changes won't be shared across multiple devices in multiplayer mode, resulting in weird behaviors or even crashes during runtime. This issue has been acknowledged by us and will be fixed on future update. The current workaround is to have the host send his level files to all the clients before hosting a session.

## NOTES
- Ensure that all required libraries, modules are installed if you want to compile and run the game directly from source.

## CONTRIBUTIONS
@Ahmedbne - Product Owner 🥷🏻

@adamchafay23 🥷🏻

@AnouarBouy 🥷🏻

@YassirCHAOUB 🥷🏻

@Faza20-lab 🥷🏻

@NadaBOUGHABA03 🥷🏻

@danandoha 🥷🏻
