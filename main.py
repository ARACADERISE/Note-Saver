from backend import (
    Database
)
import os

NOTE_APPLICATION = Database()
NOTE_APPLICATION.CreateDbTable()

if os.path.isfile('info.json'):
    NOTE_APPLICATION._StartupNotes_()
    NOTE_APPLICATION._FinishDatabase_()