# Incan Gold CLI

A faithful command-line implementation of the popular board game **Incan Gold** (also known as Diamant). Explore ancient Incan temples, collect treasures, and outwit your AI opponents in this thrilling push-your-luck adventure!

## 🏛️ Features

- **Complete Original Rules**: Full implementation with artifacts, hazards, and all 5 expedition rounds
- **ASCII Art Cards**: Beautiful terminal-based card representations
- **Smart AI Opponents**: Three AI players with different risk tolerance levels
- **Colored Terminal Output**: Rich visual experience with terminal colors
- **Persistent Leaderboard**: Track your best scores across games
- **Cross-Platform**: Works on Linux, macOS, and Windows (with appropriate Python setup)

## 🚀 Quick Start

### Prerequisites
- Python 3.6 or higher
- Terminal/Command prompt with color support

### Installation & Running

1. **Clone or download** this repository to your local machine
2. **Make the launcher executable** (Linux/macOS):
   ```bash
   chmod +x incan-gold
   ```
3. **Run the game**:
   ```bash
   ./incan-gold
   ```

### Command Line Options

```bash
./incan-gold --help     # Show help and usage information
./incan-gold --version  # Display version information
./incan-gold --rules    # Show complete game rules
./incan-gold            # Start the game
```

## 🎮 How to Play

### Game Overview
You and three AI explorers venture into ancient temples over 5 rounds. Each round, cards are revealed one by one. After each card, you must decide: **continue exploring** for more treasure, or **return to camp** to secure what you've found.

### Card Types

**🟡 Treasure Cards (1-15)**
- Split treasure value among all players still in the temple
- Remainder stays on the path for departing players

**🔴 Hazard Cards (5 types: Snake, Spider, Mummy, Fire, Collapse)**
- First of each type: No effect
- Second of same type: All temple explorers lose their round treasures!

**🔵 Artifact Cards**
- Worth 5-10 points at game end
- Only goes to a player who leaves the temple alone

### Scoring
- **Turquoise**: 1 point each
- **Obsidian**: 5 points each
- **Gold**: 10 points each
- **Artifacts**: First 3 worth 5 points, next 2 worth 10 points each

### Strategy Tips
- 🎯 Balance greed with caution - know when to quit!
- 👀 Watch what hazards have been revealed
- 🏃 Sometimes it pays to be the only one leaving
- 💎 Path treasures are split among departing players

## 🤖 AI Opponents

Meet your three AI companions:

- **Maya the Bold**: High risk tolerance, stays in temples longer
- **Diego the Cautious**: Conservative player, leaves early to secure treasures
- **Carmen the Lucky**: Moderate risk-taker with balanced play

Each AI has unique decision-making algorithms that consider:
- Current hazards revealed
- Treasures accumulated this round
- Number of players remaining
- Individual risk tolerance

## 📊 Leaderboard

The game maintains a persistent leaderboard of your best scores. Only human player victories are recorded, and the top 10 scores are preserved between game sessions.

## 🛠️ Technical Details

### File Structure
```
incan-gold-cli/
├── incan-gold              # Bash launcher script
├── incan_gold.py          # Main Python game implementation
├── README.md              # This file
└── incan_gold_leaderboard.json  # Leaderboard data (created automatically)
```

### Dependencies
- **Python 3.6+**: Core language requirement
- **Standard Library Only**: No external dependencies required

### Compatibility
- **Linux**: Full support with colored terminal output
- **macOS**: Full support with colored terminal output
- **Windows**: Supported with Windows Terminal or PowerShell (colors may vary)

## 🎨 Visual Features

The game includes:
- Rich ASCII art for treasure, hazard, and artifact cards
- Color-coded game states and player actions
- Formatted game displays with clear information hierarchy
- Progress tracking through each expedition round

## 🏆 Game Modes

1. **Play Game**: Full 5-round expedition with scoring
2. **View Leaderboard**: Check your best previous scores
3. **Rules Display**: Complete rule reference

## 🐛 Troubleshooting

**Game won't start**
- Ensure Python 3 is installed: `python3 --version`
- Check script permissions: `chmod +x incan-gold`

**Colors not displaying**
- Try a different terminal (Windows Terminal, iTerm2, etc.)
- Colors work best with modern terminal emulators

**Leaderboard issues**
- Leaderboard file is created automatically on first win
- Check write permissions in the game directory

## 🎲 Game Balance

The AI opponents use sophisticated decision-making that considers:
- Risk assessment based on revealed hazards
- Treasure accumulation vs. security trade-offs
- Player count dynamics
- Individual personality traits

This creates engaging gameplay where each opponent feels distinct and challenging.

## 📝 License

This is a fan implementation of the Incan Gold board game for educational and entertainment purposes.

## 🎉 Enjoy!

May your temples be rich with treasure and your escapes perfectly timed!

---

*Happy exploring, adventurer! 🏛️💎*