import click
import tokenizer
from pathlib import Path

@click.group()
def jack_analyzer():
    pass

def get_jack_files(path):
    return 

@jack_analyzer.command()
@click.argument('path', type=click.Path(exists=True))
def tokenize(path):
    '''Command on jack_analyzer'''
    path = Path(path)
    if path.is_dir():
        filenames = [d for d in path.iterdir() if d.suffix == '.jack']
    else:
        filenames = [path]
    for fname in filenames:
        with open(fname) as stream:
            string = stream.read()
            result = tokenizer.tokenize(string)
            result_fname = fname.with_suffix('.xml')
            with open(result_fname, 'w') as f:
                f.write(result)

@jack_analyzer.command()
def parse():
    '''Command on jack_analyzer'''
    click.echo('calling parse')

if __name__ == '__main__':
    jack_analyzer()
