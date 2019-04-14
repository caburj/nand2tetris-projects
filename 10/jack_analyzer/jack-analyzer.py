import click
import tokenizer
import parser
from pathlib import Path


@click.group()
def jack_analyzer():
    pass


def files_to_process(path: Path):
    """Returns the path of the jack files in the given path if dir."""
    if path.is_dir():
        return [d for d in path.iterdir() if d.suffix == ".jack"]
    else:
        return [path] if path.suffix == ".jack" else []


@jack_analyzer.command()
@click.argument("path", type=click.Path(exists=True))
def tokenize(path):
    """tokenizer"""
    filenames = files_to_process(Path(path))
    if not filenames:
        click.echo(f"Unable to detect jack files in the given path: {path}")
        return
    for fname in filenames:
        with open(fname) as stream:
            tokens_list = tokenizer.tokenize(stream.read())
            result_string = (
                "<tokens>\n"
                + "\n".join(map(lambda t: f"<{t[0]}> {t[1]} </{t[0]}>", tokens_list))
                + "\n</tokens>\n"
            )
            # append 'T' to the stem
            result_fname = (fname.parent / (fname.stem + "T")).with_suffix(".xml")
            with open(result_fname, "w") as f:
                f.write(result_string)


@jack_analyzer.command()
@click.argument("path", type=click.Path(exists=True))
def parse(path):
    """parser"""
    filenames = files_to_process(Path(path))
    if not filenames:
        click.echo(f"Unable to detect jack files in the given path: {path}")
        return
    for fname in filenames:
        with open(fname) as stream:
            result = parser.parse(stream.read())
            result_string = "\n".join(result) + "\n"
            with open(fname.with_suffix(".xml"), "w") as ans:
                ans.write(result_string)


if __name__ == "__main__":
    jack_analyzer()
