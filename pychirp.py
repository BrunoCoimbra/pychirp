import sys
import argparse
import re
import htchirp

from inspect import getargspec

# Every callable function not starting with "_" defined here will be a valid pychirp sub-command.
# When defining a new function, please refer to an existing one as a model.
# All functions should implement both interactive and non-interactive parameter input.

# Functions take arguments from the command line when True
interactive = False

def _interactive(custom={}):
    """Makes the function callable from a console.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if interactive:
                # Parser initialization
                parser = argparse.ArgumentParser()
                
                # Define command usage
                parser.prog = "%s %s" % (parser.prog, func.__name__)
                
                # Define command help based on an available docstring
                if func.__doc__:
                    parser.description = re.split(r"\n\s*\n", func.__doc__)[0]
                
                # Retrieve function signature to build arguments
                args, _, _, defaults = getargspec(func)
                if defaults:
                    defaults = dict(zip(args[-len(defaults):], defaults))
                else:
                    defaults = {}

                # Add arguments to the parser and tries to extract help from an available docstring
                for arg in args:
                    arghelp = None
                    if func.__doc__:
                        argdoc = re.findall(r"%s\s\(.*\)\:\s(.*)" % arg, func.__doc__)
                        if argdoc:
                            arghelp = re.sub(r"\sdefaults\sto\s.*", "", argdoc[0].lower()).strip(".")
                    argname = arg
                    argoptions = {"help": arghelp}
                    if arg in defaults:
                        argname = "-" + arg
                    if arg in custom:
                        argoptions.update(custom[arg])
                    parser.add_argument(argname, **argoptions)

                # Parse system args
                parsed_args = vars(parser.parse_args(sys.argv[2:]))
                parsed_args = dict(filter(lambda item: item[1] or item[0] not in defaults, parsed_args.items()))
                
                return func(**parsed_args)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@_interactive()
def fetch(remote_file, local_file):
    """Copy the remote_file from the submit machine to the execute machine, naming it local_file.
    
    Args:
        remote_file (string, optional): File on submit machine.
        local_file (string, optional): File on execute machine.
    
    Returns:
        integer: Bytes written
    """

    with htchirp.HTChirp() as chirp:
        return chirp.fetch(remote_file, local_file)

@_interactive()
def put(remote_file, local_file, mode="wct", perm=None):
    """Copy the local_file from the execute machine to the submit machine, naming it remote_file.
       The optional perm argument describes the file access permissions in a Unix format.
       The optional mode argument is one or more of the following characters describing the remote_file file:
       w, open for writing; a, force all writes to append; t, truncate before use;
       c, create the file, if it does not exist; x, fail if c is given and the file already exists.
    
    Args:
        remote_file (string, optional): File on submit machine.
        local_file (string, optional): File on execute machine.
        mode (string, optional): File open modes (one or more of 'watcx'). Defaults to 'wct'.
            w, open for writing;
            a, force all writes to append;
            t, truncate before use;
            c, create the file, if it does not exist;
            x, fail if c is given and the file already exists. Defaults to None.
        perm (string, optional): Describes the file access permissions in a Unix format. Defaults to None.
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
        chirp.put(remote_file, local_file, mode, perm)

@_interactive()
def remove(remote_file):
    """Remove the remote_file file from the submit machine.
    
    Args:
        remote_file (string, optional): File on submit machine.
    """

    with htchirp.HTChirp() as chirp:
        chirp.remove(remote_file)

@_interactive()
def get_job_attr(job_attribute):
    """Prints the named job ClassAd attribute to standard output.
    
    Args:
        job_attribute (string, optional): Job ClassAd attribute.
    
    Returns:
        string: The value of the job attribute as a string
    """

    with htchirp.HTChirp() as chirp:
        return chirp.get_job_attr(job_attribute)

@_interactive()
def set_job_attr(job_attribute, attribute_value):
    """Sets the named job ClassAd attribute with the given attribute value.
    
    Args:
        job_attribute (string): Job ClassAd attribute.
        attribute_value (string): Job ClassAd value.
    """

    with htchirp.HTChirp() as chirp:
        chirp.set_job_attr(job_attribute, attribute_value)

@_interactive()
def get_job_attr_delayed(job_attribute):
    """Prints the named job ClassAd attribute to standard output, potentially reading the cached value from a recent set_job_attr_delayed.
    
    Args:
        job_attribute (string, optional): Job ClassAd attribute.
    
    Returns:
        string: The value of the job attribute as a string
    """

    with htchirp.HTChirp() as chirp:
        return chirp.get_job_attr_delayed(job_attribute)

@_interactive()
def set_job_attr_delayed(job_attribute, attribute_value):
    """Sets the named job ClassAd attribute with the given attribute value, but does not immediately
       synchronize the value with the submit side. It can take 15 minutes before the synchronization occurs.
       This has much less overhead than the non delayed version. With this option, jobs do not need ClassAd
       attribute WantIOProxy set. With this option, job attribute names are restricted to begin with the case
       sensitive substring Chirp. 
    
    Args:
        job_attribute (string): Job ClassAd attribute.
        attribute_value (string): Job ClassAd value.
    """

    with htchirp.HTChirp() as chirp:
        chirp.set_job_attr_delayed(job_attribute, attribute_value)

@_interactive()
def ulog(text):
    """Appends Message to the job event log.
    
    Args:
        text (string): Message to log.
    """

    with htchirp.HTChirp() as chirp:
        chirp.ulog(text)

@_interactive({"stride":{"nargs": 2, "metavar": ("LENGTH", "SKIP")}})
def read(remote_file, length, offset=None, stride=(None, None)):
    """Read length bytes from remote_file. Optionally, implement a stride by starting the read at offset
       and reading stride(length) bytes with a stride of stride(skip) bytes.
    
    Args:
        remote_file (string): File on the submit machine.
        length (integer): Number of bytes to read.
        offset (integer, optional): Number of bytes to offset from beginning of file. Defaults to None.
        stride (tuple, optional): Number of bytes to read followed by number of bytes to skip per stride. Defaults to (None, None).
    
    Returns:
        string: Data read from file
    """

    with htchirp.HTChirp() as chirp:
        return chirp.read(remote_file, length, offset, stride[0], stride[1])

@_interactive({"length": {"nargs": "?"}, "stride":{"nargs": 2, "metavar": ("LENGTH", "SKIP")}})
def write(remote_file, local_file, length, offset=None, stride=(None, None)):
    """Write the contents of local_file to remote_file. Optionally, start writing to the remote file at offset
       and write stride(length) bytes with a stride of stride(skip) bytes. If the optional length follows
       local_file, then the write will halt after length input bytes have been written. Otherwise, the entire
       contents of local_file will be written.
    
    Args:
        remote_file (string): File on the submit machine.
        local_file (string): File on execute machine.
        length (int): Number of bytes to write.
        offset (integer, optional): Number of bytes to offset from beginning of file. Defaults to None.
        stride (tuple, optional): Number of bytes to read followed by number of bytes to skip per stride. Defaults to (None, None).
    """

    data = open(local_file).read()

    with htchirp.HTChirp() as chirp:
        chirp.write(data, remote_file, length=length, offset=offset, stride_length=stride[0], stride_skip=stride[1])

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