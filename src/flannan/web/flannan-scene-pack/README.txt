FLANNAN: THE LAST LIGHT — Scene artwork pack

18 original PNG illustrations, named to match SCENES keys in story.py.
Image bytes are unchanged: no resizing, conversion, or regeneration.
The corrected captain_call image is included. The rejected realistic exterior
and the superseded lit-beacon captain_call draft are excluded.

INSTALL
1. Extract this ZIP.
2. Copy the assets folder into:
   D:\Projects\Flannan-The-Last-Light\src\flannan\web\
3. Example resulting path:
   D:\Projects\Flannan-The-Last-Light\src\flannan\web\assets\scenes\entry_hall.png

MAPPING
assets/scene-images.json maps every scene ID to its path relative to the web folder.
All images follow: assets/scenes/<scene_id>.png
No manual image renaming is needed.

This pack does not modify app.js, HTML, or API routes. The frontend still needs
to display the matching image when scene_id changes. Browser URL prefixes depend
on the existing FastAPI static mount; prepend its mount path when using the map.

These are flattened static illustrations. Animated figures, doors, fog, sound,
and Rive integration are separate work.
