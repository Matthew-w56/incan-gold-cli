#!/usr/bin/env python3

import random
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

class HazardType(Enum):
    SNAKE = "Snake"
    SPIDER = "Spider"
    MUMMY = "Mummy"
    FIRE = "Fire"
    COLLAPSE = "Collapse"

class CardType(Enum):
    TREASURE = "treasure"
    HAZARD = "hazard"
    ARTIFACT = "artifact"

class TreasureType(Enum):
    TURQUOISE = 1
    OBSIDIAN = 5
    GOLD = 10

@dataclass
class Card:
    card_type: CardType
    value: int = 0
    hazard_type: Optional[HazardType] = None
    name: str = ""

class Player:
    def __init__(self, name: str, is_human: bool = False):
        self.name = name
        self.is_human = is_human
        self.tent_treasures = {TreasureType.TURQUOISE: 0, TreasureType.OBSIDIAN: 0, TreasureType.GOLD: 0}
        self.artifacts = 0
        self.round_treasures = {TreasureType.TURQUOISE: 0, TreasureType.OBSIDIAN: 0, TreasureType.GOLD: 0}
        self.in_temple = True
        self.total_score = 0

    def add_treasure_to_tent(self, treasure_type: TreasureType, amount: int):
        self.tent_treasures[treasure_type] += amount

    def add_treasure_to_round(self, treasure_type: TreasureType, amount: int):
        self.round_treasures[treasure_type] += amount

    def move_round_treasures_to_tent(self):
        for treasure_type in TreasureType:
            self.tent_treasures[treasure_type] += self.round_treasures[treasure_type]
            self.round_treasures[treasure_type] = 0

    def lose_round_treasures(self):
        self.round_treasures = {TreasureType.TURQUOISE: 0, TreasureType.OBSIDIAN: 0, TreasureType.GOLD: 0}

    def calculate_score(self):
        score = 0
        for treasure_type, amount in self.tent_treasures.items():
            score += amount * treasure_type.value

        # Artifact scoring: first 3 worth 5 each, next 2 worth 10 each
        if self.artifacts <= 3:
            score += self.artifacts * 5
        else:
            score += 3 * 5 + (self.artifacts - 3) * 10

        self.total_score = score
        return score

    def reset_for_round(self):
        self.round_treasures = {TreasureType.TURQUOISE: 0, TreasureType.OBSIDIAN: 0, TreasureType.GOLD: 0}
        self.in_temple = True

class AIPlayer(Player):
    def __init__(self, name: str):
        super().__init__(name, is_human=False)
        self.risk_tolerance = random.uniform(0.3, 0.8)  # How risk-averse this AI is

    def make_decision(self, game_state) -> Tuple[bool, str]:
        """Returns (decision, reasoning) - True to continue, False to leave temple"""
        # Factor in current hazards seen
        hazard_counts = game_state['hazard_counts']
        max_hazards = max(hazard_counts.values()) if hazard_counts else 0
        hazards_at_one = sum(1 for count in hazard_counts.values() if count == 1)

        # Factor in round treasures accumulated
        round_treasure_value = sum(amount * ttype.value for ttype, amount in self.round_treasures.items())

        # Factor in how many players are left
        players_remaining = game_state['players_remaining']

        # Base decision on risk tolerance and current situation
        risk_factor = max_hazards / 2.0  # Higher risk if we've seen more hazards
        treasure_factor = min(round_treasure_value / 20.0, 1.0)  # More likely to leave with more treasure
        player_factor = 1.0 / max(players_remaining, 1)  # More likely to stay if fewer players

        # Calculate probability of leaving
        leave_probability = (risk_factor + treasure_factor - player_factor + (1 - self.risk_tolerance)) / 2

        # Add some randomness
        decision = random.random() > leave_probability

        # Generate reasoning
        reasoning_parts = []

        if round_treasure_value > 15:
            reasoning_parts.append(f"carrying {round_treasure_value} treasure")
        elif round_treasure_value > 5:
            reasoning_parts.append("moderate treasure secured")
        else:
            reasoning_parts.append("little treasure so far")

        if hazards_at_one >= 3:
            reasoning_parts.append("many single hazards seen (risky!)")
        elif hazards_at_one >= 2:
            reasoning_parts.append("some hazards revealed")
        elif hazards_at_one == 1:
            reasoning_parts.append("one hazard seen")
        else:
            reasoning_parts.append("no hazards yet")

        if players_remaining <= 2:
            reasoning_parts.append("few players left (good treasure share)")
        elif players_remaining == 3:
            reasoning_parts.append("moderate competition")
        else:
            reasoning_parts.append("crowded temple")

        # Add personality factor
        if self.risk_tolerance > 0.6:
            personality = "bold nature"
        elif self.risk_tolerance < 0.4:
            personality = "cautious approach"
        else:
            personality = "balanced strategy"

        reasoning_parts.append(personality)

        reasoning = f"({', '.join(reasoning_parts)})"

        return decision, reasoning

class Game:
    def __init__(self):
        self.players = []
        self.current_round = 0
        self.max_rounds = 5
        self.deck = []
        self.path = []  # Cards revealed this round
        self.hazard_counts = defaultdict(int)
        self.artifacts_on_path = []
        self.leaderboard_file = "incan_gold_leaderboard.json"

        # Color codes for terminal
        self.COLORS = {
            'RED': '\033[91m',
            'GREEN': '\033[92m',
            'YELLOW': '\033[93m',
            'BLUE': '\033[94m',
            'MAGENTA': '\033[95m',
            'CYAN': '\033[96m',
            'WHITE': '\033[97m',
            'BOLD': '\033[1m',
            'END': '\033[0m'
        }

    def create_deck(self):
        """Create the full deck for one round"""
        cards = []

        # Add treasure cards (values 1-15, multiple of some)
        treasure_values = [1,2,3,4,5,5,6,7,8,9,10,11,12,13,14,15]
        for value in treasure_values:
            cards.append(Card(CardType.TREASURE, value=value, name=f"Treasure {value}"))

        # Add hazard cards (2 of each type)
        for hazard_type in HazardType:
            for _ in range(2):
                cards.append(Card(CardType.HAZARD, hazard_type=hazard_type, name=hazard_type.value))

        # Add one artifact per round
        cards.append(Card(CardType.ARTIFACT, value=0, name="Ancient Artifact"))

        return cards

    def setup_round(self):
        """Setup a new round"""
        self.current_round += 1
        self.deck = self.create_deck()
        random.shuffle(self.deck)
        self.path = []
        self.hazard_counts = defaultdict(int)
        self.artifacts_on_path = []

        # Reset all players for the round
        for player in self.players:
            player.reset_for_round()

    def draw_ascii_card(self, card: Card) -> List[str]:
        """Generate ASCII art for a card"""
        if card.card_type == CardType.TREASURE:
            return [
                "┌─────────────┐",
                f"│   TREASURE  │",
                f"│             │",
                f"│     {card.value:2d}      │",
                f"│             │",
                f"│  ♦ ♦ ♦ ♦ ♦  │",
                "└─────────────┘"
            ]
        elif card.card_type == CardType.HAZARD:
            hazard_symbols = {
                HazardType.SNAKE: "🐍",
                HazardType.SPIDER: "🕷",
                HazardType.MUMMY: "🧟",
                HazardType.FIRE: "🔥",
                HazardType.COLLAPSE: "💥"
            }
            symbol = hazard_symbols.get(card.hazard_type, "⚠")
            return [
                "┌─────────────┐",
                f"│   HAZARD    │",
                f"│             │",
                f"│      {symbol}      │",
                f"│             │",
                f"│{card.hazard_type.value:^13}│",
                "└─────────────┘"
            ]
        else:  # ARTIFACT
            return [
                "┌─────────────┐",
                f"│  ARTIFACT   │",
                f"│             │",
                f"│     ⚱️      │",
                f"│             │",
                f"│   ANCIENT   │",
                "└─────────────┘"
            ]

    def print_colored(self, text: str, color: str = 'WHITE'):
        """Print text with color"""
        print(f"{self.COLORS[color]}{text}{self.COLORS['END']}")

    def clear_screen(self):
        """Clear the console screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def display_game_state(self):
        """Display current game state with full screen layout"""
        self.clear_screen()

        # Header
        print("=" * 80)
        self.print_colored(f"🏛️  INCAN GOLD - ROUND {self.current_round}/5 - TEMPLE EXPLORATION  🏛️", 'BOLD')
        print("=" * 80)

        # Player status bar
        in_temple = [p for p in self.players if p.in_temple]
        at_camp = [p for p in self.players if not p.in_temple]

        if in_temple:
            self.print_colored(f"👥 In Temple: {', '.join([p.name for p in in_temple])}", 'GREEN')
        if at_camp:
            self.print_colored(f"🏕️  At Camp: {', '.join([p.name for p in at_camp])}", 'BLUE')

        # Hazard status
        if any(count > 0 for count in self.hazard_counts.values()):
            hazard_display = []
            for hazard_type, count in self.hazard_counts.items():
                if count > 0:
                    danger = "⚠️ " if count == 1 else "🚨 "
                    hazard_display.append(f"{danger}{hazard_type.value}: {count}")
            self.print_colored(f"☠️  Hazards: {', '.join(hazard_display)}", 'RED')

        # Path treasures
        path_treasures = sum(getattr(card, 'remaining_treasure', 0) for card in self.path)
        if path_treasures > 0:
            self.print_colored(f"💰 Unclaimed treasure on path: {path_treasures}", 'YELLOW')

        print("-" * 80)

        # Display cards in the path
        if self.path:
            self.print_colored("🗂️  CARDS REVEALED THIS ROUND:", 'BOLD')
            self.display_card_path()
        else:
            self.print_colored("🚪 The temple entrance beckons... No cards revealed yet.", 'CYAN')

        print("-" * 80)

    def display_card_path(self):
        """Display all cards revealed this round in rows"""
        if not self.path:
            return

        cards_per_row = 5  # Show 5 cards per row

        for start_idx in range(0, len(self.path), cards_per_row):
            end_idx = min(start_idx + cards_per_row, len(self.path))
            row_cards = self.path[start_idx:end_idx]

            # Get ASCII art for each card
            card_arts = [self.draw_ascii_card(card) for card in row_cards]

            # Print each line of the ASCII art side by side
            for line_idx in range(7):  # Cards are 7 lines tall
                line_parts = []
                for card_art in card_arts:
                    line_parts.append(card_art[line_idx])
                print("  ".join(line_parts))

            # Show any remaining treasure on cards
            treasure_info = []
            for i, card in enumerate(row_cards, start_idx + 1):
                remaining = getattr(card, 'remaining_treasure', 0)
                if remaining > 0:
                    treasure_info.append(f"Card {i}: {remaining} treasure left")

            if treasure_info:
                print("  " + " | ".join(treasure_info))

            print()  # Empty line between rows

    def get_human_decision(self) -> Optional[bool]:
        """Get decision from human player. Returns None if quitting game."""
        while True:
            choice = input("\nDo you want to (C)ontinue exploring, (L)eave the temple, or (Q)uit game? ").upper().strip()
            if choice in ['C', 'CONTINUE']:
                return True
            elif choice in ['L', 'LEAVE']:
                return False
            elif choice in ['Q', 'QUIT']:
                return None
            else:
                print("Please enter 'C' to continue, 'L' to leave, or 'Q' to quit.")

    def process_card(self, card: Card) -> bool:
        """Process a drawn card. Returns False if round should end."""
        self.path.append(card)

        # Show the new card immediately with the full display
        self.display_game_state()

        if card.card_type == CardType.TREASURE:
            self.print_colored(f"💰 TREASURE DISCOVERED! Value: {card.value}", 'YELLOW')
            return self.distribute_treasure(card)

        elif card.card_type == CardType.HAZARD:
            self.hazard_counts[card.hazard_type] += 1
            if self.hazard_counts[card.hazard_type] == 1:
                self.print_colored(f"⚠️  HAZARD ENCOUNTERED: {card.hazard_type.value} (first one)", 'RED')
                return True
            else:
                self.print_colored(f"🚨 DISASTER! SECOND {card.hazard_type.value.upper()}! Temple collapses!", 'RED')
                self.print_colored("All temple explorers lose their round treasures and flee!", 'RED')
                return False  # Round ends

        else:  # ARTIFACT
            self.artifacts_on_path.append(card)
            self.print_colored("✨ ANCIENT ARTIFACT DISCOVERED! It will go to the next person who leaves alone.", 'CYAN')
            return True

    def distribute_treasure(self, card: Card) -> bool:
        """Distribute treasure among players in temple"""
        players_in_temple = [p for p in self.players if p.in_temple]
        if not players_in_temple:
            return True

        treasure_per_player = card.value // len(players_in_temple)
        remaining_treasure = card.value % len(players_in_temple)

        # Distribute treasure (always as turquoise for simplicity, could be enhanced)
        for player in players_in_temple:
            if treasure_per_player > 0:
                player.add_treasure_to_round(TreasureType.TURQUOISE, treasure_per_player)

        # Store remaining treasure on the card
        card.remaining_treasure = remaining_treasure

        if treasure_per_player > 0:
            self.print_colored(f"Each explorer receives {treasure_per_player} treasure(s)", 'GREEN')
        if remaining_treasure > 0:
            self.print_colored(f"{remaining_treasure} treasure(s) left on the path", 'YELLOW')

        return True

    def get_player_decisions(self) -> Optional[Dict[Player, bool]]:
        """Get decisions from all players in temple. Returns None if player quits."""
        decisions = {}
        players_in_temple = [p for p in self.players if p.in_temple]

        # Get human decisions first
        for player in players_in_temple:
            if player.is_human:
                self.display_player_status(player)
                human_decision = self.get_human_decision()
                if human_decision is None:
                    return None  # Player wants to quit
                decisions[player] = human_decision

        # Get AI decisions
        game_state = {
            'hazard_counts': dict(self.hazard_counts),
            'players_remaining': len(players_in_temple),
            'round': self.current_round
        }

        # Display AI decisions in aligned format
        ai_players = [p for p in players_in_temple if not p.is_human]
        if ai_players:
            print("\n🤖 AI Decisions:")
            max_name_length = max(len(p.name) for p in ai_players)

            for player in ai_players:
                decision, reasoning = player.make_decision(game_state)
                decisions[player] = decision
                decision_text = "Continue" if decision else "Return to camp!"
                print(f"   {player.name:<{max_name_length}}:  {decision_text}")

        return decisions

    def display_player_status(self, player: Player):
        """Display current player status"""
        print(f"\n📊 {player.name}'s Status:")
        round_value = sum(amount for amount in player.round_treasures.values())
        tent_value = sum(amount * ttype.value for ttype, amount in player.tent_treasures.items())

        print(f"   🎒 Round treasures: {round_value} (at risk)")
        print(f"   🏕️  Safe in tent: {tent_value} points")
        print(f"   ⚱️  Artifacts: {player.artifacts}")

        if round_value > 0:
            self.print_colored(f"   ⚠️  You stand to lose {round_value} treasures if a second hazard appears!", 'YELLOW')

    def process_departures(self, decisions: Dict[Player, bool]):
        """Process players leaving the temple"""
        leaving_players = [p for p, decision in decisions.items() if not decision]

        if not leaving_players:
            return

        # Move round treasures to tent for leaving players
        for player in leaving_players:
            player.move_round_treasures_to_tent()
            player.in_temple = False

        # Distribute path treasures among leaving players
        total_path_treasure = sum(getattr(card, 'remaining_treasure', 0) for card in self.path)
        if total_path_treasure > 0 and leaving_players:
            treasure_per_leaver = total_path_treasure // len(leaving_players)
            remaining = total_path_treasure % len(leaving_players)

            for player in leaving_players:
                if treasure_per_leaver > 0:
                    player.add_treasure_to_tent(TreasureType.TURQUOISE, treasure_per_leaver)

            self.print_colored(f"Departing explorers split {total_path_treasure} path treasures", 'GREEN')

            # Clear path treasures
            for card in self.path:
                if hasattr(card, 'remaining_treasure'):
                    card.remaining_treasure = 0

        # Handle artifacts
        if len(leaving_players) == 1 and self.artifacts_on_path:
            leaving_players[0].artifacts += len(self.artifacts_on_path)
            self.print_colored(f"{leaving_players[0].name} gets {len(self.artifacts_on_path)} artifact(s)!", 'CYAN')
            self.artifacts_on_path = []

    def play_round(self) -> bool:
        """Play one complete round. Returns False if player quits."""
        self.setup_round()

        # Initial display
        self.display_game_state()
        input(f"\n🏛️  ROUND {self.current_round} BEGINS! Press Enter to start exploring...")

        # Draw the first card immediately without asking for decisions
        if self.deck:
            card = self.deck.pop(0)
            continue_round = self.process_card(card)

            if not continue_round:
                # First card was a second hazard - extremely rare but possible
                for player in self.players:
                    player.lose_round_treasures()
                input("\nPress Enter to continue...")
                return True

            input("\nPress Enter to continue...")

        while True:
            players_in_temple = [p for p in self.players if p.in_temple]

            if not players_in_temple:
                self.display_game_state()
                self.print_colored("🏕️  All explorers have returned to camp safely!", 'BLUE')
                input("\nPress Enter to continue...")
                break

            if not self.deck:
                self.display_game_state()
                self.print_colored("📜 The temple's secrets have been exhausted! No more cards remain.", 'YELLOW')
                input("\nPress Enter to continue...")
                break

            # Show current state and get player decisions
            self.display_game_state()

            # Get player decisions
            decisions = self.get_player_decisions()
            if decisions is None:
                # Player chose to quit
                self.print_colored("Game ended by player choice. Thanks for playing!", 'YELLOW')
                return False

            # Process departures
            self.process_departures(decisions)

            # Check if anyone is still in temple
            remaining_players = [p for p in self.players if p.in_temple]
            if not remaining_players:
                continue  # Go back to check loop conditions

            # Draw and process next card
            input("\n🎴 Press Enter to draw the next temple card...")

            card = self.deck.pop(0)
            continue_round = self.process_card(card)

            if not continue_round:
                # Hazard triggered - all remaining players lose round treasures
                for player in remaining_players:
                    player.lose_round_treasures()
                input("\nPress Enter to continue...")
                break

        return True  # Round completed successfully

    def display_final_scores(self):
        """Display final game results"""
        print("\n" + "="*60)
        self.print_colored("🏆 FINAL RESULTS 🏆", 'BOLD')
        print("="*60)

        # Calculate and sort scores
        for player in self.players:
            player.calculate_score()

        sorted_players = sorted(self.players, key=lambda p: (-p.total_score, -p.artifacts))

        for i, player in enumerate(sorted_players, 1):
            place = f"{i}{'st' if i==1 else 'nd' if i==2 else 'rd' if i==3 else 'th'}"
            color = 'YELLOW' if i == 1 else 'WHITE'

            self.print_colored(f"{place} Place: {player.name}", color)
            print(f"   Score: {player.total_score}")
            print(f"   Turquoise: {player.tent_treasures[TreasureType.TURQUOISE]}")
            print(f"   Obsidian: {player.tent_treasures[TreasureType.OBSIDIAN]}")
            print(f"   Gold: {player.tent_treasures[TreasureType.GOLD]}")
            print(f"   Artifacts: {player.artifacts}")
            print()

        return sorted_players[0]  # Winner

    def save_leaderboard(self, winner: Player):
        """Save winner to leaderboard"""
        try:
            if os.path.exists(self.leaderboard_file):
                with open(self.leaderboard_file, 'r') as f:
                    leaderboard = json.load(f)
            else:
                leaderboard = []

            # Only save human player wins
            if winner.is_human:
                leaderboard.append({
                    'name': winner.name,
                    'score': winner.total_score,
                    'artifacts': winner.artifacts
                })

                # Sort by score, then artifacts
                leaderboard.sort(key=lambda x: (-x['score'], -x['artifacts']))

                # Keep top 10
                leaderboard = leaderboard[:10]

                with open(self.leaderboard_file, 'w') as f:
                    json.dump(leaderboard, f, indent=2)

                self.print_colored("Score saved to leaderboard!", 'GREEN')

        except Exception as e:
            print(f"Error saving leaderboard: {e}")

    def display_leaderboard(self):
        """Display the leaderboard"""
        try:
            if not os.path.exists(self.leaderboard_file):
                print("No leaderboard data found.")
                return

            with open(self.leaderboard_file, 'r') as f:
                leaderboard = json.load(f)

            if not leaderboard:
                print("Leaderboard is empty.")
                return

            print("\n" + "="*40)
            self.print_colored("🏆 LEADERBOARD 🏆", 'BOLD')
            print("="*40)

            for i, entry in enumerate(leaderboard, 1):
                print(f"{i:2}. {entry['name']:<15} {entry['score']:>6} pts  ({entry['artifacts']} artifacts)")

        except Exception as e:
            print(f"Error loading leaderboard: {e}")

    def play_game(self):
        """Main game loop"""
        # Setup players
        print("Welcome to Incan Gold!")
        player_name = input("Enter your name: ").strip() or "Explorer"

        self.players = [
            Player(player_name, is_human=True),
            AIPlayer("Maya the Bold"),
            AIPlayer("Diego the Cautious"),
            AIPlayer("Carmen the Lucky")
        ]

        # Play 5 rounds
        for round_num in range(1, 6):
            if not self.play_round():
                # Player quit mid-game
                return

            if round_num < 5:
                input(f"\nRound {round_num} complete! Press Enter to continue to round {round_num + 1}...")

        # Display final results
        winner = self.display_final_scores()
        self.save_leaderboard(winner)

        # Show leaderboard
        print()
        self.display_leaderboard()

def main():
    """Main entry point"""
    try:
        game = Game()

        while True:
            print("\n" + "="*50)
            print("🏛️  INCAN GOLD - TEMPLE EXPLORER  🏛️")
            print("="*50)
            print("1. Play Game")
            print("2. View Leaderboard")
            print("3. Quit")

            choice = input("\nSelect option (1-3): ").strip()

            if choice == '1':
                game.play_game()
            elif choice == '2':
                game.display_leaderboard()
            elif choice == '3':
                print("Thanks for playing Incan Gold!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()