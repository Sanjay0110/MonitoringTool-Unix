from .models import sshData
from paramiko import *
import paramiko

def connect(command, user):
    values = []
    ssh_login = sshData.objects.get(user=user)
    username = ssh_login.hostname
    password = ssh_login.passwd
    ip = ssh_login.IPAddr
    ssh = paramiko.client.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username= username, password= password)
        cmd = command
        stdin,stdout,stderr = ssh.exec_command(cmd)
        values = stdout.readlines()
        ssh.close()
        return values
    except(BadHostKeyException, AuthenticationException, SSHException) as exc:
        return exc