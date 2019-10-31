import htchirp
import argparse

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

if __name__ == "__main__":

    # Handle command line arguments
    parser = argparse.ArgumentParser()
    parser.description = description
    parser.usage = usage
    parser.epilog = epilog
    parser.formatter_class = argparse.RawTextHelpFormatter
    parser.add_argument("command", help="one of the commands listed below")
    args = parser.parse_args()

    # Call the command function
    try:
        eval(args.command)()
    except NameError:
        print("error: command not implemented")