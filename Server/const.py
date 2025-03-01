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


#Type of answers
ERROR_TYPE = 50
SUCCESS_TYPE = 51
MATCHING_FILES_TYPE = 52

# Multicast
MCAST_GRP = '224.0.0.1'
MCAST_PORT = 10000

DEFAULT_NODE_PORT = 8001
DEFAULT_SERVER_PORT = 8005