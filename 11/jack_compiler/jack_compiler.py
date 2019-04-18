import click
import tokenizer
import compiler
from pathlib import Path


@click.group()
def jack_compiler():
    pass


def files_to_process(path: Path):
    """Returns the path of the jack files in the given path if dir."""
    if path.is_dir():
        return [d for d in path.iterdir() if d.suffix == ".jack"]
    else:
        return [path] if path.suffix == ".jack" else []


@jack_compiler.command()
@click.argument("path", type=click.Path(exists=True))
def compile(path):
    """compiler"""
    filenames = files_to_process(Path(path))
    if not filenames:
        click.echo(f"Unable to detect jack files in the given path: {path}")
        return
    for fname in filenames:
        with open(fname) as stream:
            jack_code = compiler.JackCompiler(stream.read())
            result_string = "\n".join(jack_code.compile()) + "\n"
            with open(fname.with_suffix(".vm"), "w") as ans:
                ans.write(result_string)


if __name__ == "__main__":
    jack_compiler()
