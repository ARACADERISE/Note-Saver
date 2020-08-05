import sqlite3, json, os
from datetime import date
from Port import (
    Port
)

# Temporary information to keep everything up to date
DATA = {'DatabaseCreated':False,'NoteId':1, 'NoteTitles':[],'IsUpdated':False, 'UpdatedTitles':[], 'RecentlyUpdatedStatus':'','LastOldInfo':''}

"""
    The following functions are "helper" functions for this file and for the Database class
"""
def UpdateDatabase(database,information):
    database.execute(information)
    database.commit()

def UpdateJSON(number,NoteTitles,IsUpdated,UpdatedTitles,UpdStat,LOI):
    DATA['DatabaseCreated'] = True
    DATA['NoteId'] = number
    DATA['NoteTitles'] = NoteTitles
    DATA['IsUpdated'] = IsUpdated
    DATA['UpdatedTitles'] = UpdatedTitles
    DATA['RecentlyUpdatedStatus'] = UpdStat
    DATA['LastOldInfo'] = LOI

    with open('info.json','w') as file:
        file.write(json.dumps(
            DATA,
            indent=2,
            sort_keys=False
        ))

def Menu():
    print('Welcome to Notes! Here you can write a note, then it\'ll automatically save!\n\nKey Commands:\nnew - Create new note\nexit - Leave Application\nShow - Show all notes\ndel - Delete a specific NoteTitle\nupd - Update a specific NoteTitle\nclr - Clear Terminal\n')

def PrintTitles(database,titles_):
    titles = database.execute('SELECT NoteTitle FROM Notes')
    f = 1

    print('------------\nTITLES:\n')
    for i in titles:
        print(str(f)+') ',i[0],'\t')
        titles_.append(i[0])
        f+=1
    print('------------\n')

class Database:

    def __init__(self):
        self.db = sqlite3.connect('DB.db')
        self.NoteTitle = ''
        self.NoteDetails = ''
        self.run = True
        self.TodaysDate = date.today()
        self.PortDb = Port(self.db)
        self.PortIdName = ''
        self.Port_Connection = ''

        if not os.path.isfile('info.json'):
            self.HasCreatedTable = False
            self.IsUpdated = False
            self.NoteId = 1 # Starts with 1 note
            self.NoteTitles = []
            self.UpdatedTitles = []
            self.RecentlyUpdateStatus = ''
            self.LastOldInfo = ''            

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
            self.LastOldInfo = DATA['LastOldInfo']
    
    def CreateDbTable(self):
        
        if not self.HasCreatedTable:

            self.db.execute('''
                CREATE TABLE Notes (
                    NoteId INT PRIMARY KEY NOT NULL,
                    NoteTitle TEXT NOT NULL,
                    NoteDetails TEXT NOT NULL,
                    Port_Connection TEXT NOTE NULL,
                    UPDATE_DETAILS TEXT,
                    DATE TEXT NOT NULL,
                    UPDATE_DATE TEXT
                );
            ''')
            self.PortDb._CreatePortTable_()

            self.HasCreatedTable = True
            DATA['DatabaseCreated'] = self.HasCreatedTable

            with open('info.json','w') as file:
                file.write(json.dumps(
                    DATA,
                    indent=2,
                    sort_keys=False
                ))
            
            self.PortDb._Update_Data_(DATA)
    
    def _StartupNotes_(self):

        Menu()

        while self.run:
            if not os.path.isfile('port_info.json'):
                CREATE_PORT = input('Create A Port(random number that you will be able to remember) -> ')
                PORT_NAME = input(f'Port {CREATE_PORT} Name -> ')

                CREATE_PORT,PORT_NAME = self.PortDb._CHECK_NEW_PORT_DETAIL_(CREATE_PORT,PORT_NAME)
                self.PortDb._INSERT_(f'''INSERT INTO Ports(PortId,PortId_Name,Notes_In_Port) VALUES ("{CREATE_PORT}","{PORT_NAME}",{self.NoteId})''')
                self.PortDb._Connect_To_Port_(self.PortDb._Port_Connection_())

                Menu()
                self.PortIdName = self.PortDb.GatherPortName()
            elif os.path.isfile('port_info.json'):
                self.PortIdName = self.PortDb.GatherPortName()

                if self.PortIdName == '':
                    self.PortDb.PrintPorts()
                    Port_To_Connect_To = input('Port To Connect To -> ')
                    self.Port_Connection = self.PortDb._Connect_To_Port_(Port_To_Connect_To)

                    Menu()
                    self.PortIdName = self.PortDb.GatherPortName()
            
            self.Port_Connection = self.PortDb._Port_Connection_()
            if self.PortIdName != '':
                print(f'\n"{self.PortIdName}"')
            action = input('Action -> ')

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
                        INSERT INTO Notes(NoteId,NoteTitle,NoteDetails,Port_Connection,UPDATE_DETAILS,DATE)
                        VALUES({self.NoteId},"{self.NoteTitle}","{self.NoteDetails}","{self.PortDb._Port_Connection_()}","ORIGINAL","{self.TodaysDate}")
                        ''')

                        self.NoteId += 1
                        UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus,self.LastOldInfo)
                    else:
                        self.NoteTitles.remove(self.NoteTitle)
                        print('NoteDetail was not assigned')
                else:
                    print('NoteTitle was not assigned')
            if action.lower() == 'exit':
                self.run = False
                print("Successfully left project.\n")
            if action.lower() == 'show':
                #db_connect = sqlite3.connect('db.db')
                info = self.db.execute(f'SELECT NoteId, NoteTitle, NoteDetails, UPDATE_DETAILS, DATE, Port_Connection FROM Notes WHERE Port_Connection="{self.Port_Connection}"')

                for r in info:
                    #if r[5] == self.PortIdName:
                    if r[1] in self.UpdatedTitles:
                        if self.RecentlyUpdateStatus == 'Updated NoteTitle':
                            print(f'\nInformation for Note "{r[1]}"(#{r[0]}) \033[1mUPDATED -> {self.RecentlyUpdateStatus}\033[0m ({r[4]})\nOLD NoteTitle -> "{self.LastOldInfo}"\n')
                        else:
                            print(f'\nInformation for Note "{r[1]}"(#{r[0]}) \033[1mUPDATED -> {self.RecentlyUpdateStatus}\033[0m ({r[4]})\n')

                        self.IsUpdated = False
                        UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus,self.LastOldInfo)

                        if self.RecentlyUpdateStatus == 'Updated NoteDetails':
                            print(f'\tOLD INFO -> {self.LastOldInfo}\n\tNEW INFO -> {r[2]}')
                        else:
                            print(f'\t{r[2]}')
                    else:
                        print(f'\nInformation for Note "{r[1]}"(#{r[0]}) \033[1mORIGINAL\033[0m ({r[4]})\n')
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
                        UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus,self.LastOldInfo)
                        print('Successfully deleted \033[1mALL\033[0m notes')
                elif TITLE in self.NoteTitles:

                    self.db.execute(f'DELETE FROM Notes WHERE NoteTitle="{TITLE}"')
                    self.db.commit()

                    self.NoteTitles.remove(f'{TITLE}')
                    UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus,self.LastOldInfo)
                    self.NoteId -= 1

                    print(f'\033[0;36mSuccessfully deleted "{TITLE}"(#{self.NoteId})\033[0m')
                else:
                    print(f'"{TITLE}" doesn\'t exist')
            if action.lower() == 'upd':

                TO_UPD = input('\nWhat To Update(NoteTitle, NoteDetail): ')
                
                if TO_UPD.lower() == 'notedetail':
                    titles=[]
                    PrintTitles(self.db,titles)

                    TITLE_TO_UPDATE = input('NoteTitle to update: ')

                    if TITLE_TO_UPDATE.isdigit():
                        TITLE_TO_UPDATE = titles[int(TITLE_TO_UPDATE)-1]

                    if TITLE_TO_UPDATE in self.NoteTitles:
                        NEW_DETAILS = input(f'New NoteDetails for "{TITLE_TO_UPDATE}": ')

                        LAST_UPDATE_DETAIL = self.db.execute('SELECT UPDATE_DETAILS FROM Notes')

                        for i in LAST_UPDATE_DETAIL:
                            LAST_UPDATE_DETAIL = " "+str(i[0])
                            break
                        
                        LAST_INFORMATION = self.db.execute('SELECT NoteDetails FROM Notes')

                        for i in LAST_INFORMATION:
                            self.LastOldInfo = i[0]
                            break

                        self.db.execute(f'''
                        UPDATE Notes
                        SET NoteDetails="{NEW_DETAILS}"
                        WHERE NoteTitle="{TITLE_TO_UPDATE}"
                        ''')

                        if LAST_UPDATE_DETAIL != "Updated NoteDetail":
                            if LAST_UPDATE_DETAIL == " ORIGINAL": LAST_UPDATE_DETAIL = "."
                            self.RecentlyUpdateStatus = "Updated NoteDetails"
                            self.db.execute(f'''
                            UPDATE Notes
                            SET UPDATE_DETAILS="Updated NoteDetail{LAST_UPDATE_DETAIL}"
                            WHERE NoteTitle="{TITLE_TO_UPDATE}"
                            ''')
                            self.db.execute(f'''
                            UPDATE Notes
                            SET UPDATE_DATE="Updated On {self.TodaysDate}"
                            WHERE NoteTitle="{TITLE_TO_UPDATE}"
                            ''')
                        self.db.commit()

                        self.IsUpdated = True
                        self.UpdatedTitles.append(TITLE_TO_UPDATE)

                        UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus,self.LastOldInfo)

                        print(f'Successfully updated "{TITLE_TO_UPDATE}"')
                    else:
                        print(f'"{TITLE_TO_UPDATE}" doesn\'t exist')
                elif TO_UPD.lower() == 'notetitle':
                    titles = []
                    PrintTitles(self.db,titles)

                    TITLE_TO_UPDATE = input('NoteTitle to update: ')

                    if TITLE_TO_UPDATE.isdigit():
                        TITLE_TO_UPDATE = titles[int(TITLE_TO_UPDATE)-1]

                    if TITLE_TO_UPDATE in self.NoteTitles:
                        NEW_TITLE_NAME = input(f'New NoteTitle Name For "{TITLE_TO_UPDATE}": ')

                        if not NEW_TITLE_NAME == "":
                            LAST_UPDATE_DETAIL = self.db.execute('SELECT UPDATE_DETAILS FROM Notes')

                            LAST_INFORMATION = self.db.execute('SELECT NoteTitle FROM Notes')

                            for i in LAST_INFORMATION:
                                self.LastOldInfo = i[0]
                                break

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
                                self.db.execute(f'''
                                UPDATE Notes
                                SET UPDATE_DATE="Updated On {self.TodaysDate}"
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

                            UpdateJSON(self.NoteId,self.NoteTitles,self.IsUpdated,self.UpdatedTitles,self.RecentlyUpdateStatus,self.LastOldInfo)

                            print(f'Successfully updated NoteTitle of {TITLE_TO_UPDATE}')
                        else:
                            print(f'Cannot reassign NoteTitle to "". NoteTitle "{TITLE_TO_UPDATE}" remains the same')
                    else:
                        print(f'NoteTitle "{TITLE_TO_UPDATE}" doesn\'t exist')

    def _FinishDatabase_(self):
        ALL_INFO = self.db.execute(f'SELECT NoteId, NoteTitle, NoteDetails, UPDATE_DETAILS, DATE, UPDATE_DATE FROM Notes WHERE Port_Connection="{self.Port_Connection}"')

        print('------------------\nALL INFORMATION STORED\n')
        for i in ALL_INFO:
            print(i)
        else:
            if len(self.NoteTitles) < 1:
                print('No information stored(must\'ve been deleted!)')

        self.db.close()
        self.PortDb.FinishPortDb()
