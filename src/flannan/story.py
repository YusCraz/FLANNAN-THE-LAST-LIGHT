""" Define story scenes, narration an allowed player choices. """

#Each scene has a uniqe ID that the game state can reference.

SCENES = {
    "lighthouse_exterior": {
        "title": "The Last light ",
        
        
        #Scripted narration until we cannect the AI director
        "narration":(
            "You REach the lighthouse door. Rain runs down the stone walls."
            "the Lantern above you is dark. \n\n"
            "Your radio carckles: 'Go inside, Do not look at the upper window.' \n\n"
            "then you hear Three knocks from behind the door"
            ),
        
        
        # only these keyword are valid while the player is in this scene.
        "choices":{
            "ENTER":{
                "label": "Open the lighthouse door",
                "next_scene": "entry_hall",
                "tension_change": 5,
                "trust_change": 5,
                },
            
            "LOOK":{
                "label": "Look at the upper window",
                "next_scene": "upper_window",
                "tension_change": 10,
                "trust_change": -5,
                },
            
            "ASK":{
                "label": "Ask the voice what is upstairs",
                "next_scene": "radio_warning",
                "tension_change": 3,
                "trust_change": 0,
                },
            
            },
            
        },
    
    
    "entry_hall": {
        "title": "The Open Door",
        "narration":(
            "The door opens before you touch the handle."
            "Your light catches wet footprints crossing the hall. \n\n"
            "The radio whispers: ' Close it before they notice.'"
            
            
            
            
        ),
        
        
        #this branch stops here wntill we write its next decisions
        "choices": {},
        
        
    
    },
    
    
    
    "upper_window": {
        "title": "The Watcher",
        "narration":(
            "You look up. Someone stands behind the upper window, "
            "holding a lantern that gives off no light.\n\n"
            "Your radio falls silent. The figure slowly raises "
            "one finger to its lips."
            
        ),
        
        #An empty choice dictionary marks a stooping point for now. 
        "choices": {},
        
        
        
        
    }, 
    
    "radio_warning": {
        "title": "The Voice",
        "narration":(
            "'What is Upstairs?' you ask. \n\n"
            "Static fills the radio. Then the voice returns:"
            "'I said the window. I never said it was upstairs.'\n\n"
            "Behind the door, the knocking stops."
        
            
            
        ),
        
        "choices": {},
        
        
        
        
        
    },
    
}
    
    


