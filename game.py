#!/usr/bin/env python3
"""
Main game logic for Incan Gold CLI game.
"""

import random
import json
import os
from typing import List, Dict, Optional
from collections import defaultdict

from cards import Card, CardType, TreasureType, create_deck
from player import Player, AIPlayer
from ui import GameUI
from utils import get_validated_player_name, print_colored
from config import (
    MAX_ROUNDS, LEADERBOARD_FILE, LEADERBOARD_MAX_ENTRIES,
    DEFAULT_AI_NAMES, MAX_PLAYERS, MIN_PLAYERS
)


class Game:
    def __init__(self, num_ai_players: int = 3):
        self.players = []
        self.current_round = 0
        self.max_rounds = MAX_ROUNDS
        self.deck = []
        self.path = []  # Cards revealed this round
        self.hazard_counts = defaultdict(int)
        self.artifacts_on_path = []
        self.leaderboard_file = LEADERBOARD_FILE
        self.ui = GameUI()
        self.num_ai_players = max(MIN_PLAYERS, min(num_ai_players, MAX_PLAYERS - 1))  # -1 for human player

    def setup_players(self):
        """Setup human and AI players for the game"""
        # Get human player
        print("Welcome to Incan Gold!")
        player_name = get_validated_player_name("Enter your name: ", "Explorer")
        human_player = Player(player_name, is_human=True)
        self.players = [human_player]

        # Add AI players
        ai_names = DEFAULT_AI_NAMES[:self.num_ai_players]
        for name in ai_names:
            self.players.append(AIPlayer(name))

    def setup_round(self):
        """Setup a new round"""
        self.current_round += 1
        self.deck = create_deck()
        random.shuffle(self.deck)
        self.path = []
        self.hazard_counts = defaultdict(int)
        self.artifacts_on_path = []

        # Reset all players for the round
        for player in self.players:
            player.reset_for_round()

    def process_card(self, card: Card) -> bool:
        """Process a drawn card. Returns False if round should end."""
        self.path.append(card)

        # Show the new card immediately with the full display
        game_state = {
            'current_round': self.current_round,
            'deck_remaining': len(self.deck)
        }
        self.ui.display_game_state(game_state, self.players, self.path, self.hazard_counts)
        self.ui.display_card_drawn(card)

        if card.card_type == CardType.TREASURE:
            return self.distribute_treasure(card)
        elif card.card_type == CardType.HAZARD:
            return self.process_hazard(card)
        else:  # ARTIFACT
            self.artifacts_on_path.append(card)
            return True

    def distribute_treasure(self, card: Card) -> bool:
        """Distribute treasure among players in temple"""
        players_in_temple = [p for p in self.players if p.in_temple]
        if not players_in_temple:
            return True

        treasure_per_player = card.value // len(players_in_temple)
        remaining_treasure = card.value % len(players_in_temple)

        # Distribute treasure (always as turquoise for simplicity)
        for player in players_in_temple:
            if treasure_per_player > 0:
                player.add_treasure_to_round(TreasureType.TURQUOISE, treasure_per_player)

        # Store remaining treasure on the card
        card.remaining_treasure = remaining_treasure

        self.ui.display_treasure_distribution(treasure_per_player, remaining_treasure)
        return True

    def process_hazard(self, card: Card) -> bool:
        """Process hazard card. Returns False if round should end."""
        self.hazard_counts[card.hazard_type] += 1
        count = self.hazard_counts[card.hazard_type]

        self.ui.display_hazard_result(card.hazard_type, count, count >= 2)

        return count < 2  # Round ends if second hazard of same type

    def get_player_decisions(self) -> Optional[Dict[Player, bool]]:
        """Get decisions from all players in temple. Returns None if player quits."""
        decisions = {}
        players_in_temple = [p for p in self.players if p.in_temple]

        # Get human decisions first
        for player in players_in_temple:
            if player.is_human:
                self.ui.display_player_status(player)
                human_decision = self.ui.get_human_decision()
                if human_decision is None:
                    return None  # Player wants to quit
                decisions[player] = human_decision

        # Get AI decisions
        game_state = {
            'hazard_counts': dict(self.hazard_counts),
            'players_remaining': len(players_in_temple),
            'round': self.current_round
        }

        # Get AI decisions and reasoning
        ai_players = [p for p in players_in_temple if not p.is_human]
        ai_decision_data = {}

        for player in ai_players:
            decision, reasoning = player.make_decision(game_state)
            decisions[player] = decision
            ai_decision_data[player] = (decision, reasoning)

        # Display AI decisions
        self.ui.display_ai_decisions(ai_players, ai_decision_data)

        return decisions

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

            for player in leaving_players:
                if treasure_per_leaver > 0:
                    player.add_treasure_to_tent(TreasureType.TURQUOISE, treasure_per_leaver)

            self.ui.display_departures_summary(leaving_players, total_path_treasure)

            # Clear path treasures
            for card in self.path:
                if hasattr(card, 'remaining_treasure'):
                    card.remaining_treasure = 0

        # Handle artifacts - only if exactly one player leaves
        if len(leaving_players) == 1 and self.artifacts_on_path:
            leaving_players[0].artifacts += len(self.artifacts_on_path)
            self.ui.display_artifact_award(leaving_players[0], len(self.artifacts_on_path))
            self.artifacts_on_path = []

    def play_round(self) -> bool:
        """Play one complete round. Returns False if player quits."""
        self.setup_round()

        # Initial display
        game_state = {
            'current_round': self.current_round,
            'deck_remaining': len(self.deck)
        }
        self.ui.display_game_state(game_state, self.players, self.path, self.hazard_counts)
        self.ui.display_round_start(self.current_round)

        # Draw the first card immediately
        if self.deck:
            card = self.deck.pop(0)
            continue_round = self.process_card(card)

            if not continue_round:
                # First card caused round to end
                for player in self.players:
                    player.lose_round_treasures()
                input("\nPress Enter to continue...")
                return True

            input("\nPress Enter to continue...")

        # Main game loop
        while True:
            players_in_temple = [p for p in self.players if p.in_temple]

            # Check end conditions
            if not players_in_temple:
                game_state = {
                    'current_round': self.current_round,
                    'deck_remaining': len(self.deck)
                }
                self.ui.display_game_state(game_state, self.players, self.path, self.hazard_counts)
                self.ui.display_round_end_messages(players_in_temple, False)
                input("\nPress Enter to continue...")
                break

            if not self.deck:
                game_state = {
                    'current_round': self.current_round,
                    'deck_remaining': len(self.deck)
                }
                self.ui.display_game_state(game_state, self.players, self.path, self.hazard_counts)
                self.ui.display_round_end_messages(players_in_temple, True)
                input("\nPress Enter to continue...")
                break

            # Show current state and get player decisions
            game_state = {
                'current_round': self.current_round,
                'deck_remaining': len(self.deck)
            }
            self.ui.display_game_state(game_state, self.players, self.path, self.hazard_counts)

            # Get player decisions
            decisions = self.get_player_decisions()
            if decisions is None:
                print_colored("Game ended by player choice. Thanks for playing!", 'YELLOW')
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

        return True

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

                # Keep top entries
                leaderboard = leaderboard[:LEADERBOARD_MAX_ENTRIES]

                with open(self.leaderboard_file, 'w') as f:
                    json.dump(leaderboard, f, indent=2)

                print_colored("Score saved to leaderboard!", 'GREEN')

        except IOError as e:
            print_colored(f"Error saving leaderboard: {e}", 'RED')
        except json.JSONDecodeError as e:
            print_colored(f"Error reading leaderboard file: {e}", 'RED')

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
            print_colored("🏆 LEADERBOARD 🏆", 'BOLD')
            print("="*40)

            for i, entry in enumerate(leaderboard, 1):
                print(f"{i:2}. {entry['name']:<15} {entry['score']:>6} pts  ({entry['artifacts']} artifacts)")

        except IOError as e:
            print_colored(f"Error loading leaderboard: {e}", 'RED')
        except json.JSONDecodeError as e:
            print_colored(f"Error parsing leaderboard file: {e}", 'RED')

    def play_game(self):
        """Main game loop"""
        self.setup_players()

        # Play all rounds
        for round_num in range(1, self.max_rounds + 1):
            if not self.play_round():
                # Player quit mid-game
                return

            if round_num < self.max_rounds:
                input(f"\nRound {round_num} complete! Press Enter to continue to round {round_num + 1}...")

        # Display final results
        winner = self.ui.display_final_scores(self.players)
        self.save_leaderboard(winner)

        # Show leaderboard
        print()
        self.display_leaderboard()