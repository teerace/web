import os


def get_revision():
    return os.environ.get("GIT_COMMIT", "")
