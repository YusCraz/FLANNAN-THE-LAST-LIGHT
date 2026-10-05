"""Validate player choices and update the story state    """

#Import story content from the same python package
from .story import SCENES


def apply_choice(game_state, user_choice):
    """ Apply an allowed choice. Return False if the input is invalid."""
    
    
    #Normalize input so "enter" and "ENTER" mean same things.
    
    keyword = user_choice.strip().upper()
    
    #Get the choice available in the player's current scene.
    current_scene_id = game_state["scene"]
    allowed_choice = SCENES[current_scene_id]["choices"]
    
    #reject invalid input before changing any state. 
    if keyword not in allowed_choice:
        return False
    
    
    #Read te hthe selected choice and its destination. 
    choice = allowed_choice[keyword]
    next_scene_id = choice["next_scene"]
    
    #A missing destination means our story content needs fixing.
    if next_scene_id not in SCENES:
        raise ValueError(f"Unknown destination scene: {next_scene_id}")
    
    #Calculate both gameplay value before updating the dictionary.
    #clamp each value to the allowed range og 0-100.
    new_tension = max(
        0, min(100, game_state["tension"] + choice["tension_change"])
    )
    
    new_trust = max(
        0, min(100, game_state["trust_ai"] + choice["trust_change"])
    )    
     
     #aplly the validate transation.
    game_state["tension"] = new_tension
    game_state["trust_ai"] = new_trust
    game_state["scene"] = next_scene_id
    
    #recoed waht the player chose and where that choice led.
    game_state["previous_choices"].append({
         "scene": current_scene_id,
         "choice": keyword,
        "next_scene": next_scene_id,
        
    
    }) 
     
        
 #keep the ordered list of scenes visited
    game_state["scene_history"].append(next_scene_id)
 
    return True