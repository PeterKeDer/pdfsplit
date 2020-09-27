#!/bin/sh
"exec" "`dirname $0`/env/bin/python" "$0" "$@"

import os
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter

FILE_EXTENSION = '.pdf'


def main():
    # Parse arguments
    if len(sys.argv) >= 2:
        file_arg = sys.argv[1]
    else:
        print('Expect argument.')
        sys.exit(1)

    # Check whether given file exists
    if file_arg.endswith(FILE_EXTENSION) and os.path.exists(file_arg):
        document_name = file_arg[:-len(FILE_EXTENSION)]
    else:
        print(f'Argument \'{file_arg}\' not a PDF file.')
        sys.exit(1)

    # Open pdf reader
    pdf = PdfFileReader(open(file_arg, 'rb'))

    # Parse slices arguments
    if len(sys.argv) >= 3:
        slices_arg = sys.argv[2]
        slices = []

        def parse_int(s: str) -> int:
            """Utility function for parsing integers from string."""
            if s.isdigit():
                return int(s)
            else:
                print(f'Expect integer in slices, got \'{s}\'.')
                sys.exit(1)

        for slice_str in slices_arg.split(','):
            # A slice can have format either 'start-end' or 'start'
            if len(strs := slice_str.split('-')) == 2:
                start, end = [parse_int(s.strip()) for s in strs]
                slices.append((start - 1, end))
            else:
                n = parse_int(slice_str.strip())
                slices.append((n - 1, n))

        # Validate that all slices are valid
        for start, end in slices:
            if start >= end:
                print(f'Invalid slice {start + 1}-{end}, start must be smaller or equal to end.')
                sys.exit(1)
            elif end > pdf.numPages:
                print(f'Invalid slice {start + 1}-{end}, the PDF has only {pdf.numPages} pages.')
                sys.exit(1)
    else:
        # By default, split all pages
        slices = [(i, i + 1) for i in range(pdf.numPages)]

    # Create output directory if necessary
    output_dir = f'{document_name}-pages'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Write output
    for (start, end) in slices:
        output = PdfFileWriter()

        for i in range(start, end):
            output.addPage(pdf.getPage(i))

        output_pages_str = str(start + 1) if start + 1 == end else f'{start + 1}-{end}'
        output_filename = f'{document_name}_{output_pages_str}{FILE_EXTENSION}'
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, 'wb') as output_stream:
            output.write(output_stream)

    print('PDF successfully split.')


if __name__ == '__main__':
    main()
