import sqlite3, json, os

DATA = {'DatabaseCreated':False,'NoteId':1, 'NoteTitles':[]}

"""
    The following functions are "helper" functions for this file and for the Database class
"""
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

def PrintTitles(database):
    titles = database.execute('SELECT NoteTitle FROM Notes')

    print('------------\nTITLES:\n')
    for i in titles:
        print(i[0],'\t')
    print('------------\n')

class Database:

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
                PrintTitles(self.db)

                TITLE = input('NoteTitle to delete(all to delete all of notes): ')

                if TITLE.lower() == 'all':
                    titles = self.db.execute('SELECT NoteTitle FROM Notes')
                    deleted = False

                    #if len(self.NoteTitles)>0:
                    for i in titles:
                        self.db.execute(f'DELETE FROM Notes WHERE NoteTitle="{i[0]}"')
                        self.db.commit()
                        deleted = True
                    else:
                        print('No NoteTitle(s) to delete.')
                    
                    if deleted:
                        # All go back to default
                        self.NoteTitles = []
                        self.NoteId = 1
                        UpdateJSON(self.NoteId,self.NoteTitles)
                        print('Successfully deleted \033[1mALL\033[0m notes')
                elif TITLE in self.NoteTitles:

                    self.db.execute(f'DELETE FROM Notes WHERE NoteTitle="{TITLE}"')
                    self.db.commit()

                    self.NoteTitles.remove(f'{TITLE}')
                    UpdateJSON(self.NoteId,self.NoteTitles)
                    self.NoteId -= 1

                    print(f'\033[0;36mSuccessfully deleted "{TITLE}"(#{self.NoteId})\033[0m')
                else:
                    print(f'"{TITLE}" doesn\'t exist')
            if action.lower() == 'upd':

                TO_UPD = input('\nWhat To Update(NoteTitle, NoteDetail): ')
                
                if TO_UPD.lower() == 'notedetail':
                    PrintTitles(self.db)

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
                elif TO_UPD.lower() == 'notetitle':
                    PrintTitles(self.db)

                    TITLE_TO_UPDATE = input('NoteTitle to update: ')

                    if TITLE_TO_UPDATE in self.NoteTitles:
                        NEW_TITLE_NAME = input(f'New NoteTitle Name For "{TITLE_TO_UPDATE}": ')

                        self.db.execute(f'''
                        UPDATE Notes
                        SET NoteTitle="{NEW_TITLE_NAME}"
                        where NoteTitle="{TITLE_TO_UPDATE}"
                        ''')
                        self.db.commit()

                        self.NoteTitles.remove(TITLE_TO_UPDATE)
                        self.NoteTitles.append(NEW_TITLE_NAME)
                        UpdateJSON(self.NoteId,self.NoteTitles)

                        print(f'Successfully updated NoteTitle of {TITLE_TO_UPDATE}')
                    else:
                        print(f'NoteTitle "{TITLE_TO_UPDATE}" doesn\'t exist')

    def _FinishDatabase_(self):
        ALL_INFO = self.db.execute('SELECT NoteId, NoteTitle, NoteDetails from Notes')

        print('------------------\nALL INFORMATION STORED\n')
        for i in ALL_INFO:
            print(i)
        else:
           print('No information stored(must\'ve been deleted!)')

        self.db.close()