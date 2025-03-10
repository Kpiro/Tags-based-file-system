# Operation codes in ChordNode
FIND_PREDECESSOR = 1
FIND_SUCCESSOR = 2
GET_SUCCESSOR = 3
GET_PREDECESSOR = 4
NOTIFY = 5
REVERSE_NOTIFY = 6
NOT_ALONE_NOTIFY = 7
CHECK_NODE = 8
LOOKUP = 9

# Operations in Database
ADD_FILES_TO_TAG = 10
ADD_TAGS_TO_FILE = 11
GET_FILES_FROM_TAG=12
DELETE_FILE = 13
GET_TAGS_FROM_FILE=14
DELETE_FILES_FROM_TAG=15
DELETE_TAGS_FROM_FILE = 16
GET_ALL_FILES = 17
DOWNLOAD_FILE = 18
UPLOAD_FILE = 19
DOWNLOAD_FILE = 20
ADD_TAGS_TO_FILE_UPLOAD=21

END_FILE = 30
END_FILES = 31


PULL_MY_INFO = 33
PULL_PRED_INFO = 34
PULL_SUCC_INFO = 35
PUSH_MY_INFO = 36
PUSH_PRED_INFO = 37
PUSH_SUCC_INFO = 38

# PULL_REPLICATION=32
# PUSH_DATA = 33


#Type of answers
ERROR_TYPE = 50
SUCCESS_TYPE = 51
MATCHING_FILES_TYPE = 52

# Multicast
MCAST_GRP = '224.0.0.1'
MCAST_PORT = 10000

DEFAULT_DATA_PORT = 10000
DEFAULT_SERVER_PORT = 10001
DEFAULT_CLIENT_PORT = 10002
DEFAULT_NODE_PORT = 10003

PRED_INFO = 60
SUCC_INFO = 61
MY_INFO = 62

MAIN_DIR = "./Server/Data_base"

# Etiquetas para notificar a los vecinos
HANDLE_ADD_TAGS_TO_FILE_PRED = 100
HANDLE_ADD_TAGS_TO_FILE_SUCC = 101

HANDLE_ADD_FILES_TO_TAG_PRED = 102
HANDLE_ADD_FILES_TO_TAG_SUCC = 103

HANDLE_REMOVE_FILES_FROM_TAG_PRED = 104
HANDLE_REMOVE_FILES_FROM_TAG_SUCC = 105

HANDLE_REMOVE_TAGS_FROM_FILE_PRED = 106
HANDLE_REMOVE_TAGS_FROM_FILE_SUCC = 107

HANDLE_DELETE_TAG_PRED = 108
HANDLE_DELETE_TAG_SUCC = 109

HANDLE_DELETE_FILE_PRED = 110
HANDLE_DELETE_FILE_SUCC = 111

HANDLE_UPLOAD_PRED = 112
HANDLE_UPLOAD_SUCC = 113