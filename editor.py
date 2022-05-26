import io
import struct
from collections import OrderedDict

def unpack(file, upstream_data_set, loaded_data = 0):
    loaded_data = loaded_data + 1
    # print(f"Data {loaded_data} / {numOfData}")
    currentCursor = file.tell()  # off:0
    # print("Current Cursor: " + hex(currentCursor))
    nameOffset = int.from_bytes(file.read(4), byteorder='little')  # off:4
    # print("Name Offset: " + hex(nameOffset))
    file.seek(nameOffset, 0)
    variable_name = ""
    try:
        variable_name = file.read(200).split(b'\x00')[0].decode('UTF8')  # Use UTF8 because some strings are in Japanese
    except:
        raise Exception(f"There was an error reading Variable Name at {hex(currentCursor)}")
    file.seek(currentCursor + 4, 0)  # off:4
    type = int.from_bytes(file.read(4), byteorder='little')  # off:8
    dataType = type & 7
    if dataType == 0:  # List
        list_length = int.from_bytes(file.read(4), byteorder='little')
        name_hash = file.read(4).hex()
        data_location = file.tell()
        value = {}
        # print(f"List of size {list_length}")
        for i in range(0, list_length):
            loaded_data = unpack(file, value, loaded_data)
        value = OrderedDict(sorted(value.items()))
    elif dataType == 1:  # Float
        data_location = file.tell()
        file.seek(4, 1)
        value = data_location
    elif dataType == 2:  # Vector
        data_location = type >> 4
        file.seek(4, 1)
        # value = struct.unpack('ffff', file.read(16))
        value = data_location
    elif dataType == 3:  # String
        strCursorPointer = file.tell()
        string_length = int.from_bytes(file.read(4), byteorder='little') - 1
        data_location = type >> 4
        if data_location != 0:
            file.seek(data_location, 0)
            try:
                value = file.read(string_length).decode('UTF8')
                # if (variable_name == "playtime"):
                #     print("Player playtime: " + value)
            except:
                value = "ERROR EXTRACTING STRING"
        value = data_location
        file.seek(strCursorPointer + 4, 0)
    elif dataType == 4:  # Boolean
        data_location = file.tell()
        value = int.from_bytes(file.read(1), byteorder='little') > 0
        value = data_location
        file.seek(3, 1)
    else:
        value = "Unknown type " + hex(dataType) + " with value " + hex(type)
        print(value)

    if dataType != 0:
        name_hash = file.read(4).hex()

    if variable_name == None:
        variable_name = hex(data_location)
    upstream_data_set[variable_name] = value
    return loaded_data

def loadSavedata(file, savedata):
    data_set = OrderedDict()
    if len(savedata) > 0x40 and savedata[0:4] == b'ggdL':
        file.seek(0x0c, 0)
        numOfData = int.from_bytes(file.read(4), byteorder='little')
        loaded_data = 0
        while loaded_data < numOfData:
            loaded_data = unpack(file, data_set, loaded_data)
    else:
        raise Exception("Savedata incorrect")
    return data_set

def getOffset(savedata, location):
    # print(location)
    locallist = savedata
    for name in location:
        locallist = locallist[name]
    # print(hex(locallist))
    return locallist

def edit(raw_savedata, edits):
    file = io.BytesIO(raw_savedata)
    savedata = loadSavedata(file, raw_savedata)
    for edit in edits:
        offset = getOffset(savedata, edit[0])
        file.seek(offset, 0)
        if type(edit[1]) is float:
            # print("float")
            file.write(struct.pack('<f', edit[1]))
        elif type(edit[1]) is bool:
            # print("bool")
            file.write(struct.pack('<?', edit[1]))
        elif type(edit[1]) is list:  # Vector
            # print("list")
            for value in edit[1]:
                if type(value) is float:
                    # print("float")
                    file.write(struct.pack('<f', value))
                # else:
                # print("unknown" + str(type(value)))
        elif type(edit[1]) is str:
            # print("string")
            # assume same length
            file.write(edit[1].encode('utf-8'))

        #export
        return file.read()


