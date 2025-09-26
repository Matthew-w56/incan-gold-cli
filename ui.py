#!/usr/bin/env python3
"""
User interface functions for Incan Gold CLI game.
"""

from typing import List, Optional
from cards import Card, draw_ascii_card, TreasureType
from player import Player
from utils import clear_screen, print_colored
from config import CARDS_PER_ROW, SEPARATOR_LENGTH, HEADER_SEPARATOR, SUB_SEPARATOR


class GameUI:
    """Handles all user interface operations for the game"""

    def __init__(self):
        pass

    def display_game_state(self, game_state: dict, players: List[Player], path: List[Card], hazard_counts: dict):
        """Display current game state with full screen layout"""
        clear_screen()

        # Header
        print(HEADER_SEPARATOR * SEPARATOR_LENGTH)
        print_colored(f"🏛️  INCAN GOLD - ROUND {game_state['current_round']}/5 - TEMPLE EXPLORATION  🏛️", 'BOLD')
        print(HEADER_SEPARATOR * SEPARATOR_LENGTH)

        # Player status bar
        in_temple = [p for p in players if p.in_temple]
        at_camp = [p for p in players if not p.in_temple]

        if in_temple:
            print_colored(f"👥 In Temple: {', '.join([p.name for p in in_temple])}", 'GREEN')
        if at_camp:
            print_colored(f"🏕️  At Camp: {', '.join([p.name for p in at_camp])}", 'BLUE')

        # Hazard status
        if any(count > 0 for count in hazard_counts.values()):
            hazard_display = []
            for hazard_type, count in hazard_counts.items():
                if count > 0:
                    danger = "⚠️ " if count == 1 else "🚨 "
                    hazard_display.append(f"{danger}{hazard_type.value}: {count}")
            print_colored(f"☠️  Hazards: {', '.join(hazard_display)}", 'RED')

        # Path treasures
        path_treasures = sum(getattr(card, 'remaining_treasure', 0) for card in path)
        if path_treasures > 0:
            print_colored(f"💰 Unclaimed treasure on path: {path_treasures}", 'YELLOW')

        print(SUB_SEPARATOR * SEPARATOR_LENGTH)

        # Display cards in the path
        if path:
            print_colored("🗂️  CARDS REVEALED THIS ROUND:", 'BOLD')
            self.display_card_path(path)
        else:
            print_colored("🚪 The temple entrance beckons... No cards revealed yet.", 'CYAN')

        print(SUB_SEPARATOR * SEPARATOR_LENGTH)

    def display_card_path(self, path: List[Card]):
        """Display all cards revealed this round in rows"""
        if not path:
            return

        for start_idx in range(0, len(path), CARDS_PER_ROW):
            end_idx = min(start_idx + CARDS_PER_ROW, len(path))
            row_cards = path[start_idx:end_idx]

            # Get ASCII art for each card
            card_arts = [draw_ascii_card(card) for card in row_cards]

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

    def display_player_status(self, player: Player):
        """Display current player status"""
        print(f"\n📊 {player.name}'s Status:")
        round_value = player.get_round_treasure_value()
        tent_value = player.get_tent_treasure_value()

        print(f"   🎒 Round treasures: {round_value} (at risk)")
        print(f"   🏕️  Safe in tent: {tent_value} points")
        print(f"   ⚱️  Artifacts: {player.artifacts}")

        if round_value > 0:
            print_colored(f"   ⚠️  You stand to lose {round_value} treasures if a second hazard appears!", 'YELLOW')

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

    def display_ai_decisions(self, ai_players: List[Player], decisions: dict):
        """Display AI player decisions in aligned format"""
        if not ai_players:
            return

        print("\n🤖 AI Decisions:")
        max_name_length = max(len(p.name) for p in ai_players)

        for player in ai_players:
            decision, reasoning = decisions[player]
            decision_text = "Continue" if decision else "Return to camp!"
            print(f"   {player.name:<{max_name_length}}:  {decision_text}")

    def display_final_scores(self, players: List[Player]) -> Player:
        """Display final game results and return winner"""
        print("\n" + HEADER_SEPARATOR * 60)
        print_colored("🏆 FINAL RESULTS 🏆", 'BOLD')
        print(HEADER_SEPARATOR * 60)

        # Calculate and sort scores
        for player in players:
            player.calculate_score()

        sorted_players = sorted(players, key=lambda p: (-p.total_score, -p.artifacts))

        for i, player in enumerate(sorted_players, 1):
            place = f"{i}{'st' if i==1 else 'nd' if i==2 else 'rd' if i==3 else 'th'}"
            color = 'YELLOW' if i == 1 else 'WHITE'

            print_colored(f"{place} Place: {player.name}", color)
            print(f"   Score: {player.total_score}")
            print(f"   Turquoise: {player.tent_treasures[TreasureType.TURQUOISE]}")
            print(f"   Obsidian: {player.tent_treasures[TreasureType.OBSIDIAN]}")
            print(f"   Gold: {player.tent_treasures[TreasureType.GOLD]}")
            print(f"   Artifacts: {player.artifacts}")
            print()

        return sorted_players[0]  # Winner

    def show_main_menu(self):
        """Display main menu"""
        print("\n" + HEADER_SEPARATOR * 50)
        print("🏛️  INCAN GOLD - TEMPLE EXPLORER  🏛️")
        print(HEADER_SEPARATOR * 50)
        print("1. Play Game")
        print("2. View Leaderboard")
        print("3. Quit")

    def display_round_start(self, round_num: int):
        """Display round start message"""
        input(f"\n🏛️  ROUND {round_num} BEGINS! Press Enter to start exploring...")

    def display_card_drawn(self, card: Card):
        """Display message for newly drawn card"""
        if card.card_type.value == "treasure":
            print_colored(f"💰 TREASURE DISCOVERED! Value: {card.value}", 'YELLOW')
        elif card.card_type.value == "hazard":
            print_colored(f"⚠️  HAZARD ENCOUNTERED: {card.name}", 'RED')
        else:  # artifact
            print_colored("✨ ANCIENT ARTIFACT DISCOVERED! It will go to the next person who leaves alone.", 'CYAN')

    def display_treasure_distribution(self, treasure_per_player: int, remaining_treasure: int):
        """Display treasure distribution results"""
        if treasure_per_player > 0:
            print_colored(f"Each explorer receives {treasure_per_player} treasure(s)", 'GREEN')
        if remaining_treasure > 0:
            print_colored(f"{remaining_treasure} treasure(s) left on the path", 'YELLOW')

    def display_hazard_result(self, hazard_type, count: int, round_ends: bool):
        """Display hazard encounter results"""
        if count == 1:
            print_colored(f"⚠️  HAZARD ENCOUNTERED: {hazard_type.value} (first one)", 'RED')
        else:
            print_colored(f"🚨 DISASTER! SECOND {hazard_type.value.upper()}! Temple collapses!", 'RED')
            print_colored("All temple explorers lose their round treasures and flee!", 'RED')

    def display_departures_summary(self, leaving_players: List[Player], total_path_treasure: int):
        """Display information about players leaving"""
        if total_path_treasure > 0 and leaving_players:
            print_colored(f"Departing explorers split {total_path_treasure} path treasures", 'GREEN')

    def display_artifact_award(self, player: Player, artifact_count: int):
        """Display artifact award message"""
        print_colored(f"{player.name} gets {artifact_count} artifact(s)!", 'CYAN')

    def display_round_end_messages(self, players_in_temple: List[Player], deck_empty: bool):
        """Display appropriate round end messages"""
        if not players_in_temple:
            print_colored("🏕️  All explorers have returned to camp safely!", 'BLUE')
        elif deck_empty:
            print_colored("📜 The temple's secrets have been exhausted! No more cards remain.", 'YELLOW')