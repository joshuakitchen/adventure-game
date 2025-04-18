# 🏰 Nymirith

![Version](https://img.shields.io/badge/version-alpha-blue)
![Status](https://img.shields.io/badge/status-in%20development-yellow)

## 🌍 Welcome to the World of Nymirith

Nymirith is an immersive, text-based multiplayer adventure game inspired by classic MUDs (Multi-User Dungeons). Explore procedurally generated landscapes, battle fearsome creatures, gather resources, and interact with other adventurers in a rich fantasy world.

**[Play Now](https://nymirith.joshua.kitchen/)** | [Report a Bug](https://github.com/joshuakitchen/adventure-game/issues)

> 🚧 **Note:** Nymirith is actively under development. The game is very much a work in progress, developed because I wanted to learn about WebSockets and was interested in classic MUD's at the time.

## ✨ Features

- **Multiplayer Experience** - Adventure alongside other players in a shared persistent world
- **Procedural World Generation** - Explore diverse biomes including forests, mountains, plains, and seas
- **Dynamic Combat System** - Battle various creatures from harmless rabbits to fearsome bears
- **Resource Gathering** - Scavenge for herbs, rocks, sticks, and other valuable materials
- **Character Progression** - Develop skills like herbalism and gain experience as you adventure
- **Text-based Interface** - Experience the rich world through descriptive text and your imagination
- **Command or Sentence Input** - Interact with the world using either command-based or natural language input

## 🎮 Gameplay Preview

```
@green@Welcome to Nymirith!@res@
You are standing in a lush forest. Tall trees surround you, their branches swaying gently in the breeze.
To the north, you can see mountains in the distance.
A small rabbit hops nearby, unaware of your presence.

> look around

You carefully observe your surroundings. You notice:
- A @yellow@fallen log@res@ that might contain useful items
- Several @green@sagewort plants@res@ growing near a large rock
- A narrow @brown@path@res@ leading east
```

## 🔧 Tech Stack

- **Backend**: Python with FastAPI, WebSockets for real-time gameplay
- **Frontend**: TypeScript with Solid.js for a responsive web interface
- **Deployment**: Docker and Nginx for containerized deployment

## 🚀 Getting Started

### Requirements

#### Local Development
- [NodeJS](https://nodejs.org/en/)
- [Python](https://www.python.org/)

#### Production Deployment
- [Docker](https://www.docker.com/)

### Installation & Setup

#### VSCode (Recommended)

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/adventure-game.git
   cd adventure-game
   ```

2. Install frontend dependencies
   ```bash
   cd web
   npm install
   ```

3. Install backend dependencies
   ```bash
   cd ../api
   pip install -r requirements.txt
   ```

4. Run using the VSCode launch configurations

#### Docker Setup

```bash
docker-compose up -d
```

## 🧪 Project Structure

- `api/` - Python backend with FastAPI
  - `adventure_api/` - Core API functionality
  - `game/` - Game logic and mechanics
- `web/` - TypeScript/Solid.js frontend
  - `src/client/` - Frontend application code
  - `src/server/` - Server rendering setup

## 📝 License

This project is not under a distribution license. All rights reserved.

## 👤 Author

- Created with ❤️ by Joshua
