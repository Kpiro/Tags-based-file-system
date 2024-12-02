from colorama import Fore, Style

class Response():
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return f'✅ [RESPONSE] {Fore.LIGHTBLUE_EX} {self.text}\n'

class MatchingFiles():
    def __init__(self, files):
        self.files = files

    def __str__(self):
        ans = ""
        for i,file in enumerate(self.files):
            ans += f'{Fore.WHITE}{i+1}- {file}\n'

        return f'🗂️ {Fore.LIGHTCYAN_EX}[FILES] \n{ans}'

# class FilesWithTags():
#     def __init__(self, files):
#         self.files = files

class Error(Exception):
    def __init__(self, text):
        super().__init__(text)

    @property
    def error_type(self):
        return 'Error'

    @property
    def text(self):
        return self.args[0]

    def __str__(self):
        return f'❌ [ERROR] {Fore.RED} {self.error_type}: {self.text}'

    def __repr__(self):
        return str(self)
    
class InvalidCommandError(Error):

    def __init__(self, text):
        super().__init__(text)

    @property
    def error_type(self):
        return 'INVALID COMMAND'
    
class InvalidPathError(Error):
    def __init__(self, text):
        super().__init__(text)

    @property
    def error_type(self):
        return 'INVALID PATH'
    
class NoFilesMatch(Error):
    def __init__(self, text):
        super().__init__(text)

    @property
    def error_type(self):
        return 'NO FILES MATCH'

    
class InvalidParams(Error):
    def __init__(self, text):
        super().__init__(text)

    @property
    def error_type(self):
        return 'INVALID PARAM'
    
class InvalidQuery(Error):
    def __init__(self, text):
        super().__init__(text)

    @property
    def error_type(self):
        return 'INVALID QUERY'

class FailCopy(Error):
    def __init__(self, text):
        super().__init__(text)

    @property
    def error_type(self):
        return 'FAIL COPY'
    

class StorageFiles():
    def __init__(self, files):
        self.files = files

    def __str__(self):
        ans = ""
        for i, (file, tags) in enumerate(self.files.items()):
            ans += f'{Fore.WHITE}{i+1}- {file}: '
            for tag in list(tags):
                ans += f'{tag} '
            ans+='\n'
        return f'🗂️ {Fore.LIGHTCYAN_EX}[FILES] \n{ans}'
