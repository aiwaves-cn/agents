import os
import json
import datetime
import tempfile


def count_files_in_directory(directory):
    # Get the number of files in the specified directory
    file_count = len(
        [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    )
    return file_count


def delete_oldest_files(directory, delete_count):
    # Get a list of files in a directory, sorted by modification time
    files = [
        (f, os.path.getmtime(os.path.join(directory, f)))
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]

    # Delete the first delete_count file.
    for i in range(min(delete_count, len(files))):
        file_to_delete = os.path.join(directory, files[i][0])
        os.remove(file_to_delete)


def delete_files_if_exceed_threshold(directory, threshold):
    file_count = count_files_in_directory(directory)
    if file_count > threshold:
        delete_count = file_count - threshold
        delete_oldest_files(directory, delete_count)


def save_logs(log_path, messages, response):
    """Write each exchange to a distinct timestamped JSON log."""
    if not os.path.exists(log_path):
        os.makedirs(log_path, exist_ok=True)
    delete_files_if_exceed_threshold(log_path, 20)
    log_path = log_path if log_path else "logs"
    log = {}
    log["input"] = messages
    log["output"] = response
    os.makedirs(log_path, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-",
        suffix=".json",
        dir=log_path,
        delete=False,
    ) as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
