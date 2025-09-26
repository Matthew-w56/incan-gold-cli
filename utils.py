#!/usr/bin/env python3
"""
Utility functions for Incan Gold CLI game.
"""

import os
import re
import sys
import subprocess
from config import COLORS, MAX_PLAYER_NAME_LENGTH, MIN_PLAYER_NAME_LENGTH


def clear_screen():
    """
    Clear the console screen in a cross-platform way.
    Uses the most appropriate method for the current OS.
    """
    try:
        # Try the standard approach first
        if os.name == 'posix':  # Unix/Linux/MacOS
            os.system('clear')
        elif os.name == 'nt':  # Windows
            os.system('cls')
        else:
            # Fallback for other systems
            print('\033[2J\033[H', end='')
    except Exception:
        # If all else fails, print newlines to simulate clearing
        print('\n' * 50)


def print_colored(text: str, color: str = 'WHITE'):
    """Print text with color"""
    if color in COLORS:
        print(f"{COLORS[color]}{text}{COLORS['END']}")
    else:
        print(text)


def validate_player_name(name: str) -> str:
    """
    Validate and sanitize player name input.

    Args:
        name: Raw input string

    Returns:
        Sanitized name string

    Raises:
        ValueError: If name is invalid after sanitization
    """
    # Strip whitespace
    name = name.strip()

    # Replace multiple spaces with single space
    name = re.sub(r'\s+', ' ', name)

    # Remove any control characters or non-printable characters
    name = ''.join(char for char in name if char.isprintable())

    # Check length constraints
    if len(name) < MIN_PLAYER_NAME_LENGTH:
        raise ValueError(f"Name must be at least {MIN_PLAYER_NAME_LENGTH} character(s) long")

    if len(name) > MAX_PLAYER_NAME_LENGTH:
        name = name[:MAX_PLAYER_NAME_LENGTH].strip()
        if len(name) < MIN_PLAYER_NAME_LENGTH:
            raise ValueError(f"Name too short after truncation to {MAX_PLAYER_NAME_LENGTH} characters")

    # Remove leading/trailing special characters but allow them in the middle
    name = name.strip('.,!?@#$%^&*()[]{}|\\:";\'<>/')

    # Final length check after cleanup
    if len(name) < MIN_PLAYER_NAME_LENGTH:
        raise ValueError("Name invalid after sanitization")

    return name


def get_validated_player_name(prompt: str = "Enter your name: ", default: str = "Explorer") -> str:
    """
    Get and validate player name with retries.

    Args:
        prompt: Input prompt text
        default: Default name if input is empty

    Returns:
        Valid player name
    """
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            raw_input = input(prompt).strip()

            # Use default if empty
            if not raw_input:
                raw_input = default

            validated_name = validate_player_name(raw_input)
            return validated_name

        except ValueError as e:
            remaining = max_attempts - attempt - 1
            print_colored(f"Invalid name: {e}", 'RED')

            if remaining > 0:
                print_colored(f"Please try again ({remaining} attempts remaining)", 'YELLOW')
            else:
                print_colored(f"Too many invalid attempts. Using default name: {default}", 'YELLOW')
                return default

    return default


def get_terminal_size():
    """Get terminal size, with fallback defaults"""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except (AttributeError, OSError):
        return 80, 24  # Default fallback


def center_text(text: str, width: int = None) -> str:
    """Center text within given width (or terminal width)"""
    if width is None:
        width, _ = get_terminal_size()

    text_width = len(text)
    if text_width >= width:
        return text

    padding = (width - text_width) // 2
    return ' ' * padding + text


def format_separator(char: str = '=', width: int = None) -> str:
    """Create a separator line of given character and width"""
    if width is None:
        width, _ = get_terminal_size()
    return char * width