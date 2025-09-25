from skull_and_roses_game import *

# Create players (mix of human and AI)
players = [
    InteractiveHumanPlayer("Marie", "balanced"),           # Real human player
    SimpleAIPlayer("Alice", "balanced"),     # AI opponent  
    SimpleAIPlayer("Bob", "aggressive"),     # AI opponent
    SimpleAIPlayer("Charlie", "conservative") # AI opponent
]

# Create and start interactive game
game = InteractiveSkullGame(players)
game.play_interactive_game()
