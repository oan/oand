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
    setup_trail()

    #We might not need to use this, now when we are using twisted unit test.
    #import util_network_simulation
    #util_network_simulation.start_test_network()

    trail_run()

    #util_network_simulation.stop_test_network()

def setup_env():
    sys.path.insert(1, get_base_dir())
    sys.path.insert(1, get_base_dir() + "/tests")
    os.chdir(get_base_dir())

def get_base_dir():
    '''
    Return the path to the root folder of the project.

    '''
    return os.path.abspath(__file__ + "/../../") + "/"

def set_global_options_and_args():
    '''
    Set cmd line arguments in global vars OPTIONS and ARGS.

    '''
    global OPTIONS, ARGS

    usage = "usage: %prog [-t] -f filename"

    parser = OptionParser(usage=usage)

    parser.add_option("-f", dest="filename",
                      help="only run the tests in the file")

    (OPTIONS, ARGS) = parser.parse_args()

def remove_cmd_line_arguments():
    '''
    Or unit test classes will try to get the arguments.

    '''
    del sys.argv[1:]

def setup_trail():
    '''
    Set command line options for twisted trail.

    '''
    modules_to_test = find_modules_and_add_paths(os.getcwd())
    sys.argv.extend(modules_to_test)

def trail_run():
    '''
    Start unit test with twisted trail.

    '''
    import twisted.scripts.trial

    config = twisted.scripts.trial.Options()
    try:
        config.parseOptions()
    except usage.error, ue:
        raise SystemExit, "%s: %s" % (sys.argv[0], ue)
    twisted.scripts.trial._initialDebugSetup(config)
    trialRunner = twisted.scripts.trial._makeRunner(config)
    suite = twisted.scripts.trial._getSuite(config)
    if config['until-failure']:
        test_result = trialRunner.runUntilFailure(suite)
    else:
        test_result = trialRunner.run(suite)
    if config.tracer:
        sys.settrace(None)
        results = config.tracer.results()
        results.write_results(
            show_missing=1, summary=False,
            coverdir=config.coverdir
        )

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

if __name__ == '__main__':
    run()
