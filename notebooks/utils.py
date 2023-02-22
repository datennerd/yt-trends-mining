"""Serveral helper functions for eda.ipynb."""

# Import libraries
import os

from emoji import EMOJI_DATA
from google.cloud import storage
from tqdm import tqdm

# Dictionary to map category id to category name
category_dict = {
    1: "Film & Animation",
    2: "Autos & Vehicles",
    10: "Music",
    15: "Pets & Animals",
    17: "Sports",
    18: "Short Movies",
    19: "Travel & Events",
    20: "Gaming",
    21: "Videoblogging",
    22: "People & Blogs",
    23: "Comedy",
    24: "Entertainment",
    25: "News & Politics",
    26: "Howto & Style",
    27: "Education",
    28: "Science & Technology",
    29: "Nonprofits & Activism",
    30: "Movies",
    31: "Anime/Animation",
    32: "Action/Adventure",
    33: "Classics",
    34: "Comedy",
    35: "Documentary",
    36: "Drama",
    37: "Family",
    38: "Foreign",
    39: "Horror",
    40: "Sci-Fi/Fantasy",
    41: "Thriller",
    42: "Shorts",
    43: "Shows",
    44: "Trailers",
}


def list_blobs(bucket_name: str) -> list[str]:
    """Lists all the blobs in the bucket.

    Args:
        bucket_name: ID of the GCS bucket
    """
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)
    return [blob.name for blob in blobs]


def list_blobs_with_prefix(bucket_name: str, prefix: str, delimiter=None) -> list[str]:
    """Lists all the blobs in the bucket that begin with the prefix.

    Args:
        bucket_name: ID of the GCS bucket
        prefix: This can be used to list all blobs in a "folder", e.g. "public/".
        delimiter: Can be used to restrict the results to only the "files" in the given "folder".
            Without the delimiter, the entire tree under the prefix is returned.
            For example, given these blobs:

                a/1.txt
                a/b/2.txt

            If you specify prefix ='a/', without a delimiter, you'll get back:

                a/1.txt
                a/b/2.txt

            However, if you specify prefix='a/' and delimiter='/', you'll get back
            only the file directly under 'a/':

                a/1.txt

            As part of the response, you'll also get back a blobs.prefixes entity
            that lists the "subfolders" under `a/`:

                a/b/

    Returns:
        List of GCS objects
    """
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter)
    return [blob.name for blob in blobs]


def download_blob(
    bucket_name: str, source_blob_name: str, destination_file_name: str
) -> None:
    """Downloads a blob from the GCS bucket.

    Args:
        bucket_name: ID of the GCS bucket
        source_blob_name: ID of the GCS object
        destination_file_name: The path to which the file should be downloaded
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


def filter_list(list: list[str], pattern: str) -> list[str]:
    """Returns only strings of a list that match a pattern.

    Args:
        list: List of strings
        pattern: Pattern to match
    """
    return [x for x in list if pattern in x]


def list_csvs(path: str) -> list[str]:
    """Lists all the csvs in a folder.

    Args:
        path: Path to the data folder
    """
    return [file for file in os.listdir(path) if file.endswith(".csv")]


def check_downloaded(
    blobs: list[str], csvs: list[str], blobs_prefix: str = "data/"
) -> list[str]:
    """Checks which csvs are not already downloaded.

    Args:
        blobs: List of GCS objects
        csvs: List of csvs
        blobs_prefix: Prefix to remove from the blobs
    """
    return [blob for blob in blobs if blob.replace(blobs_prefix, "") not in csvs]


def get_data_from_gcs(region_code: str) -> None:
    """Downloads YouTube trend data from GCS.

    Args:
        region_code: Region code to filter the blobs
    """
    # Check if region code is valid
    if region_code not in ["US", "BR", "RU", "JP", "IN", "GB", "DE", "FR", "CA", "AU"]:
        raise ValueError("Region code not valid")

    # Create data & region folder if it doesn't exist
    if not os.path.exists("../data"):
        os.mkdir("../data")

    if not os.path.exists(f"../data/{region_code}"):
        os.mkdir(f"../data/{region_code}")

    # List all available blobs in a GCS bucket
    blobs = list_blobs_with_prefix("yt-trends-mining", "data")

    # Filter blobs which match the region code
    regional_blobs = filter_list(blobs, region_code)

    # List all downloaded csvs in the data folder
    csvs_downloaded = list_csvs(f"../data/{region_code}")

    # Check if there are any csvs downloaded
    if csvs_downloaded:

        # Checks which csvs are not already downloaded
        blobs_to_download = check_downloaded(regional_blobs, csvs_downloaded)

        if blobs_to_download:
            print(f"Found {len(blobs_to_download)} new blobs. Start downloading...")
            for blob in tqdm(blobs_to_download):
                destination_file_name = f"../data/{region_code}/{blob.split('/')[1]}"
                download_blob("yt-trends-mining", blob, destination_file_name)
        else:
            print("All blobs already downloaded.")

    else:
        print(
            f"No csvs downloaded yet. Start downloading {len(regional_blobs)} blobs..."
        )
        for blob in tqdm(regional_blobs):
            destination_file_name = f"../data/{region_code}/{blob.split('/')[1]}"
            download_blob("yt-trends-mining", blob, destination_file_name)


def print_size(path: str) -> None:
    """Prints the size of all csvs in a folder.

    Args:
        path: Path to the data folder
    """
    size = (
        sum(
            os.path.getsize(path + file)
            for file in os.listdir(path)
            if file.endswith(".csv")
        )
        / 1e6
    )
    print(f"Size of all csvs in {path}: {size} MB")


def get_seconds(duration: str) -> int | None:
    """Get seconds from the "duration" column.

    Args:
        duration (str): Duration in the format "PT1H2M3S" will return 3723 seconds.
    """
    try:
        time = (
            duration.replace("PT", "")
            .replace("H", ":")
            .replace("M", ":")
            .replace("S", "")
        )
        time_list = time.split(":")
        hours = int(time_list[0]) * 3600 if len(time_list) == 3 else 0
        minutes = int(time_list[-2]) * 60 if len(time_list) >= 2 else 0
        seconds = int(time_list[-1]) if len(time_list[-1]) >= 1 else 0
        return hours + minutes + seconds
    except Exception:
        return None


def extract_emojis(s: str) -> str:
    """Extract emojis from a string."""
    return "".join(c for c in s if c in EMOJI_DATA)
