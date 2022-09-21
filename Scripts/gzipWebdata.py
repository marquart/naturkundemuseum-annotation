import os
import gzip
import shutil


if __name__ == "__main__":
    webAssests = "../Website/public/data/"
    with os.scandir(webAssests) as files:
        for file in files:
            if file.is_file() and file.name.endswith('.json'):
                with open(file.path, 'rb') as f_in:
                    with gzip.open(os.path.join(webAssests, f'{file.name}.gz'), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"Gzipped {file.name}")
