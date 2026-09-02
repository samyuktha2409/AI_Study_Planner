from datetime import datetime


def calculate_task_priority(task, current_date):
    """
    Calculate the urgency and importance of a task.
    Higher score = more important.
    """

    deadline = datetime.strptime(
        task["deadline"], "%Y-%m-%d"
    ).date()

    today = datetime.strptime(
        current_date, "%Y-%m-%d"
    ).date()

    days_left = (deadline - today).days

    # Deadline score
    if days_left <= 0:
        deadline_score = 100
    elif days_left == 1:
        deadline_score = 90
    elif days_left <= 3:
        deadline_score = 75
    elif days_left <= 7:
        deadline_score = 50
    else:
        deadline_score = 25

    # Priority and difficulty
    priority_score = int(task["priority"]) * 10
    difficulty_score = int(task["difficulty"]) * 5

    score = (
        deadline_score
        + priority_score
        + difficulty_score
    )

    return score


def calculate_schedule_score(schedule, current_date):
    """
    Evaluate the quality of the complete schedule.

    Returns a score between 0 and 100.
    """

    if not schedule:
        return 0

    total_score = 0
    task_count = 0

    for position, task in enumerate(schedule):

        # Ignore breaks
        if task.get("type") == "Break":
            continue

        task_score = calculate_task_priority(
            task,
            current_date
        )

        # Earlier positions get a small advantage
        position_penalty = position * 2

        final_task_score = max(
            task_score - position_penalty,
            0
        )

        total_score += final_task_score
        task_count += 1

    if task_count == 0:
        return 0

    # Normalize to 100
    maximum_possible = task_count * 175

    score = (
        total_score / maximum_possible
    ) * 100

    return round(
        min(score, 100),
        2
    )