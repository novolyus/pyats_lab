import logging

from genie.conf import Genie

from os import path
from os import mkdir

# To handel errors with connections to devices
from unicon.core import errors

log = logging.getLogger(__name__)
log.level = logging.INFO

testbed = './pyats_testbed.yaml'
testbed = Genie.init(testbed)


def create_non_existing_dir(dir_path):
    if not path.exists(dir_path):
        try:
            mkdir(dir_path)
        except PermissionError as e:
            log.error(f'Unable to create directory: {dir_path}. Insufficient privileges. Error: {e}')


def write_commands_to_file(abs_filename, command_output):
    try:
        with open(abs_filename, "w") as file_output:
            file_output.write(command_output)

    except IOError as e:
        log.error(f'Unable to write output to file: {abs_filename}. Due to error: {e}')

    except PermissionError as e:
        log.error(f'Unable to write output to file: {abs_filename}. Insufficient privileges. Error: {e}')


def collect_device_commands(commands_to_gather, dir_name):
    abs_dir_path = path.join(path.dirname(__file__), dir_name)

    create_non_existing_dir(abs_dir_path)

    for device_name, device in testbed.devices.items():

        device_os = device.os #  get operating system of a device from pyats_testbed.yaml
        device_path = path.join(abs_dir_path, device_name)
        create_non_existing_dir(device_path)

        try:
            device.connect(stdout=False)
        except errors.ConnectionError:
            log.error(f'Failed to establish connection to: {device.name}. Check connectivity and try again.')
            continue

        device.connectionmgr.log.setLevel(logging.ERROR)
        # device.log_user(enable=False)

        if commands_to_gather.get(device_os):
            for command in commands_to_gather[device_os]:
                filename = device_name + '_' + command
                abs_filename = path.join(device_path, filename)
                log.info(f'filename = {abs_filename}')

                command_output = device.execute(command)

                write_commands_to_file(abs_filename, command_output)
        else:
            log.error(f'No commands for operating system: {device_os} of device: {device_name} has been defined. This device has been skipped. Specify list of commands for {device_os} and try again.')


def main():
    commands_to_gather = {
        'asa': ['show inventory', 'show running-config', 'show route', 'show ospf neighbor', 'show license all'],
        'iosxe': ['show inventory', 'show running-config', 'show ip route vrf *', 'show ip ospf neighbor',
                       'show license feature'],
        'nxos': ['show inventory', 'show running-config', 'show ip route vrf all', 'show ip ospf neighbor vrf all',
                       'show license usage']}

    dir_name = 'gathered_commands'

    collect_device_commands(commands_to_gather, dir_name)


if __name__ == '__main__':
    main()


