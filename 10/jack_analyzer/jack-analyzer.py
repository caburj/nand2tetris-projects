import click
import tokenizer
import parser
from pathlib import Path


@click.group()
def jack_analyzer():
    pass


@jack_analyzer.command()
@click.argument("path", type=click.Path(exists=True))
def tokenize(path):
    """tokenizer cli"""
    path = Path(path)
    if path.is_dir():
        filenames = [d for d in path.iterdir() if d.suffix == ".jack"]
    else:
        filenames = [path]
    for fname in filenames:
        with open(fname) as stream:
            string = stream.read()
            tokens_list = tokenizer.tokenize(string)
            result_string = (
                "<tokens>\n"
                + "\n".join(map(lambda t: f"<{t[0]}> {t[1]} </{t[0]}>", tokens_list))
                + "\n</tokens>\n"
            )
            parent_dir = fname.parent
            new_name = fname.stem + "T"
            result_fname = (parent_dir / new_name).with_suffix(".xml")
            with open(result_fname, "w") as f:
                f.write(result_string)


@jack_analyzer.command()
@click.argument("path", type=click.Path(exists=True))
def parse(path):
    """parser cli"""
    path = Path(path)
    if path.is_dir():
        filenames = [d for d in path.iterdir() if d.suffix == ".jack"]
    else:
        filenames = [path]
    for fname in filenames:
        with open(fname) as stream:
            source_code_string = stream.read()
            result = parser.parse(source_code_string)
            string = "\n".join(result) + "\n"
            with open(fname.with_suffix(".xml"), "w") as ans:
                ans.write(string)


if __name__ == "__main__":
    jack_analyzer()
