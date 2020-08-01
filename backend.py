import sqlite3, json, os

DATA = {'DatabaseCreated':False,'NoteId':1, 'NoteTitles':[],'IsUpdated':False, 'UpdatedTitles':[], 'RecentlyUpdatedStatus':''}

"""
    The following functions are "helper" functions for this file and for the Database class
"""
def UpdateDatabase(database,information):
    database.execute(information)
    database.commit()

def UpdateJSON(number,NoteTitles,IsUpdated,UpdatedTitles,UpdStat):
    DATA['DatabaseCreated'] = True
    DATA['NoteId'] = number
    DATA['NoteTitles'] = NoteTitles
    DATA['IsUpdated'] = IsUpdated
    DATA['UpdatedTitles'] = UpdatedTitles
    DATA['RecentlyUpdatedStatus'] = UpdStat

    with open('info.json','w') as file:
        file.write(json.dumps(
            DATA,
            indent=2,
            sort_keys=False
        ))

def Menu():
    print('Welcome to Notes! Here you can write a note, then it\'ll automatically save!\n\nKey Commands:\nnew - Create new note\nexit - Leave Application\nShow - Show all notes\ndel - Delete a specific NoteTitle\nupd - Update a specific NoteTitle\nclr - Clear Terminal\n')

def PrintTitles(database):
    titles = database.execute('SELECT NoteTitle FROM Notes')

    print('------------\nTITLES:\n')
    for i in titles:
        print(i[0],'\t')
    print('------------\n')

class Database:

    def __init__(self):
        self.db = sqlite3.connect('DB.db')
        self.NoteTitle = ''
        self.NoteDetails = ''
        self.run = True

        if not os.path.isfile('info.json'):
            self.HasCreatedTable = False
            self.IsUpdated = False
            self.NoteId = 1 # Starts with 1 note
            self.NoteTitles = []
            self.UpdatedTitles = []
            self.RecentlyUpdateStatus = ''
        else:
            DATA = json.loads(
                open('info.json','r').read()
            )
            self.HasCreatedTable = True
            self.NoteId = DATA['NoteId']
            self.NoteTitles = DATA['NoteTitles']
            self.IsUpdated = DATA['IsUpdated']
            self.UpdatedTitles = DATA['UpdatedTitles']
            self.RecentlyUpdateStatus = DATA['RecentlyUpdatedStatus']
    
    def CreateDbTable(self):
        
        if not self.HasCreatedTable:

            self.db.execute('''
                CREATE TABLE Notes (
                    NoteId INT PRIMARY KEY NOT NULL,
                    NoteTitle TEXT NOT NULL,
                    NoteDetails TEXT NOT NULL,
                    UPDATE_DETAILS TEXT
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

        Menu()

        while self.run:
            action = input('\nAction -> ')

            if action.lower() == 'new':

                self.NoteTitle = input(f'Title Of Note #{self.NoteId}: ')

                if self.NoteTitle in self.NoteTitles:

                    while self.NoteTitle in self.NoteTitles:
                      print(f'\nError: NoteTitle {self.NoteTitle} is already taken..make a new one!\n')
                      self.NoteTitle = input(f'Title Of Note #{self.NoteId}: ')

                if not self.NoteTitle == "":
                    self.NoteTitles.append(self.NoteTitle)
                    self.NoteDetails = input(f'Deatails for Note #{self.NoteId}({self.NoteTitle}): ')

                    if not self.NoteDetails == "":
                        UpdateDatabase(self.db,f'''
                        INSERT INTO Notes(NoteId,NoteTitle,NoteDetails,UPDATE_DETAILS)
                        VALUES({self.NoteId},"{self.NoteTitle}","{self.NoteDetails}","ORIGINAL")
                        ''')

                        self.NoteId += 1
                        UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus)
                    else:
                        print('NoteDetail was not assigned')
                else:
                    print('NoteTitle was not assigned')
            if action.lower() == 'exit':
                self.run = False
                print("Successfully left project.\n")
            if action.lower() == 'show':
                #db_connect = sqlite3.connect('db.db')
                info = self.db.execute('SELECT NoteId, NoteTitle, NoteDetails, UPDATE_DETAILS from Notes')

                for r in info:
                    if r[1] in self.UpdatedTitles:
                        print(f'\nInformation for Note "{r[1]}"(#{r[0]}) \033[1mUPDATED -> {self.RecentlyUpdateStatus}\033[0m\n')

                        self.IsUpdated = False
                        UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus)
                    else:
                        print(f'\nInformation for Note "{r[1]}"(#{r[0]}) \033[1mORIGINAL\033[0m\n')
                    print(f'\t{r[2]}')
            if action.lower() == 'clr':
                os.system('clear')
                Menu()
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
                        if len(self.NoteTitles) < 1:
                            print('No NoteTitle(s) to delete.')
                    
                    if deleted:
                        # All go back to default
                        self.NoteTitles = []
                        self.NoteId = 1
                        UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus)
                        print('Successfully deleted \033[1mALL\033[0m notes')
                elif TITLE in self.NoteTitles:

                    self.db.execute(f'DELETE FROM Notes WHERE NoteTitle="{TITLE}"')
                    self.db.commit()

                    self.NoteTitles.remove(f'{TITLE}')
                    UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus)
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

                        LAST_UPDATE_DETAIL = self.db.execute('SELECT UPDATE_DETAILS FROM Notes')

                        for i in LAST_UPDATE_DETAIL:
                            LAST_UPDATE_DETAIL = " "+str(i[0])

                        self.db.execute(f'''
                        UPDATE Notes
                        SET NoteDetails="{NEW_DETAILS}"
                        WHERE NoteTitle="{TITLE_TO_UPDATE}"
                        ''')

                        if LAST_UPDATE_DETAIL != "Updated NoteDetail":
                            if LAST_UPDATE_DETAIL == " ORIGINAL": LAST_UPDATE_DETAIL = "."
                            self.RecentlyUpdateStatus = "Updated NoteDetail"
                            self.db.execute(f'''
                            UPDATE Notes
                            SET UPDATE_DETAILS="Updated NoteDetail{LAST_UPDATE_DETAIL}"
                            WHERE NoteTitle="{TITLE_TO_UPDATE}"
                            ''')
                        self.db.commit()

                        self.IsUpdated = True
                        self.UpdatedTitles.append(TITLE_TO_UPDATE)

                        UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus)

                        print(f'Successfully updated "{TITLE_TO_UPDATE}"')
                    else:
                        print(f'"{TITLE_TO_UPDATE}" doesn\'t exist')
                elif TO_UPD.lower() == 'notetitle':
                    PrintTitles(self.db)

                    TITLE_TO_UPDATE = input('NoteTitle to update: ')

                    if TITLE_TO_UPDATE in self.NoteTitles:
                        NEW_TITLE_NAME = input(f'New NoteTitle Name For "{TITLE_TO_UPDATE}": ')

                        LAST_UPDATE_DETAIL = self.db.execute('SELECT UPDATE_DETAILS FROM Notes')

                        for i in LAST_UPDATE_DETAIL:
                            LAST_UPDATE_DETAIL = " "+i[0]
                            break
                        
                        if LAST_UPDATE_DETAIL != "Updated NoteTitle":
                            if LAST_UPDATE_DETAIL == " ORIGINAL": LAST_UPDATE_DETAIL = "."
                            self.db.execute(f'''
                            UPDATE Notes
                            SET UPDATE_DETAILS="Updated NoteTitle{LAST_UPDATE_DETAIL}"
                            WHERE NoteTitle="{TITLE_TO_UPDATE}"
                            ''')
                            self.RecentlyUpdateStatus = "Updated NoteTitle"

                        self.db.execute(f'''
                        UPDATE Notes
                        SET NoteTitle="{NEW_TITLE_NAME}"
                        WHERE NoteTitle="{TITLE_TO_UPDATE}"
                        ''')
                        self.db.commit()

                        self.NoteTitles.remove(TITLE_TO_UPDATE)
                        self.NoteTitles.append(NEW_TITLE_NAME)
                        self.IsUpdated = True
                        self.UpdatedTitles.append(NEW_TITLE_NAME)

                        UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus)

                        print(f'Successfully updated NoteTitle of {TITLE_TO_UPDATE}')
                    else:
                        print(f'NoteTitle "{TITLE_TO_UPDATE}" doesn\'t exist')

    def _FinishDatabase_(self):
        ALL_INFO = self.db.execute('SELECT NoteId, NoteTitle, NoteDetails, UPDATE_DETAILS from Notes')

        print('------------------\nALL INFORMATION STORED\n')
        for i in ALL_INFO:
            print(i)
        else:
            if len(self.NoteTitles) < 1:
                print('No information stored(must\'ve been deleted!)')

        self.db.close()
