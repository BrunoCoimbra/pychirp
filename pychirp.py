import sys
import argparse
import re
import htchirp

from inspect import signature, Parameter

# Every callable function not starting with "_" defined here will be a valid pychirp sub-command.
# When defining a new function, please refer to an existing one as a model.
# All functions should implement both interactive and non-interactive parameter input.

# Functions take arguments from the command line when True
interactive = False

def _interactive(func):
    """Makes the function callable from a console.
    """
    def wrapper(*args, **kwargs):
        if interactive:
            parser = argparse.ArgumentParser()
            parser.prog = "%s %s" % (parser.prog, func.__name__)
            parser.description = re.split(r"\n\s*\n", func.__doc__)[0]
            for arg in signature(func).parameters.values():
                if arg.default is Parameter.empty:
                    parser.add_argument(arg.name)
                else:
                    parser.add_argument("-" + arg.name)
            parsed_args = parser.parse_args(sys.argv[2:])
            return func(**vars(parsed_args))
        return func(*args, **kwargs)
    return wrapper

@_interactive
def fetch(remote_file, local_file):
    """Copy the remote_file from the submit machine to the execute machine, naming it local_file.
    
    Args:
        remote_file (string, optional): File on submit machine. Defaults to None.
        local_file (string, optional): File on execute machine. Defaults to None.
    
    Returns:
        integer: Bytes written
    """

    with htchirp.HTChirp() as chirp:
        return chirp.fetch(remote_file, local_file)

@_interactive
def put(remote_file, local_file, mode=None, perm=None):
    """Copy the local_file from the execute machine to the submit machine, naming it remote_file.
       The optional perm argument describes the file access permissions in a Unix format.
       The optional mode argument is one or more of the following characters describing the remote_file file:
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
    
    Returns:
        integer: Size of written file
    """
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
        return chirp.put(remote_file, local_file, mode, perm)

@_interactive
def remove(remote_file):
    """Remove the remote_file file from the submit machine.
    
    Args:
        remote_file (string, optional): File on submit machine. Defaults to None.
    """

    with htchirp.HTChirp() as chirp:
        chirp.remove(remote_file)

@_interactive
def get_job_attr(job_attribute):
    """Prints the named job ClassAd attribute to standard output.
    
    Args:
        job_attribute (string, optional): Job ClassAd attribute. Defaults to None.
    
    Returns:
        string: The value of the job attribute as a string
    """

    with htchirp.HTChirp() as chirp:
        return chirp.get_job_attr(job_attribute)

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
    if args.command in dir() \
    and not args.command.startswith("_") \
    and callable(eval(args.command)):
        interactive = True
        response = eval(args.command)()
        if response is not None:
            print(response)
    else:
        print("error: command not implemented")