# Autor : FanaticPythoner.
# Please read the "LICENSE" file before doing anything.
import os
from os.path import abspath
from requests import get

db_dir = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(db_dir, "DB.txt")

def _getAllFileTypes():
    return open(db_file,'r').readlines()

def _updateDBFromGithub():
    try:
        newDB = get('https://raw.githubusercontent.com/FanaticPythoner/pyMagicBytes/master/DB').text
        with open(db_dir,'w') as f:
            f.write(newDB)
    except Exception as e:
        return str(e.args)
    print('[LOG INFO] : Updated DB successfully.')
    return 'Success'

class FileObject:
    def __init__(self, filePath, updateDB=False):
        if updateDB:
            output = _updateDBFromGithub()
            if output != 'Success':
                raise Exception('An error occured when trying to update the DB from Github: ' + output)
        self.allFileTypes = _getAllFileTypes()
        self.fileStream = open(abspath(filePath),'rb')

    def getPossibleTypes(self, ReturnArray=True):
        typesFound = []
        for row in self.allFileTypes:
            matchedCurrentFileType = True
            size, offs, sign, ext, desc = row.split('|')
            size = int(size)
            offsArr = offs.split('..')
            for off in offsArr:
                self.fileStream.seek(int(off))
                redBytesString = self.fileStream.read(size).hex().upper()
                for byteHex, hexByteSign in zip(redBytesString, sign):
                    if hexByteSign != '?':
                        if hexByteSign != byteHex:
                            matchedCurrentFileType = False
                            break
            if matchedCurrentFileType:
                typesFound.append([('Bytes Offsets', offs.replace('..',' and ')), ('File Signature', sign), ('File Extension', ext), ('Description', desc.replace('\n',''))])
        if ReturnArray:
            return typesFound
        else:
            newTypeFound = [''] * len(typesFound)
            for item in typesFound:
                tempItemFromTuples = ''
                for tuples in item:
                    if tempItemFromTuples != '':
                        tempItemFromTuples = tempItemFromTuples + ' -> ' + tuples[0] + ' : ' + str(tuples[1])
                    else:
                        tempItemFromTuples = tuples[0] + ' : ' + str(tuples[1])
                newTypeFound.append(tempItemFromTuples)
            newTypeFound = [x for x in newTypeFound if x != '']
            return str(newTypeFound).replace("', '", ",\n").replace("['Bytes Offsets :","Bytes Offsets :").replace("']","")
