import os
import json
import random
import string
from six.moves import xrange

from django.conf import settings
from django.utils import timezone

# from projects.models import Project


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in xrange(size))


# def generate_json_file(project_id):
#     project = Project.objects.get(id=project_id)
#     project_type = project.project_type
#     if project_type == 'TextClassification':
#         model = 'tasks.textclassification'
#     elif project_type == 'ImageClassification':
#         model = 'tasks.imageclassification'
#
#     path = os.path.join(os.path.dirname(settings.BASE_DIR), 'media_root', str(project_id))
#     file_name_list = os.listdir(path)
#     tasks = []
#
#     for file_name in file_name_list:
#         temp_dict = dict()
#         temp_dict['model'] = model
#         temp_dict['fields'] = dict()
#         temp_dict['fields']['project'] = project_id
#         if project_type == 'TextClassification':
#             temp_dict['fields']['text_file'] = '{project_id}/{file_name}'.format(
#                 project_id=project_id,
#                 file_name=file_name,
#             )
#         elif project_type == 'ImageClassification':
#             temp_dict['fields']['image_file'] = '{project_id}/{file_name}'.format(
#                 project_id=project_id,
#                 file_name=file_name,
#             )
#         temp_dict['fields']['updated'] = str(timezone.now())
#         temp_dict['fields']['timestamp'] = str(timezone.now())
#         tasks.append(temp_dict)
#
#     with open(os.path.join(settings.BASE_DIR, 'tasks', 'fixtures', 'tasks.json'), 'w') as file:
#         json.dump(tasks, file)
#
#     return tasks
