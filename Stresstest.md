Für Action Control von Gesture Recognition:
-> als Standart sind immer die HalloWelt Programme ausgewählt. Wenn der User das ändern möchte muss das gewünchste Skript bei der passenden Geste aus dem drop_down menue auswählen.
-> neue Scripte müsen als eine Lua_datei hochgeladen werden, heißt sie müssen auf .lua enden
-> Sollte die Funktion nicht Ausführbar sein wird "Skript nicht erkannt" zurückgegen. Wird keien Geste erkannt wird auch "Skript nicht erkannt" ausgegeben
-> momentan kann man mit dem Lua_script nur auf die Math Bib von Python und auf die print von Python zugreifen, welche in die Konsole schreibt. 
-> dass, was mit return zurückgegeben wird, wird im Textfeld ausgegeben, solange es sich um einen String handelt oder als solcher dargestellt werden kann.

Für GestureReco: 
-> Wenn eine Geste erkannt wird, wird das dazugehörige Lua_Skript ausgeführt. Wenn das Lua_Skript eine Rückgabe hat, so wird diese im Textfeld dargestellt. Es wird immer nur das aktuellste im Textfeld dargestellt
