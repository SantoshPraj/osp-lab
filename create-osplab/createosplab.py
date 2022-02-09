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
tiout = 120 #time to wait after instance creation
imgpath = "/home/himanshu/Ubuntu20-Cli-Img.qcow2"
##########################################Create Ansible VM############################################
for i in anshosts:
    print (colors.fg.green,"\n Adding image for Ansible VM",colors.reset)
    print (colors.fg.green,"\n Ssh for Ansible hosts initiated",colors.reset)
    ansiblessh = "ssh -o StrictHostKeyChecking=no root@"+i
    chansssh = pexpect.spawn(ansiblessh)
    chansssh.expect('')
    chansssh.sendline('ubuntu')
    chansssh.expect('password:')
    chansssh.sendline('ubuntu')
    print (colors.fg.green,"\n Connected to ansible host {}".format(i),colors.reset)
    chansssh.expect(':~#')
    scpcmd = 'sshpass -p "ubuntu" scp -o StrictHostKeyChecking=no root@'+fileserver+':'+imgpath+' /root/'
    chansssh.sendline(scpcmd)
    time.sleep(30)
    chansssh.expect(':~#')
    print (colors.fg.green,"\n Output of SCP: {}".format(chansssh.before.decode()),colors.reset)
    imgcmd = ("cp /root/Ubuntu20-Cli-Img.qcow2 /var/lib/libvirt/images/ans-{}.qcow2".format(str(ipstart)))
    chansssh.sendline(imgcmd)
    time.sleep(15)
    chansssh.expect(':~#')
    print (colors.fg.green,"\n Output of CP: {}".format(chansssh.before.decode()),colors.reset)
    if ansspec["hdd"] > 100:
        ddexp = (ansspec["hdd"] - 100)
        diskresize = ("qemu-img resize /var/lib/libvirt/images/ans-"+str(ipstart)+".qcow2 +{}G".format(hddexp))
        print(colors.fg.pink,"\n resized disk: \n{}".format(diskresize),colors.reset)
        chansssh.sendline(diskresize)
        print (colors.fg.pink,"\n Output of diskresize: {}".format(chansssh.before.decode())),colors.reset
    vmcreate_cmd = "virt-install -n ans-"+str(ipstart)+" -r "+ansspec["mem"]+" --vcpus="+ansspec["cpu"]+" --os-type=Linux --os-variant=ubuntu20.04 --graphics=none --console pty,target_type=serial --network=bridge:br-mgmt,model=virtio --import --disk /var/lib/libvirt/images/ans-"+str(ipstart)+".qcow2 --noautoconsole -v"
    chansssh.sendline(vmcreate_cmd)
    print (colors.fg.blue,"\n Output of Vm create command: {}".format(vmcreate_cmd),colors.reset)
    time.sleep(tiout)
    chansssh.expect(':~#')
    print (colors.fg.blue,"\n Output of VIRT-INSTALL: {}".format(chansssh.before.decode()),colors.reset)
    vconsole = ("virsh console ans-{}".format(ipstart))
    chansssh.sendline(vconsole)
    chansssh.sendline("")
    print (colors.fg.green,"\n Instance console is ready for Login",colors.reset)
    chansssh.expect('login:')
    chansssh.sendline('root')
    chansssh.expect('Password:')
    chansssh.sendline('ubuntu')
    print (colors.fg.green,"\n Instance virsh console connected, ready for network config \n {}".format(chansssh.before.decode()),colors.reset)
    chansssh.expect(':~#')
    ipsetin = ipblock+str(ipstart)
    netpconfig = """cat << EOF > /etc/netplan/01-netcfg.yaml
# This is the network config written by 'subiquity'
network:
  version: 2
  ethernets:
    enp1s0:
      dhcp4: false
      dhcp6: false

  vlans:
    enp1s0.10:
      id: 10
      link: enp1s0
    enp1s0.20:
      id: 20
      link: enp1s0
    enp1s0.30:
      id: 30
      link: enp1s0
    enp1s0.40:
      id: 40
      link: enp1s0

  bridges:
    br-mgmt:
      addresses: [10.10.10.{}/24]
      interfaces: [enp1s0.10]
      parameters:
        stp: false
        forward-delay: 4
    br-storage:
      addresses: [10.10.20.{}/24]
      interfaces: [enp1s0.20]
      parameters:
        stp: false
        forward-delay: 4
    br-vxlan:
      addresses: [10.10.30.{}/24]
      interfaces: [enp1s0.30]
      parameters:
        stp: false
        forward-delay: 4
    br-dhcp:
      addresses: [10.10.40.{}/24]
      interfaces: [enp1s0.40]
      parameters:
        stp: false
        forward-delay: 4
    br-vlan:
      addresses: [{}/24]
      gateway4: {}
      interfaces: [enp1s0]
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
      parameters:
        stp: false
        forward-delay: 4    
EOF""".format(str(ipstart), str(ipstart), str(ipstart), str(ipstart), ipsetin, ipgw)
    chansssh.sendline(netpconfig)
    chansssh.expect(':~#')
    chansssh.sendline("netplan apply")
    time.sleep(5)
    chansssh.expect(':~#')
    chansssh.sendline("exit")
    print (colors.fg.blue,"\n Output for exit command: {}".format(chansssh.before.decode()),colors.reset)
    if chansssh.isalive():
        print (colors.fg.pink,"\n The child process is still alive, closing connection to {}".format(i),colors.reset)
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
    chconssh = pexpect.spawn(controlssh)
    chconssh.expect('password:')
    chconssh.sendline('ubuntu')
    print (colors.fg.green,"\n Connected to control host {}".format(i),colors.reset)
    chconssh.expect(':~#')
    scpcmd = 'sshpass -p "ubuntu" scp -o StrictHostKeyChecking=no root@'+fileserver+':'+imgpath+' /root/'
    chconssh.sendline(scpcmd)
    time.sleep(30)
    chconssh.expect(':~#')
    print (colors.fg.green,"\n Output of SCP: {}".format(chconssh.before.decode()),colors.reset)
    imgcmd = ("cp /root/Ubuntu20-Cli-Img.qcow2 /var/lib/libvirt/images/cont-{}.qcow2".format(str(ipstart)))
    chconssh.sendline(imgcmd)
    time.sleep(15)
    chconssh.expect(':~#')
    print (colors.fg.green,"\n Output of CP: {}".format(chconssh.before.decode()),colors.reset)
    if contspec["hdd"] > 100:
        ddexp = (contspec["hdd"] - 100)
        diskresize = ("qemu-img resize /var/lib/libvirt/images/cont-"+str(ipstart)+".qcow2 +{}G".format(hddexp))
        print(colors.fg.pink,"\n resized disk: \n{}".format(diskresize),colors.reset)
        chconssh.sendline(diskresize)
        print (colors.fg.pink,"\n Output of diskresize: {}".format(chconssh.before.decode()),colors.reset)
    vmcreate_cmd = "virt-install -n cont-"+str(ipstart)+" -r "+contspec["mem"]+" --vcpus="+contspec["cpu"]+" --os-type=Linux --os-variant=ubuntu20.04 --graphics=none --console pty,target_type=serial --network=bridge:br-mgmt,model=virtio --import --disk /var/lib/libvirt/images/cont-"+str(ipstart)+".qcow2 --noautoconsole -v"
    chconssh.sendline(vmcreate_cmd)
    print (colors.fg.blue,"\n Output of Vm create command: {}".format(vmcreate_cmd),colors.reset)
    time.sleep(tiout)
    chconssh.expect(':~#')
    print (colors.fg.blue,"\n Output of VIRT-INSTALL: {}".format(chconssh.before.decode()),colors.reset)
    vconsole = ("virsh console cont-{}".format(ipstart))
    chconssh.sendline(vconsole)
    chconssh.sendline("")
    print (colors.fg.green,"\n Instance console is ready for Login"),colors.reset
    chconssh.expect('login:')
    chconssh.sendline('root')
    chconssh.expect('Password:')
    chconssh.sendline('ubuntu')
    print (colors.fg.yellow,"\n Instance virsh console connected, ready for network config \n {}".format(chconssh.before.decode()),colors.reset)
    chconssh.expect(':~#')
    ipsetin = ipblock+str(ipstart)  
    netpconfig = """cat << EOF > /etc/netplan/01-netcfg.yaml
# This is the network config written by 'subiquity'
network:
  version: 2
  ethernets:
    enp1s0:
      dhcp4: false
      dhcp6: false

  vlans:
    enp1s0.10:
      id: 10
      link: enp1s0
    enp1s0.20:
      id: 20
      link: enp1s0
    enp1s0.30:
      id: 30
      link: enp1s0
    enp1s0.40:
      id: 40
      link: enp1s0

  bridges:
    br-mgmt:
      addresses: [10.10.10.{}/24]
      interfaces: [enp1s0.10]
      parameters:
        stp: false
        forward-delay: 4
    br-storage:
      addresses: [10.10.20.{}/24]
      interfaces: [enp1s0.20]
      parameters:
        stp: false
        forward-delay: 4
    br-vxlan:
      addresses: [10.10.30.{}/24]
      interfaces: [enp1s0.30]
      parameters:
        stp: false
        forward-delay: 4
    br-dhcp:
      addresses: [10.10.40.{}/24]
      interfaces: [enp1s0.40]
      parameters:
        stp: false
        forward-delay: 4
    br-vlan:
      addresses: [{}/24]
      gateway4: {}
      interfaces: [enp1s0]
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
      parameters:
        stp: false
        forward-delay: 4    
EOF""".format(str(ipstart), str(ipstart), str(ipstart), str(ipstart), ipsetin, ipgw)
    chconssh.sendline(netpconfig)
    chconssh.expect(':~#')
    chconssh.sendline("netplan apply")
    time.sleep(5)
    chconssh.expect(':~#')
    chconssh.sendline("exit")
    print (colors.fg.blue,"\n Output for logout command: {}".format(chconssh.before.decode()),colors.reset)      
    if chconssh.isalive():
        print (colors.fg.pink,"\n The child process is still alive, closing connection to {}".format(i),colors.reset)
        chconssh.close()
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
    chcompssh.expect(':~#')
    scpcmd = 'sshpass -p "ubuntu" scp -o StrictHostKeyChecking=no root@'+fileserver+':'+imgpath+' /root/'
    chcompssh.sendline(scpcmd)
    time.sleep(30)
    chcompssh.expect(':~#')
    print (colors.fg.green,"\n Output of SCP: {}".format(chcompssh.before.decode()),colors.reset)
    imgcmd = ("cp /root/Ubuntu20-Cli-Img.qcow2 /var/lib/libvirt/images/comp-{}.qcow2".format(str(ipstart)))
    chcompssh.sendline(imgcmd)
    time.sleep(15)
    chcompssh.expect(':~#')
    print (colors.fg.green,"\n Output of CP: {}".format(chcompssh.before.decode()),colors.reset)
    if compspec["hdd"] > 100:
        ddexp = (compspec["hdd"] - 100)
        diskresize = ("qemu-img resize /var/lib/libvirt/images/comp-"+str(ipstart)+".qcow2 +{}G".format(hddexp))
        print(colors.fg.pink,"\n resized disk: \n{}".format(diskresize),colors.reset)
        chcompssh.sendline(diskresize)
        print (colors.fg.pink,"\n Output of diskresize: {}".format(chcompssh.before.decode()),colors.reset)
    vmcreate_cmd = "virt-install -n comp-"+str(ipstart)+" -r "+compspec["mem"]+" --vcpus="+compspec["cpu"]+" --os-type=Linux --os-variant=ubuntu20.04 --graphics=none --console pty,target_type=serial --network=bridge:br-mgmt,model=virtio --import --disk /var/lib/libvirt/images/comp-"+str(ipstart)+".qcow2 --noautoconsole -v"
    chcompssh.sendline(vmcreate_cmd)
    print (colors.fg.blue,"\n Output of Vm create command: {}".format(vmcreate_cmd),colors.reset)
    time.sleep(tiout)
    chcompssh.expect(':~#')
    print (colors.fg.blue,"\n Output of VIRT-INSTALL: {}".format(chcompssh.before.decode()),colors.reset)
    vconsole = ("virsh console comp-{}".format(ipstart))
    chcompssh.sendline(vconsole)
    chcompssh.sendline("")
    print (colors.fg.blue,"\n Instance console is ready for Login",colors.reset)
    chcompssh.expect('login:')
    chcompssh.sendline('root')
    chcompssh.expect('Password:')
    chcompssh.sendline('ubuntu')
    print (colors.fg.yellow,"\n Instance virsh console connected, ready for network config \n {}".format(chcompssh.before.decode()),colors.reset)
    chcompssh.expect(':~#')
    ipsetin = ipblock+str(ipstart)
    netpconfig = """cat << EOF > /etc/netplan/01-netcfg.yaml
# This is the network config written by 'subiquity'
network:
  version: 2
  ethernets:
    enp1s0:
      dhcp4: false
      dhcp6: false

  vlans:
    enp1s0.10:
      id: 10
      link: enp1s0
    enp1s0.20:
      id: 20
      link: enp1s0
    enp1s0.30:
      id: 30
      link: enp1s0
    enp1s0.40:
      id: 40
      link: enp1s0

  bridges:
    br-mgmt:
      addresses: [10.10.10.{}/24]
      interfaces: [enp1s0.10]
      parameters:
        stp: false
        forward-delay: 4
    br-storage:
      addresses: [10.10.20.{}/24]  
      parameters:
        stp: false
        forward-delay: 4
    br-vxlan:
      addresses: [10.10.30.{}/24]
      interfaces: [enp1s0.30]
      parameters:
        stp: false
        forward-delay: 4
    br-dhcp:
      addresses: [10.10.40.{}/24]
      interfaces: [enp1s0.40]
      parameters:
        stp: false
        forward-delay: 4
    br-vlan:
      addresses: [{}/24]
      gateway4: {}
      interfaces: [enp1s0]
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
      parameters:
        stp: false
        forward-delay: 4    
EOF""".format(str(ipstart), str(ipstart), str(ipstart), str(ipstart), ipsetin, ipgw)
    chcompssh.sendline(netpconfig)
    chcompssh.expect(':~#')
    chcompssh.sendline("netplan apply")
    time.sleep(5)
    chcompssh.expect(':~#')
    chcompssh.sendline("exit")
    print (colors.fg.blue,"\n Output of exit command: {}".format(chcompssh.before.decode()),colors.reset)         
    if chcompssh.isalive():
        print (colors.fg.pink,"\n The child process is still alive, closing connection to {}".format(i),colors.reset)
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
    chstrssh.expect(':~#')
    scpcmd = 'sshpass -p "ubuntu" scp -o StrictHostKeyChecking=no root@'+fileserver+':'+imgpath+' /root/'
    chstrssh.sendline(scpcmd)
    time.sleep(30)
    chstrssh.expect(':~#')
    print (colors.fg.green,"\n Output of SCP: {}".format(chstrssh.before.decode()),colors.reset)
    imgcmd = ("cp /root/Ubuntu20-Cli-Img.qcow2 /var/lib/libvirt/images/str-{}.qcow2".format(str(ipstart)))
    chstrssh.sendline(imgcmd)
    time.sleep(15)
    chstrssh.expect(':~#')
    if strspec["hdd"] > 100:
        hddexp = (strspec["hdd"] - 100)
        diskresize = "qemu-img resize /var/lib/libvirt/images/str-"+str(ipstart)+".qcow2 +"+hddexp+"G"
        print(colors.fg.pink,"\n resized disk: \n{}".format(diskresize),colors.reset)
         print (colors.fg.pink,"\n Output of diskresize: {}".format(chstrssh.before.decode()),colors.reset)
    vmcreate_cmd = "virt-install -n str-"+str(ipstart)+" -r "+strspec["mem"]+" --vcpus="+strspec["cpu"]+" --os-type=Linux --os-variant=ubuntu20.04 --graphics=none --console pty,target_type=serial --network=bridge:br-mgmt,model=virtio --import --disk /var/lib/libvirt/images/str-"+str(ipstart)+".qcow2 --noautoconsole -v"
    chstrssh.sendline(vmcreate_cmd)
    print (colors.fg.blue,"\n Output of Vm create command: {}".format(vmcreate_cmd),colors.reset)
    time.sleep(tiout)
    chstrssh.expect(':~#')
    print (colors.fg.blue,"\n Output of VIRT-INSTALL: {}".format(chstrssh.before.decode()),colors.reset)
    vconsole = ("virsh console str-{}".format(ipstart))
    chstrssh.sendline(vconsole)
    chstrssh.sendline("")
    print (colors.fg.green,"\n Instance console is ready for Login",colors.reset)
    chstrssh.expect('login:')
    chstrssh.sendline('root')
    chstrssh.expect('Password:')
    chstrssh.sendline('ubuntu')
    print (colors.fg.yellow,"\n Instance virsh console connected, ready for network config \n {}".format(chstrssh.before.decode()),colors.reset)
    chstrssh.expect(':~#')
    ipsetin = ipblock+str(ipstart)  
    netpconfig = """cat << EOF > /etc/netplan/01-netcfg.yaml
# This is the network config written by 'subiquity'
network:
  version: 2
  ethernets:
    enp1s0:
      dhcp4: false
      dhcp6: false

  vlans:
    enp1s0.10:
      id: 10
      link: enp1s0
    enp1s0.20:
      id: 20
      link: enp1s0
    enp1s0.30:
      id: 30
      link: enp1s0
    enp1s0.40:
      id: 40
      link: enp1s0

  bridges:
    br-mgmt:
      addresses: [10.10.10.{}/24]
      interfaces: [enp1s0.10]
      parameters:
        stp: false
        forward-delay: 4
    br-storage:
      addresses: [10.10.20.{}/24]  
      parameters:
        stp: false
        forward-delay: 4
    br-vxlan:
      addresses: [10.10.30.{}/24]
      interfaces: [enp1s0.30]
      parameters:
        stp: false
        forward-delay: 4
    br-dhcp:
      addresses: [10.10.40.{}/24]
      interfaces: [enp1s0.40]
      parameters:
        stp: false
        forward-delay: 4
    br-vlan:
      addresses: [{}/24]
      gateway4: {}
      interfaces: [enp1s0]
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
      parameters:
        stp: false
        forward-delay: 4    
EOF""".format(str(ipstart), str(ipstart), str(ipstart), str(ipstart), ipsetin, ipgw)
    chstrssh.sendline(netpconfig)
    chstrssh.expect(':~#')
    chstrssh.sendline("netplan apply")
    time.sleep(5)
    chstrssh.expect(':~#')
    chstrssh.sendline("exit")
    print (colors.fg.blue,"\n Output of exit command: {}".format(chstrssh.before.decode()),colors.reset)         
    if chstrssh.isalive():
        print (colors.fg.pink,"\n The child process is still alive, closing connection to {}".format(i),colors.reset)
    #Incrementing the IP block within the for loop
    ipstart+=1
    print (colors.fg.red,"\n The ip for next iteration {}".format(str(ipstart)),colors.reset)
