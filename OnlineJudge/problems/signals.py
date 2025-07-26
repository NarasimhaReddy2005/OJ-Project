import os
import zipfile
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TestCaseBundle
from django.conf import settings

import zipfile
import os
from django.core.exceptions import ValidationError

def validate_testcase_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = [f for f in zip_ref.namelist() if not f.endswith('/')]

        # Detect root prefix (like powerProblemTestcases/)
        common_prefix = os.path.commonprefix(file_list)
        if '/' in common_prefix:
            root_folder = common_prefix.split('/')[0]
        else:
            root_folder = ""

        # Normalize file paths to ignore root folder
        normalized_files = [
            '/'.join(f.split('/')[1:]) if f.startswith(root_folder + '/') else f
            for f in file_list
        ]

        inputs = set()
        outputs = set()

        for file in normalized_files:
            if not (file.startswith("input/") or file.startswith("output/")):
                raise ValidationError("All files must be inside 'input/' or 'output/' folders.")
            if not file.endswith(".txt"):
                raise ValidationError("Only .txt files allowed in input/output folders.")

            basename = os.path.basename(file)
            if file.startswith("input/"):
                inputs.add(basename)
            elif file.startswith("output/"):
                outputs.add(basename)

        if inputs != outputs:
            missing_inputs = outputs - inputs
            missing_outputs = inputs - outputs
            raise ValidationError(
                f"Mismatched test cases:\n"
                f"{'Missing input(s): ' + ', '.join(missing_inputs) if missing_inputs else ''} "
                f"{'Missing output(s): ' + ', '.join(missing_outputs) if missing_outputs else ''}"
            )

def extract_zip_to_dir(zip_path, dest_dir):
    validate_testcase_zip(zip_path)
    os.makedirs(dest_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = [f for f in zip_ref.namelist() if not f.endswith('/')]

        # Detect and remove top-level folder if exists
        common_prefix = os.path.commonprefix(file_list)
        if '/' in common_prefix:
            root_folder = common_prefix.split('/')[0]
        else:
            root_folder = ""

        for member in file_list:
            # Remove top-level folder
            relative_path = '/'.join(member.split('/')[1:]) if root_folder else member
            target_path = os.path.join(dest_dir, relative_path)

            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'wb') as f:
                f.write(zip_ref.read(member))


@receiver(post_save, sender=TestCaseBundle)
def auto_extract_zip(sender, instance, **kwargs):
    if instance.zip_file:
        extract_path = instance.get_full_path()
        extract_zip_to_dir(instance.zip_file.path, extract_path)
