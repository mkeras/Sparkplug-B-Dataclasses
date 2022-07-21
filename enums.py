from enum import Enum


class MessageTypes(Enum):
    """
    Sparkplug B Message Types
    Note: state is only subscribed to by sparkplug b clients
    """
    NBIRTH = 'NBIRTH'
    NDEATH = 'NDEATH'
    DBIRTH = 'DBIRTH'
    DDEATH = 'DDEATH'
    NDATA = 'NDATA'
    DDATA = 'DDATA'
    NCMD = 'NCMD'
    DCMD = 'DCMD'
    STATE = 'STATE'


class DataTypes(Enum):
    """ Indexes of Data Types """

    """ Unknown placeholder for future expansion. """
    Unknown = 0

    """ Basic Types """
    Int8 = 1
    Int16 = 2
    Int32 = 3
    Int64 = 4
    UInt8 = 5
    UInt16 = 6
    UInt32 = 7
    UInt64 = 8
    Float = 9
    Double = 10
    Boolean = 11
    String = 12
    DateTime = 13
    Text = 14

    """ Additional Metric Types """
    UUID = 15
    DataSet = 16
    Bytes = 17
    File = 18
    Template = 19

    """ Additional PropertyValue Types """
    PropertySet = 20
    PropertySetList = 21

    """ json data types to be used for modifying edge node settings/configuration """
    JSONBytes = 22
    JSONString = 23


class SpecialValues(Enum):
    """
    This is a special class to represent None, to signal that it should be ignored during payload serialization.
    Python constant 'None' is not used in order that 'None' values may still be sent in a payload
    """
    DO_NOT_SERIALIZE = None
