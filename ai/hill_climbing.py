# ============================================================
# STUDYPILOT - HEURISTIC HILL CLIMBING
# ============================================================

from datetime import datetime


# ============================================================
# TASK TYPE IMPORTANCE
# ============================================================

TASK_TYPE_WEIGHT = {
    "Semester Exam": 10,
    "Assessment": 9,
    "Assignment": 7,
    "Lab Work": 6,
    "Lab": 6,
    "Project": 5,
    "Homework": 4
}


# ============================================================
# SAFE NUMBER CONVERSION
# ============================================================

def safe_float(value, default=5.0):

    try:
        return float(value)

    except (ValueError, TypeError):
        return default


# ============================================================
# DEADLINE URGENCY SCORE
# ============================================================

def deadline_urgency(deadline, current_date):
    """
    Returns urgency from 0 to 100.

    Closer deadline = higher urgency.
    Overdue task = maximum urgency.
    """

    try:

        deadline_date = datetime.strptime(
            str(deadline),
            "%Y-%m-%d"
        ).date()

        current = datetime.strptime(
            str(current_date),
            "%Y-%m-%d"
        ).date()

    except (ValueError, TypeError):

        return 20.0


    days_left = (
        deadline_date - current
    ).days


    # --------------------------------------------------------
    # DEADLINE URGENCY
    # --------------------------------------------------------

    if days_left < 0:
        return 100.0

    elif days_left == 0:
        return 95.0

    elif days_left == 1:
        return 90.0

    elif days_left == 2:
        return 82.0

    elif days_left <= 3:
        return 75.0

    elif days_left <= 5:
        return 65.0

    elif days_left <= 7:
        return 55.0

    elif days_left <= 14:
        return 40.0

    elif days_left <= 30:
        return 25.0

    else:
        return 10.0


# ============================================================
# TASK TYPE SCORE
# ============================================================

def task_type_score(task):

    task_type = str(
        task.get(
            "type",
            "Homework"
        )
    ).strip()

    return float(
        TASK_TYPE_WEIGHT.get(
            task_type,
            4
        )
    ) * 10.0


# ============================================================
# INDIVIDUAL TASK HEURISTIC
# ============================================================

def task_heuristic(task, current_date):
    """
    Calculates the importance of one task.

    Factors:
        Deadline urgency : 40%
        Priority         : 25%
        Difficulty       : 15%
        Task type        : 15%
        Study hours      : 5%

    Returns a value approximately between 0 and 100.
    """

    # --------------------------------------------------------
    # 1. DEADLINE
    # --------------------------------------------------------

    urgency = deadline_urgency(
        task.get("deadline"),
        current_date
    )


    # --------------------------------------------------------
    # 2. PRIORITY
    # --------------------------------------------------------

    priority = safe_float(
        task.get("priority", 5),
        5
    )

    priority = max(
        1,
        min(10, priority)
    )

    priority_score = (
        priority / 10
    ) * 100


    # --------------------------------------------------------
    # 3. DIFFICULTY
    # --------------------------------------------------------

    difficulty = safe_float(
        task.get("difficulty", 5),
        5
    )

    difficulty = max(
        1,
        min(10, difficulty)
    )

    difficulty_score = (
        difficulty / 10
    ) * 100


    # --------------------------------------------------------
    # 4. TASK TYPE
    # --------------------------------------------------------

    type_score = task_type_score(
        task
    )


    # --------------------------------------------------------
    # 5. REQUIRED STUDY HOURS
    # --------------------------------------------------------

    hours = safe_float(
        task.get("hours", 1),
        1
    )

    hours = max(
        0.5,
        min(20, hours)
    )

    # More required work gives a small additional weight.
    hours_score = min(
        100,
        hours * 10
    )


    # ========================================================
    # WEIGHTED HEURISTIC
    # ========================================================

    score = (

        urgency * 0.40

        +

        priority_score * 0.25

        +

        difficulty_score * 0.15

        +

        type_score * 0.15

        +

        hours_score * 0.05
    )


    return round(
        score,
        2
    )


# ============================================================
# SCHEDULE QUALITY
# ============================================================

def schedule_score(
    tasks,
    current_date
):
    """
    Calculates a 0-100 score for the ORDER of tasks.

    Important:
    Earlier positions receive more weight.

    Therefore:
        urgent/high-priority tasks
        should appear earlier.

    This makes task swapping meaningful for
    Hill Climbing.
    """

    if not tasks:
        return 0.0


    total_weight = 0.0
    weighted_score = 0.0


    number_of_tasks = len(tasks)


    for index, task in enumerate(tasks):

        # ----------------------------------------------------
        # POSITION WEIGHT
        # ----------------------------------------------------
        #
        # First task gets highest weight.
        # Later tasks receive slightly less weight.
        #
        position_weight = (
            number_of_tasks - index
        )


        # ----------------------------------------------------
        # TASK HEURISTIC
        # ----------------------------------------------------

        task_score = task_heuristic(
            task,
            current_date
        )


        weighted_score += (
            task_score
            * position_weight
        )

        total_weight += position_weight


    if total_weight == 0:
        return 0.0


    final_score = (
        weighted_score
        / total_weight
    )


    return round(
        max(
            0.0,
            min(100.0, final_score)
        ),
        2
    )


# ============================================================
# GENERATE NEIGHBOURS
# ============================================================

def generate_neighbors(tasks):
    """
    Generates neighboring states by swapping
    two task positions.
    """

    neighbors = []

    n = len(tasks)


    for i in range(n):

        for j in range(
            i + 1,
            n
        ):

            neighbor = tasks.copy()


            # ------------------------------------------------
            # SWAP TWO TASKS
            # ------------------------------------------------

            neighbor[i], neighbor[j] = (
                neighbor[j],
                neighbor[i]
            )


            neighbors.append(
                neighbor
            )


    return neighbors


# ============================================================
# REMOVE COMPLETED TASKS
# ============================================================

def remove_completed_tasks(tasks):

    pending = []


    for task in tasks:

        completed = task.get(
            "completed",
            False
        )


        # ----------------------------------------------------
        # HANDLE CSV BOOLEAN VALUES
        # ----------------------------------------------------

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

            pending.append(task)


    return pending


# ============================================================
# INITIAL STATE
# ============================================================

def create_initial_state(
    tasks,
    current_date
):
    """
    Creates the initial solution by sorting tasks
    according to their individual heuristic value.
    """

    return sorted(

        tasks,

        key=lambda task:
            task_heuristic(
                task,
                current_date
            ),

        reverse=True
    )


# ============================================================
# HILL CLIMBING ALGORITHM
# ============================================================

def hill_climbing(
    tasks,
    current_date,
    max_iterations=100
):
    """
    Hill Climbing searches for a better task ordering.

    State:
        Ordered list of academic tasks

    Neighbor:
        Swap two task positions

    Heuristic:
        Schedule quality from 0 to 100

    Goal:
        Maximize schedule quality
    """

    # ========================================================
    # STEP 1 - REMOVE COMPLETED TASKS
    # ========================================================

    pending_tasks = remove_completed_tasks(
        tasks
    )


    if not pending_tasks:

        return [], 0.0


    # ========================================================
    # STEP 2 - CREATE INITIAL STATE
    # ========================================================

    current_state = create_initial_state(
        pending_tasks,
        current_date
    )


    current_score = schedule_score(
        current_state,
        current_date
    )


    # Store best solution found
    best_state = current_state.copy()

    best_score = current_score


    # ========================================================
    # STEP 3 - HILL CLIMBING
    # ========================================================

    iteration = 0


    while iteration < max_iterations:

        iteration += 1


        neighbors = generate_neighbors(
            current_state
        )


        if not neighbors:
            break


        # ----------------------------------------------------
        # FIND BEST NEIGHBOUR
        # ----------------------------------------------------

        best_neighbor = None
        best_neighbor_score = current_score


        for neighbor in neighbors:

            neighbor_score = schedule_score(
                neighbor,
                current_date
            )


            if (
                neighbor_score
                > best_neighbor_score
            ):

                best_neighbor = neighbor

                best_neighbor_score = (
                    neighbor_score
                )


        # ----------------------------------------------------
        # NO BETTER NEIGHBOUR
        # ----------------------------------------------------

        if best_neighbor is None:

            break


        # ----------------------------------------------------
        # MOVE UPHILL
        # ----------------------------------------------------

        current_state = best_neighbor

        current_score = (
            best_neighbor_score
        )


        # ----------------------------------------------------
        # SAVE BEST STATE
        # ----------------------------------------------------

        if current_score > best_score:

            best_state = (
                current_state.copy()
            )

            best_score = (
                current_score
            )


    # ========================================================
    # FINAL SCORE
    # ========================================================

    optimization_score = round(
        max(
            0.0,
            min(100.0, best_score)
        ),
        2
    )


    # ========================================================
    # RETURN
    # ========================================================

    return (
        best_state,
        optimization_score
    )
