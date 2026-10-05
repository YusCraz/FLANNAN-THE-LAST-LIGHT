def create_game_state():
    """ create a separate starting sate for each new playthough"""
    return {
        #current positionin the story
        "scene": "missing_report",
        "chapter": 1,
        
        #gameplay values, messured from 0 to 100.
        "tension": 20, 
        "trust_ai": 50,
        
        #information collected during this playthrough.
        "clues": [],
        "previous_choices": [],
        "scene_history": ["missing_report"],
        
        #no scare has happened at the begining of the game, so this is set to false.
        "last_scare": None,
        
    }
    
    