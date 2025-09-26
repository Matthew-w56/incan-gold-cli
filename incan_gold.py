#!/usr/bin/env python3
"""
Incan Gold CLI Game - Main Entry Point
A faithful command-line implementation of the popular board game Incan Gold.
"""

import sys
import argparse
from game import Game
from utils import print_colored
from config import DEFAULT_NUM_PLAYERS, MAX_PLAYERS, MIN_PLAYERS


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Incan Gold CLI - Temple exploration adventure game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Play with default 3 AI players
  %(prog)s --players 5        # Play with 5 AI players
  %(prog)s -p 1               # Play with 1 AI player (minimum)

Game Features:
  • Full original rules with artifacts and hazards
  • ASCII art cards and colored terminal output
  • Smart AI opponents with varying risk tolerance
  • Persistent leaderboard system
  • 5-round expedition gameplay
        """
    )

    parser.add_argument(
        '-p', '--players',
        type=int,
        default=DEFAULT_NUM_PLAYERS,
        metavar='N',
        help=f'Number of AI players (default: {DEFAULT_NUM_PLAYERS}, min: {MIN_PLAYERS}, max: {MAX_PLAYERS-1})'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Incan Gold CLI v1.0.0'
    )

    return parser.parse_args()


def validate_player_count(num_players: int) -> int:
    """Validate and adjust player count"""
    if num_players < MIN_PLAYERS:
        print_colored(f"Warning: Minimum {MIN_PLAYERS} AI players required. Setting to {MIN_PLAYERS}.", 'YELLOW')
        return MIN_PLAYERS
    elif num_players > MAX_PLAYERS - 1:  # -1 for human player
        print_colored(f"Warning: Maximum {MAX_PLAYERS-1} AI players allowed. Setting to {MAX_PLAYERS-1}.", 'YELLOW')
        return MAX_PLAYERS - 1
    return num_players


def main():
    """Main entry point"""
    try:
        args = parse_arguments()
        num_ai_players = validate_player_count(args.players)

        if num_ai_players != args.players:
            input("Press Enter to continue...")

        game = Game(num_ai_players=num_ai_players)

        while True:
            game.ui.show_main_menu()
            choice = input("\nSelect option (1-3): ").strip()

            if choice == '1':
                game.play_game()
                # Reset game for potential replay
                game = Game(num_ai_players=num_ai_players)
            elif choice == '2':
                game.display_leaderboard()
            elif choice == '3':
                print("Thanks for playing Incan Gold!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
        sys.exit(0)
    except Exception as e:
        print_colored(f"An error occurred: {e}", 'RED')
        sys.exit(1)


if __name__ == "__main__":
    main()