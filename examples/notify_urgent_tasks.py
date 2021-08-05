#!/usr/bin/python2

# A notification server as "notification-daemon" should be used and started
import sys
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify
sys.path.append('/home/dionisos/logiciels/myPyOrgMode')
from PyOrgMode import PyOrgMode


def sendmessage(title, message):
    Notify.init("Test")
    notice = Notify.Notification.new(title, message)
    notice.set_timeout(300000)
    notice.set_urgency(2)
    notice.show()
    return

base = PyOrgMode.OrgDataStructure()
base.load_from_file("/home/dionisos/organisation/agenda.org")

urgent_tasks = []
for task in base.extract_todo_list():
    if (task.priority == 'A'):
        if hasattr(task, "scheduled") and task.scheduled and task.scheduled.should_be_done():
            urgent_tasks.append(task)

if len(urgent_tasks) != 0:
    message = ""
    for task in urgent_tasks:
        message += str(task) + "\n"
    sendmessage('You have some urgent tasks !!!', message)
