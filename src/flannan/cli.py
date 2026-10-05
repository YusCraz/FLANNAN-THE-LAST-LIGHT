"""Play FLANNAN with instant transitions and background AI."""

import logging

from .session import FastSession
from .story import SCENES


def show_scene(session):
    """Display the story and choices without development labels."""

    scene = SCENES[session.state["scene"]]

    print(f"\n--- {scene['title']} ---")
    print(session.presentation["narration"])
    print()

    for keyword, choice in scene["choices"].items():
        print(f"[{keyword}] {choice['label']}")


def run_game():
    """Play the story without waiting for AI responses."""

    # Keep actual API warnings visible so failures aren't hidden.
       # Write technical warnings to a local log instead of the game screen.
    logging.basicConfig(
        filename="flannan.log",
        encoding="utf-8",
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s: %(message)s",
        force=True,
    )
    session = FastSession()

    try:
        print("FLANNAN: THE LAST LIGHT")
        print("Type a displayed keyword, or EXIT to quit.")

        while True:
            # Show the scene immediately.
            show_scene(session)

            if not SCENES[session.state["scene"]]["choices"]:
                print("End of playthrough.")
                break

            # Prepare upcoming narration while the player reads.
            session.prepare_choices()

            while True:
                user_choice = input("\nYour choice: ")

                if user_choice.strip().upper() == "EXIT":
                    print("Closing the game.")
                    return

                if session.choose(user_choice):
                    break

                print("Invalid choice. Use one of the displayed keywords.")

    except (KeyboardInterrupt, EOFError):
        print("\nClosing the game.")

    finally:
        session.close()


if __name__ == "__main__":
    run_game()