#!/usr/bin/env python

# A notification server as "notification-daemon" should be used and started
import sys
import os
import argparse
from datetime import datetime, timedelta
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify
sys.path.append('/home/dionisos/logiciels/myPyOrgMode')
from PyOrgMode import PyOrgMode

MAX_MUTE_MINUTES = 600  # 10 hours maximum


def get_mute_file_path():
    """Return the path to the mute file."""
    return '/tmp/notify_urgent_tasks_muted_until'


def set_mute(minutes):
    """Mute notifications for the specified number of minutes.

    Duration is capped at MAX_MUTE_MINUTES (600 = 10 hours).
    If minutes <= 0, effectively unmutes.
    """
    if minutes <= 0:
        # Remove mute file if it exists
        mute_file = get_mute_file_path()
        if os.path.exists(mute_file):
            os.remove(mute_file)
        return

    # Cap at maximum
    minutes = min(minutes, MAX_MUTE_MINUTES)

    unmute_time = datetime.now() + timedelta(minutes=minutes)
    with open(get_mute_file_path(), 'w') as f:
        f.write(str(unmute_time.timestamp()))


def is_muted():
    """Check if notifications are currently muted."""
    mute_file = get_mute_file_path()
    if not os.path.exists(mute_file):
        return False

    try:
        with open(mute_file, 'r') as f:
            unmute_timestamp = float(f.read().strip())
        return datetime.now().timestamp() < unmute_timestamp
    except (ValueError, IOError):
        return False


def get_remaining_mute_time():
    """Return the remaining mute time in minutes, or 0 if not muted."""
    mute_file = get_mute_file_path()
    if not os.path.exists(mute_file):
        return 0

    try:
        with open(mute_file, 'r') as f:
            unmute_timestamp = float(f.read().strip())
        remaining_seconds = unmute_timestamp - datetime.now().timestamp()
        if remaining_seconds <= 0:
            return 0
        return remaining_seconds / 60
    except (ValueError, IOError):
        return 0


def sendmessage(title, message):
    Notify.init("Test")
    notice = Notify.Notification.new(title, message)
    notice.set_timeout(300000)
    notice.set_urgency(2)
    notice.show()
    return


def main():
    parser = argparse.ArgumentParser(description='Notify urgent tasks from org-mode')
    parser.add_argument('--mute', type=int, metavar='MINUTES',
                        help=f'Mute notifications for MINUTES (max {MAX_MUTE_MINUTES} = 10h)')
    parser.add_argument('--status', action='store_true',
                        help='Show remaining mute time')
    args = parser.parse_args()

    if args.status:
        remaining = get_remaining_mute_time()
        if remaining > 0:
            hours = int(remaining // 60)
            minutes = int(remaining % 60)
            if hours > 0:
                print(f"Notifications muted for {hours}h {minutes}min")
            else:
                print(f"Notifications muted for {minutes}min")
        else:
            print("Notifications are active")
        return

    if args.mute is not None:
        set_mute(args.mute)
        if args.mute > 0:
            actual_minutes = min(args.mute, MAX_MUTE_MINUTES)
            print(f"Notifications muted for {actual_minutes} minutes")
        else:
            print("Notifications unmuted")
        return

    if is_muted():
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


if __name__ == '__main__':
    main()
