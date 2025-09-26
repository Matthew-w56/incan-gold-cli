#!/usr/bin/env python3
"""
Player classes for Incan Gold CLI game.
"""

import random
from typing import Tuple, Dict
from cards import TreasureType
from config import (
    AI_RISK_TOLERANCE_MIN, AI_RISK_TOLERANCE_MAX,
    ARTIFACT_FIRST_TIER_COUNT, ARTIFACT_FIRST_TIER_VALUE,
    ARTIFACT_SECOND_TIER_VALUE, AI_DECISION_FACTORS
)


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
        """Add treasure directly to tent (safe storage)"""
        self.tent_treasures[treasure_type] += amount

    def add_treasure_to_round(self, treasure_type: TreasureType, amount: int):
        """Add treasure to current round (at risk)"""
        self.round_treasures[treasure_type] += amount

    def move_round_treasures_to_tent(self):
        """Move all round treasures to safe tent storage"""
        for treasure_type in TreasureType:
            self.tent_treasures[treasure_type] += self.round_treasures[treasure_type]
            self.round_treasures[treasure_type] = 0

    def lose_round_treasures(self):
        """Lose all treasures collected this round"""
        self.round_treasures = {TreasureType.TURQUOISE: 0, TreasureType.OBSIDIAN: 0, TreasureType.GOLD: 0}

    def calculate_score(self):
        """Calculate total score from treasures and artifacts"""
        score = 0

        # Score treasures
        for treasure_type, amount in self.tent_treasures.items():
            score += amount * treasure_type.value

        # Score artifacts with tier system
        if self.artifacts <= ARTIFACT_FIRST_TIER_COUNT:
            score += self.artifacts * ARTIFACT_FIRST_TIER_VALUE
        else:
            score += (ARTIFACT_FIRST_TIER_COUNT * ARTIFACT_FIRST_TIER_VALUE +
                     (self.artifacts - ARTIFACT_FIRST_TIER_COUNT) * ARTIFACT_SECOND_TIER_VALUE)

        self.total_score = score
        return score

    def reset_for_round(self):
        """Reset player state for new round"""
        self.round_treasures = {TreasureType.TURQUOISE: 0, TreasureType.OBSIDIAN: 0, TreasureType.GOLD: 0}
        self.in_temple = True

    def get_round_treasure_value(self) -> int:
        """Get total value of treasures at risk this round"""
        return sum(amount * ttype.value for ttype, amount in self.round_treasures.items())

    def get_tent_treasure_value(self) -> int:
        """Get total value of safe treasures in tent"""
        return sum(amount * ttype.value for ttype, amount in self.tent_treasures.items())


class AIPlayer(Player):
    def __init__(self, name: str):
        super().__init__(name, is_human=False)
        self.risk_tolerance = random.uniform(AI_RISK_TOLERANCE_MIN, AI_RISK_TOLERANCE_MAX)

    def make_decision(self, game_state: Dict) -> Tuple[bool, str]:
        """
        Make AI decision to continue or leave temple.

        Args:
            game_state: Dictionary containing current game state

        Returns:
            Tuple of (decision: bool, reasoning: str)
            True = continue exploring, False = leave temple
        """
        hazard_counts = game_state.get('hazard_counts', {})
        players_remaining = game_state.get('players_remaining', 1)
        current_round = game_state.get('round', 1)

        # Calculate risk factors
        max_hazards = max(hazard_counts.values()) if hazard_counts else 0
        hazards_at_one = sum(1 for count in hazard_counts.values() if count == 1)
        round_treasure_value = self.get_round_treasure_value()

        # Decision factors (weighted)
        risk_factor = max_hazards * AI_DECISION_FACTORS['RISK_WEIGHT']
        treasure_factor = min(round_treasure_value / 20.0, 1.0) * AI_DECISION_FACTORS['TREASURE_WEIGHT']
        player_factor = (1.0 / max(players_remaining, 1)) * AI_DECISION_FACTORS['PLAYER_WEIGHT']

        # Base leave probability
        leave_probability = (
            risk_factor + treasure_factor - player_factor +
            (1 - self.risk_tolerance) +
            random.uniform(-AI_DECISION_FACTORS['RANDOMNESS_FACTOR'],
                          AI_DECISION_FACTORS['RANDOMNESS_FACTOR'])
        ) / 2

        # Adjust for round number (more cautious in later rounds)
        round_factor = current_round / 10.0
        leave_probability += round_factor

        # Make decision
        decision = random.random() > leave_probability

        # Generate reasoning
        reasoning = self._generate_reasoning(round_treasure_value, hazards_at_one, players_remaining)

        return decision, reasoning

    def _generate_reasoning(self, round_treasure_value: int, hazards_at_one: int, players_remaining: int) -> str:
        """Generate human-readable reasoning for AI decision"""
        reasoning_parts = []

        # Treasure assessment
        if round_treasure_value > 15:
            reasoning_parts.append(f"carrying {round_treasure_value} treasure")
        elif round_treasure_value > 5:
            reasoning_parts.append("moderate treasure secured")
        else:
            reasoning_parts.append("little treasure so far")

        # Hazard assessment
        if hazards_at_one >= 3:
            reasoning_parts.append("many single hazards seen (risky!)")
        elif hazards_at_one >= 2:
            reasoning_parts.append("some hazards revealed")
        elif hazards_at_one == 1:
            reasoning_parts.append("one hazard seen")
        else:
            reasoning_parts.append("no hazards yet")

        # Player count assessment
        if players_remaining <= 2:
            reasoning_parts.append("few players left (good treasure share)")
        elif players_remaining == 3:
            reasoning_parts.append("moderate competition")
        else:
            reasoning_parts.append("crowded temple")

        # Personality factor
        if self.risk_tolerance > 0.6:
            personality = "bold nature"
        elif self.risk_tolerance < 0.4:
            personality = "cautious approach"
        else:
            personality = "balanced strategy"

        reasoning_parts.append(personality)

        return f"({', '.join(reasoning_parts)})"