# ----------------------------------------------------------------------
# |
# |  DuplicateEnvironment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-03-21 19:52:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Creates a script that duplicates the active environment."""

import os

from pathlib import Path
from typing import Optional

import typer

from typer.core import TyperGroup

from Common_Foundation.Shell.All import CurrentShell
from Common_Foundation.Shell import Commands
from Common_Foundation.Streams.DoneManager import DoneManager, DoneManagerFlags
from Common_Foundation import Types


# ----------------------------------------------------------------------
class NaturalOrderGrouper(TyperGroup):
    # pylint: disable=missing-class-docstring
    # ----------------------------------------------------------------------
    def list_commands(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.commands.keys()


# ----------------------------------------------------------------------
app                                         = typer.Typer(
    cls=NaturalOrderGrouper,
    help=__doc__,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
)


# ----------------------------------------------------------------------
@app.command(
    "EntryPoint",
    help=__doc__,
    no_args_is_help=True,
)
def EntryPoint(
    output_filename: str=typer.Argument(..., help="Name of the file to write or 'stdout' to write to standard output."),
    verbose: bool=typer.Option(False, "--verbose", help="Write verbose information to the terminal."),
    debug: bool=typer.Option(False, "--debug", help="Write debug information to the terminal."),
) -> None:
    with DoneManager.CreateCommandLine(
        output_flags=DoneManagerFlags.Create(verbose=verbose, debug=debug),
    ) as dm:
        commands: list[Commands.Command] = [
            Commands.EchoOff(),
            Commands.PushDirectory(Path.cwd()),
            Commands.WindowTitle(Types.EnsureValid(os.getenv("DEVELOPMENT_ENVIRONMENT_WINDOW_TITLE")))
        ]

        for k, v in os.environ.items():
            commands.append(Commands.Set(k, v))

        content = CurrentShell.GenerateCommands(commands)

        if output_filename == "stdout":
            dm.WriteLine(content)
            return

        output_file = Path(output_filename)

        with dm.Nested("Writing '{}'...".format(output_file)):
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with output_file.open("w") as f:
                f.write(content)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()
