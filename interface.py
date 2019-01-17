from pathlib import Path
import sys
# get the dir of current python file
code_dir = Path(__file__).absolute().parent

try:
    md_fname = sys.argv[1]
    convert_type = sys.argv[2]
except:
    print("usage: python interface.py [markdown filename] [convert type]")
    exit()

config = dict()
config["path"] = code_dir/"config.json"

if convert_type == "local":
    from converter import MarkdownConverter
    converter = MarkdownConverter(md_fname, **config)
    converter.convert()
    converter.generate_temp_md()
elif convert_type == "revealjs":
    from revealjs_converter import MarkdownRevealjsConverter
    converter = MarkdownRevealjsConverter(md_fname, **config) 
    converter.convert()
else:
    print("type error")
    exit()

