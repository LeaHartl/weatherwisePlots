# weatherwisePlots

wwMaps_LH.py is the main file and calls makeFigs.py to make the plots. uncomment lines for scatter plots if you want those.

wwMaps_LH checks if data files for AK, canada, russia are present and runs helper functions to generate them if not. 
run like so with desired year/ month - this does it for August 2018: ./wwMaps_LH.py 2018 08. 
May not work for dates far in the past, I have no idea what the older russia & canada data looks like.
