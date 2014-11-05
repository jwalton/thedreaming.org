---
title: "Exploring Ansible with Vagrant"
tags:
- ansible
- vagrant
---
I'm learning Ansible at the moment.  In order to play around with it with in nice safe disposable environment, I've created an "Ansible playground" with Vagrant.

<!--more-->

This assumes you already have [Vagrant](https://docs.vagrantup.com/v2/installation/index.html) and [Ansible](http://docs.ansible.com/intro_installation.html) installed.

Vagrant has an [Ansible provisioner](https://docs.vagrantup.com/v2/provisioning/ansible.html) which can automatically run ansible when you `vagrant up`, but we're not going to use that (for now); we're just going to use vagrant to give us a VM we can play on.

## Setup

First, create a project directory.  Inside that directory, run:

````
$ vagrant init ubuntu/trusty64
$ vagrant up
$ mkdir ansible
$ mkdir ansible/roles
$ mkdir ansible/playbooks
````

In the vagrant output, notice the following lines:

````
==> default: Booting VM...
==> default: Waiting for machine to boot. This may take a few minutes...
    default: SSH address: 127.0.0.1:2222
    default: SSH username: vagrant
    default: SSH auth method: private key
````

The SSH address is important - remember that IP and port; we'll need them in a moment.  Now create a file called `ansible/hosts`:

````
[vagrantboxes]
vagrant ansible_ssh_host=127.0.0.1 ansible_ssh_port=2222

[vagrantboxes:vars]
ansible_ssh_user=vagrant
ansible_ssh_private_key_file=~/.vagrant.d/insecure_private_key
````

This is an [Ansible inventory file](http://docs.ansible.com/intro_inventory.html) which tells Ansible how to connect to our vagrant VM.  The `ansible_ssh_port` must be the port number from our `vagrant up` command, and `ansible_ssh_host` is the IP.

One more file to create.  By default, Ansible goes looking for configuration in /etc/ansible.  We want it to use our local inventory file, though, so create `./ansible.cfg`:

````
[defaults]
host_key_checking = False
hostfile = ./ansible/hosts
roles_path = ./ansible/roles
````

This tells Ansible to use our custom hosts file (and to look for roles in the custom "roles" folder - we'll get to that in a minute.)  Now you should be able to run [Ansible ad-hoc commands](http://docs.ansible.com/intro_adhoc.html) on your vagrant machine:

````
$ ansible all -m ping
vagrrant | success >> {
    "changed": false,
    "ping": "pong"
}

$ ansible all -a "/bin/echo hello"
vagrant | success | rc=0 >>
hello
````

## Running a Playbook

Now let's use Ansible to install docker on our vagrant VM.  We'll use Paul Durivage's [Docker role](https://github.com/angstwad/docker.ubuntu) for this.  First, we install the role in `./ansible/roles`:

````
$ ansible-galaxy install -p ./ansible/roles angstwad.docker_ubuntu
````

Now we need to create a playbook which uses this role.  Create `./ansible/playbooks/docker.yml`:

````
---
- name: Install pycurl
  hosts: all
  sudo: yes
  tasks:
    apt: pkg=python-pycurl update_cache=yes cache_valid_time=600

- name: Install Docker
  hosts: all
  sudo: yes
  roles:
    - angstwad.docker_ubuntu
````

Run the playbook with:

````
$ ansible-playbook ./ansible/playbooks/docker.yml
````

This will take a few minutes, but when it's done, let's see if it worked!

````
$ vagrant ssh
vagrant$ sudo docker pull ubuntu:12.04
Pulling repository ubuntu

vagrant$ sudo docker run ubuntu:12.04 echo "Hello world"
Hello world
````

## Vagrant Provisioner

Now let's get Vagrant to provision our VM for us.  First, we need to modify our vagrant file to look like this:

````
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/playbooks/docker.yml"
  end
end
````

Vagrant will create an inventory file for you in `.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory`, so update ansible.cfg too look like:

````
[defaults]
host_key_checking = False
hostfile = .vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory
roles_path = ./ansible/roles
````

Now run:

````
$ vagrant provision
````

And vagrant will converge your VM with Ansible.
