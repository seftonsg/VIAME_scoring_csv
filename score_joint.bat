@echo off

REM Setup VIAME Paths (no need to set if installed to registry or already set up)

SET VIAME_INSTALL=C:\VIAME-v0.9.13

CALL "%VIAME_INSTALL%\setup_viame.bat"

REM Run score tracks on data for singular metrics

SET TRUTHS=TRUTH_CSL_manual_ML_4.csv
SET TRACKS=COMPUTED_1c_tracks_ML_4.csv

python %VIAME_INSTALL%\configs\score_results.py ^
 -computed %TRACKS% ^
 -truth    %TRUTHS% ^
 -threshold 0.05 -stats output_score_tracks.txt

REM Generate ROC

python %VIAME_INSTALL%\configs\score_results.py ^
 -computed %TRACKS% ^
 -truth    %TRUTHS% ^
 -roc output_roc.png

pause
