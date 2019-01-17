from pathlib import Path
from revealjs_converter import MarkdownRevealjsConverter
import sys
# get the dir of current python file
code_dir = Path(__file__).absolute().parent

try:
    md_fname = sys.argv[1]
except:
    print("usage: python md2slide.py [markdown filename]")
    exit()

config = dict()
config["path"] = code_dir/"config.json"

converter = MarkdownRevealjsConverter(md_fname, **config) 
converter.convert()


