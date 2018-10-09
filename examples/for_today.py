#!/usr/bin/python

import sys
sys.path.append('/home/dionisos/logiciels/myPyOrgMode')
from PyOrgMode import PyOrgMode
from datetime import date


def get_today_todo(file_path):
    base = PyOrgMode.OrgDataStructure()
    base.load_from_file(file_path)

    nb_task_missed = 0
    nb_task_for_today = 0

    for task in base.extract_todo_list():
        print(task)
        if hasattr(task, "scheduled") and task.scheduled and task.scheduled.should_be_done():
            if task.scheduled.should_be_done_today():
                nb_task_for_today += 1
            else:
                nb_task_missed += 1

    return (nb_task_for_today, nb_task_missed)

