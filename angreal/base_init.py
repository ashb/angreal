"""
    angreal.base_init
    ~~~~~~~~~~~~~~~~~

    Just a pass through to cookie-cutter

"""


import os
import shutil
import tempfile

import click
from click.testing import CliRunner

from cookiecutter.exceptions import OutputDirExistsException

import angreal
from angreal.cutter import initialize_cutter
from angreal.utils import get_angreal_path, import_from_file


def print_nested_help(repository):
    """
    Prints a general
    :param repository:
    :return:
    """

    with click.Context(base_init) as ctx:
        click.echo(base_init.get_help(ctx))

    try:
        tmp_dir = tempfile.mkdtemp()
        project_path = initialize_cutter(repository,no_input=True,output_dir=tmp_dir)
        os.chdir(project_path)
        mod = import_from_file(os.path.join(get_angreal_path(),'init.py'))

        mod = mod.init
        click.echo("""
    These are the options for the repository ({}) you are attempting to initialize
        """.format(repository))
        with click.Context(mod) as ctx:
            click.echo(mod.get_help(ctx))

        shutil.rmtree(tmp_dir)
    except Exception:
        pass


    exit(0)




@angreal.command(context_settings=dict(ignore_unknown_options=True),
                 add_help_option=False)
@angreal.argument('repository')
@angreal.argument('init_args', nargs=-1, type=click.UNPROCESSED)
@angreal.option('--help','-h', is_flag=True, help='Display a help message')
def base_init(repository,init_args,help):
    """
    Initialize an angreal based project.
    """
    if help:
        print_nested_help(repository)
        exit(0)

    try:
        project_path = initialize_cutter(repository)
    except OutputDirExistsException:
        exit(-2)
    os.chdir(project_path)
    file = os.path.join(get_angreal_path(), 'init.py')

    try:
        # First try to import the file
        mod = import_from_file(file)

        try:
            # Try to run the "init" function in the task_init file, pass through all of the init_args
            result = CliRunner().invoke(mod.init, init_args)
            if result.exit_code != 0 :
                raise Exception(result.__dict__)
            if result.exception :
                raise result.exception
        except Exception as e:
            # Something happened in the sub init execution
            shutil.rmtree(project_path)
            raise
            exit (-1)

        # Init commands should only be run ONCE
        os.unlink(file)

    except (ImportError, FileNotFoundError):
        # if the file doesn't exist or import fails pass
        shutil.rmtree(project_path)
        exit(-1)

    return




