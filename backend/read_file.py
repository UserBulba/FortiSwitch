'''Process file'''
# read_file.py

class ProcessFile:
    '''Process file to import'''

    def __init__(self):
        pass

    @staticmethod
    def import_file(file_name):
        '''Import file'''

        try:
            with open(file_name) as file:
                content = file.read().splitlines()

            return content

        except FileNotFoundError:
            return None
