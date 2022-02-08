#!/usr/bin/env python
#######################Script to create OSP Lab Infra ################################
import os, sys
import subprocess
import pexpect, time
from pexpect import pxssh
class colors:
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg:
        red='\033[31m'
        green='\033[32m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
#print(colors.fg.blue,"\n Current Size of the partition is ",colors.fg.green,currentsize,colors.reset)
###############Generic Global Variables ##############################################
fileserver = "192.168.1.54"
anshosts = ["192.168.1.53"]
conthosts = ["192.168.1.53"]
comphosts = ["192.168.1.52", "192.168.1.54", "192.168.1.55"]
strhosts = ["192.168.1.52", "192.168.1.54", "192.168.1.55"]
contspec = {"cpu": "12", "mem": "16384", "hdd": 100}
compspec = {"cpu": "8", "mem": "8192", "hdd": 100}
ansspec = {"cpu": "2", "mem": "4096", "hdd": 100}
strspec = {"cpu": "4", "mem": "8192", "hdd": 100}
ipblock = "192.168.1."
ipstart = 211
ipgw = "192.168.1.1"
##########################################Create Ansible VM############################################
for i in anshosts:
    print (colors.fg.green,"\n Adding image for Ansible VM",colors.reset)
    print (colors.fg.green,"\n Ssh for Ansible hosts initiated",colors.reset)
    ansiblessh = "ssh -o StrictHostKeyChecking=no root@"+i
    chansssh = pexpect.spawn(ansiblessh)
    chansssh.expect('password:')
    chansssh.sendline('ubuntu')
    print (colors.fg.green,"\n Connected to ansible host {}".format(i),colors.reset)
    time.sleep(5)
    chansssh.expect(':~#')
    shutdown = ("virsh shutdown ans-{}".format(ipstart))
    chansssh.sendline(shutdown)
    time.sleep(10)
    chansssh.expect(':~#')
    delete = ("virsh undefine ans-{} --remove-all-storage".format(ipstart))
    chansssh.sendline(delete)
    chansssh.expect(':~#')
    print (colors.fg.pink,"\n Output of Undefine command: {}".format(chansssh.before.decode()),colors.reset)
    if chansssh.isalive():
        print (colors.fg.blue,"\n The child process is still alive, closing connection to {}".format(i),colors.reset)
        chansssh.close()
        time.sleep(2)
    #Incrementing the IP block within the for loop
    ipstart+=1
    print (colors.fg.red,"\n The ip for next iteration {}".format(str(ipstart)),colors.reset)


##############Create Controller VM's #################################################
##############Need to write logic, if virtual size  is greater than 100G do qemu-img resize beforeproceeding######

for i in conthosts:
    print (colors.fg.green,"\n Adding image for controller VM",colors.reset)
    print (colors.fg.green,"\n Ssh for control hosts initiated",colors.reset)
    controlssh = "ssh -o StrictHostKeyChecking=no root@"+i
    chcontssh = pexpect.spawn(controlssh)
    chcontssh.expect('password:')
    chcontssh.sendline('ubuntu')
    print (colors.fg.green,"\n Connected to control host {}".format(i),colors.reset)
    time.sleep(5)
    chcontssh.expect(':~#')
    shutdown = ("virsh shutdown cont-{}".format(ipstart))
    chcontssh.sendline(shutdown)
    time.sleep(10)
    chcontssh.expect(':~#')
    delete = ("virsh undefine cont-{} --remove-all-storage".format(ipstart))
    chcontssh.sendline(delete)
    chcontssh.expect(':~#')
    print (colors.fg.pink,"\n Output of Undefine command: {}".format(chansssh.before.decode()),colors.reset)
    if chcontssh.isalive():
        print (colors.fg.blue,"\n The child process is still alive, closing connection to {}".format(i),colors.reset)
        chcontssh.close()
        time.sleep(2)
    #Incrementing the IP block within the for loop
    ipstart+=1
    print (colors.fg.red,"\n The ip for next iteration {}".format(str(ipstart)),colors.reset)


############################Create Compute VM's################

for i in comphosts:
    print (colors.fg.green,"\n Adding image for compute VM",colors.reset)
    print (colors.fg.green,"\n Ssh for compute hosts initiated",colors.reset)
    computessh = "ssh -o StrictHostKeyChecking=no root@"+i
    chcompssh = pexpect.spawn(computessh)
    chcompssh.expect('password:')
    chcompssh.sendline('ubuntu')
    print (colors.fg.green,"\n Connected to compute host {}".format(i),colors.reset)
    time.sleep(5)
    chcompssh.expect(':~#')
    shutdown = ("virsh shutdown comp-{}".format(ipstart))
    chcompssh.sendline(shutdown)    
    time.sleep(10)
    chcompssh.expect(':~#')
    delete = ("virsh undefine comp-{} --remove-all-storage".format(ipstart))
    chcompssh.sendline(delete)
    chcompssh.expect(':~#')
    print (colors.fg.pink,"\n Output of Undefine command: {}".format(chansssh.before.decode()),colors.reset)
    if chcompssh.isalive():
        print (colors.fg.blue,"\n The child process is still alive, closing connection to {}".format(i),colors.reset)
    #Incrementing the IP block within the for loop
    ipstart+=1
    print (colors.fg.red,"\n The ip for next iteration {}".format(str(ipstart)),colors.reset)

###################################################Create Storage VM############################################################33

for i in strhosts:
    print (colors.fg.green,"\n Adding image for Storage VM",colors.reset)
    print (colors.fg.green,"\n Ssh for Storage hosts initiated",colors.reset)
    storagessh = "ssh -o StrictHostKeyChecking=no root@"+i
    chstrssh = pexpect.spawn(storagessh)
    chstrssh.expect('password:')
    chstrssh.sendline('ubuntu')
    print (colors.fg.green,"\n Connected to storage host {}".format(i),colors.reset)
    time.sleep(5)
    chstrssh.expect(':~#')
    shutdown = ("virsh shutdown str-{}".format(ipstart))
    chstrssh.sendline(shutdown)
    time.sleep(10)
    chstrssh.expect(':~#')
    vdelete = ("virsh undefine str-{} --remove-all-storage".format(ipstart))
    chstrssh.sendline(vdelete)
    chstrssh.expect(':~#')
    print (colors.fg.pink,"\n Output of virsh undefine command: {}".format(chstrssh.before.decode()),colors.reset)
    if chstrssh.isalive():
        print (colors.fg.blue,"\n The child process is still alive, closing connection to {}".format(i),colors.reset)
    #Incrementing the IP block within the for loop
    ipstart+=1
    print (colors.fg.red,"\n The ip for next iteration {}".format(str(ipstart)),colors.reset)
