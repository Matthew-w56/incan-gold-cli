#!/usr/bin/env python3
"""
Card-related classes and functions for Incan Gold CLI game.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
import random
from config import TREASURE_CARD_VALUES, HAZARD_TYPES_COUNT, ARTIFACTS_PER_ROUND


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
    remaining_treasure: int = 0  # For tracking unclaimed treasure on path


def create_deck() -> List[Card]:
    """Create the full deck for one round"""
    cards = []

    # Add treasure cards
    for value in TREASURE_CARD_VALUES:
        cards.append(Card(CardType.TREASURE, value=value, name=f"Treasure {value}"))

    # Add hazard cards (2 of each type)
    for hazard_type in HazardType:
        for _ in range(HAZARD_TYPES_COUNT):
            cards.append(Card(CardType.HAZARD, hazard_type=hazard_type, name=hazard_type.value))

    # Add artifacts
    for _ in range(ARTIFACTS_PER_ROUND):
        cards.append(Card(CardType.ARTIFACT, value=0, name="Ancient Artifact"))

    return cards


def draw_ascii_card(card: Card) -> List[str]:
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