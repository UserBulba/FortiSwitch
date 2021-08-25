'''FortiSwitch API integrator'''
# fortiswitch.py

import configparser  # Read config file.
import json  # JSON module.
import logging  # Logging errors.
import os  # Just os module?
import socket  # Check if port is open.
from contextlib import closing  # Ensure the port after check will be closed.
from pathlib import Path  # Create a directory if needed.

import requests  # Requests HTTP Library.
import urllib3  # Disable HTTPS warnings.
from python_settings import settings  # Importing configuration file.

from backend.credential_manager import restore_credential as credentials

os.environ["SETTINGS_MODULE"] = 'settings'
PYTHONDONTWRITEBYTECODE = True # cspell: disable-line
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

current_dir = (os.path.dirname(os.path.realpath(__file__)))
Path(os.path.join(current_dir, "logs")).mkdir(parents=True, exist_ok=True)
logging_path = os.path.join(current_dir, "logs", "FortiSwitch.log")
logging.basicConfig(filename=logging_path, level=logging.WARNING,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

class FortiSwitch: # pylint: disable=too-few-public-methods
    '''FortiSwitch class'''
    def __init__(self, ip, port):
        config = configparser.ConfigParser()
        config.read(os.path.join(current_dir, "conf", "conf.ini"))

        self.error = False
        self.ip_addres = ip
        self.apscookie = None
        self.ident = 1

        self.port = self.port_req  = port
        if self.port == '443':
            self.port_req = ""

        try:
            service = config.get("Credential_Manager", "service")
            if service != "None":
                credential_manager = credentials(service=service)
                self.forti_user = credential_manager["username"]
                self.forti_secret = credential_manager["password"]

        except configparser.NoOptionError as error:
            logger.info(error)
            self.error = True

        except TypeError as error:
            logger.info(error)
            self.error = True

        except Exception as error: # pylint: disable=broad-except
            logger.info(error)
            self.error = True

    def __get_forti_request(self):
        '''Get FortiSwitch api request'''

        self.client = requests.session()

        # Escape when error
        if self.error:
            logger.error("Error occurred for {error}", error = self.ip_addres)
            return None

        # Login request
        url = "https://{}/logincheck{}".format(self.ip_addres, self.port_req)
        payload = "username={}&secretkey={}".format(self.forti_user, self.forti_secret)
        try:
            response = self.client.post(url, data=payload, verify=False)
        # Add normal exceptions with logging.
        except Exception as error: # pylint: disable=broad-except
            logger.info(error)
        # Return error code form __get_forti_requests.
            return None

        self.apscookie = response.cookies

        for cookie in self.client.cookies:
            if cookie.name =='ccsrftoken':
                csrftoken=cookie.value[1:-1]

        self.client.headers.update({'X-CSRFTOKEN':csrftoken})

    @property
    def get_forti_interface(self):
        '''Get FortiSwitch SNMP community'''

        # Escape when error.
        if self.error:
            return None

        # Get auth token.
        try:
            if not self.client.headers:
                self.__get_forti_request()

        except AttributeError as error:
            self.__get_forti_request()

        except Exception as error:
            raise Exception("Unknown error {}.".format(error)) from None  # noqa: E501

        url = "https://{}/api/v2/cmdb/system/interface/{}".format(self.ip_addres, settings.INTERFACE)
        try:
            response = self.client.get(url, cookies = self.apscookie)
        except Exception as error: # pylint: disable=broad-except
            logger.info(error)

        results = response.json()
        loop = results["results"]
        current = loop[0]

        return current

    def put_forti_interface(self):
        '''Update FortiSwitch allowaccess'''

        # Escape when error
        if self.error:
            return None

        # Get auth token.
        try:
            if not self.client.headers:
                self.__get_forti_request()

        except AttributeError as error:
            self.__get_forti_request()

        except Exception as error:
            raise Exception("Unknown error {}.".format(error)) from None  # noqa: E501

        url = "https://{}/api/v2/cmdb/system/interface/{}".format(self.ip_addres, settings.INTERFACE)

        payload = {
            "allowaccess" : "ping https snmp ssh",
        }

        try:
            response = self.client.put(url, data=json.dumps(payload), cookies = self.apscookie)
            return response.json()

        except Exception as error: # pylint: disable=broad-except
            logger.info(error)
            return None


    @property
    def get_forti_community(self):
        '''Get FortiSwitch SNMP community'''

        # Escape when error
        if self.error:
            return None

        # Get auth token.
        try:
            if not self.client.headers:
                self.__get_forti_request()

        except AttributeError as error:
            self.__get_forti_request()

        except Exception as error:
            raise Exception("Unknown error {}.".format(error)) from None  # noqa: E501


        url = "https://{}/api/v2/cmdb/system.snmp/community".format(self.ip_addres)
        try:
            response = self.client.get(url, cookies = self.apscookie)
        except Exception as error: # pylint: disable=broad-except
            logger.info(error)

        results = response.json()
        loop = results["results"]
        dictionary = {}

        for item in range(len(loop)):
            try:
                dictionary["community_name"] = results["results"][item]["name"]

            except Exception as error: # pylint: disable=broad-except
                logger.info(error)

            try:
                dictionary["community_id"] = results["results"][item]["id"]

            except Exception as error: # pylint: disable=broad-except
                logger.info(error)

            try:
                dictionary["hosts"] = results["results"][item]["hosts"]

            except Exception as error: # pylint: disable=broad-except
                logger.info(error)

        return dictionary

    def delete_forti_community(self, community_id):
        '''Delete FortiSwitch SNMP community'''

        # Escape when error
        if self.error:
            return None

        # Get auth token.
        try:
            if not self.client.headers:
                self.__get_forti_request()

        except AttributeError as error:
            self.__get_forti_request()

        except Exception as error:
            raise Exception("Unknown error {}.".format(error)) from None  # noqa: E501


        url = "https://{}/api/v2/cmdb/system.snmp/community/{}".format(self.ip_addres, community_id)
        try:
            response = self.client.delete(url, cookies = self.apscookie)
            return response.json()

        except Exception as error: # pylint: disable=broad-except
            logger.info(error)
            # Return error code form __get_forti_requests.
            return None

    def create_forti_community(self):
        '''Create FortiSwitch SNMP community'''

        # Escape when error
        if self.error:
            return None

        # Get auth token.
        try:
            if not self.client.headers:
                self.__get_forti_request()

        except AttributeError as error:
            self.__get_forti_request()

        except Exception as error:
            raise Exception("Unknown error {}.".format(error)) from None  # noqa: E501


        url = "https://{}/api/v2/cmdb/system.snmp/community".format(self.ip_addres)

        payload = {
            "status" : "enable",
            "name" : settings.COMMUNITY,
            "hosts" : [],
            "id" : self.ident
        }

        try:
            for counter, host in enumerate(settings.HOSTS, start=1):
                payload["hosts"].append({
                    "ip":host,
                    "id":counter,
                    "interface":settings.INTERFACE
                })

        except Exception as error: # pylint: disable=broad-except
            logger.info(error)

        try:
            response = self.client.post(url, data=json.dumps(payload), cookies = self.apscookie)
            return response.json()

        except Exception as error: # pylint: disable=broad-except
            logger.info(error)
            return None


    @property
    def get_forti_sysinfo(self):
        '''Get FortiSwitch SNMP sysinfo'''

        # Escape when error
        if self.error:
            return None

        # Get auth token.
        try:
            if not self.client.headers:
                self.__get_forti_request()

        except AttributeError as error:
            self.__get_forti_request()

        except Exception as error:
            raise Exception("Unknown error {}.".format(error)) from None  # noqa: E501


        url = "https://{}/api/v2/cmdb/system.snmp/sysinfo".format(self.ip_addres)
        try:
            response = self.client.get(url, cookies = self.apscookie)

        except Exception as error: # pylint: disable=broad-except
            logger.info(error)

        results = response.json()
        dictionary = {}
        try:
            dictionary["status"] = results["results"]["status"]
            dictionary["location"] = results["results"]["location"]
            dictionary["description"] = results["results"]["description"]
            dictionary["contact-info"] = results["results"]["contact-info"]

        except Exception as error: # pylint: disable=broad-except
            logger.info(error)

        return dictionary

    def put_forti_sysinfo(self):
        '''Update FortiSwitch SNMP sysinfo'''

        # Escape when error
        if self.error:
            return None

        # Get auth token.
        try:
            if not self.client.headers:
                self.__get_forti_request()

        except AttributeError as error:
            self.__get_forti_request()

        except Exception as error:
            raise Exception("Unknown error {}.".format(error)) from None  # noqa: E501


        url = "https://{}/api/v2/cmdb//system.snmp/sysinfo".format(self.ip_addres)

        payload = {
            "status" : "enable",
            "location" : settings.LOCATION,
            "description" : settings.DESCRIPTION,
            "contact-info" : settings.CONTACT
        }

        try:
            response = self.client.put(url, data=json.dumps(payload), cookies = self.apscookie)
            return response.json()

        except Exception as error: # pylint: disable=broad-except
            logger.info(error)
            return None

    def check_socket(self):
        '''Check if port is open'''
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(5)
            if sock.connect_ex((self.ip_addres, int(self.port))) == 0:
                return True

            return False

def main():
    '''main'''
    print("There is nothing to do here ;)")

    if __name__ == "__main__":
        main()
