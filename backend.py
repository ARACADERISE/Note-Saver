import sqlite3, json, os

DATA = {'DatabaseCreated':False,'NoteId':1, 'NoteTitles':[]}

def UpdateDatabase(database,information):
    database.execute(information)
    database.commit()

def UpdateJSON(number,NoteTitles):
    DATA['DatabaseCreated'] = True
    DATA['NoteId'] = number
    DATA['NoteTitles'] = NoteTitles

    with open('info.json','w') as file:
        file.write(json.dumps(
            DATA,
            indent=2,
            sort_keys=False
        ))

class SetupDatabase:

    def __init__(self):
        self.db = sqlite3.connect('db.db')
        self.NoteTitle = ''
        self.NoteDetails = ''
        self.run = True

        if not os.path.isfile('info.json'):
            self.HasCreatedTable = False
            self.NoteId = 1 # Starts with 1 note
            self.NoteTitles = []
        else:
            DATA = json.loads(
                open('info.json','r').read()
            )
            self.HasCreatedTable = True
            self.NoteId = DATA['NoteId']
            self.NoteTitles = DATA['NoteTitles']
    
    def CreateDbTable(self):
        
        if not self.HasCreatedTable:

            self.db.execute('''
                CREATE TABLE Notes (
                    NoteId INT PRIMARY KEY NOT NULL,
                    NoteTitle TEXT NOT NULL,
                    NoteDetails TEXT NOT NULL
                );
            ''')

            self.HasCreatedTable = True
            DATA['DatabaseCreated'] = self.HasCreatedTable

            with open('info.json','w') as file:
                file.write(json.dumps(
                    DATA,
                    indent=2,
                    sort_keys=False
                ))
    
    def _StartupNotes_(self):
        print('Welcome to Notes! Here you can write a note, then it\'ll automatically save!\n\nKey Commands:\nnew - Create new note\nexit - Leave Application\nShow - Show all notes\ndel - Delete a specific NoteTitle\nupd - Update a specific NoteTitle\n')

        while self.run:
            action = input('\nAction -> ')

            if action.lower() == 'new':

                self.NoteTitle = input(f'Title Of Note #{self.NoteId}: ')

                if self.NoteTitle in self.NoteTitles:

                    while self.NoteTitle in self.NoteTitles:
                      print(f'\nError: NoteTitle {self.NoteTitle} is already taken..make a new one!\n')
                      self.NoteTitle = input(f'Title Of Note #{self.NoteId}: ')

                self.NoteTitles.append(self.NoteTitle)
                self.NoteDetails = input(f'Deatails for Note #{self.NoteId}({self.NoteTitle}): ')

                UpdateDatabase(self.db,f'''
                INSERT INTO Notes(NoteId,NoteTitle,NoteDetails)
                VALUES({self.NoteId},'{self.NoteTitle}','{self.NoteDetails}')
                ''')

                self.NoteId += 1
                UpdateJSON(self.NoteId,self.NoteTitles)
            if action.lower() == 'exit':
                self.run = False
                print("Successfully left project.\n")
            if action.lower() == 'show':
                #db_connect = sqlite3.connect('db.db')
                info = self.db.execute('SELECT NoteId, NoteTitle, NoteDetails from Notes')

                for r in info:
                    print(f'\nInformation for Note "{r[1]}"(#{r[0]})\n')
                    print(f'\t{r[2]}')
            if action.lower() == 'del':

              TITLE = input('\nNoteTitle to delete: ')

              if TITLE in self.NoteTitles:

                self.db.execute(f'DELETE FROM Notes WHERE NoteTitle="{TITLE}"')
                self.db.commit()

                self.NoteTitles.remove(f'{TITLE}')
                UpdateJSON(self.NoteId,self.NoteTitles)
                self.NoteId -= 1

                print(f'\033[0;36mSuccessfully deleted "{TITLE}"(#{self.NoteId})\033[0m')
              else:
                print(f'"{TITLE}" doesn\'t exist')
            if action.lower() == 'upd':

              TITLE_TO_UPDATE = input('NoteTitle to update: ')
              if TITLE_TO_UPDATE in self.NoteTitles:
                NEW_DETAILS = input(f'New NoteDetails for "{TITLE_TO_UPDATE}": ')
                self.db.execute(f'''
                UPDATE Notes
                SET NoteDetails="{NEW_DETAILS}"
                WHERE NoteTitle="{TITLE_TO_UPDATE}"
                ''')
                self.db.commit()

                print(f'Successfully updated "{TITLE_TO_UPDATE}"')
              else:
                print(f'"{TITLE_TO_UPDATE}" doesn\'t exist')


    def _FinishDatabase_(self):
        ALL_INFO = self.db.execute('SELECT NoteId, NoteTitle, NoteDetails from Notes')

        print('------------------\nPRINTING ALL INFORMATION\n')
        for i in ALL_INFO:
            print(i)

        self.db.close()