import sys
import argparse
import htchirp

# Every callable function defined here will be a valid pychirp sub-command.
# When defining a new function, please refer to an existing one as a model.
# All functions should implement both interactive and non-interactive parameter input.

# Functions take arguments from the command line when True
interactive = False

def fetch(remote_file=None, local_file=None):
    """Copy the remote_file from the submit machine to the execute machine, naming it local_file.
    
    Args:
        remote_file (string, optional): File on submit machine. Defaults to None.
        local_file (string, optional): File on execute machine. Defaults to None.
    
    Raises:
        TypeError: If `remote_file` or `local_file` are not given in non-interactive mode.
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
        raise TypeError("fetch() requires remote_file and local_file")

    with htchirp.HTChirp() as chirp:
        chirp.fetch(remote_file, local_file)

def put(remote_file=None, local_file=None, mode=None, perm=None):
    """Copy the local_file from the execute machine to the submit machine, naming it remote_file.
       The optional -mode mode argument is one or more of the following characters describing the remote_file file:
       w, open for writing; a, force all writes to append; t, truncate before use;
       c, create the file, if it does not exist; x, fail if c is given and the file already exists.
    
    Args:
        remote_file (string, optional): File on submit machine. Defaults to None.
        local_file (string, optional): File on execute machine. Defaults to None.
        mode (string, optional): Decribes remote_file open mode with one of the following characters. Defaults to None.
            w, open for writing;
            a, force all writes to append;
            t, truncate before use;
            c, create the file, if it does not exist;
            x, fail if c is given and the file already exists. Defaults to None.
        perm (string, optional): Describes the file access permissions in a Unix format.
    
    Raises:
        TypeError: If `remote_file` or `local_file` are not given in non-interactive mode.
    """
    description = """Copy the local_file from the execute machine to the submit machine, naming it remote_file.

The optional -perm UnixPerm argument describes the file access permissions in a Unix format;
660 is an example Unix format.

The optional -mode mode argument is one or more of the following characters describing the remote_file file:
w, open for writing; a, force all writes to append; t, truncate before use;
c, create the file, if it does not exist; x, fail if c is given and the file already exists. 
"""

    if interactive:
        parser = argparse.ArgumentParser()
        parser.prog = "%s fetch" % parser.prog
        parser.description = description
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.add_argument("local_file")
        parser.add_argument("remote_file")
        parser.add_argument("-mode")
        parser.add_argument("-perm")
        args = parser.parse_args(sys.argv[2:])
        local_file = args.local_file
        remote_file = args.remote_file
        mode = args.mode
        perm = args.perm
    
    if not isinstance(remote_file, str) or not isinstance(local_file, str):
        raise TypeError("put() requires at least remote_file and local_file")

    opt_params = {}
    if mode:
        # Add "w" to along with the following characters to reproduce condor_chirp behavior
        for c in "act":
            if c in mode:
                mode += "w"
                break
        opt_params["flags"] = mode
    if perm:
        opt_params["mode"] = perm

    with htchirp.HTChirp() as chirp:
        chirp.put(local_file, remote_file, **opt_params)

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