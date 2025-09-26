#!/usr/bin/env python3
"""
Configuration file for Incan Gold CLI game.
Contains all configurable values and game constants.
"""

# Game settings
MAX_ROUNDS = 5
DEFAULT_NUM_PLAYERS = 3  # AI players (human is always added)
MAX_PLAYERS = 7  # Including human player
MIN_PLAYERS = 1  # Just AI players

# Player validation
MAX_PLAYER_NAME_LENGTH = 18
MIN_PLAYER_NAME_LENGTH = 1

# AI settings
AI_RISK_TOLERANCE_MIN = 0.3
AI_RISK_TOLERANCE_MAX = 0.8

# Default AI player names (will be used based on number requested)
DEFAULT_AI_NAMES = [
    "Maya the Bold",
    "Diego the Cautious",
    "Carmen the Lucky",
    "Zara the Wise",
    "Felix the Daring",
    "Iris the Patient",
    "Thor the Brave"
]

# Scoring values
TREASURE_VALUES = {
    'TURQUOISE': 1,
    'OBSIDIAN': 5,
    'GOLD': 10
}

# Artifact scoring
ARTIFACT_FIRST_TIER_COUNT = 3
ARTIFACT_FIRST_TIER_VALUE = 5
ARTIFACT_SECOND_TIER_VALUE = 10

# Deck composition
TREASURE_CARD_VALUES = [1, 2, 3, 4, 5, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
HAZARD_TYPES_COUNT = 2  # 2 of each hazard type per deck
ARTIFACTS_PER_ROUND = 1

# UI settings
CARDS_PER_ROW = 5
CARD_ART_HEIGHT = 7

# File settings
LEADERBOARD_FILE = "incan_gold_leaderboard.json"
LEADERBOARD_MAX_ENTRIES = 10

# Terminal colors
COLORS = {
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

# Game balance settings
AI_DECISION_FACTORS = {
    'RISK_WEIGHT': 0.5,
    'TREASURE_WEIGHT': 0.3,
    'PLAYER_WEIGHT': 0.2,
    'RANDOMNESS_FACTOR': 0.1
}

# Display settings
SEPARATOR_LENGTH = 80
HEADER_SEPARATOR = "="
SUB_SEPARATOR = "-"