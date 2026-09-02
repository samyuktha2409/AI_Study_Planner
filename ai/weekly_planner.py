import random
from datetime import datetime, timedelta


# ============================================================
# TIME UTILITIES
# ============================================================

def time_to_minutes(time_string):
    hours, minutes = map(
        int,
        time_string.split(":")
    )

    return hours * 60 + minutes


def minutes_to_time(minutes):
    hours = minutes // 60
    mins = minutes % 60

    return f"{hours:02d}:{mins:02d}"


# ============================================================
# WEEK DATES
# ============================================================

def get_week_dates(start_date):

    start = datetime.strptime(
        start_date,
        "%Y-%m-%d"
    ).date()

    monday = start - timedelta(
        days=start.weekday()
    )

    return [
        monday + timedelta(days=i)
        for i in range(5)
    ]


# ============================================================
# TASK HEURISTIC
# ============================================================

def calculate_task_score(
    task,
    current_date
):

    try:

        deadline = datetime.strptime(
            str(task["deadline"]),
            "%Y-%m-%d"
        ).date()

        today = datetime.strptime(
            current_date,
            "%Y-%m-%d"
        ).date()

        days_left = (
            deadline - today
        ).days

    except Exception:

        days_left = 14


    # --------------------------------------------------------
    # DEADLINE URGENCY
    # --------------------------------------------------------

    if days_left < 0:
        urgency = 100

    elif days_left == 0:
        urgency = 100

    elif days_left == 1:
        urgency = 95

    elif days_left <= 3:
        urgency = 85

    elif days_left <= 7:
        urgency = 70

    elif days_left <= 14:
        urgency = 50

    elif days_left <= 30:
        urgency = 30

    else:
        urgency = 15


    # --------------------------------------------------------
    # PRIORITY
    # --------------------------------------------------------

    try:
        priority = float(
            task.get("priority", 5)
        )
    except Exception:
        priority = 5

    priority = max(
        1,
        min(10, priority)
    )

    priority_score = (
        priority / 10
    ) * 100


    # --------------------------------------------------------
    # DIFFICULTY
    # --------------------------------------------------------

    try:
        difficulty = float(
            task.get("difficulty", 5)
        )
    except Exception:
        difficulty = 5

    difficulty = max(
        1,
        min(10, difficulty)
    )

    difficulty_score = (
        difficulty / 10
    ) * 100


    # --------------------------------------------------------
    # REQUIRED HOURS
    # --------------------------------------------------------

    try:
        hours = float(
            task.get("hours", 1)
        )
    except Exception:
        hours = 1

    hours = max(
        0.5,
        min(20, hours)
    )

    work_score = min(
        hours * 10,
        100
    )


    # --------------------------------------------------------
    # TASK TYPE
    # --------------------------------------------------------

    task_type = str(
        task.get("type", "Homework")
    ).lower()


    if "exam" in task_type:

        type_score = 100

    elif "assessment" in task_type:

        type_score = 90

    elif "project" in task_type:

        type_score = 80

    elif "assignment" in task_type:

        type_score = 70

    elif "lab" in task_type:

        type_score = 65

    elif "homework" in task_type:

        type_score = 55

    else:

        type_score = 50


    # ========================================================
    # FINAL HEURISTIC
    # ========================================================

    score = (

        urgency * 0.30

        + priority_score * 0.25

        + difficulty_score * 0.15

        + work_score * 0.15

        + type_score * 0.15
    )


    return round(
        max(
            0,
            min(100, score)
        ),
        2
    )


# ============================================================
# FREE TIME
# ============================================================

def get_daily_free_time(
    timetable,
    day,
    start_time="16:30",
    end_time="22:00"
):

    day_data = timetable[
        timetable["day"].str.lower()
        == day.lower()
    ]

    start = time_to_minutes(
        start_time
    )

    end = time_to_minutes(
        end_time
    )

    busy = []


    for _, row in day_data.iterrows():

        subject = str(
            row["subject"]
        ).strip().upper()


        if subject == "FREE":

            continue


        class_start = time_to_minutes(
            row["start_time"]
        )

        class_end = time_to_minutes(
            row["end_time"]
        )


        if (
            class_start < end
            and class_end > start
        ):

            busy.append(
                (
                    max(
                        class_start,
                        start
                    ),
                    min(
                        class_end,
                        end
                    )
                )
            )


    busy.sort()

    free_slots = []

    current = start


    for busy_start, busy_end in busy:

        if current < busy_start:

            free_slots.append(
                (
                    current,
                    busy_start
                )
            )

        current = max(
            current,
            busy_end
        )


    if current < end:

        free_slots.append(
            (
                current,
                end
            )
        )


    return free_slots


# ============================================================
# INITIAL SOLUTION
# ============================================================

def create_initial_solution(
    tasks,
    timetable,
    start_date
):

    week_dates = get_week_dates(
        start_date
    )


    scored_tasks = []


    for task in tasks:

        task_copy = task.copy()


        task_copy[
            "heuristic_score"
        ] = calculate_task_score(
            task_copy,
            start_date
        )


        scored_tasks.append(
            task_copy
        )


    # Highest heuristic first

    scored_tasks.sort(
        key=lambda x:
            x["heuristic_score"],
        reverse=True
    )


    solution = []

    task_index = 0


    for current_date in week_dates:

        if task_index >= len(
            scored_tasks
        ):

            break


        day_name = current_date.strftime(
            "%A"
        )


        free_slots = get_daily_free_time(
            timetable,
            day_name
        )


        for slot_start, slot_end in free_slots:

            current_time = slot_start


            while (
                task_index < len(scored_tasks)
                and current_time < slot_end
            ):

                task = scored_tasks[
                    task_index
                ]


                required_minutes = int(
                    float(
                        task["hours"]
                    ) * 60
                )


                available = (
                    slot_end
                    - current_time
                )


                # Maximum single study session = 90 minutes

                study_time = min(
                    required_minutes,
                    available,
                    90
                )


                if study_time <= 0:

                    break


                # ------------------------------------------------
                # STUDY SESSION
                # ------------------------------------------------

                solution.append({

                    "date":
                        current_date.strftime(
                            "%Y-%m-%d"
                        ),

                    "day":
                        day_name,

                    "start":
                        minutes_to_time(
                            current_time
                        ),

                    "end":
                        minutes_to_time(
                            current_time
                            + study_time
                        ),

                    "task":
                        task["task"],

                    "subject":
                        task["subject"],

                    "type":
                        task["type"],

                    "heuristic_score":
                        task[
                            "heuristic_score"
                        ]

                })


                task["hours"] = (

                    float(
                        task["hours"]
                    )

                    - study_time / 60

                )


                current_time += study_time


                # ------------------------------------------------
                # BREAK
                # ------------------------------------------------

                if current_time < slot_end:

                    break_end = min(
                        current_time + 15,
                        slot_end
                    )


                    solution.append({

                        "date":
                            current_date.strftime(
                                "%Y-%m-%d"
                            ),

                        "day":
                            day_name,

                        "start":
                            minutes_to_time(
                                current_time
                            ),

                        "end":
                            minutes_to_time(
                                break_end
                            ),

                        "task":
                            "Break",

                        "subject":
                            "-",

                        "type":
                            "Break",

                        "heuristic_score":
                            0

                    })


                    current_time = break_end


                # ------------------------------------------------
                # TASK COMPLETED
                # ------------------------------------------------

                if task["hours"] <= 0:

                    task_index += 1

                else:

                    break


    return solution


# ============================================================
# NORMALIZED WEEKLY SCORE
# ============================================================

def calculate_solution_score(
    solution
):

    if not solution:

        return 0.0


    study_items = [

        item

        for item in solution

        if item.get("type") != "Break"

    ]


    if not study_items:

        return 0.0


    # ========================================================
    # 1. TASK QUALITY
    # ========================================================

    task_scores = [

        float(
            item.get(
                "heuristic_score",
                0
            )
        )

        for item in study_items

    ]


    average_task_score = (

        sum(task_scores)
        / len(task_scores)

    )


    # ========================================================
    # 2. DEADLINE / PRIORITY QUALITY
    # ========================================================

    # Since tasks are initially arranged according
    # to heuristic score, this measures how well
    # important work is represented in the plan.

    task_quality = (
        average_task_score
    )


    # ========================================================
    # 3. STUDY TIME UTILIZATION
    # ========================================================

    total_minutes = 0


    for item in study_items:

        start = time_to_minutes(
            item["start"]
        )

        end = time_to_minutes(
            item["end"]
        )

        total_minutes += (
            end - start
        )


    # Reasonable weekly study target:
    # 20 hours = 1200 minutes.

    utilization_score = min(
        100,
        (
            total_minutes / 1200
        ) * 100
    )


    # ========================================================
    # 4. WORKLOAD BALANCE
    # ========================================================

    daily_minutes = {}


    for item in study_items:

        day = item["day"]


        start = time_to_minutes(
            item["start"]
        )

        end = time_to_minutes(
            item["end"]
        )


        duration = end - start


        daily_minutes[day] = (

            daily_minutes.get(
                day,
                0
            )

            + duration

        )


    if len(daily_minutes) > 1:

        values = list(
            daily_minutes.values()
        )


        average = (
            sum(values)
            / len(values)
        )


        deviation = sum(

            abs(
                value - average
            )

            for value in values

        ) / len(values)


        balance_score = max(

            0,

            100 - deviation * 0.5

        )

    else:

        balance_score = 70


    # ========================================================
    # 5. BREAK QUALITY
    # ========================================================

    break_count = sum(

        1

        for item in solution

        if item.get("type") == "Break"

    )


    if len(study_items) <= 1:

        break_score = 70

    elif break_count >= len(study_items) - 1:

        break_score = 100

    elif break_count > 0:

        break_score = 85

    else:

        break_score = 60


    # ========================================================
    # FINAL 0-100 SCORE
    # ========================================================

    final_score = (

        task_quality * 0.50

        + utilization_score * 0.20

        + balance_score * 0.20

        + break_score * 0.10

    )


    return round(

        max(
            0.0,
            min(
                100.0,
                final_score
            )
        ),

        2

    )


# ============================================================
# GENERATE NEIGHBOR
# ============================================================

def generate_neighbor(
    solution
):

    if len(solution) < 2:

        return solution.copy()


    neighbor = [

        item.copy()

        for item in solution

    ]


    study_indices = [

        i

        for i, item
        in enumerate(neighbor)

        if item.get("type") != "Break"

    ]


    if len(study_indices) < 2:

        return neighbor


    i, j = random.sample(
        study_indices,
        2
    )


    # --------------------------------------------------------
    # SWAP TASK INFORMATION
    # --------------------------------------------------------

    task_i = neighbor[i].copy()

    task_j = neighbor[j].copy()


    neighbor[i]["task"] = (
        task_j["task"]
    )

    neighbor[i]["subject"] = (
        task_j["subject"]
    )

    neighbor[i]["type"] = (
        task_j["type"]
    )

    neighbor[i]["heuristic_score"] = (
        task_j["heuristic_score"]
    )


    neighbor[j]["task"] = (
        task_i["task"]
    )

    neighbor[j]["subject"] = (
        task_i["subject"]
    )

    neighbor[j]["type"] = (
        task_i["type"]
    )

    neighbor[j]["heuristic_score"] = (
        task_i["heuristic_score"]
    )


    return neighbor


# ============================================================
# WEEKLY HILL CLIMBING
# ============================================================

def weekly_hill_climbing(
    initial_solution,
    iterations=200
):

    current = [

        item.copy()

        for item in initial_solution

    ]


    current_score = (
        calculate_solution_score(
            current
        )
    )


    best = [

        item.copy()

        for item in current

    ]


    best_score = current_score


    for _ in range(iterations):

        neighbor = generate_neighbor(
            current
        )


        neighbor_score = (
            calculate_solution_score(
                neighbor
            )
        )


        # ----------------------------------------------------
        # MOVE UPHILL
        # ----------------------------------------------------

        if neighbor_score > current_score:

            current = neighbor

            current_score = (
                neighbor_score
            )


        # ----------------------------------------------------
        # SAVE BEST
        # ----------------------------------------------------

        if current_score > best_score:

            best = [

                item.copy()

                for item in current

            ]

            best_score = current_score


    return (
        best,
        round(
            best_score,
            2
        )
    )


# ============================================================
# MAIN WEEKLY PLANNER
# ============================================================

def create_weekly_plan(
    tasks,
    timetable,
    start_date
):

    # --------------------------------------------------------
    # REMOVE COMPLETED TASKS
    # --------------------------------------------------------

    pending_tasks = []


    for task in tasks:

        completed = task.get(
            "completed",
            False
        )


        if isinstance(
            completed,
            bool
        ):

            is_completed = completed

        else:

            is_completed = str(
                completed
            ).strip().lower() in [
                "true",
                "1",
                "yes",
                "y"
            ]


        if not is_completed:

            pending_tasks.append(
                task
            )


    if not pending_tasks:

        return [], 0.0


    # --------------------------------------------------------
    # INITIAL SOLUTION
    # --------------------------------------------------------

    initial_solution = (
        create_initial_solution(
            pending_tasks,
            timetable,
            start_date
        )
    )


    # --------------------------------------------------------
    # HILL CLIMBING
    # --------------------------------------------------------

    best_solution, score = (
        weekly_hill_climbing(
            initial_solution,
            iterations=200
        )
    )


    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return (
        best_solution,
        score
    )