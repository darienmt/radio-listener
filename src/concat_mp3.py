import argparse
from os import listdir
from os.path import isfile, join
from pydub import AudioSegment

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", help="Directory to find the .mp3s", required=True)
    parser.add_argument("--subdir", help="Sub-directory to find the .mp3s", required=True)
    args = parser.parse_args()
    dir = args.dir
    subdir = args.subdir
    path = join(dir, subdir)
    files = [f for f in listdir(path) if isfile(join(path, f)) and f.endswith(".mp3")]
    segment = None
    counter = 0;
    for file in files:
        file_path = join(path, file)
        if segment is None:
            segment = AudioSegment.from_mp3(file=file_path)
        else:
            segment = segment + AudioSegment.from_mp3(file=file_path)
        counter += 1
    segment.export(f"{path}.mp3", format="mp3" )
    print(f"File count: {counter}, Output: {path + '.mp3'}")


if __name__ == "__main__":
    main()