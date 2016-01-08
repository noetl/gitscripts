#!/usr/bin/python
from __future__ import print_function

# Script migrates existing git repository to a new remote repository.
# Follow the prompt's answers. It will use/create local git folder,
# push existing git branches and tags to the new remote repository
# and point the local git repository to the new remote repository.
# If you'd like to run script with input parameters the following order is expected:
# ./migrate_git_repository.py <repository name> <repository local path> <remote repository url>
# ./migrate_git_repository.py gitscripts ~/noetl/gitscripts https://github.com/noetl/gitscripts

import os, sys, subprocess, re


prompt = '> '


def exec_shell(commands):
   try:
        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err =  process.communicate(commands)
        print("Stdout: ", out,"\nError:",err,"\n")
        return out, err
   except:
        e = sys.exc_info()
        print("exec_shell failed: ", e)
        ret = raw_input("Would you like to continue?\n" + prompt)
        if re.match(ret, 'yes', re.IGNORECASE):
            return None,None
        else:
            sys.exit(main())


def add_path(repopath, command):
    return '''
cd ''' + repopath + ''' +
''' + command + '''
'''


def assign_vars(*args):
    try:
        return str(args[1]),str(args[2]),str(args[3])
    except:
        return None, None, None


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    global workingdir, reponame, repopath, reporigin, reporemote

    if argv is None:
        argv = sys.argv
        print("Lenght of arguments is: ", len(argv) )

    try:
        if len(argv)==4:
            reponame, repopath, reporemote = assign_vars(*argv)
        else:
            reponame = raw_input("Enter git repository name:\n" + prompt)
            ret = raw_input("Would you like to clone migrating repository first? Yes/No:\n" + prompt)
            if re.match(ret, 'yes', re.IGNORECASE):
               workingdir = raw_input("Enter local directory path to clone existing git:\n" + prompt)
               repopath = workingdir + os.sep + reponame
               command = "mkdir -p " + repopath
               out, err = exec_shell(add_path(workingdir,command))
               reporigin =  raw_input("Enter original git repository url:\n" + prompt)
               command = "git clone " + reporigin + " " + repopath
               out, err = exec_shell(add_path(workingdir,command))
            else:
                repopath = raw_input("Enter local git repository path:\n" + prompt)
            reporemote = raw_input("Enter remote git repository url in single quotes:\n" + prompt)

        print("git repository name: ",reponame, "\ngit repository local path: ",repopath, \
              "\ngit repository remote url: ", reporemote)
        out, err = exec_shell(add_path(repopath,"git branch -a"))

        for line in out.splitlines(True):
            if "remotes/origin" in line and "master" not in line:
                command = "git checkout -b " + line.rsplit('/')[-1].rstrip('\n') + " origin/" + line.rsplit('/')[-1].rstrip('\n')
                print("Checkout remote branch: ", command)
                out, err = exec_shell(add_path(repopath,command))

        print("Adding remote repo", reporemote)
        command = "git remote add remote-origin " + reporemote
        out, err = exec_shell(add_path(repopath,command))

        print("Push local branches to remote-origin ", reporemote)
        command = "git push --all remote-origin"
        out, err = exec_shell(add_path(repopath,command))

        print("git push tags to remote-origin ", reporemote)
        command = "git push --tags remote-origin"
        out, err = exec_shell(add_path(repopath,command))

        print("git remove current origin repository")
        command = "git remote rm origin"
        out, err = exec_shell(add_path(repopath,command))

        print("git remote rename remote-origin to origin")
        command = "git remote rename remote-origin origin"
        out, err = exec_shell(add_path(repopath,command))

        print("steps to migrate git repo are done.")

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
