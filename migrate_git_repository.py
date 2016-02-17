#!/usr/bin/python
from __future__ import print_function


# Script migrates existing git repository to a new remote repository.
# Follow the prompt's answers. It will use/create local git folder,
# push existing git branches and tags to the new remote repository
# and point the local git repository to the new remote repository.
# ./migrate_git_repository.py -help


import os, sys, subprocess, re, argparse, json


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

    parser = argparse.ArgumentParser(description= """
        Script migrates existing git repository to a new remote repository.
        Follow the prompt's answers. It will use/create local git folder,
        push existing git branches and tags to the new remote repository
        and point the local git repository to the new remote repository.""",
                usage='%(prog)s [OPTIONS]',
                formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--working_dir", help="working_dir is a local folder where git repository will be created.", default="")

    parser.add_argument("--repo_name", help="repo_name is a git repository name that will be used as a folder name", default="")

    parser.add_argument("--repo_path", help="repo_path is local git repository path if already exists.", default="")

    parser.add_argument("--repo_origin", help="repo_origin is a source origin git repository url", default="")

    parser.add_argument("--repo_remote", help="repo_remote is a remote repository url", default="")

    args = parser.parse_args()

    print("Number of input arguments is: ", len(sys.argv),"\nGiven arguments are: ", json.dumps(vars(args), indent = 4))

    working_dir, repo_name, repo_path, repo_origin, repo_remote = \
        args.working_dir, args.repo_name, args.repo_path, args.repo_origin, args.repo_remote

    try:
        if not (len(repo_name)>0 and len(repo_path)>0 and len(repo_remote)>0):

            repo_name = raw_input("Enter git repository name:\n" + prompt)

            ret = raw_input("Would you like to clone migrating repository first? Yes/No:\n" + prompt)

            if re.match(ret, 'yes', re.IGNORECASE):

               working_dir = raw_input("Enter local directory path to clone existing git:\n" + prompt)

               repo_path = working_dir + os.sep + repo_name

               command = "mkdir -p " + repo_path

               out, err = exec_shell(add_path(working_dir,command))

               repo_origin =  raw_input("Enter original git repository url:\n" + prompt)

               command = "git clone " + repo_origin + " " + repo_path

               out, err = exec_shell(add_path(working_dir,command))

            else:

                repo_path = raw_input("Enter local git repository path:\n" + prompt)

            repo_remote = raw_input("Enter remote git repository url in single quotes:\n" + prompt)
 
        print("git repository name: ",repo_name, "\ngit repository local path: ",repo_path, \
              "\ngit repository remote url: ", repo_remote)

        out, err = exec_shell(add_path(repo_path,"git branch -a"))

        for line in out.splitlines(True):

            if "remotes/origin" in line and "master" not in line:

                command = "git checkout -b " + line.rsplit('/')[-1].rstrip('\n') + " origin/" + line.rsplit('/')[-1].rstrip('\n')

                print("Checkout remote branch: ", command)

                out, err = exec_shell(add_path(repo_path,command))

        print("Adding remote repo", repo_remote)

        command = "git remote add remote-origin " + repo_remote

        out, err = exec_shell(add_path(repo_path,command))

        print("Push local branches to remote-origin ", repo_remote)

        command = "git push --all remote-origin"

        out, err = exec_shell(add_path(repo_path,command))

        print("git push tags to remote-origin ", repo_remote)

        command = "git push --tags remote-origin"

        out, err = exec_shell(add_path(repo_path,command))

        print("git remove current origin repository")

        command = "git remote rm origin"

        out, err = exec_shell(add_path(repo_path,command))

        print("git remote rename remote-origin to origin")

        command = "git remote rename remote-origin origin"

        out, err = exec_shell(add_path(repo_path,command))

        print("steps to migrate git repo are done.")

    except Usage, err:

        print >>sys.stderr, err.msg

        print >>sys.stderr, "for help use --help"

        return 2


if __name__ == "__main__":
    sys.exit(main())
