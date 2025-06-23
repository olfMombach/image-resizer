import subprocess
from argparse import ArgumentParser
from itertools import repeat
from multiprocessing import Pool
from os import mkdir
from pathlib import Path
from typing import List


def process_image(image_path: Path, max_length: int, quality: int):
    output_name = Path(f"./resized/{image_path.stem}_resized{image_path.suffix}")
    command = [
        'ffmpeg',
        '-i', image_path.as_posix(),
        '-vf', f"scale='if(gt(iw,ih),{max_length},-1)':'if(gt(iw,ih),-1,{max_length})'",
        '-q:v', f'{quality}',
        output_name.as_posix()
    ]
    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Finished processing {image_path.name}")


def main():
    parser = ArgumentParser(description="Tool to batch resize images in a directory to a specific maximum width/height and with a specific quality setting using ffmpeg.")
    subparsers = parser.add_subparsers(dest="command")

    folder_parser = subparsers.add_parser("folder", help="Convert all images in a given folder. Searches for .jpg, .JPG, and .jpeg files")
    # folder_parser.add_argument("folder", type=Path, help="Folder holding images to convert")
    folder_parser.add_argument("-m", "--max-length", required=False, type=int, default=1999)
    folder_parser.add_argument("-q", "--quality", help="Quality setting for ffmpeg, influences resulting file size, higher = worse", type=int, required=False, default=1)

    image_parser = subparsers.add_parser("image", help="Convert all given image files")
    image_parser.add_argument("image", nargs="+", type=Path)
    image_parser.add_argument("-m", "--max-length", required=False, type=int, default=1999)
    image_parser.add_argument("-q", "--quality", help="Quality setting for ffmpeg, influences resulting file size, higher = worse", type=int, required=False, default=1)

    args = parser.parse_args()

    if args.command == "folder":
        # root_folder: Path = args.folder
        # print(f"Using root folder {root_folder.as_posix()}")
        root_folder = Path(".")
        images_to_process: List[Path] = []
        for extension in ("jpg", "jpeg"):
            images_to_process.extend(root_folder.glob(f"*.{extension}"))
        print(f"Ignoring {len(list(root_folder.glob('*'))) - len(images_to_process)} files")
    else:
        images_to_process: List[Path] = args.image
    
    print(f"Found {len(images_to_process)} images")

    max_val: int = args.max_length
    quality_val: int = args.quality

    print(f"Resizing images to max length {max_val} with quality {quality_val}")

    try:
        mkdir(Path("./resized"))
    except FileExistsError:
        print(f"Please remove or rename existing 'resized' folder to ensure no file loss")
        exit(1)

    # Process images multithreaded
    with Pool() as pool:
        pool.starmap(process_image, zip(images_to_process, repeat(max_val), repeat(quality_val)))
    
    print(f"Finished processing {len(images_to_process)} files.")

if __name__ == "__main__":
    main()
