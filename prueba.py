class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def start():
        info = f"""=COMMANDS===================================
        => {bcolors.OKBLUE}add           {bcolors.ENDC}<file-list>  <tag-list>  <=
        => {bcolors.OKBLUE}delete        {bcolors.ENDC}<tag-query>              <=
        => {bcolors.OKBLUE}list          {bcolors.ENDC}<tag-query>              <=
        => {bcolors.OKBLUE}add-tags      {bcolors.ENDC}<tag-query>  <tag-list>  <=
        => {bcolors.OKBLUE}delete-tags   {bcolors.ENDC}<tag-query>  <tag-list>  <=
        => {bcolors.OKBLUE}download      {bcolors.ENDC}<tag-query>              <=
        => {bcolors.OKBLUE}inspect-tag   {bcolors.ENDC}<tag>                    <=
        => {bcolors.OKBLUE}inspect-file  {bcolors.ENDC}<file-name>              <=
        => {bcolors.OKBLUE}info          {bcolors.ENDC}                         <=
        => {bcolors.OKBLUE}exit          {bcolors.ENDC}                         <=
        ============================================
        {bcolors.WARNING}⚠ Use (;) separator for lists of elements
        example {bcolors.ENDC} <tag-list> {bcolors.OKBLUE} as {bcolors.ENDC} red;blue
        {bcolors.WARNING}⚠ {bcolors.OKGREEN} green text {bcolors.WARNING}means succeded
        {bcolors.WARNING}⚠ {bcolors.FAIL} red text   {bcolors.WARNING}means failed
        {bcolors.ENDC}============================================"""
        print(info)

start()