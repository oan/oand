#!/usr/bin/env python
'''
This script runs all tests in a directory. It does not need to know about the
tests ahead of time. It recursively descends from the current directory and
automatically builds up a list of tests to run. Only directories named 'tests'
are processed. The path to each 'tests' directory is added to the PYTHONPATH.
Only python scripts that start with 'test_' are added to the list of scripts in
the test suite.

This script is heavly based on Noah Spurriers testall.py script that are used
with pexpect. Original URL
http://pexpect.svn.sourceforge.net/viewvc/pexpect/trunk/pexpect/tools/testall.py?revision=447&view=markup

'''

__author__ = "Daniel Lindh"
__maintainer__ = "daniel.lindh@cybercow.se"

import unittest
import os
import os.path
import sys
import trace
from optparse import OptionParser

def run():
    setup_env()
    set_global_options_and_args()
    remove_cmd_line_arguments()

    import util_network_simulation
    util_network_simulation.start_test_network()

    if OPTIONS.trace:
        run_main_with_trace()
    else:
        main()

    util_network_simulation.stop_test_network()

def setup_env():
    sys.path.insert(1, get_base_dir())
    sys.path.insert(1, get_base_dir() + "src")
    sys.path.insert(1, get_base_dir() + "src/tests")
    os.chdir(get_base_dir())

def get_base_dir():
    '''
    Return the path to the root folder of the project.

    '''

    return os.path.abspath(__file__ + "/../../../") + "/" # MPA I need this to get down to base_dir
    # return os.path.abspath(__file__ + "/../../") + "/"

def set_global_options_and_args():
    '''
    Set cmd line arguments in global vars OPTIONS and ARGS.

    '''
    global OPTIONS, ARGS

    usage = "usage: %prog [-t] -f filename"

    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--trace", action="store_true",
                      help="run with trace.Trace")

    parser.add_option("-f", dest="filename",
                      help="only run the tests in the file")

    (OPTIONS, ARGS) = parser.parse_args()

def remove_cmd_line_arguments():
    '''
    Or unit test classes will try to get the arguments.

    '''
    del sys.argv[1:]

def run_main_with_trace():
    cover_dir = sys.path[0] + "/cover/"
    print "Look in %s for cover files" % cover_dir

    # create a Trace object, telling it what to ignore, and whether to
    # do tracing or line-counting or both.
    tracer = trace.Trace(
        ignoredirs = [sys.prefix, sys.exec_prefix],
        trace = 0,
        count = 1,
        countfuncs = 1,
        countcallers = 1,
        infile = cover_dir + "cover.tmp",
        outfile = cover_dir + "cover.tmp"
    )

    # run the new command using the given tracer
    tracer.run('main()')

    # make a report, placing output in /tmp
    r = tracer.results()
    r.write_results(show_missing = True, summary = True, coverdir = cover_dir)

def main():
    unittest.TextTestRunner().run(suite())

def add_tests_to_list (import_list, dirname, names):
    global OPTIONS

    # Only check directories named 'tests'.
    if os.path.basename(dirname) != 'tests':
        return

    # Add any files that start with 'test_' and end with '.py'.
    for f in names:
        filename, ext = os.path.splitext(f)
        if ext == '.py' and filename.find('test_') == 0:
            if OPTIONS.filename == None or OPTIONS.filename == filename:
                import_list.append (os.path.join(dirname, filename))

def find_modules_and_add_paths (root_path):
    import_list = []
    module_list = []
    os.path.walk (root_path, add_tests_to_list, import_list)
    for module_file in import_list:
        path, module = os.path.split(module_file)
        module_list.append (module)
        print 'Adding:', module_file
        if not path in sys.path:
            sys.path.append (path)
        if not os.path.dirname(path) in sys.path:
            sys.path.append (os.path.dirname(path))
    module_list.sort()
    return module_list

def suite():
  modules_to_test = find_modules_and_add_paths(os.getcwd())
  alltests = unittest.TestSuite()
  for module in map(__import__, modules_to_test):
    alltests.addTest(unittest.findTestCases(module))
  return alltests

if __name__ == '__main__':
    run()
