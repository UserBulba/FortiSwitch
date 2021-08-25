'''Get credential'''
import keyring


def restore_credential(service):
    '''Get credential from Credential Manager'''
    try:
        credential = keyring.get_credential(service, 'None') # Retrieve credentials

        result = {
            "username" : credential.username,
            "password" : credential.password
        }

        return result

    except AttributeError:
        return None

    except Exception:  # pylint: disable=broad-except
        return None
