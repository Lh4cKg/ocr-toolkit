import os
import pathlib
import logging
import typing as typ
from PIL import Image
from tesserocr import PyTessBaseAPI, image_to_text

from .conf import settings
from .convert import PdfToImages


logger = logging.getLogger(__name__)


class GeolangOcr(object):
    SUPPORTED_LANGUAGES = ('Georgian', 'kat', 'kat_old')

    def __init__(self, lang: str = 'Georgian', save: bool = False,
                 check_convert_pdf: bool = False,
                 del_converted_images: bool = False,
                 del_converted_texts: bool = False) -> None:
        """

        :param lang:
        :type lang: str
        :param save:
        :type save: bool
        :param check_convert_pdf:
        :type check_convert_pdf: bool
        :param del_converted_images:
        :type del_converted_images: bool
        :param del_converted_texts:
        :type del_converted_texts: bool
        """
        if lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f'`{lang}` is not supported. '
                f'Available languages are: {", ".join(self.SUPPORTED_LANGUAGES)}'
            )
        self.lang = lang
        self.check_convert_pdf = check_convert_pdf
        self.save = save
        self.del_converted_images = del_converted_images
        self.del_converted_texts = del_converted_texts

    @staticmethod
    def convert_pdf2images() -> None:
        pdf = PdfToImages(thread_count=os.cpu_count())
        pdf.run()

    def run(self) -> None:
        if self.check_convert_pdf:
            self.convert_pdf2images()

        for image in settings.OUTPUT_DIR.iterdir():
            logger.info(f'`{image.name}` is Processing...')
            self.process_image(image)

    def process_image(self, image) -> str:
        file_name = image.name.rsplit('.', 1)[0]
        image = Image.open(image)
        text = image_to_text(image, lang=self.lang)
        if self.save:
            self.save_file(file_name, text)
        return text

    @staticmethod
    def save_file(file_name: str, text: str) -> None:
        output_dir: pathlib.Path = settings.INPUT_DIR / 'texts'
        if output_dir.exists() is False:
            output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / f'{file_name}.txt', 'w') as f:
            f.write(text)

    def stop(self) -> None:
        # TODO
        pass