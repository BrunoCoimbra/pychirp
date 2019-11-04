import sys
import argparse
import htchirp

# Every callable function defined here will be a valid pychirp sub-command.
# When defining a new function, please refer to an existing one as a model.
# All functions should implement both interactive and non-interactive parameter input.

# Functions take arguments from the command line when True
interactive = False

def fetch(remote_file = None, local_file = None):
    """Copy the remote_file from the submit machine to the execute machine, naming it local_file.
    
    Keyword Arguments:
        remote_file {string} -- File on submit machine (default: {None})
        local_file {string} -- File on execute machine (default: {None})
    """
    if interactive:
        parser = argparse.ArgumentParser()
        parser.prog = "%s fetch" % parser.prog
        parser.description = "Copy the remote_file from the submit machine to the execute machine, naming it local_file."
        parser.add_argument("remote_file")
        parser.add_argument("local_file")
        args = parser.parse_args(sys.argv[2:])
        remote_file = args.remote_file
        local_file = args.local_file
    
    if not isinstance(remote_file, str) or not isinstance(local_file, str):
        raise TypeError("fetch() requires two strings")

    with htchirp.HTChirp() as chirp:
        chirp.fetch(remote_file, local_file)

if __name__ == "__main__":
    # Help text
    description = "Drop-in replacement of condor_chirp in Pure Python"
    usage = "pychirp.py [-h] command [args]"
    epilog = """
commands:
  fetch remote_file local_file
  put [-mode mode] [-perm perm] local_file remote_file
  remove remote_file
  get_job_attr job_attribute
  get_job_attr_delayed job_attribute
  set_job_attr job_attribute attribute_value
  set_job_attr_delayed job_attribute attribute_value
  ulog text
  phase phasestring
  read [-offset offset] [-stride length skip] remote_file length
  write [-offset remote_offset] [-stride length skip] remote_file local_file
  rmdir [-r] remotepath
  getdir [-l] remotepath
  whoami
  whoareyou remotepath
  link [-s] oldpath newpath
  readlink remotepath length
  stat remotepath
  lstat remotepath
  statfs remotepath
  access remotepath mode(rwxf)
  chmod remotepath mode
  chown remotepath uid gid
  lchown remotepath uid gid
  truncate remotepath length
  utime remotepath actime mtime
"""

    # Handle command line arguments
    parser = argparse.ArgumentParser()
    parser.description = description
    parser.usage = usage
    parser.epilog = epilog
    parser.formatter_class = argparse.RawTextHelpFormatter
    parser.add_argument("command", help="one of the commands listed below")
    args = parser.parse_args(sys.argv[1:2])

    # Call the command function
    if args.command in dir() and callable(eval(args.command)):
        interactive = True
        eval(args.command)()
    else:
        print("error: command not implemented")