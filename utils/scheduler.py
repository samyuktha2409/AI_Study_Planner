import pandas as pd


def time_to_minutes(time_string):
    hours, minutes = map(int, time_string.split(":"))
    return hours * 60 + minutes


def minutes_to_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def get_free_slots(
    timetable,
    day,
    start_time="16:00",
    end_time="22:00"
):
    day_classes = timetable[
        timetable["day"].str.lower() == day.lower()
    ]

    start = time_to_minutes(start_time)
    end = time_to_minutes(end_time)

    busy_slots = []

    for _, row in day_classes.iterrows():

        if row["subject"].upper() == "FREE":
            continue

        class_start = time_to_minutes(row["start_time"])
        class_end = time_to_minutes(row["end_time"])

        # Only consider classes inside the requested period
        if class_end > start and class_start < end:
            busy_slots.append(
                (
                    max(class_start, start),
                    min(class_end, end)
                )
            )

    busy_slots.sort()

    free_slots = []
    current = start

    for busy_start, busy_end in busy_slots:

        if current < busy_start:
            free_slots.append(
                (current, busy_start)
            )

        current = max(current, busy_end)

    if current < end:
        free_slots.append(
            (current, end)
        )

    return free_slots


def create_daily_schedule(tasks, free_slots):

    schedule = []

    # Keep the order produced by Hill Climbing
    tasks = tasks.copy()

    # Store remaining time for every task
    remaining_tasks = []

    for task in tasks:
        remaining_tasks.append({
            "task": task["task"],
            "subject": task["subject"],
            "type": task["type"],
            "remaining": int(float(task["hours"]) * 60)
        })

    task_index = 0

    for slot_start, slot_end in free_slots:

        current_time = slot_start

        while (
            task_index < len(remaining_tasks)
            and current_time < slot_end
        ):

            task = remaining_tasks[task_index]

            available = slot_end - current_time

            # Maximum continuous study = 90 minutes
            study_time = min(
                task["remaining"],
                available,
                90
            )

            # Add study session
            schedule.append({
                "start": minutes_to_time(current_time),
                "end": minutes_to_time(
                    current_time + study_time
                ),
                "task": task["task"],
                "subject": task["subject"],
                "type": task["type"]
            })

            # Reduce remaining task time
            task["remaining"] -= study_time

            current_time += study_time

            # Task completed
            if task["remaining"] <= 0:

                task_index += 1

            # Add break
            if (
                task_index < len(remaining_tasks)
                and remaining_tasks[task_index]["remaining"] > 0
                and current_time + 15 < slot_end
            ):

                schedule.append({
                    "start": minutes_to_time(
                        current_time
                    ),
                    "end": minutes_to_time(
                        current_time + 15
                    ),
                    "task": "Break",
                    "subject": "-",
                    "type": "Break"
                })

                current_time += 15

    return schedule
