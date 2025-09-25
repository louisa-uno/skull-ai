"""
Skull and Roses Card Game Simulation - Interactive Version

A complete implementation of the bluffing card game Skull and Roses (also known as Skull) 
in Python with object-oriented design, multiple AI strategies, and TRULY INTERACTIVE human players.

Author: AI Assistant
Features:
- Object-oriented design with inheritance
- Multiple AI strategies (aggressive, conservative, balanced, random)
- Support for 2-6 players (human or AI)
- TRULY INTERACTIVE human players with real user input
- Comprehensive statistics and logging  
- Easy extensibility for new AI implementations
- Full game rule implementation with proper elimination and winning conditions
- Enhanced user interface with emojis and clear prompts
"""

import random
from enum import Enum
from typing import List, Optional, Tuple, Dict
import copy

def wait_for_human_conformation(text):
    # input(text)
    print(text)

class CardType(Enum):
    ROSE = "Rose"
    SKULL = "Skull"

class Card:
    def __init__(self, card_type: CardType):
        self.card_type = card_type

    def __str__(self):
        return self.card_type.value

    def __repr__(self):
        return f"Card({self.card_type.value})"

class GameState(Enum):
    INITIAL_PLACEMENT = "initial_placement"
    CARD_PLACEMENT = "card_placement" 
    BIDDING = "bidding"
    CHALLENGE = "challenge"
    GAME_OVER = "game_over"

class Player:
    """Base player class with core game mechanics"""

    def __init__(self, name: str, is_ai: bool = False):
        self.name = name
        self.is_ai = is_ai
        self.hand = [Card(CardType.ROSE), Card(CardType.ROSE), Card(CardType.ROSE), Card(CardType.SKULL)]
        self.played_cards = []  # Stack of face-down cards
        self.rounds_won = 0
        self.is_eliminated = False
        self.has_passed = False

        # Statistics tracking
        self.stats = {
            'challenges_won': 0,
            'challenges_lost': 0,
            'cards_lost': 0,
            'skulls_played': 0,
            'roses_played': 0
        }

    def add_card_to_hand(self, card: Card):
        self.hand.append(card)

    def play_card(self, card: Card):
        """Play a card face-down to the player's stack"""
        if card in self.hand:
            self.hand.remove(card)
            self.played_cards.append(card)

            # Update stats
            if card.card_type == CardType.SKULL:
                self.stats['skulls_played'] += 1
            else:
                self.stats['roses_played'] += 1
            return True
        return False

    def retrieve_cards(self):
        """Retrieve all played cards back to hand"""
        self.hand.extend(self.played_cards)
        self.played_cards = []

    def lose_random_card(self) -> Card:
        """Lose a random card permanently"""
        if self.hand:
            card = random.choice(self.hand)
            self.hand.remove(card)
            self.stats['cards_lost'] += 1
            if len(self.hand) == 0:
                self.is_eliminated = True
            return card
        return None

    def lose_chosen_card(self, card: Card):
        """Lose a specific card (when player reveals own skull)"""
        if card in self.hand:
            self.hand.remove(card)
            self.stats['cards_lost'] += 1
            if len(self.hand) == 0:
                self.is_eliminated = True
            return card
        return None

    def has_cards_to_play(self) -> bool:
        return len(self.hand) > 0

    def cards_played_count(self) -> int:
        return len(self.played_cards)

    def has_skull_in_hand(self) -> bool:
        return any(card.card_type == CardType.SKULL for card in self.hand)

    def count_roses_in_hand(self) -> int:
        return sum(1 for card in self.hand if card.card_type == CardType.ROSE)

    def reset_for_new_round(self):
        """Reset player state for new round"""
        self.has_passed = False

    def get_game_state_info(self, game) -> Dict:
        """Get information about current game state for decision making"""
        return {
            'cards_in_hand': len(self.hand),
            'has_skull': self.has_skull_in_hand(),
            'roses_in_hand': self.count_roses_in_hand(),
            'cards_played': len(self.played_cards),
            'total_cards_on_table': game.total_cards_on_table(),
            'active_players': len(game.get_active_players()),
            'current_bid': game.current_bid,
            'rounds_won': self.rounds_won
        }

    def __str__(self):
        return f"{self.name} - Cards in hand: {len(self.hand)}, Played: {len(self.played_cards)}, Wins: {self.rounds_won}"

class InteractiveHumanPlayer(Player):
    """Truly interactive human player with real user input"""

    def __init__(self, name: str):
        super().__init__(name, is_ai=False)

    def display_hand(self):
        """Display the player's current hand"""
        print(f"\n{self.name}'s hand:")
        roses = [i for i, card in enumerate(self.hand) if card.card_type == CardType.ROSE]
        skulls = [i for i, card in enumerate(self.hand) if card.card_type == CardType.SKULL]

        for i, card in enumerate(self.hand):
            card_type = "🌹 Rose" if card.card_type == CardType.ROSE else "💀 Skull"
            print(f"  {i+1}. {card_type}")

    def choose_card_to_play(self, game_info: Dict = None) -> Card:
        """Interactive card selection for human players"""
        if not self.hand:
            return None

        print(f"\n--- {self.name}'s Turn to Play a Card ---")

        # Show game context
        if game_info:
            print(f"Cards on table: {game_info['total_cards_on_table']}")
            print(f"Active players: {game_info['active_players']}")

        self.display_hand()

        while True:
            try:
                choice = input(f"\nChoose a card to play (1-{len(self.hand)}): ").strip()
                if choice.lower() in ['q', 'quit']:
                    print("Game quit by player.")
                    return None

                card_index = int(choice) - 1
                if 0 <= card_index < len(self.hand):
                    selected_card = self.hand[card_index]
                    card_name = "Rose" if selected_card.card_type == CardType.ROSE else "Skull"
                    print(f"You chose to play: {card_name}")
                    return selected_card
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(self.hand)}")
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("\nGame interrupted by player.")
                return None

    def decide_play_or_bid(self, game_info: Dict) -> bool:
        """Interactive decision to play another card or start bidding"""
        print(f"\n--- {self.name}'s Turn Decision ---")
        print(f"You have {game_info['cards_in_hand']} cards remaining in hand")
        print(f"Total cards on table: {game_info['total_cards_on_table']}")
        print(f"You have played {game_info['cards_played']} cards")

        while True:
            choice = input("\nDo you want to (P)lay another card or (B)id? [P/B]: ").strip().upper()
            if choice == 'P':
                return False  # Play another card
            elif choice == 'B':
                return True   # Start bidding
            elif choice.lower() in ['q', 'quit']:
                print("Game quit by player.")
                return True  # Default to bidding to avoid issues
            else:
                print("Please enter 'P' to play another card or 'B' to bid.")

    def make_bid(self, current_bid: int, max_possible: int, game_info: Dict = None) -> Optional[int]:
        """Interactive bidding for human players"""
        print(f"\n--- {self.name}'s Bidding Turn ---")
        print(f"Current bid: {current_bid}")
        print(f"Maximum possible bid: {max_possible}")

        if game_info:
            print(f"You have {game_info['roses_in_hand']} roses and {'a skull' if game_info['has_skull'] else 'no skull'} in hand")

        while True:
            try:
                choice = input(f"\nEnter your bid ({current_bid + 1}-{max_possible}) or 'p' to pass: ").strip().lower()

                if choice == 'p' or choice == 'pass':
                    print("You passed.")
                    return None
                elif choice in ['q', 'quit']:
                    print("Game quit by player.")
                    return None

                bid = int(choice)
                if current_bid < bid <= max_possible:
                    print(f"You bid {bid}")
                    return bid
                else:
                    print(f"Invalid bid. Must be between {current_bid + 1} and {max_possible}")
            except ValueError:
                print("Please enter a valid number or 'p' to pass.")
            except KeyboardInterrupt:
                print("\nGame interrupted by player.")
                return None

    def choose_card_to_lose(self) -> Card:
        """Interactive card selection when losing a card"""
        if not self.hand:
            return None

        print(f"\n--- {self.name} Must Lose a Card ---")
        print("You revealed your own skull and must choose a card to lose permanently.")

        self.display_hand()

        while True:
            try:
                choice = input(f"\nChoose a card to lose (1-{len(self.hand)}): ").strip()
                if choice.lower() in ['q', 'quit']:
                    print("Game quit by player.")
                    return random.choice(self.hand)  # Fallback

                card_index = int(choice) - 1
                if 0 <= card_index < len(self.hand):
                    selected_card = self.hand[card_index]
                    card_name = "Rose" if selected_card.card_type == CardType.ROSE else "Skull"
                    print(f"You chose to lose: {card_name}")
                    return selected_card
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(self.hand)}")
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("\nGame interrupted by player.")
                return random.choice(self.hand)  # Fallback

class SimpleAIPlayer(Player):
    """Simple AI player for testing with human players"""

    def __init__(self, name: str, strategy: str = "balanced"):
        super().__init__(name, is_ai=True)
        self.strategy = strategy

    def choose_card_to_play(self, game_info: Dict = None) -> Card:
        """AI chooses which card to play"""
        if not self.hand:
            return None

        skulls = [card for card in self.hand if card.card_type == CardType.SKULL]
        roses = [card for card in self.hand if card.card_type == CardType.ROSE]

        # Strategy-based decision
        if self.strategy == "aggressive":
            skull_prob = 0.4
        elif self.strategy == "conservative":
            skull_prob = 0.2
        else:  # balanced
            skull_prob = 0.3

        if random.random() < skull_prob and skulls:
            return random.choice(skulls)
        elif roses:
            return random.choice(roses)
        else:
            return random.choice(self.hand)

    def decide_play_or_bid(self, game_info: Dict) -> bool:
        """AI decides whether to play another card or start bidding"""
        total_cards = game_info.get('total_cards_on_table', 0)
        # Strategy affects bidding eagerness
        if self.strategy == "aggressive":
            bid_probability = 0.4 + (total_cards * 0.05)
        elif self.strategy == "conservative":
            bid_probability = 0.2 + (total_cards * 0.03)
        else:  # balanced
            bid_probability = 0.3 + (total_cards * 0.04)

        return random.random() < bid_probability

    def make_bid(self, current_bid: int, max_possible: int, game_info: Dict = None) -> Optional[int]:
        """AI makes a bid or returns None to pass"""
        if current_bid >= max_possible:
            return None

        # Strategy affects bidding aggressiveness
        if self.strategy == "aggressive":
            raise_prob = 0.5
        elif self.strategy == "conservative":
            raise_prob = 0.3
        else:  # balanced
            raise_prob = 0.4

        if random.random() < raise_prob:
            return min(current_bid + 1, max_possible)
        return None

class InteractiveSkullGame:
    """Enhanced Skull game controller that supports interactive human players"""

    def __init__(self, players: List[Player], verbose: bool = True):
        if len(players) < 2 or len(players) > 6:
            raise ValueError("Game requires 2-6 players")

        self.players = players
        self.current_player_index = 0
        self.game_state = GameState.INITIAL_PLACEMENT
        self.current_bid = 0
        self.challenger = None
        self.skull_revealer = None
        self.round_number = 1
        self.game_log = []
        self.verbose = verbose
        self.game_stats = {
            'total_rounds': 0,
            'total_challenges': 0,
            'successful_challenges': 0,
            'eliminations': 0
        }

        # Shuffle initial player order
        random.shuffle(self.players)

    def log(self, message: str, force_print: bool = False):
        """Add message to game log with optional printing"""
        log_entry = f"Round {self.round_number}: {message}"
        self.game_log.append(log_entry)
        if self.verbose or force_print:
            print(log_entry)

    def display_game_state(self):
        """Display current game state for human players"""
        print(f"\n{'='*60}")
        print(f"ROUND {self.round_number} - {self.game_state.value.replace('_', ' ').title()}")
        print(f"{'='*60}")

        active_players = self.get_active_players()
        print(f"Active Players: {len(active_players)}")

        for player in active_players:
            status_icon = "👤" if isinstance(player, InteractiveHumanPlayer) else "🤖"
            cards_display = f"Hand: {len(player.hand)} cards, Played: {len(player.played_cards)} cards"
            wins_display = f"Rounds won: {player.rounds_won}"
            print(f"  {status_icon} {player.name}: {cards_display}, {wins_display}")

        if self.game_state == GameState.BIDDING and self.current_bid > 0:
            print(f"\nCurrent bid: {self.current_bid}")
            print(f"Total cards on table: {self.total_cards_on_table()}")

        print()

    def get_current_player(self) -> Player:
        return self.players[self.current_player_index]

    def get_active_players(self) -> List[Player]:
        """Get players who are not eliminated"""
        return [p for p in self.players if not p.is_eliminated]

    def next_player(self):
        """Move to next active player"""
        attempts = 0
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            if not self.players[self.current_player_index].is_eliminated:
                break
            attempts += 1
            if attempts >= len(self.players):
                break

    def total_cards_on_table(self) -> int:
        """Count total cards played by all players"""
        return sum(len(p.played_cards) for p in self.players if not p.is_eliminated)

    def initial_card_placement(self):
        """Phase 1: All players place their initial card"""
        self.display_game_state()
        self.log("=== Initial Card Placement Phase ===")
        print("All players must place one card face-down to start the round.\n")

        active_players = self.get_active_players()

        if len(active_players) < 2:
            self.log("Not enough active players to continue")
            self.game_state = GameState.GAME_OVER
            return

        for player in active_players:
            if not player.has_cards_to_play():
                self.log(f"{player.name} has no cards and is eliminated!")
                player.is_eliminated = True
                continue

            # Get game info for decision making
            game_info = player.get_game_state_info(self)

            if isinstance(player, InteractiveHumanPlayer):
                card = player.choose_card_to_play(game_info)
                if card is None:  # Player quit
                    self.game_state = GameState.GAME_OVER
                    return
            elif player.is_ai:
                card = player.choose_card_to_play(game_info)
                print(f"🤖 {player.name} placed a card face-down")
            else:
                card = random.choice(player.hand) if player.hand else None
                print(f"{player.name} placed a card face-down")

            if card:
                player.play_card(card)
                self.log(f"{player.name} placed a card face-down")

        remaining_players = self.get_active_players()
        if len(remaining_players) < 2:
            self.log("Not enough players remaining to continue")
            self.game_state = GameState.GAME_OVER
            return

        self.game_state = GameState.CARD_PLACEMENT
        self.log("All active players have placed their initial cards")
        print("\nInitial placement complete! Moving to card placement phase...\n")

    def card_placement_phase(self):
        """Phase 2: Players continue placing cards or start bidding"""
        if self.game_state != GameState.CARD_PLACEMENT:
            return False

        self.display_game_state()
        current_player = self.get_current_player()

        if not current_player.has_cards_to_play():
            print(f"{current_player.name} has no cards left and must start bidding!")
            self.start_bidding_phase()
            return True

        # Get game info for decision making
        game_info = current_player.get_game_state_info(self)

        # Decide whether to play card or bid
        if isinstance(current_player, InteractiveHumanPlayer):
            should_bid = current_player.decide_play_or_bid(game_info)
        elif hasattr(current_player, 'decide_play_or_bid'):
            should_bid = current_player.decide_play_or_bid(game_info)
        else:
            should_bid = random.random() < 0.3  # Simple fallback

        if should_bid:
            self.start_bidding_phase()
        else:
            # Play another card
            if isinstance(current_player, InteractiveHumanPlayer):
                card = current_player.choose_card_to_play(game_info)
                if card is None:  # Player quit
                    self.game_state = GameState.GAME_OVER
                    return False
            elif hasattr(current_player, 'choose_card_to_play'):
                card = current_player.choose_card_to_play(game_info)
                print(f"🤖 {current_player.name} played another card")
            else:
                card = random.choice(current_player.hand) if current_player.hand else None
                print(f"{current_player.name} played another card")

            if card:
                current_player.play_card(card)
                self.log(f"{current_player.name} played another card (now has {current_player.cards_played_count()} cards)")
                self.next_player()
            else:
                self.log(f"{current_player.name} has no cards left and must start bidding")
                self.start_bidding_phase()

        return True

    def start_bidding_phase(self):
        """Initialize the bidding phase"""
        self.game_state = GameState.BIDDING
        self.current_bid = 1
        current_player = self.get_current_player()

        print(f"\n🎯 {current_player.name} starts the bidding at {self.current_bid}!")
        self.log(f"=== Bidding Phase Started by {current_player.name} ===")
        self.log(f"Total cards on table: {self.total_cards_on_table()}")
        self.log(f"{current_player.name} bids {self.current_bid}")

        self.next_player()

    def bidding_phase(self):
        """Phase 3: Handle bidding until only one player remains"""
        if self.game_state != GameState.BIDDING:
            return False

        self.display_game_state()
        current_player = self.get_current_player()

        if current_player.has_passed:
            self.next_player()
            return True

        max_possible_bid = self.total_cards_on_table()
        game_info = current_player.get_game_state_info(self)

        # Make bid decision
        if isinstance(current_player, InteractiveHumanPlayer):
            new_bid = current_player.make_bid(self.current_bid, max_possible_bid, game_info)
        elif hasattr(current_player, 'make_bid'):
            new_bid = current_player.make_bid(self.current_bid, max_possible_bid, game_info)
            if new_bid:
                print(f"🤖 {current_player.name} bids {new_bid}")
            else:
                print(f"🤖 {current_player.name} passes")
        else:
            # Simple fallback
            if random.random() < 0.4 and self.current_bid < max_possible_bid:
                new_bid = self.current_bid + 1
                print(f"{current_player.name} bids {new_bid}")
            else:
                new_bid = None
                print(f"{current_player.name} passes")

        if new_bid is not None:
            self.current_bid = new_bid
            self.log(f"{current_player.name} bids {self.current_bid}")
        else:
            current_player.has_passed = True
            self.log(f"{current_player.name} passes")

        # Check if only one player hasn't passed
        active_bidders = [p for p in self.get_active_players() if not p.has_passed]
        if len(active_bidders) == 1:
            self.challenger = active_bidders[0]
            print(f"\n🏆 {self.challenger.name} wins the bidding with {self.current_bid}!")
            self.log(f"{self.challenger.name} is the challenger with bid of {self.current_bid}")
            self.game_state = GameState.CHALLENGE
            self.game_stats['total_challenges'] += 1
            wait_for_human_conformation("\nPress Enter to continue to the challenge phase...")
        else:
            self.next_player()

        return True

    def challenge_phase(self):
        """Phase 4: Challenger attempts to reveal the bid number of roses"""
        if self.game_state != GameState.CHALLENGE:
            return False

        self.display_game_state()
        print(f"🎯 CHALLENGE PHASE")
        print(f"{self.challenger.name} must reveal {self.current_bid} cards without hitting a skull!")
        print("Cards will be revealed from the challenger's stack first, then from other players.\n")
        wait_for_human_conformation("Press Enter to start revealing cards...")

        self.log(f"=== Challenge Phase ===")
        self.log(f"{self.challenger.name} must reveal {self.current_bid} cards")

        cards_to_reveal = self.current_bid

        # First, reveal challenger's own cards (mandatory)
        if self.challenger.played_cards:
            print(f"\nRevealing {self.challenger.name}'s cards first...")
            while cards_to_reveal > 0 and self.challenger.played_cards:
                wait_for_human_conformation("Press Enter to reveal next card...")
                card = self.challenger.played_cards.pop()
                self.challenger.hand.append(card)
                cards_to_reveal -= 1
                
                if len(self.challenger.hand) + len(self.challenger.played_cards) + self.challenger.stats['challenges_lost'] != 4:
                    raise ValueError(f"{self.name} cannot have more or less than 4 cards total")

                if card.card_type == CardType.SKULL:
                    print(f"💀 SKULL REVEALED!")
                    print(f"Challenge failed! {self.challenger.name} hit a skull.")
                else:
                    print(f"🌹 ROSE REVEALED!")

                self.log(f"Revealed: {card.card_type.value}")

                if card.card_type == CardType.SKULL:
                    self.log(f"💀 SKULL REVEALED! Challenge failed!")
                    self.skull_revealer = self.challenger
                    self.challenger.stats['challenges_lost'] += 1
                    self.handle_failed_challenge()
                    return True

        # If still need to reveal cards, choose from other players
        other_players = [p for p in self.get_active_players() if p != self.challenger and p.played_cards]

        while cards_to_reveal > 0 and other_players:
            print(f"\nNeed to reveal {cards_to_reveal} more cards from other players...")
            target_player = random.choice(other_players)

            wait_for_human_conformation(f"Press Enter to reveal a card from {target_player.name}...")
            card = target_player.played_cards.pop()
            target_player.hand.append(card)
            cards_to_reveal -= 1

            if card.card_type == CardType.SKULL:
                print(f"💀 SKULL REVEALED from {target_player.name}!")
                print(f"Challenge failed!")
            else:
                print(f"🌹 ROSE REVEALED from {target_player.name}!")

            self.log(f"Revealed {target_player.name}'s card: {card.card_type.value}")

            if card.card_type == CardType.SKULL:
                self.log(f"💀 SKULL REVEALED! Challenge failed!")
                self.skull_revealer = target_player
                self.challenger.stats['challenges_lost'] += 1
                self.handle_failed_challenge()
                return True

            if not target_player.played_cards:
                other_players.remove(target_player)

        # Challenge succeeded!
        print(f"\n🎉 SUCCESS! All {self.current_bid} cards were roses!")
        print(f"{self.challenger.name} wins the round!")
        self.log(f"🌹 Challenge succeeded! All {self.current_bid} cards were roses!")
        self.challenger.stats['challenges_won'] += 1
        self.game_stats['successful_challenges'] += 1
        self.handle_successful_challenge()
        return True


    def handle_failed_challenge(self):
        """Handle the consequences of a failed challenge"""
        print(f"\n💥 CHALLENGE FAILED!")
        

        # Challenger loses a card, chosen if revealed own skull
        if self.skull_revealer == self.challenger:
            # Player revealed own skull: chooses card to lose (or random if AI)
            lost_card = None
            if isinstance(self.challenger, InteractiveHumanPlayer):
                lost_card = self.challenger.choose_card_to_lose()
                if lost_card:
                    self.challenger.lose_chosen_card(lost_card)
            else:
                lost_card = self.challenger.lose_random_card()
            self.log(f"{self.challenger.name} revealed their own skull and loses a card")
        else:
            # Skull revealed on another player's stack: challenger loses a random card
            lost_card = self.challenger.lose_random_card()
            self.log(f"{self.skull_revealer.name}'s skull was revealed. {self.challenger.name} loses a random card")

        if self.challenger.is_eliminated:
            print(f"⚰️ {self.challenger.name} is eliminated from the game!")
            self.log(f"⚰️ {self.challenger.name} is eliminated from the game!")
            self.game_stats['eliminations'] += 1

        # All players retrieve their cards
        for player in self.players:
            player.retrieve_cards()

        wait_for_human_conformation("\nPress Enter to continue to next round...")
        self.start_new_round()

    def handle_successful_challenge(self):
        """Handle the consequences of a successful challenge"""
        self.challenger.rounds_won += 1
        self.log(f"🏆 {self.challenger.name} wins round {self.challenger.rounds_won}!")

        if self.challenger.rounds_won >= 2:
            print(f"\n🎉🎉🎉 {self.challenger.name} WINS THE GAME! 🎉🎉🎉")
            print(f"Congratulations! You won with {self.challenger.rounds_won} rounds!")
            self.log(f"🎉 {self.challenger.name} WINS THE GAME! 🎉", force_print=True)
            self.game_state = GameState.GAME_OVER
            return

        # All players retrieve their cards
        for player in self.players:
            player.retrieve_cards()

        print(f"\n{self.challenger.name} needs one more round to win!")
        wait_for_human_conformation("Press Enter to continue to next round...")
        self.start_new_round()

    def start_new_round(self):
        """Initialize a new round"""
        self.round_number += 1
        self.game_stats['total_rounds'] = self.round_number - 1

        for player in self.players:
            player.reset_for_new_round()

        active_players = self.get_active_players()
        if len(active_players) <= 1:
            if active_players:
                print(f"\n🎉 {active_players[0].name} wins by elimination! 🎉")
                self.log(f"🎉 {active_players[0].name} wins by elimination! 🎉", force_print=True)
            else:
                print("Game ends with no remaining players!")
                self.log("Game ends with no remaining players!", force_print=True)
            self.game_state = GameState.GAME_OVER
            return

        # Set first player for next round (challenger goes first)
        if self.challenger and not self.challenger.is_eliminated:
            self.current_player_index = self.players.index(self.challenger)
        else:
            self.current_player_index = 0
            while self.players[self.current_player_index].is_eliminated:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # Reset game state
        self.current_bid = 0
        self.challenger = None
        self.skull_revealer = None
        self.game_state = GameState.INITIAL_PLACEMENT

        self.log(f"Starting round {self.round_number}")

    def play_turn(self) -> bool:
        """Execute one turn of the game. Returns True if game continues, False if over"""
        if self.game_state == GameState.GAME_OVER:
            return False

        try:
            if self.game_state == GameState.INITIAL_PLACEMENT:
                self.initial_card_placement()
            elif self.game_state == GameState.CARD_PLACEMENT:
                self.card_placement_phase()
            elif self.game_state == GameState.BIDDING:
                self.bidding_phase()
            elif self.game_state == GameState.CHALLENGE:
                self.challenge_phase()
        except KeyboardInterrupt:
            print("\n\nGame interrupted by user.")
            self.game_state = GameState.GAME_OVER
            return False
        
        for player in self.players:
            if player.rounds_won >= 2:
                self.game_state = GameState.GAME_OVER
                return False

        return self.game_state != GameState.GAME_OVER

    def play_interactive_game(self):
        """Play a complete interactive game"""
        print("\n" + "="*80)
        print("🎲 WELCOME TO SKULL AND ROSES! 🎲")
        print("="*80)
        print("\nGame Rules:")
        print("• Each player has 3 Roses and 1 Skull")
        print("• Win 2 rounds by successfully completing challenges")  
        print("• Challenge: Reveal your bid number of cards without hitting a skull")
        print("• Lose cards when challenges fail, elimination at 0 cards")
        print("• Type 'q' or 'quit' at any prompt to exit")
        print("\nPress Ctrl+C at any time to quit the game")

        players_info = []
        for player in self.players:
            if isinstance(player, InteractiveHumanPlayer):
                players_info.append(f"👤 {player.name} (Human)")
            else:
                players_info.append(f"🤖 {player.name} (AI)")

        print(f"\nPlayers: {', '.join(players_info)}")

        wait_for_human_conformation("\nPress Enter to start the game...")

        turn_count = 0
        max_turns = 500  # Prevent infinite games

        try:
            while self.play_turn() and turn_count < max_turns:
                turn_count += 1

                # Check for game end
                if self.game_state == GameState.GAME_OVER:
                    break

            if turn_count >= max_turns:
                print("\nGame ended due to turn limit.")

            self.print_final_results()

        except KeyboardInterrupt:
            print("\n\nGame interrupted. Thanks for playing!")
        except Exception as e:
            print(f"\nGame error: {e}")
            print("Game ended unexpectedly.")

    def print_final_results(self):
        """Print comprehensive final results"""
        print("\n" + "="*60)
        print("🏁 FINAL GAME RESULTS 🏁")
        print("="*60)

        active_players = self.get_active_players()
        if active_players:
            winner = max(active_players, key=lambda p: p.rounds_won)
            if winner.rounds_won >= 2:
                print(f"🏆 Winner: {winner.name} with {winner.rounds_won} rounds won!")
            else:
                print(f"🏆 Winner by elimination: {winner.name}")

        print(f"\n📊 Game Statistics:")
        print(f"  • Total rounds played: {self.game_stats['total_rounds']}")
        print(f"  • Total challenges attempted: {self.game_stats['total_challenges']}")
        print(f"  • Successful challenges: {self.game_stats['successful_challenges']}")
        print(f"  • Players eliminated: {self.game_stats['eliminations']}")

        print(f"\n👥 Player Performance:")
        for player in self.players:
            status = "ELIMINATED" if player.is_eliminated else "ACTIVE"
            icon = "👤" if isinstance(player, InteractiveHumanPlayer) else "🤖"
            print(f"  {icon} {player.name} [{status}]:")
            print(f"     Rounds won: {player.rounds_won}")
            print(f"     Cards remaining: {len(player.hand) + len(player.played_cards)}")
            print(f"     Challenges: {player.stats['challenges_won']} won, {player.stats['challenges_lost']} lost")
            print(f"     Cards played: {player.stats['skulls_played']} skulls, {player.stats['roses_played']} roses")
            
def create_interactive_game():
    """Create and return a sample interactive game setup"""
    print("🎲 SKULL AND ROSES - INTERACTIVE GAME SETUP 🎲")
    print("="*60)

    # Create a mixed group of players
    players = [
        InteractiveHumanPlayer("Human Player"),  # The human player
        SimpleAIPlayer("AI Alice", "balanced"),
        SimpleAIPlayer("AI Bob", "aggressive"), 
        SimpleAIPlayer("AI Charlie", "conservative")
    ]

    print("\n👥 Players:")
    print("👤 Human Player - You! (Interactive)")
    print("🤖 AI Alice - Balanced strategy")
    print("🤖 AI Bob - Aggressive strategy") 
    print("🤖 AI Charlie - Conservative strategy")

    print("\n🎯 To start this interactive game, run:")
    game = InteractiveSkullGame(players)
    game.play_interactive_game()

# Example usage
if __name__ == "__main__":
    create_interactive_game()
