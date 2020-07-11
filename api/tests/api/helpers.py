import os
import subprocess


def cleanup():
    """
    * remove any repositories that begin with ARK_TEST_PREFIX
    """
    ark_test_archives = list_ark_test_archives()
    if len(ark_test_archives) > 0:
        subprocess.check_output(['rm', '-rf'] + ark_test_archives)


def list_ark_test_archives():
    """
    list any archives that begin with ARK_TEST_PREFIX
    """
    return [
        f"{os.getenv('ARCHIVE_FILES')}/{name}"
        for name in subprocess.check_output(['ls', f"{os.getenv('ARCHIVE_FILES')}"])
        .decode()
        .strip()
        .split()
        if name.startswith(os.getenv('ARK_TEST_PREFIX'))
    ]
