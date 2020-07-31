from backend import (
    SetupDatabase
)
import os

NOTE_APPLICATION = SetupDatabase()
NOTE_APPLICATION.CreateDbTable()

if os.path.isfile(os.path.abspath('info.json')):
    NOTE_APPLICATION._StartupNotes_()
    NOTE_APPLICATION._FinishDatabase_()