YuppieNalle
===========


# Ideer från monks
Sprid ut kontrollerna på flera telefoner för att simulera rövarna tätt intill. Kontrollera kan sedan switchas mid game.

# Ritningar

## Infrastruktur riting 01
```
﻿ritning 01
+------------------------------------------------+
|                    Home LAN/Router             | the internet
|                                                |
|  +--------+                                    |
|  | Client |                                    |
|  | (brwsr)+---------------+                    |
|  |        |               |                    |
|  |        |               |                    |
|  +--------+      +--------v--------+           |              +------------------+
|  | Client |      | browser server  |           |              |    Apps loader   |
|  | (nativ)+------> Web RTC/Sockets |           |              | public website   |
|  |        |      | (amaru game code)           |              |                  |
|  +--------+      |                 +-----------+------------->+                  |
|  | Cleint |      |                 |     saves final state to |                  |
|  | (nativ)+------>                 |     public server        |                  |
|  |        |      |                 |           |              |                  |
|  +--------+      +--------^--------+           |              +------------------+
|  | Client |               |                    |
|  | (brwsr)|               |                    |
|  |        +---------------+                    |
|  |        |                                    |
|  +--------+                                    |
|                                                |
|                                                |
|                                                |
|                                                |
|                                                |
+------------------------------------------------+
```

# Källor

Hitta lokala IP adresser från en browser
https://github.com/diafygi/webrtc-ips

Python till javascript
https://transcrypt.org/

