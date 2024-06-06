def check_null_bytes(filename):
    with open(filename, 'rb') as f:
        for line_no, line in enumerate(f, 1):
            if b'\x00' in line:
                print(f'Null byte found in file {filename} at line {line_no}')

check_null_bytes('Mainwindow_YAKE2.py')