This directory is for Ansible modules used by this project.

The modules typically are maintained in separate git repos and added here. The preferred way to add in these repos
is with [git-subtree](https://github.com/git/git/blob/master/contrib/subtree/git-subtree.txt) as it avoids the end
user having to do anything special when downloading the code. Unfortunately this does not play well with gerrit which
is used by OpenStack. With the desire to still avoid the special clone syntax used with git submodule the files were just
imported from the upstream libraries.

- monasca comes from https://github.com/hpcloud-mon/ansible-module-monasca.git

