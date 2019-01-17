import os
from pathlib import Path
import json
import re
import time
import datetime
import shutil
import requests


class MarkdownConverter():

    def __init__(self, *args, **kwargs):
        self.source_md_fname = Path(args[0]).expanduser().absolute() 
        if self.source_md_fname.suffix == ".textbundle":
            #text bundle:
            markdown_suffix_list = list(self.source_md_fname.glob("*.markdown"))
            md_suffix_list = list(self.source_md_fname.glob("*.md"))
            self.source_md_fname = (markdown_suffix_list + md_suffix_list)[0]
        self.working_folder = Path(self.source_md_fname).parent
        self.code_dir = Path(__file__).absolute().parent
        config_json_fname = kwargs['path']
        with open(config_json_fname) as f:
            self.config = json.load(f)
        self.temp_md_fname = self.working_folder/"temp.md"
        with open(self.source_md_fname) as f:
            self.md_content = f.read()
        self.download_dir = self.working_folder / 'downloaded_images'

    def show_md(self, md_fname = None):
        if not(md_fname):
            md_fname = self.source_md_fname
        cmd = "open {}".format(md_fname)
        os.system(cmd)

    def update_source_md(self):
        with open(self.source_md_fname, 'w') as f:
            f.write(self.md_content)

    def get_absolute_path(self, link):
        # image helper of markdown preview plus for vscode bug:
        if str(link).startswith('/assets/'):
            link = Path(str(link)[1:])
        # convert a arbitary path to absolute ones
        link_path = Path(link).expanduser()
        if not link_path.is_absolute():
            link_path = self.working_folder / link
        return link_path

    def get_file_mtime(self, link):
        return self.get_absolute_path(link).stat().st_mtime

    def get_formated_mtime_filename(self, link):
        my_mtime = self.get_file_mtime(link)
        d = datetime.datetime.fromtimestamp(my_mtime)
        date_format = '%Y-%m-%d-%H-%M-%S-%f'
        timestr = d.strftime(date_format)
        suffix = self.get_absolute_path(link).suffix
        new_filename = f"assets/{timestr}{suffix}"
        return new_filename

    def get_formatted_current_time_filename(self):
        current_time = datetime.datetime.now()
        date_format = '%Y-%m-%d-%H-%M-%S-%f'
        timestr = current_time.strftime(date_format)
        return timestr


    def download_links(self):
        # prepare for the temp image download dir
        
        if self.download_dir.exists():
            shutil.rmtree(self.download_dir)
        self.download_dir.mkdir()
        new_links = []
        web_link_pattern = re.compile(r'(ht|f)tps?://')

        for link in self.original_image_links:
            if web_link_pattern.search(link): # is a web link
                ext_patt = r"\.(jpg|png|bmp|gif|svg|jpeg)"
                suffix = re.search(ext_patt, link, re.MULTILINE | re.IGNORECASE).group(1)
                download_image_filename = f"{self.get_formatted_current_time_filename()}.{suffix}"
                r = requests.get(link, stream=True)
                new_link = self.download_dir/download_image_filename
                with open(new_link, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                new_links.append(new_link)
            else:
                new_links.append(link)

        self.generated_links = new_links
        self.replace_links()
        self.original_image_links = self.generated_links

    def clean_up_download_images(self):
        # remove the temp image download dir
        if self.download_dir.exists():
            shutil.rmtree(self.download_dir)
                

    def get_image_links(self, md_content):
        return re.findall(r'\!\[.*\]\((.*)\)', md_content)

    def generate_links(self):
        self.generated_links = []
        for link in self.original_image_links:
            new_link = self.get_formated_mtime_filename(link)
            self.generated_links.append(new_link)

    def copy_image_files(self):
        for link, new_link in zip(self.original_image_links, self.generated_links):
             if link != new_link:
                # need to move
                source = self.get_absolute_path(link)
                target = self.get_absolute_path(new_link)
                shutil.copy2(source, target)


    def replace_links(self):
        content = self.md_content
        for link, new_link in zip(self.original_image_links, self.generated_links):
            content = content.replace(str(link), str(new_link))
        self.md_content = content

    def generate_temp_md(self):
        with open(self.temp_md_fname, 'w') as f:
            f.write(self.md_content)
        self.show_md(self.temp_md_fname)
        

    def convert(self):
               
        self.original_image_links = self.get_image_links(self.md_content)
        self.download_links()
        self.generate_links()
        self.replace_links()
        self.copy_image_files()
        self.clean_up_download_images()