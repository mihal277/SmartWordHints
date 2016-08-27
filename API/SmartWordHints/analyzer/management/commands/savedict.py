from django.core.management.base import BaseCommand, CommandError
from analyzer.utils import parse_xml
import zipfile


class Command(BaseCommand):
    help = 'Saves words and their definitions from ' \
           'http://clip.ipipan.waw.pl/Nowy_slownik_angielsko-polski ' \
           'to the database.'

    def add_arguments(self, parser):
        parser.add_argument('dict_path', nargs=1, type=str)

    def handle(self, *args, **options):
        try:
            with zipfile.ZipFile(options['dict_path'][0], 'r') as dict_zip:
                xml_file_names = (fn for fn in dict_zip.namelist() if fn.endswith('.xml'))
                for file_name in xml_file_names:
                    parse_xml(dict_zip.read(file_name))
        except:
            raise CommandError('File ' + options['dict_path'][0] + ' does not exist')
