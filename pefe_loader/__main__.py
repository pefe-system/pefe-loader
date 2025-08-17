import os
import time
from . import *
from .loader import AbstractLoader, SpreadFileLoader, SingleFileLoader
from .distributor import Distributor
from .error_reporter import ErrorReporter
from pefe_common.petools import is_pe_file
from typing import Type

def generate_contents():
    BENIGN = 0
    MALICIOUS = 1
    DIRECTORIES = [
        { "label": BENIGN, "path": config['self']['benign_dir'] },
        { "label": MALICIOUS, "path": config['self']['malicious_dir'] },
    ]

    for DIRECTORY in DIRECTORIES:
        for dirpath, _dirnames, filenames in os.walk(DIRECTORY["path"], followlinks=True):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if is_pe_file(file_path):
                    print("Loading PE file:", file_path)
                    yield {
                        "title": file_path,
                        "path": file_path,
                        "label": DIRECTORY["label"],
                    }
                else:
                    print("Skipping non-PE file:", file_path)

def main():
    content_generator = generate_contents()
    def next_content():
        return next(content_generator)
    
    Loader = AbstractLoader # type: Type[AbstractLoader]
    LOADER_OPTIONS = {
        "1": SingleFileLoader,
        "2": SpreadFileLoader,
    } # type: dict[str, Type[AbstractLoader]]
    options_text = ", ".join(
        (f"{option}={loader_class.__name__}" for option, loader_class in LOADER_OPTIONS.items())
    )
    while True:
        ans = input(f"Enter loader type ({options_text}, 0=display help on this): ")
        if ans == '0':
            for loader_class in LOADER_OPTIONS.values():
                print(loader_class.__name__, ":")
                print(loader_class.__doc__)
                print()
            continue
        try:
            Loader = LOADER_OPTIONS[ans]
        except KeyError:
            print("Unexpected answer. Try again.")
        else:
            break

    loader = Loader(next_content)
    error_reporter = ErrorReporter()
    distributor = Distributor(loader, error_reporter)

    distributor.start()

    try:
        input("When all clients are connected, press Enter to begin.\n")

        loader.run()
    except KeyboardInterrupt:
        pass
    finally:
        print()
        print("Stopping... ", end="", flush=True)
        loader.stop()
        distributor.stop()
        print("Done.")

if __name__ == "__main__":
    main()
