import os

COURSE_NAME = "Full Cycle 3.0 - School of Net"
ROOT_PATH = os.path.expanduser(f"~/Documents/Library/{COURSE_NAME}")
DESTINATION_PATH = os.path.expanduser("~/Documents/Media/Courses/")
RED_COLOR = "\033[1;31m"
GREEN_COLOR = "\033[1;32m"
END_COLOR = "\033[m"


def custom_sort_key(item):
    parts = item.split(".")  # split on the dot
    return (
        int(parts[0]) if parts[0].isdigit() else float("inf"),
        item,
    )  # sort by the first part as an int, or inf if not an int


def create_directory(directory):
    if not os.path.exists(directory):
        print(f"Creating directory: {directory}")
        os.mkdir(directory)


def create_symlink(src, dest):
    if not os.path.exists(dest):
        print(f"Creating symlink: {src} -> {dest}")
        os.symlink(src, dest)


def has_video_files_in_directory(dir_path: str) -> bool:
    """Checks if the directory contains any video files with extensions .mp4, .mkv, .mov, etc."""

    # List of common video file extensions
    video_extensions = [".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv"]

    for _, _, filenames in os.walk(dir_path):
        if any(
            filename.endswith(extension)
            for filename in filenames
            for extension in video_extensions
        ):
            return True
    return False


def process_deepest_directory(
    directory_path: str,
    items: list,
    dry_run: bool,
    indent: str,
    season_number: int,
    episode_counter: int,
) -> int:
    """Handles the logic for the deepest directory."""
    directory_name = f"Season {season_number} - {directory_path.split('/')[-1]}"

    if not dry_run:
        create_directory(os.path.join(DESTINATION_PATH, directory_name))

    print(
        f"{indent}{RED_COLOR}{directory_path.split('/')[-1]}{END_COLOR} -> {GREEN_COLOR}{directory_name}{END_COLOR}"
    )

    index = episode_counter - 1  # Initialize index

    for index, item in enumerate(
        (i for i in items if i.endswith(".mp4")), start=episode_counter
    ):
        symlink_name = f"S{season_number:02d}E{index:02d} - {item}"
        symlink_path = os.path.join(DESTINATION_PATH, directory_name, symlink_name)

        if not dry_run:
            create_symlink(os.path.join(directory_path, item), symlink_path)

        print(f"{indent}\t{item} -> {symlink_name}")

    return index


def sym_link_generator(
    directory_path: str,
    indent: str = "",
    is_deepest: bool = False,
    dry_run: bool = True,
    season_number: int = 1,
    episode_counter: int = 1,
) -> (int, int):
    # Fetches all the items in the given directory path and sorts them
    items = sorted(os.listdir(directory_path), key=custom_sort_key)

    # Check if the current directory is the deepest by seeing if it contains no other subdirectories
    is_deepest = not any(
        os.path.isdir(os.path.join(directory_path, subitem)) for subitem in items
    )

    # Base case: When the directory being processed is the deepest (contains media files, and no subdirectories)
    if is_deepest:
        # Processes the files in the directory (e.g., creating symlinks)
        episode_counter = process_deepest_directory(
            directory_path, items, dry_run, indent, season_number, episode_counter
        )
        # Increment the season number once the deepest directory has been processed
        season_number += 1

    # Iterate over items in the current directory
    for item in items:
        full_path = os.path.join(directory_path, item)

        # Checks if the current item is a directory
        if os.path.isdir(full_path):
            # If the directory does not contain .mp4 files, then skip it
            if not has_video_files_in_directory(full_path):
                continue

            # Check if the current subdirectory is the deepest by seeing if it contains no other subdirectories
            is_deepest_subdirectory = not any(
                os.path.isdir(os.path.join(full_path, subitem))
                for subitem in os.listdir(full_path)
            )

            # Recursive call: If the item is a directory, then delve deeper
            episode_counter, season_number = sym_link_generator(
                full_path,
                indent + "\t",
                is_deepest_subdirectory,
                dry_run,
                season_number,
                episode_counter,
            )

    # Return the updated episode counter and season number
    return episode_counter, season_number


def main(dry_run=True):
    global DESTINATION_PATH  # Indicate that you're using the global variable
    file_tree = natsorted(os.listdir(ROOT_PATH), key=custom_sort_key)
    if not dry_run:
        create_directory(os.path.join(DESTINATION_PATH, COURSE_NAME))
        DESTINATION_PATH = os.path.join(DESTINATION_PATH, COURSE_NAME)

    season_counter = 1
    for directory in file_tree:
        _, season_counter = sym_link_generator(
            os.path.join(ROOT_PATH, directory),
            dry_run=dry_run,
            season_number=season_counter,
        )


if __name__ == "__main__":
    main(dry_run=False)
