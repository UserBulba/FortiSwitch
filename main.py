'''FortiSwitch API integrator'''
# main.py

from python_settings import settings  # Importing configuration file.

import backend.read_file as read_file  # Read file.
from fortiswitch import FortiSwitch  # FortiSwitch API.
from backend.threader import threader  # pylint: disable=import-error

PYTHONDONTWRITEBYTECODE = True # cspell: disable-line

def main(device):
    '''Main'''
    forti = FortiSwitch(ip=device["ip"], port=device["port"])
    output = {"ip": device["ip"]}

    validator = forti.check_socket()
    if validator:
        output["connectivity"] = True

        # Get FortiSwitch interface.
        request = forti.get_forti_interface

        # configure allowaccess" : "ping https snmp ssh"
        request = forti.put_forti_interface()
        output["interface"] = request["status"]

        # Get FortiSwitch community.
        request = forti.get_forti_community
        if request is None:
            return

        # Remove community getting id from dictionary.
        if "community_id" in request:
            request = forti.delete_forti_community(community_id=request["community_id"])
            output["remove"] = request["status"]

        # Create SNMP community.
        request = forti.create_forti_community()
        output["create"] = request["status"]

        # Fill SysInfo.
        request = forti.put_forti_sysinfo()
        output["sysinfo"] = request["status"]

        if output:
            print(output)

def create_dict(switch_list):
    """Create dict from list"""
    devices_mapped_list = []

    if switch_list:

        for switch in switch_list:
            devices_dict = {}

            ip, tcp_port = switch.split(":")
            devices_dict["ip"] = ip
            devices_dict["port"] = tcp_port

            devices_mapped_list.append(devices_dict)

        return devices_mapped_list

        # forti = FortiSwitch(ip=ip, port=tcp_port)

        # Create list of validated items
        # validated_list = []
        # validator = forti.check_socket()

        # Start config generator in threads.

try:
    Switch = read_file.ProcessFile
    switch_list = Switch.import_file(settings.PATH)
except Exception as error:
    raise Exception("Cannot read list file: {}.".format(error)) from None  # noqa: E501

device_dict = create_dict(switch_list)
threader(main, device_dict)

# print(main(ip_addres=ip, port=tcp_port))

# if __name__ == "__main__":
#     main()
