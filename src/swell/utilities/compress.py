# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import gzip
import os
import shutil
import subprocess

# --------------------------------------------------------------------------------------------------


def compress_file(source_file: str,
                  algorithm: str = 'gzip',
                  level: int = 6,
                  num_threads: int = 4) -> str:

    if not os.path.isfile(source_file):
        raise FileNotFoundError(f"Source file not found: {source_file}")

    compressed_path = source_file + '.gz'

    if algorithm == 'gzip':
        _compress_gzip(source_file, compressed_path, level)
    elif algorithm == 'pigz':
        _compress_pigz(source_file, level, num_threads)

    return compressed_path


# --------------------------------------------------------------------------------------------------


def _compress_gzip(source_file: str, compressed_path: str, level: int) -> None:
    """Compress using Python stdlib gzip (single-threaded, streaming)."""

    with open(source_file, 'rb') as f_in:
        with gzip.open(compressed_path, 'wb', compresslevel=level) as f_out:
            shutil.copyfileobj(f_in, f_out)


# --------------------------------------------------------------------------------------------------


def _compress_pigz(source_file: str, level: int, num_threads: int) -> None:
    """Compress using the external ``pigz`` binary (parallel gzip).

    ``pigz -k`` keeps the original file and writes ``source_file.gz``
    alongside it — exactly the same convention as :func:`compress_file`.
    """

    pigz_bin = shutil.which('pigz')
    if pigz_bin is None:
        raise FileNotFoundError(
            "pigz binary not found on PATH. "
            "Install pigz (e.g. 'module load pigz' on NCCS Discover) "
            "or set compress_algorithm to 'gzip'."
        )

    # -k  : keep the original file (do not delete it)
    # -p  : number of threads
    # -N  : compression level (1–9)
    subprocess.run(
        [pigz_bin, f'-{level}', '-k', f'-p{num_threads}', source_file],
        check=True,
    )


# --------------------------------------------------------------------------------------------------


def decompress_file(compressed_file: str, target_file: str) -> None:
    if not os.path.isfile(compressed_file):
        raise FileNotFoundError(f"Compressed file not found: {compressed_file}")

    with gzip.open(compressed_file, 'rb') as f_in:
        with open(target_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    os.remove(compressed_file)


# --------------------------------------------------------------------------------------------------


def decompress_if_needed(file_path: str) -> str:
    if not file_path.endswith('.gz'):
        return file_path

    decompressed_path = file_path[:-3]  # strip the trailing '.gz'
    decompress_file(file_path, decompressed_path)
    return decompressed_path


# --------------------------------------------------------------------------------------------------


def compressed_extension(original_ext: str) -> str:
    return original_ext + '.gz'
