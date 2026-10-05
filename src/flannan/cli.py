"""Provide a terminal interface for playing the story."""

from .engine import apply_choice
from .state import create_game_state
from .story import SCENES


def show_scene(game_state):
    """Display the current scene and its available choices."""

    # Look up the scene using the player's current position.
    scene = SCENES[game_state["scene"]]

    print(f"\n--- {scene['title']} ---")
    print(scene["narration"])
    print()

    # Display each keyword alongside its description.
    for keyword, choice in scene["choices"].items():
        print(f"[{keyword}] {choice['label']}")


def run_game():
    """Start a playthrough and process choices until it ends."""

    # Create fresh memory for this playthrough.
    game_state = create_game_state()

    print("FLANNAN: THE LAST LIGHT")
    print("Type a displayed keyword to choose, or EXIT to quit.")

    while True:
        # Display the opening scene or the scene we just entered.
        show_scene(game_state)

        # An empty choices dictionary means this branch stops here.
        if not SCENES[game_state["scene"]]["choices"]:
            print("You have reached the end of the current story branch.")
            break

        # Keep asking until the player submits a valid choice.
        while True:
            try:
                user_choice = input("\nYour choice: ")
            except (KeyboardInterrupt, EOFError):
                # Exit cleanly if the player interrupts terminal input.
                print("\nClosing the game.")
                return

            # EXIT is an interface command, not a story decision.
            if user_choice.strip().upper() == "EXIT":
                print("Closing the game.")
                return

            # The engine validates the choice and updates the state.
            if apply_choice(game_state, user_choice):
                break

            print("Invalid choice. Enter one of the displayed keywords.")


# Start the interface only when this module is run directly.
if __name__ == "__main__":
    run_game()