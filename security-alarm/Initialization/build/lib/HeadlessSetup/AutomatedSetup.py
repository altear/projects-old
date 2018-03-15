'''
Script for setting up installations
'''

# TODO: Create/use paramiko expect (Action - [Response1, Response2])

import argparse
import yaml
import paramiko
import pkg_resources
import logging
import re
import sys

config_file_path = 'data/configuration_v00_01.ini'
buffer_pattern = '\s(\w*?)@(\w*?):(.*?)\$(?:\s*)$'

# initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.info("Welcome to the Wonder Emporium")
logger.info("Logger started")

class Reaction:
    pass

class Action:
    pass

def is_connected(client):
    '''
    check if paramiko ssh client is connected

    :param client:
    :return is_connected:
    '''
    try:
        transport = client.get_transport()
        transport.send_ignore()
        return True
    except EOFError:
        return False

def listen(channel, prompt=None, buffer_len=4096, decode='utf-8'):
    '''

    :param channel:
    :param prompt: early exit if provided command prompt is found. Do not use when executing bash files.
    :param buffer_len:
    :param decode:
    :return:
    '''
    buffer = ''
    try:
        buffer = channel.recv(buffer_len)
        while True:
            current_buffer = channel.recv(buffer_len)
            # if len of current buffer is 0, then channel has been closed
            if len(current_buffer) == 0:
                break
            buffer += current_buffer
            # early exit if we find the prompt
            if prompt and re.match(prompt, buffer.decode(decode), re.MULTILINE):
                break
    except: pass

    if decode:
        return buffer.decode('utf-8')
    return buffer

def ssh_get(channel, message=None, prompt=None, buffer_len=4096, decode='utf-8'):
    '''

    :param channel:
    :param message:
    :param expect:
    :param buffer_len:
    :param decode:
    :return:
    '''

    # send message
    if message:
        channel.send(message + '\n')

    # recv response
    buffer = ''
    try:
        buffer = channel.recv(buffer_len)
        while True:
            current_buffer = channel.recv(buffer_len)
            # if len of current buffer is 0 then channel has been closed
            if len(current_buffer) == 0: break
            buffer += current_buffer
            # early exit if empty command prompt is found
            if prompt and re.search(re.escape(prompt), buffer.decode(decode), re.DOTALL):
                break
    except: pass

    # cleanup
    bash_response_pattern = r'(.*?)'
    if message:
        bash_response_pattern = r"(?:\s*{}\s*)".format(re.escape(message)) + bash_response_pattern
    bash_response_pattern = '^' + bash_response_pattern + '$' # this is necessary so that lazy expressions capture all
    response = re.search(bash_response_pattern, buffer.decode(decode), re.DOTALL)
    return response.group(1) if response else buffer.decode(decode)

# connection is closed
def main():
    # load resources
    logger.info("Loading resources")
    config_file = pkg_resources.resource_filename(__name__, "data/configuration_v00_01.yml")

    # read config file
    logger.info("Reading config file")
    with open(config_file, 'rb') as f:
        config = yaml.load(f)

    # parse command line arguments
    logger.info("Reading commandline arguments")
    config_defaults = config['default']
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='host of target node')
    parser.add_argument('-p', '--port', help='ssh port', default=config_defaults['connection']['port'])
    parser.add_argument('-u', '--username', help='username', default=config_defaults['secure-login']['username'])
    parser.add_argument('-w', '--password', help='password', default=config_defaults['secure-login']['password'])
    args = parser.parse_args()

    # create client for ssh connection
    logger.info("Preparing ssh client")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    # connect ssh client and create channel
    connection_args = {
        'hostname' : args.host,
        'port' : args.port,
        'username' : args.username,
        'password' : args.password
    }
    logger.info("Connecting ssh client to {username}@{hostname}:{port}".format(**connection_args))
    try:
        client.connect(**connection_args)
    except paramiko.AuthenticationException:
        logger.warn("Authentication with credentials provided by arguments failed")
        try:
            logger.info("Attempting credentials stored in configuration file")
            logger.info("Connecting ssh client to {username}@{hostname}:{port}".format(**connection_args))
            connection_args['username'] = config_defaults['secure-login']['username']
            connection_args['password'] = config_defaults['secure-login']['password']
            client.connect(**connection_args)
        except Exception as e:
            logger.error("Authentication failed")
            sys.exit(1)
    except:
        logger.error("Connection failed")
        sys.exit(1)

    if is_connected(client):
        logger.info("SSH connection successful")
    else:
        logger.error("SSH connection failed")
        raise Exception("SSH connection failed")
    channel = client.invoke_shell()
    channel.settimeout(config_defaults['connection']['timeout'])

    # parse prompt
    logger.info("Parsing prompt")
    bash_prompt_pattern = "^((\w*?)@(\w*?):(.*?))?\$\s" # user, host, current_dir
    msg = listen(channel)
    match = re.search(bash_prompt_pattern, msg, flags=re.MULTILINE)
    if match:
        prompt = match.group(0)
    else:
        print("Problem", msg)
    # Setup some of the basic raspi security as specified here:
    # https://www.raspberrypi.org/documentation/configuration/security.md
    #
    # Steps:
    # 1. Create new user and set password
    # 2. Make sudo require password
    # 3. Set cron up to install daily steps
    #
    _secure_user_exists_flag = False
    _secure_password_exists_flag = False
    _deleted_default_user = False
    logger.info("Checking if secure user exists")
    def user_in_system(user):
        '''
        little function to check if user is in system
        '''
        # _response = ssh_get(channel, r"cut -d: -f1 /etc/passwd", prompt)
        # _find_user_pattern = r"\s({})\s".format(re.escape(user))
        # _match = re.search(_find_user_pattern, _response, re.DOTALL)
        _response = ssh_get(channel, r"id -u {}".format(user), prompt)
        _match = re.search(".*?no such user.*?", _response, re.M)
        return not _match

    if user_in_system(config_defaults['secure-login']['username']):
        logger.info("Secure user exists")
        _secure_user_exists_flag = True
    else:
        logger.info("Secure user does not exist")
        # quick sanity check that we could find current user
        if not user_in_system(connection_args['username']):
            logger.error("Sanity check finding current user failed")
            raise Exception("Problem finding system users")
        logger.info("Creating secure user")
        _cmd = r"sudo useradd -m {} -G sudo".format(config_defaults['secure-login']['username'])
        _response = ssh_get(channel, _cmd, prompt)
        logger.info(_response)

        if user_in_system(config_defaults['secure-login']['username']):
            logger.info("Created secure user " + str(user_in_system(config_defaults['secure-login']['username'])))
            _secure_user_exists_flag = True
        else:
            logger.error("Creating secure user failed")
            sys.exit(1)

    # create password
    def check_password(user, pw):
        _cmd = "su {}".format(user)
        _response = ssh_get(channel, _cmd)
        assert re.search("Password", _response, re.DOTALL), "No password prompt in message: " + _response
        _response = ssh_get(channel, pw)
        if re.search("Authentication failure", _response, re.M):
            return False
        elif re.search("^\s*\$\s*$", _response, re.DOTALL):
            return True

        raise Exception("Unexpected result from authentication attempt")

    # TODO: Rewrite section neatly
    if _secure_user_exists_flag:
        logger.info("Checking if secure password is set")
        _secure_password_exists_flag = check_password(
            config_defaults['secure-login']['username'],
            config_defaults['secure-login']['password']
        )

        if not _secure_password_exists_flag:
            logger.info("Secure pass word is not set")
            logger.info("Setting secure password")

            _cmd = "sudo passwd {}".format(config_defaults['secure-login']['username'])
            _response = ssh_get(channel, _cmd)
            # print(_cmd, "\t:\t" ,_response)

            _cmd = config_defaults['secure-login']['password']
            _response = ssh_get(channel, _cmd)
            # print(_cmd, "\t:\t", _response)

            _cmd = config_defaults['secure-login']['password']
            _response = ssh_get(channel, _cmd)
            # print(_cmd, "\t:\t", _response)

            success_msg = "passwd: password udpated successfully"
            _secure_password_exists_flag = check_password(
                config_defaults['secure-login']['username'],
                config_defaults['secure-login']['password']
            )

            if _secure_password_exists_flag:
                logger.info("Successfully set secure password")
            else:
                logger.error("Failed to set secure password")
        else:
            logger.info("Confirmed secure password is set")


    # cleanup
    try: client.close()
    except: pass
