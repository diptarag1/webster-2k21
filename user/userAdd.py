import os
import subprocess
import sys
import getpass


# add user function
def add_user(username,password):
    # Ask for the input
    # Asking for users password
    try:
        # executing useradd command using subprocess module
        command = ['sudo', 'htpasswd', '-i', "/var/www/html/git/htpasswd", username]
        execute = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        execute.communicate(input=password)
    except:
        print(f"Failed to add user.")
        sys.exit(1)