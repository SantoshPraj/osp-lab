#!/usr/bin/env python
#######################Script to create OSP Lab Infra ################################
import os, sys
import subprocess
import pexpect, time
from pexpect import pxssh

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
    print ("\n Adding image for Ansible VM")
    print ("\n Ssh for Ansible hosts initiated")
    ansiblessh = "ssh root@"+i
    chansssh = pexpect.spawn(ansiblessh)
    chansssh.expect('password:')
    chansssh.sendline('ubuntu')
    print ("\n Connected to ansible host {}".format(i))
    chansssh.expect(':~#')
    scpcmd = 'sshpass -p "ubuntu" scp -o StrictHostKeyChecking=no root@'+fileserver+':/home/himanshu/Ubuntu20-Cli-Img.qcow2 /root/'
    chansssh.sendline(scpcmd)
    time.sleep(30)
    chansssh.expect(':~#')
    print ("\n Output of SCP: {}".format(chansssh.before.decode()))
    imgcmd = ("cp /root/Ubuntu20-Cli-Img.qcow2 /var/lib/libvirt/images/ans-{}.qcow2".format(str(ipstart)))
    chansssh.sendline(imgcmd)
    time.sleep(15)
    chansssh.expect(':~#')
    print ("\n Output of CP: {}".format(chansssh.before.decode()))
    if ansspec["hdd"] > 100:
        ddexp = (ansspec["hdd"] - 100)
        diskresize = ("qemu-img resize /var/lib/libvirt/images/ans-"+str(ipstart)+".qcow2 +{}G".format(hddexp))
        print("\n resized disk: \n{}".format(diskresize))
        chansssh.sendline(diskresize)
        print ("\n Output of diskresize: {}".format(chansssh.before.decode()))
    vmcreate_cmd = "virt-install -n ans-"+str(ipstart)+" -r "+ansspec["mem"]+" --vcpus="+ansspec["cpu"]+" --os-type=Linux --os-variant=ubuntu20.04 --graphics=none --console pty,target_type=serial --network=bridge:br-mgmt,model=virtio --import --disk /var/lib/libvirt/images/ans-"+str(ipstart)+".qcow2 --noautoconsole -v"
    print ("\n vmcreate_cmd output: \n{}".format(vmcreate_cmd))
    chansssh.sendline(vmcreate_cmd)
    time.sleep(10)
    chansssh.expect(':~#')
    print ("\n Output of VIRT-INSTALL: {}".format(chansssh.before.decode()))
    vconsole = ("virsh console ans-{}".format(ipstart))
    chansssh.sendline(vconsole)
    chansssh.sendline("")
    print ("\n Output of virsh console command: {}".format(chansssh.before.decode()))
    print ("\n Instance console is ready for Login")
    chansssh.expect('login:')
    chansssh.sendline('root')
    chansssh.expect('Password:')
    chansssh.sendline('ubuntu')
    print ("\n Instance virsh console connected, ready for network config \n {}".format(chansssh.before.decode()))
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
    print ("\n {}".format(netpconfig))
    chansssh.sendline(netpconfig)
    chansssh.expect(':~#')
    chansssh.sendline("netplan apply")
    time.sleep(5)
    print ("\n Output of netplan apply: {}".format(chansssh.before.decode()))
    chansssh.expect(':~#')
    chansssh.sendline("logout")
    print ("\n Output for logout command: {}".format(chansssh.before.decode()))
    if chansssh.isalive():
        print ("\n The child process is still alive, closing connection to {}".format(i))
        chansssh.close()
        time.sleep(2)
    #Incrementing the IP block within the for loop
    ipstart+=1
    print ("\n The ip for next iteration {}".format(str(ipstart)))


##############Create Controller VM's #################################################
##############Need to write logic, if virtual size  is greater than 100G do qemu-img resize beforeproceeding######

for i in conthosts:
    print ("\n Adding image for controller VM")
    print ("\n Ssh for control hosts initiated")
    controlssh = "ssh root@"+i
    chconssh = pexpect.spawn(controlssh)
    chconssh.expect('password:')
    chconssh.sendline('ubuntu')
    print ("\n Connected to control host {}".format(i))
    chconssh.expect(':~#')
    scpcmd = 'sshpass -p "ubuntu" scp -o StrictHostKeyChecking=no root@'+fileserver+':/home/himanshu/Ubuntu20-Cli-Img.qcow2 /root/'
    chconssh.sendline(scpcmd)
    time.sleep(30)
    chconssh.expect(':~#')
    print ("\n Output of SCP: {}".format(chconssh.before.decode()))
    imgcmd = ("cp /root/Ubuntu20-Cli-Img.qcow2 /var/lib/libvirt/images/cont-{}.qcow2".format(str(ipstart)))
    chconssh.sendline(imgcmd)
    time.sleep(15)
    chconssh.expect(':~#')
    print ("\n Output of CP: {}".format(chconssh.before.decode()))
    if contspec["hdd"] > 100:
        ddexp = (contspec["hdd"] - 100)
        diskresize = ("qemu-img resize /var/lib/libvirt/images/cont-"+str(ipstart)+".qcow2 +{}G".format(hddexp))
        print("\n resized disk: \n{}".format(diskresize))
        chconssh.sendline(diskresize)
        print ("\n Output of diskresize: {}".format(chconssh.before.decode()))
    vmcreate_cmd = "virt-install -n cont-"+str(ipstart)+" -r "+contspec["mem"]+" --vcpus="+contspec["cpu"]+" --os-type=Linux --os-variant=ubuntu20.04 --graphics=none --console pty,target_type=serial --network=bridge:br-mgmt,model=virtio --import --disk /var/lib/libvirt/images/cont-"+str(ipstart)+".qcow2 --noautoconsole -v"
    print ("\n vmcreate_cmd output: \n{}".format(vmcreate_cmd))
    chconssh.sendline(vmcreate_cmd)
    time.sleep(5)
    chconssh.expect(':~#')
    print ("\n Output of VIRT-INSTALL: {}".format(chconssh.before.decode()))
    vconsole = ("virsh console cont-{}".format(ipstart))
    chconssh.sendline(vconsole)
    chconssh.sendline("")
    print ("\n Output of virsh console command: {}".format(chconssh.before.decode()))
    print ("\n Instance console is ready for Login")
    chconssh.expect('login:')
    chconssh.sendline('root')
    chconssh.expect('Password:')
    chconssh.sendline('ubuntu')
    print ("\n Instance virsh console connected, ready for network config \n {}".format(chconssh.before.decode()))
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
    print ("\n {}".format(netpconfig))
    chconssh.sendline(netpconfig)
    chconssh.expect(':~#')
    chconssh.sendline("netplan apply")
    time.sleep(5)
    print ("\n Output of netplan apply: {}".format(chconssh.before.decode()))
    chconssh.expect(':~#')
    chconssh.sendline("logout")
    print ("\n Output for logout command: {}".format(chconssh.before.decode()))      
    if chconssh.isalive():
        print ("\n The child process is still alive, closing connection to {}".format(i))
        chconssh.close()
        time.sleep(2)
    #Incrementing the IP block within the for loop
    ipstart+=1
    print ("\n The ip for next iteration {}".format(str(ipstart)))


############################Create Compute VM's################

for i in comphosts:
    print ("\n Adding image for compute VM")
    print ("\n Ssh for compute hosts initiated")
    computessh = "ssh root@"+i
    chcompssh = pexpect.spawn(computessh)
    chcompssh.expect('password:')
    chcompssh.sendline('ubuntu')
    print ("\n Connected to compute host {}".format(i))
    chcompssh.expect(':~#')
    scpcmd = 'sshpass -p "ubuntu" scp -o StrictHostKeyChecking=no root@'+fileserver+':/home/himanshu/Ubuntu20-Cli-Img.qcow2 /root/'
    chcompssh.sendline(scpcmd)
    time.sleep(30)
    chcompssh.expect(':~#')
    print ("\n Output of SCP: {}".format(chcompssh.before.decode()))
    imgcmd = ("cp /root/Ubuntu20-Cli-Img.qcow2 /var/lib/libvirt/images/comp-{}.qcow2".format(str(ipstart)))
    chcompssh.sendline(imgcmd)
    time.sleep(15)
    chcompssh.expect(':~#')
    print ("\n Output of CP: {}".format(chcompssh.before.decode()))
    if compspec["hdd"] > 100:
        ddexp = (compspec["hdd"] - 100)
        diskresize = ("qemu-img resize /var/lib/libvirt/images/comp-"+str(ipstart)+".qcow2 +{}G".format(hddexp))
        print("\n resized disk: \n{}".format(diskresize))
        chcompssh.sendline(diskresize)
        print ("\n Output of diskresize: {}".format(chcompssh.before.decode()))
    vmcreate_cmd = "virt-install -n comp-"+str(ipstart)+" -r "+compspec["mem"]+" --vcpus="+compspec["cpu"]+" --os-type=Linux --os-variant=ubuntu20.04 --graphics=none --console pty,target_type=serial --network=bridge:br-mgmt,model=virtio --import --disk /var/lib/libvirt/images/comp-"+str(ipstart)+".qcow2 --noautoconsole -v"
    chcompssh.sendline(vmcreate_cmd)
    time.sleep(5)
    chcompssh.expect(':~#')
    print ("\n Output of VIRT-INSTALL: {}".format(chcompssh.before.decode()))
    vconsole = ("virsh console comp-{}".format(ipstart))
    chcompssh.sendline(vconsole)
    chcompssh.sendline("")
    print ("\n Output of virsh console command: {}".format(chcompssh.before.decode()))
    print ("\n Instance console is ready for Login")
    chcompssh.expect('login:')
    chcompssh.sendline('root')
    chcompssh.expect('Password:')
    chcompssh.sendline('ubuntu')
    print ("\n Instance virsh console connected, ready for network config \n {}".format(chcompssh.before.decode()))
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
    print ("\n {}".format(netpconfig))
    chcompssh.sendline(netpconfig)
    chcompssh.expect(':~#')
    chcompssh.sendline("netplan apply")
    time.sleep(5)
    print ("\n Output of netplan apply: {}".format(chcompssh.before.decode()))
    chcompssh.expect(':~#')
    chcompssh.sendline("logout")
    print ("\n Output of logout command: {}".format(chcompssh.before.decode()))         
    if chcompssh.isalive():
        print ("\n The child process is still alive, closing connection to {}".format(i))
    #Incrementing the IP block within the for loop
    ipstart+=1
    print ("\n The ip for next iteration {}".format(str(ipstart)))

###################################################Create Storage VM############################################################33

for i in strhosts:
    print ("\n Adding image for Storage VM")
    print ("\n Ssh for Storage hosts initiated")
    storagessh = "ssh root@"+i
    chstrssh = pexpect.spawn(storagessh)
    chstrssh.expect('password:')
    chstrssh.sendline('ubuntu')
    print ("\n Connected to storage host {}".format(i))
    chstrssh.expect(':~#')
    scpcmd = 'sshpass -p "ubuntu" scp -o StrictHostKeyChecking=no root@'+fileserver+':/home/himanshu/Ubuntu20-Cli-Img.qcow2 /root/'
    chstrssh.sendline(scpcmd)
    time.sleep(30)
    chstrssh.expect(':~#')
    print ("\n Output of SCP: {}".format(chstrssh.before.decode()))
    imgcmd = ("cp /root/Ubuntu20-Cli-Img.qcow2 /var/lib/libvirt/images/str-{}.qcow2".format(str(ipstart)))
    chstrssh.sendline(imgcmd)
    time.sleep(15)
    if strspec["hdd"] > 100:
        hddexp = (strspec["hdd"] - 100)
        diskresize = "qemu-img resize /var/lib/libvirt/images/str-"+str(ipstart)+".qcow2 +"+hddexp+"G"
        print("\n resized disk: \n{}".format(diskresize))
    chstrssh.expect(':~#')
    print ("\n Output of CP: {}".format(chstrssh.before.decode()))
    vmcreate_cmd = "virt-install -n str-"+str(ipstart)+" -r "+strspec["mem"]+" --vcpus="+strspec["cpu"]+" --os-type=Linux --os-variant=ubuntu20.04 --graphics=none --console pty,target_type=serial --network=bridge:br-mgmt,model=virtio --import --disk /var/lib/libvirt/images/str-"+str(ipstart)+".qcow2 --noautoconsole -v"
    chstrssh.sendline(vmcreate_cmd)
    time.sleep(5)
    chstrssh.expect(':~#')
    print ("\n Output of VIRT-INSTALL: {}".format(chstrssh.before.decode()))
    vconsole = ("virsh console str-{}".format(ipstart))
    chstrssh.sendline(vconsole)
    chstrssh.sendline("")
    print ("\n Output of virsh console command: {}".format(chstrssh.before.decode()))
    print ("\n Instance console is ready for Login")
    chstrssh.expect('login:')
    chstrssh.sendline('root')
    chstrssh.expect('Password:')
    chstrssh.sendline('ubuntu')
    print ("\n Instance virsh console connected, ready for network config \n {}".format(chstrssh.before.decode()))
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
    print ("\n {}".format(netpconfig))
    chstrssh.sendline(netpconfig)
    chstrssh.expect(':~#')
    chstrssh.sendline("netplan apply")
    time.sleep(5)
    print ("\n Output of netplan apply: {}".format(chstrssh.before.decode()))
    chstrssh.expect(':~#')
    chstrssh.sendline("logout")
    print ("\n Output of logout command: {}".format(chstrssh.before.decode()))         
    if chstrssh.isalive():
        print ("\n The child process is still alive, closing connection to {}".format(i))
    #Incrementing the IP block within the for loop
    ipstart+=1
    print ("\n The ip for next iteration {}".format(str(ipstart)))
