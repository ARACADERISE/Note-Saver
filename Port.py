"""
    This will setup different ports for the Notes to dwell in!
"""
import os, json
from time import sleep

PORT_DATA = {'PortIdList':[],'PortIdNameList':[]}
NOTES_IN_PORTS = {}

def UpdateJson(ListId,ListIdNames):
    PORT_DATA['PortIdList'] = ListId
    PORT_DATA['PortIdNameList'] = ListIdNames

    with open('port_info.json','w') as file:
        file.write(json.dumps(
            PORT_DATA,
            indent=2,
            sort_keys=False
        ))

def UpdateNotesInPorts(NOTES_IN_PORTS_):

    with open('n_i_p.json','w') as file:
        file.write(json.dumps(
            NOTES_IN_PORTS_,
            indent=2,
            sort_keys=False
        ))

class Port:

    def __init__(self, databaseConnection):

        self.db = databaseConnection
        self.RecentPortId = ''

        if not os.path.isfile('port_info.json'):
            self.PortIdList = []
            self.PortIdNameList = []
        if os.path.isfile('port_info.json'):
            PORT_DATA = json.loads(
                open('port_info.json','r').read()
            )
            self.PortIdList = PORT_DATA['PortIdList']
            self.PortIdNameList = PORT_DATA['PortIdNameList']

        if not os.path.isfile('info.json'): 
            self.data = {}
        if os.path.isfile('info.json'): 
            self.data = json.loads(
                open('info.json','r').read()
            )
        
        if not os.path.isfile('n_i_p.json'):
            self.NotesInPorts = {}
        if os.path.isfile('n_i_p.json'):
            self.NotesInPorts = json.loads(
                open('n_i_p.json','r').read()
            )
    
    def _CreatePortTable_(self):

        self.db.execute('''
        CREATE TABLE Ports (
            PortId TEXT NOT NULL,
            PortId_Name TEXT NOT NULL,
            Notes_In_Port INTEGER PRIMARY KEY NOT NULL
        );
        ''')
        self.db.commit()
    
    def _CHECK_NEW_PORT_DETAIL_(self, PORT_ID, PORT_ID_NAME):

        if PORT_ID in self.PortIdList:
            while PORT_ID in self.PortIdList:
                print(f'\nPort {PORT_ID} already exists\n')
                PORT_ID = input('Create A Port(random number that you will be able to remember) -> ')
        if PORT_ID_NAME in self.PortIdNameList:
            while PORT_ID_NAME in self.PortIdNameList:
                print(f'\nPort Name {PORT_ID_NAME} already exists\n')
                PORT_ID_NAME = input(f'Port {PORT_ID} Name -> ')
        
        self.RecentPortId = PORT_ID
        return PORT_ID, PORT_ID_NAME
    
    def _Port_Connection_(self):

        port = self.db.execute('SELECT PortId FROM Ports')

        for i in port:
            if i[0] == self.PortIdList[len(self.PortIdList)-1]:
                port = i[0]
                break
        return port
    
    def _INSERT_(self, info):

        self.db.execute(f'{info}')
        info = self.db.execute('SELECT PortId, PortId_Name FROM Ports')
        
        print('\nPORT CONNECTIONS:\n')
        for i in info:
            print(i)
            self.PortIdList.append(i[0])
            self.PortIdNameList.append(i[1])
            self.NotesInPorts.update({i[1]:1,i[1]+'_':[]})
        self.db.commit()

        UpdateNotesInPorts(self.NotesInPorts)
        UpdateJson(self.PortIdList,self.PortIdNameList)
    
    def _Update_Data_(self, DATA):
        if self.data == {}: self.data = DATA
    
    def PrintPorts(self):
        
        print('Existing Ports: \n')
        for i in self.PortIdList:
            print(i)
    
    def _Connect_To_Port_(self, PortId): 

        if PortId in self.PortIdList:
            ports = self.db.execute(f'SELECT PortId FROM Ports WHERE PortId="{PortId}"')

            for i in ports:
                os.system('clear')
                print(f'Connected To Port {i[0]}')
                break

            self.RecentPortId = PortId
        else:
            print(f'{PortId} port connection does not exist. Creating...')
            sleep(2)
            PORT_NAME = input(f'\nPort {PortId} name -> ')
            self.db.execute(f'INSERT INTO Ports(PortId,PortId_Name) VALUES("{PortId}","{PORT_NAME}")')
            self.db.commit()

            self.PortIdList.append(PortId)
            self.PortIdNameList.append(PORT_NAME)
            UpdateJson(self.PortIdList,self.PortIdNameList)

            self.RecentPortId = PortId

            self.NotesInPorts.update({PORT_NAME:1,PORT_NAME+'_':[]})
            UpdateNotesInPorts(self.NotesInPorts)

            return self.RecentPortId
    
    def GatherPortName(self):
        
        if self.RecentPortId != '':
            port_name = self.db.execute(f'SELECT PortId_Name FROM Ports WHERE PortId="{self.RecentPortId}"')

            for i in port_name:
                port_name = i[0]
                break

            return port_name
        else: return ''
    
    def UpdateAmmountOfNotes(self, port_name, ammount_of_notes, note_title):

        if port_name == self.PortIdNameList[len(self.PortIdNameList)-1]:
            self.NotesInPorts[port_name] = ammount_of_notes
            self.NotesInPorts[port_name+'_'].append(note_title)

            UpdateNotesInPorts(self.NotesInPorts)
    
    def RemoveNotes(self, port_name, notes_to_delete):

        if port_name == self.PortIdNameList[len(self.PortIdNameList)-1]:
            self.NotesInPorts[port_name+'_'].remove(notes_to_delete)

            UpdateNotesInPorts(self.NotesInPorts)

    
    def FinishPortDb(self, destroy=False):

        if destroy:
            self.db.execute(f'DELETE FROM Ports WHERE PortId="{self.RecentPortId}"')
            self.db.commit()
        
        self.db.close()
