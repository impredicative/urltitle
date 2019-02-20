"""Get PDF title using pikepdf in a separate process.

pikepdf==1.0.5 is not thread safe. Refer to https://github.com/pikepdf/pikepdf/issues/27
"""

from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

import pikepdf


def _get_pdf_title(pdf_bytes: bytes) -> str:
    return str(pikepdf.open(BytesIO(pdf_bytes)).docinfo.get('/Title', '')).strip()


def get_pdf_title(pdf_bytes: bytes) -> str:
    with ProcessPoolExecutor(max_workers=1) as executor:
        return next(executor.map(_get_pdf_title, [pdf_bytes]))
