"""A fictional lighthouse mystery from the missing report to three endings."""


def make_choice(label, next_scene, tension_change=0, trust_change=0):
    """Create a choice using the same fields our engine already expects."""

    # Keep the choice structure consistent throughout the story.
    return {
        "label": label,
        "next_scene": next_scene,
        "tension_change": tension_change,
        "trust_change": trust_change,
    }


# All reports, dialogue, and evidence below belong to our fictional story.
# Each next_scene value must match a key in this dictionary.
SCENES = {
    "missing_report": {
        "title": "Three Missing",
        "narration": (
            "Three keepers have stopped answering messages from the island.\n\n"
            "A passing vessel reported the lighthouse dark. "
            "No distress signal followed.\n\n"
            "You are a relief keeper, sent ahead to inspect the station "
            "while a search crew prepares to follow.\n\n"
            "Your instructions are simple: find the men, report the condition "
            "of the lighthouse, and restore the light if it is safe.\n\n"
            "The boat captain waits beside the departure gate."
        ),
        "choices": {
            "REPORT": make_choice(
                "Read the missing-keepers report", "case_report"
            ),
            "ASK": make_choice(
                "Ask the captain about the island", "captain_warning"
            ),
            "BOARD": make_choice(
                "Board the boat", "crossing"
            ),
        },
    },

    "case_report": {
        "title": "The Last Message",
        "narration": (
            "The report contains three names, a station inventory, "
            "and a copied message:\n\n"
            "'Relief delayed by weather. All three accounted for.'\n\n"
            "A note underneath reads: "
            "'Message received after the light was reported out.'\n\n"
            "Nothing explains why the keepers stopped answering.\n\n"
            "You fold the report and put it in your coat."
        ),
        "choices": {
            "BOARD": make_choice(
                "Join the captain aboard the boat", "crossing", 2
            ),
        },
    },

    "captain_warning": {
        "title": "A Familiar Voice",
        "narration": (
            "'Probably the transmitter,' the captain says. "
            "'Salt gets into everything.'\n\n"
            "He checks the fuel line before continuing.\n\n"
            "'If anyone calls you from the island, ask who they are. "
            "Yesterday, someone answered me using my brother's voice.'\n\n"
            "'Does your brother work there?'\n\n"
            "The captain tightens a fitting.\n\n"
            "'No.'"
        ),
        "choices": {
            "BOARD": make_choice(
                "Board without asking anything else", "crossing", 5
            ),
        },
    },

    "crossing": {
        "title": "The Crossing",
        "narration": (
            "By the time the island appears, the mainland is lost in rain.\n\n"
            "The captain brings the boat alongside the sheltered landing. "
            "He will wait offshore, where the swell cannot crush the hull.\n\n"
            "'Call when you want collecting. If the weather turns, "
            "stay inside until morning.'\n\n"
            "You climb onto the steps with a torch and a radio.\n\n"
            "Halfway up, a voice breaks through the static:\n\n"
            "'Relief at last. We left the door unlocked.'"
        ),
        "choices": {
            "IDENTIFY": make_choice(
                "Ask the speaker to identify himself",
                "radio_identity", 3, -5
            ),
            "CONTINUE": make_choice(
                "Continue toward the lighthouse",
                "lighthouse_exterior", 4, 5
            ),
        },
    },

    "radio_identity": {
        "title": "Which Keeper?",
        "narration": (
            "'Who is speaking?' you ask.\n\n"
            "'One of the keepers.'\n\n"
            "'Which one?'\n\n"
            "For a moment, you hear breathing in three different rhythms.\n\n"
            "'You'll know when you see us.'\n\n"
            "The transmission ends. Above the path, the lighthouse "
            "windows are black."
        ),
        "choices": {
            "CONTINUE": make_choice(
                "Reach the lighthouse door", "lighthouse_exterior", 5
            ),
        },
    },

    "lighthouse_exterior": {
        "title": "The Last Light",
        "narration": (
            "Rain runs down the lighthouse walls. The main door stands "
            "slightly open, but no light comes from inside.\n\n"
            "Your radio crackles:\n\n"
            "'Go inside. Do not look at the upper window.'\n\n"
            "Three knocks sound from behind the door."
        ),
        "choices": {
            "ENTER": make_choice(
                "Push the door open", "entry_hall", 5, 5
            ),
            "LOOK": make_choice(
                "Look at the upper window", "upper_window", 10, -5
            ),
            "ASK": make_choice(
                "Ask why you should not look", "radio_warning", 5, -5
            ),
        },
    },

    "upper_window": {
        "title": "The Fourth Shape",
        "narration": (
            "Three figures stand behind the upper window.\n\n"
            "You raise your torch. None of them moves.\n\n"
            "Then a fourth shape steps between them. "
            "It wears your coat and holds its torch exactly as you do.\n\n"
            "You lower your arm.\n\n"
            "It does not."
        ),
        "choices": {
            "ENTER": make_choice(
                "Get inside and find the stairs", "entry_hall", 8
            ),
        },
    },

    "radio_warning": {
        "title": "Behind the Door",
        "narration": (
            "'Why shouldn't I look?'\n\n"
            "'Because they haven't noticed you yet.'\n\n"
            "You switch off the radio.\n\n"
            "From behind the wooden door, the same voice says:\n\n"
            "'Both hands. The handle sticks.'"
        ),
        "choices": {
            "ENTER": make_choice(
                "Open the door", "entry_hall", 8, -5
            ),
        },
    },

    "entry_hall": {
        "title": "A Station Without Keepers",
        "narration": (
            "The hallway is empty. Three coats hang beside the stairs.\n\n"
            "You call out. No one answers.\n\n"
            "A duty notebook lies open in the adjoining room. "
            "A service door leads toward the west landing. "
            "Above you, something heavy turns in the lantern room.\n\n"
            "You need to find out what happened before touching the light."
        ),
        "choices": {
            "READ": make_choice(
                "Inspect the keeper's notebook", "keeper_notebook", 4, -5
            ),
            "WEST": make_choice(
                "Investigate the west landing", "west_landing", 6
            ),
            "CLIMB": make_choice(
                "Follow the sound upstairs", "staircase", 10, 5
            ),
        },
    },

    "keeper_notebook": {
        "title": "The Names in the Margins",
        "narration": (
            "The early entries describe ordinary station work.\n\n"
            "Later, names appear in the margins. The same names repeat "
            "beside different duties, as though the writer is checking "
            "who is still present.\n\n"
            "The last page reads:\n\n"
            "'It answers in whoever you expect to hear. "
            "We closed the shutters. We are going down to the landing.'\n\n"
            "Below that, in a different hand:\n\n"
            "'If we return asking for the light, do not let us in.'"
        ),
        "choices": {
            "WEST": make_choice(
                "Follow their route to the landing", "west_landing", 6, -5
            ),
            "CLIMB": make_choice(
                "Check whether the shutters are still closed",
                "staircase", 8, -5
            ),
        },
    },

    "west_landing": {
        "title": "Where the Steps End",
        "narration": (
            "The service path descends to broken railings and spray.\n\n"
            "A torn rope is caught around an iron post. "
            "Beyond it, waves cover the lowest steps.\n\n"
            "The keepers could have been swept away here. "
            "You cannot tell from what remains.\n\n"
            "Then your torch catches three people standing below the water.\n\n"
            "Their faces tilt upward.\n\n"
            "Your radio says, 'We can't find the steps. Give us the light.'"
        ),
        "choices": {
            "RETREAT": make_choice(
                "Return inside and inspect the lantern room",
                "staircase", 10, -5
            ),
            "CALL": make_choice(
                "Call the captain for collection", "captain_call", 5
            ),
        },
    },

    "captain_call": {
        "title": "Two Answers",
        "narration": (
            "You call the boat.\n\n"
            "'Stay at the sheltered landing,' the captain answers. "
            "'I'm coming in now.'\n\n"
            "A second transmission overlaps the first. "
            "It is also the captain:\n\n"
            "'Don't come down. That's not my boat.'\n\n"
            "Around the headland, a small navigation light appears."
        ),
        "choices": {
            "LEAVE": make_choice(
                "Take the risk and reach the sheltered landing",
                "ending_departure", -10, -5
            ),
            "STAY": make_choice(
                "Stay inside and climb to the lantern room",
                "staircase", 8, -5
            ),
        },
    },

    "staircase": {
        "title": "Another Pair of Feet",
        "narration": (
            "You climb the spiral stairs.\n\n"
            "After the first turn, footsteps begin below you. "
            "They stop when you stop.\n\n"
            "You take two steps quickly. Something below takes three.\n\n"
            "At the top, you push through the lantern-room door "
            "and slide the bolt across.\n\n"
            "A hand rests against the other side."
        ),
        "choices": {
            "INSPECT": make_choice(
                "Inspect the lamp and its controls", "lantern_room", 8
            ),
            "LISTEN": make_choice(
                "Listen at the door", "door_voice", 10, -5
            ),
        },
    },

    "door_voice": {
        "title": "Your Own Voice",
        "narration": (
            "'Open it,' someone whispers.\n\n"
            "The voice is yours.\n\n"
            "'You were supposed to wait for the search crew.'\n\n"
            "The handle turns gently, once in each direction.\n\n"
            "'It doesn't matter. We only needed one.'"
        ),
        "choices": {
            "BACK": make_choice(
                "Back away toward the lamp", "lantern_room", 8, -10
            ),
        },
    },

    "lantern_room": {
        "title": "What the Light Is For",
        "narration": (
            "The lamp is intact. Its metal shutters are closed, "
            "except for a narrow gap overlooking the sea.\n\n"
            "Through that gap, you see figures standing on the water. "
            "There are far more than three.\n\n"
            "A batteryless radio lies beside the controls.\n\n"
            "'The light gives us a way across,' it says. "
            "'Turn it on. Bring your keepers home.'\n\n"
            "You find the lamp switch, the shutter lever, "
            "and a service hatch leading to an exterior ladder.\n\n"
            "Something begins knocking on the bolted door."
        ),
        "choices": {
            "LIGHT": make_choice(
                "Open the shutters and switch on the beacon",
                "ending_beacon", 20, 15
            ),
            "SEAL": make_choice(
                "Lock the shutters closed and escape by the ladder",
                "ending_dark", 5, -15
            ),
            "ESCAPE": make_choice(
                "Leave the controls untouched and escape by the ladder",
                "ending_departure", -5, -5
            ),
        },
    },

    # Empty choice dictionaries tell the CLI that a branch has ended.
    "ending_departure": {
        "title": "Ending — An Unfinished Report",
        "narration": (
            "You reach the sheltered landing. The captain pulls you "
            "aboard without asking why you are shaking.\n\n"
            "As the island disappears behind rain, you tell him "
            "about the broken railings and the empty rooms.\n\n"
            "You leave out the people beneath the water.\n\n"
            "By morning, your report says only:\n\n"
            "'Three keepers missing. Cause undetermined.'\n\n"
            "The captain reads it, then looks at you.\n\n"
            "'Three?' he asks. 'Then who helped you into the boat?'"
        ),
        "choices": {},
    },

    "ending_dark": {
        "title": "Ending — The Last Keeper",
        "narration": (
            "You wrench the shutter lever down and engage its lock.\n\n"
            "The voice changes. For the first time, it sounds afraid.\n\n"
            "'We have been out here so long.'\n\n"
            "You leave the lamp dark and descend the exterior ladder. "
            "At the sheltered landing, the captain hauls you aboard.\n\n"
            "The search crew reaches the station after sunrise. "
            "They find no keepers and no one behind the bolted door.\n\n"
            "You cannot explain the disappearance. "
            "You can only tell them not to reopen the shutters.\n\n"
            "That night, your disconnected radio clicks.\n\n"
            "'Your shift isn't over.'"
        ),
        "choices": {},
    },

    "ending_beacon": {
        "title": "Ending — Relief Has Arrived",
        "narration": (
            "You open the shutters and press the switch.\n\n"
            "The beam sweeps across the sea. Where it touches the water, "
            "figures lift their heads and begin walking toward the island.\n\n"
            "The knocking stops.\n\n"
            "Behind you, three soaked keepers stand in the open doorway. "
            "One places a cold hand on your shoulder.\n\n"
            "'Thank you for relieving us.'\n\n"
            "Morning comes. You can see the landing, but you cannot "
            "step away from the lamp.\n\n"
            "Days later, a boat approaches. Your hand lifts the radio "
            "without your permission.\n\n"
            "'Relief at last. We left the door unlocked.'"
        ),
        "choices": {},
    },
}