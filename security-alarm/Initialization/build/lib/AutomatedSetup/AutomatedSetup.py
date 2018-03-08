'''
Script for setting up installations
'''

import argparse
import configparser
import paramiko
import pkg_resources
import logging

config_file_path = 'data/configuration_v00_01.ini'

def main():
    # initialize logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG) # logs below this level will be ignored
    logger.error("Hello World")
    # load resources
    source = pkg_resources.resource_filename(__name__, "data/configuration_v00_01.ini")

    # load config file
    config = configparser.ConfigParser()
    config.read(source)

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='host of target node')
    parser.add_argument('-p', '--port', help='ssh port', default=config['script.default.parameters']['port'])
    parser.add_argument('-u', '--username', help='username', default=config['script.default.parameters']['username'])
    parser.add_argument('-w', '--password', help='password', default=config['script.default.parameters']['password'])
    args = parser.parse_args()

    # establish ssh connection to host
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    try:
        client.connect(hostname=args.host, port=args.port, username=args.username, password=args.password)
    except paramiko.AuthenticationException as e:
        logger.error("Authentication Exception - Likely credentials have been updated")
        raise e

    # pull host information (this may be used for handling cases later)



    # first thing is first, run updates
    # interaction.send('sudo apt-get update')
    # interaction.expect('successful')

    # get
    # interaction.send('sudo apt-get python3-')
    print('Hello World')
    stdin, stdout, stderr = client.exec_command('ls -l /')
    print(stdout.read().decode('utf-8'))

    # cleanup
    try: interaction.close()
    except: pass

    try: client.close()
    except: pass
