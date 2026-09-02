import streamlit as st
import pandas as pd
from datetime import date

from ai.hill_climbing import hill_climbing
from ai.weekly_planner import create_weekly_plan

from utils.scheduler import (
    get_free_slots,
    create_daily_schedule
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StudyPilot",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🎓 StudyPilot")
st.subheader("AI Daily & Weekly Academic Study Planner")

st.write(
    "Generate optimized academic study schedules "
    "using heuristic search and Hill Climbing."
)


# ============================================================
# LOAD DATA
# ============================================================

try:

    timetable = pd.read_csv("data/timetable.csv")
    tasks = pd.read_csv("data/tasks.csv")

except FileNotFoundError:

    st.error(
        "Required CSV files were not found. "
        "Make sure timetable.csv and tasks.csv "
        "are inside the data folder."
    )

    st.stop()


# ============================================================
# CHECK TIMETABLE COLUMNS
# ============================================================

required_timetable_columns = [
    "day",
    "start_time",
    "end_time",
    "course_code",
    "subject"
]

for column in required_timetable_columns:

    if column not in timetable.columns:

        st.error(
            f"Missing column in timetable.csv: {column}"
        )

        st.stop()


# ============================================================
# CHECK TASK COLUMNS
# ============================================================

required_task_columns = [
    "task",
    "subject",
    "type",
    "deadline",
    "hours",
    "priority",
    "difficulty"
]

for column in required_task_columns:

    if column not in tasks.columns:

        st.error(
            f"Missing column in tasks.csv: {column}"
        )

        st.stop()


# ============================================================
# COMPLETED COLUMN
# ============================================================

if "completed" not in tasks.columns:

    tasks["completed"] = False


def convert_to_bool(value):

    if isinstance(value, bool):

        return value

    return str(value).strip().lower() in [
        "true",
        "1",
        "yes",
        "y"
    ]


tasks["completed"] = tasks["completed"].apply(
    convert_to_bool
)


# ============================================================
# SIDEBAR SETTINGS
# ============================================================

st.sidebar.header("⚙️ Planner Settings")


selected_date = st.sidebar.date_input(
    "Select Date",
    date.today()
)


start_time = st.sidebar.time_input(
    "Study Start Time",
    value=pd.Timestamp("16:30").time()
)


end_time = st.sidebar.time_input(
    "Study End Time",
    value=pd.Timestamp("22:00").time()
)


selected_day = selected_date.strftime("%A")

current_date = selected_date.strftime(
    "%Y-%m-%d"
)


# ============================================================
# ACADEMIC DASHBOARD
# ============================================================

st.divider()

st.subheader("📊 Academic Dashboard")


total_tasks = len(tasks)


completed_tasks = len(
    tasks[
        tasks["completed"] == True
    ]
)


pending_tasks_count = len(
    tasks[
        tasks["completed"] == False
    ]
)


pending_hours = tasks.loc[
    tasks["completed"] == False,
    "hours"
].astype(float).sum()


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "📚 Total Tasks",
    total_tasks
)


col2.metric(
    "⏳ Pending Tasks",
    pending_tasks_count
)


col3.metric(
    "✅ Completed Tasks",
    completed_tasks
)


col4.metric(
    "⏰ Pending Study Hours",
    f"{pending_hours:.1f} hrs"
)


# ============================================================
# COMPLETION RATE
# ============================================================

if total_tasks > 0:

    completion_rate = (
        completed_tasks /
        total_tasks
    ) * 100

else:

    completion_rate = 0


st.write(
    f"### 📈 Overall Completion Rate: "
    f"{completion_rate:.1f}%"
)


st.progress(
    completion_rate / 100
)


# ============================================================
# UPCOMING DEADLINES
# ============================================================

st.subheader("🚨 Upcoming Deadlines")


pending_deadlines = tasks[
    tasks["completed"] == False
].copy()


if not pending_deadlines.empty:

    pending_deadlines["deadline"] = pd.to_datetime(
        pending_deadlines["deadline"]
    )


    today = pd.Timestamp(
        date.today()
    )


    pending_deadlines["days_left"] = (
        pending_deadlines["deadline"] -
        today
    ).dt.days


    # --------------------------------------------------------
    # DEADLINE STATUS
    # --------------------------------------------------------

    def get_deadline_status(days):

        if days < 0:

            return "🔴 Overdue"

        elif days == 0:

            return "🔴 Due Today"

        elif days <= 2:

            return "🟠 Due Soon"

        elif days <= 7:

            return "🟡 This Week"

        else:

            return "🟢 Later"


    pending_deadlines["status"] = (
        pending_deadlines["days_left"]
        .apply(get_deadline_status)
    )


    pending_deadlines = (
        pending_deadlines
        .sort_values("days_left")
    )


    deadline_display = pending_deadlines[
        [
            "task",
            "subject",
            "type",
            "deadline",
            "days_left",
            "status",
            "priority"
        ]
    ].head(5).copy()


    deadline_display.columns = [
        "Task",
        "Subject",
        "Type",
        "Deadline",
        "Days Left",
        "Status",
        "Priority"
    ]


    deadline_display["Deadline"] = (
        deadline_display["Deadline"]
        .dt.strftime("%d %B %Y")
    )


    st.dataframe(
        deadline_display,
        use_container_width=True,
        hide_index=True
    )


else:

    st.success(
        "🎉 No upcoming pending deadlines!"
    )


# ============================================================
# MAIN TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(
    [
        "📅 Daily Planner",
        "📋 Task Management",
        "📆 Weekly Planner"
    ]
)


# ============================================================
# TAB 1 — DAILY PLANNER
# ============================================================

with tab1:

    st.header("📅 Daily Study Planner")


    st.write(
        f"### 📆 {selected_date.strftime('%d %B %Y')}"
    )


    st.write(
        f"**Day:** {selected_day}"
    )


    # --------------------------------------------------------
    # TODAY'S CLASSES
    # --------------------------------------------------------

    st.subheader("🏫 Today's Classes")


    todays_classes = timetable[
        timetable["day"].astype(str).str.lower()
        == selected_day.lower()
    ].copy()


    if not todays_classes.empty:

        class_display = todays_classes[
            [
                "start_time",
                "end_time",
                "course_code",
                "subject"
            ]
        ].copy()


        class_display.columns = [
            "Start",
            "End",
            "Course Code",
            "Subject"
        ]


        st.dataframe(
            class_display,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.info(
            "No classes scheduled for this day."
        )


    # --------------------------------------------------------
    # PENDING TASKS
    # --------------------------------------------------------

    st.subheader("📚 Pending Academic Tasks")


    pending_tasks = tasks[
        tasks["completed"] == False
    ].copy()


    if not pending_tasks.empty:

        task_display = pending_tasks[
            [
                "task",
                "subject",
                "type",
                "deadline",
                "hours",
                "priority",
                "difficulty"
            ]
        ].copy()


        task_display.columns = [
            "Task",
            "Subject",
            "Type",
            "Deadline",
            "Hours",
            "Priority",
            "Difficulty"
        ]


        st.dataframe(
            task_display,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.success(
            "🎉 All tasks are completed!"
        )


    # --------------------------------------------------------
    # FREE TIME
    # --------------------------------------------------------

    st.subheader("🕐 Available Study Time")


    start_string = start_time.strftime(
        "%H:%M"
    )

    end_string = end_time.strftime(
        "%H:%M"
    )


    try:

        free_slots = get_free_slots(
            timetable,
            selected_day,
            start_string,
            end_string
        )


        if free_slots:

            free_display = pd.DataFrame(
                free_slots
            )


            st.dataframe(
                free_display,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning(
                "No free study slots available."
            )


    except Exception as e:

        st.error(
            f"Unable to calculate free time: {e}"
        )

        free_slots = []


    # --------------------------------------------------------
    # GENERATE DAILY PLAN
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🤖 Generate Optimized Daily Plan"
    )


    if pending_tasks.empty:

        st.success(
            "🎉 No pending tasks available "
            "for planning."
        )

    else:

        if st.button(
            "🚀 Generate Daily Study Plan",
            use_container_width=True,
            key="generate_daily_plan"
        ):

            with st.spinner(
                "🤖 Running Hill Climbing optimization..."
            ):

                task_records = (
                    pending_tasks
                    .to_dict("records")
                )


                best_tasks, optimization_score = (
                    hill_climbing(
                        task_records,
                        current_date
                    )
                )


                schedule = create_daily_schedule(
                    best_tasks,
                    free_slots
                )


            # ------------------------------------------------
            # OPTIMIZATION SCORE
            # ------------------------------------------------

            st.success(
                "✅ Daily study plan generated!"
            )


            col1, col2, col3 = st.columns(3)


            col1.metric(
                "🎯 Optimization Score",
                f"{optimization_score:.2f}/100"
            )


            try:

                planned_hours = sum(
                    float(task.get("hours", 0))
                    for task in best_tasks
                )

            except Exception:

                planned_hours = 0


            col2.metric(
                "⏰ Planned Study Hours",
                f"{planned_hours:.1f} hrs"
            )


            col3.metric(
                "📚 Tasks Considered",
                len(best_tasks)
            )


            # ------------------------------------------------
            # SCHEDULE
            # ------------------------------------------------

            st.subheader(
                "📋 Optimized Study Schedule"
            )


            if schedule:

                schedule_df = pd.DataFrame(
                    schedule
                )


                st.dataframe(
                    schedule_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.warning(
                    "No study schedule could be generated."
                )


            # ------------------------------------------------
            # SUMMARY
            # ------------------------------------------------

            st.subheader(
                "📌 Daily Plan Summary"
            )


            if best_tasks:

                summary_data = []


                for index, task in enumerate(
                    best_tasks,
                    start=1
                ):

                    summary_data.append(
                        {
                            "Order": index,
                            "Task": task.get(
                                "task",
                                ""
                            ),
                            "Subject": task.get(
                                "subject",
                                ""
                            ),
                            "Type": task.get(
                                "type",
                                ""
                            ),
                            "Deadline": task.get(
                                "deadline",
                                ""
                            ),
                            "Hours": task.get(
                                "hours",
                                0
                            ),
                            "Priority": task.get(
                                "priority",
                                0
                            )
                        }
                    )


                summary_df = pd.DataFrame(
                    summary_data
                )


                st.dataframe(
                    summary_df,
                    use_container_width=True,
                    hide_index=True
                )


            # ------------------------------------------------
            # AI EXPLANATION
            # ------------------------------------------------

            st.subheader(
                "🧠 AI Scheduling Explanation"
            )


            st.info(
                """
The Hill Climbing algorithm prioritizes tasks by
considering multiple academic factors:

• 🚨 Deadline urgency  
• ⭐ Task priority  
• 🧠 Task difficulty  
• 📚 Task type  
• ⏰ Required study hours  
• 📍 Position of tasks in the schedule  

The algorithm starts with an initial task ordering
based on the heuristic score and generates neighboring
solutions by swapping task positions.

If a neighboring solution produces a better schedule
score, Hill Climbing moves to that solution.

This process continues until no better neighboring
solution is found.
"""
            )


# ============================================================
# TAB 2 — TASK MANAGEMENT
# ============================================================

with tab2:

    st.header("📋 Task Management")


    # ========================================================
    # ADD NEW TASK
    # ========================================================

    st.subheader("➕ Add New Academic Task")


    with st.form(
        "add_task_form"
    ):

        task_name = st.text_input(
            "Task Name"
        )


        subject = st.text_input(
            "Subject"
        )


        task_type = st.selectbox(
            "Task Type",
            [
                "Assignment",
                "Project",
                "Homework",
                "Lab Work",
                "Assessment",
                "Semester Exam"
            ]
        )


        deadline = st.date_input(
            "Deadline",
            date.today()
        )


        hours = st.number_input(
            "Required Study Hours",
            min_value=0.5,
            max_value=100.0,
            value=2.0,
            step=0.5
        )


        priority = st.slider(
            "Priority",
            min_value=1,
            max_value=10,
            value=5
        )


        difficulty = st.slider(
            "Difficulty",
            min_value=1,
            max_value=10,
            value=5
        )


        add_task = st.form_submit_button(
            "➕ Add Task",
            use_container_width=True
        )


        if add_task:

            if task_name.strip() == "":

                st.error(
                    "Please enter a task name."
                )

            elif subject.strip() == "":

                st.error(
                    "Please enter the subject."
                )

            else:

                new_task = {
                    "task": task_name,
                    "subject": subject,
                    "type": task_type,
                    "deadline": deadline.strftime(
                        "%Y-%m-%d"
                    ),
                    "hours": hours,
                    "priority": priority,
                    "difficulty": difficulty,
                    "completed": False
                }


                tasks = pd.concat(
                    [
                        tasks,
                        pd.DataFrame(
                            [new_task]
                        )
                    ],
                    ignore_index=True
                )


                tasks.to_csv(
                    "data/tasks.csv",
                    index=False
                )


                st.success(
                    f"✅ Task '{task_name}' added successfully!"
                )


                st.rerun()


    # ========================================================
    # EXISTING TASKS
    # ========================================================

    st.divider()

    st.subheader("📝 Existing Tasks")


    if tasks.empty:

        st.info(
            "No tasks available."
        )

    else:

        editable_tasks = tasks[
            [
                "task",
                "subject",
                "type",
                "deadline",
                "hours",
                "priority",
                "difficulty",
                "completed"
            ]
        ].copy()


        editable_tasks.columns = [
            "Task",
            "Subject",
            "Type",
            "Deadline",
            "Hours",
            "Priority",
            "Difficulty",
            "Completed"
        ]


        edited_tasks = st.data_editor(
            editable_tasks,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Completed": st.column_config.CheckboxColumn(
                    "Completed",
                    help="Mark task as completed"
                )
            },
            disabled=[
                "Task",
                "Subject",
                "Type",
                "Deadline",
                "Hours",
                "Priority",
                "Difficulty"
            ],
            key="task_editor"
        )


        # ====================================================
        # SAVE STATUS AND REPLAN
        # ====================================================

        st.write("")


        if st.button(
            "💾 Save Task Status & Re-plan",
            use_container_width=True,
            key="save_task_status"
        ):

            # -----------------------------------------------
            # STORE OLD STATUS
            # -----------------------------------------------

            old_completed = (
                tasks["completed"].copy()
            )


            # -----------------------------------------------
            # UPDATE COMPLETED STATUS
            # -----------------------------------------------

            tasks["completed"] = (
                edited_tasks["Completed"]
                .astype(bool)
                .values
            )


            # -----------------------------------------------
            # SAVE TO CSV
            # -----------------------------------------------

            tasks.to_csv(
                "data/tasks.csv",
                index=False
            )


            # -----------------------------------------------
            # CHECK NEWLY COMPLETED TASKS
            # -----------------------------------------------

            newly_completed = (
                (~old_completed)
                &
                (tasks["completed"])
            ).sum()


            # -----------------------------------------------
            # SUCCESS MESSAGE
            # -----------------------------------------------

            if newly_completed > 0:

                st.success(
                    f"✅ {newly_completed} task(s) completed!"
                )


                st.info(
                    "🤖 Your next Daily/Weekly plan "
                    "will automatically use the "
                    "remaining tasks."
                )

            else:

                st.success(
                    "✅ Task status updated successfully!"
                )


            # -----------------------------------------------
            # REFRESH APP
            # -----------------------------------------------

            st.rerun()


    # ========================================================
    # TASK STATISTICS
    # ========================================================

    st.divider()

    st.subheader("📊 Task Statistics")


    current_total = len(tasks)


    current_completed = len(
        tasks[
            tasks["completed"] == True
        ]
    )


    current_pending = len(
        tasks[
            tasks["completed"] == False
        ]
    )


    stat1, stat2, stat3 = st.columns(3)


    stat1.metric(
        "📚 Total Tasks",
        current_total
    )


    stat2.metric(
        "⏳ Pending",
        current_pending
    )


    stat3.metric(
        "✅ Completed",
        current_completed
    )


# ============================================================
# TAB 3 — WEEKLY PLANNER
# ============================================================

with tab3:

    st.header("📆 Weekly Study Planner")


    st.write(
        "Generate an optimized Monday–Friday "
        "academic study plan."
    )


    # ========================================================
    # WEEK SELECTION
    # ========================================================

    week_date = st.date_input(
        "Select any date in the required week",
        selected_date,
        key="weekly_date"
    )


    # --------------------------------------------------------
    # FIND MONDAY
    # --------------------------------------------------------

    monday = (
        week_date
        - pd.Timedelta(
            days=week_date.weekday()
        )
    )


    friday = monday + pd.Timedelta(
        days=4
    )


    st.info(
        f"📅 Selected Week: "
        f"{monday.strftime('%d %B %Y')} "
        f"to "
        f"{friday.strftime('%d %B %Y')}"
    )


    # ========================================================
    # PENDING WEEKLY TASKS
    # ========================================================

    weekly_tasks = tasks[
        tasks["completed"] == False
    ].copy()


    st.subheader(
        "📚 Pending Tasks for Weekly Planning"
    )


    if not weekly_tasks.empty:

        weekly_task_display = weekly_tasks[
            [
                "task",
                "subject",
                "type",
                "deadline",
                "hours",
                "priority",
                "difficulty"
            ]
        ].copy()


        weekly_task_display.columns = [
            "Task",
            "Subject",
            "Type",
            "Deadline",
            "Hours",
            "Priority",
            "Difficulty"
        ]


        st.dataframe(
            weekly_task_display,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.success(
            "🎉 No pending tasks available!"
        )


    # ========================================================
    # GENERATE WEEKLY PLAN
    # ========================================================

    st.divider()


    if weekly_tasks.empty:

        st.info(
            "Add some tasks to generate "
            "a weekly study plan."
        )

    else:

        if st.button(
            "🚀 Generate Weekly Study Plan",
            use_container_width=True,
            key="generate_weekly_plan"
        ):

            with st.spinner(
                "🤖 Optimizing weekly schedule..."
            ):

                weekly_records = (
                    weekly_tasks
                    .to_dict("records")
                )


                result = create_weekly_plan(
                    weekly_records,
                    timetable,
                    week_date.strftime(
                        "%Y-%m-%d"
                    )
                )


                # --------------------------------------------
                # HANDLE RETURN VALUE
                # --------------------------------------------

                if isinstance(
                    result,
                    tuple
                ):

                    weekly_solution = result[0]

                    weekly_score = result[1]

                else:

                    weekly_solution = result

                    weekly_score = 0


            st.success(
                "✅ Weekly study plan generated!"
            )


            # =================================================
            # SCORE
            # =================================================

            st.subheader(
                "🎯 Weekly Optimization"
            )


            score_col1, score_col2 = st.columns(2)


            score_col1.metric(
                "Hill Climbing Score",
                f"{weekly_score:.2f}/100"
            )


            score_col2.metric(
                "Planning Days",
                "Monday – Friday"
            )


            # =================================================
            # WEEKLY PLAN
            # =================================================

            st.subheader(
                "📋 Optimized Weekly Plan"
            )


            if weekly_solution:

                # --------------------------------------------
                # CASE 1 — DICTIONARY
                # --------------------------------------------

                if isinstance(
                    weekly_solution,
                    dict
                ):

                    rows = []


                    for day, sessions in (
                        weekly_solution.items()
                    ):

                        if isinstance(
                            sessions,
                            list
                        ):

                            for session in sessions:

                                if isinstance(
                                    session,
                                    dict
                                ):

                                    row = {
                                        "Day": day
                                    }

                                    row.update(
                                        session
                                    )

                                    rows.append(
                                        row
                                    )

                                else:

                                    rows.append(
                                        {
                                            "Day": day,
                                            "Session": session
                                        }
                                    )

                        else:

                            rows.append(
                                {
                                    "Day": day,
                                    "Session": sessions
                                }
                            )


                    if rows:

                        weekly_df = pd.DataFrame(
                            rows
                        )


                        st.dataframe(
                            weekly_df,
                            use_container_width=True,
                            hide_index=True
                        )


                # --------------------------------------------
                # CASE 2 — LIST
                # --------------------------------------------

                elif isinstance(
                    weekly_solution,
                    list
                ):

                    try:

                        weekly_df = pd.DataFrame(
                            weekly_solution
                        )


                        st.dataframe(
                            weekly_df,
                            use_container_width=True,
                            hide_index=True
                        )

                    except Exception:

                        st.write(
                            weekly_solution
                        )

                else:

                    st.write(
                        weekly_solution
                    )

            else:

                st.warning(
                    "No weekly schedule could be generated."
                )


            # =================================================
            # WORKLOAD VISUALIZATION
            # =================================================

            st.subheader(
                "📊 Weekly Workload"
            )


            try:

                workload = {
                    "Monday": 0,
                    "Tuesday": 0,
                    "Wednesday": 0,
                    "Thursday": 0,
                    "Friday": 0
                }


                if isinstance(
                    weekly_solution,
                    dict
                ):

                    for day in workload:

                        sessions = (
                            weekly_solution
                            .get(day, [])
                        )


                        if isinstance(
                            sessions,
                            list
                        ):

                            for session in sessions:

                                if isinstance(
                                    session,
                                    dict
                                ):

                                    value = session.get(
                                        "hours",
                                        session.get(
                                            "duration",
                                            0
                                        )
                                    )

                                    try:

                                        workload[day] += float(
                                            value
                                        )

                                    except (
                                        ValueError,
                                        TypeError
                                    ):

                                        pass


                workload_df = pd.DataFrame(
                    {
                        "Day": list(
                            workload.keys()
                        ),
                        "Study Hours": list(
                            workload.values()
                        )
                    }
                )


                st.bar_chart(
                    workload_df.set_index(
                        "Day"
                    )
                )


            except Exception:

                st.info(
                    "Workload visualization "
                    "is unavailable for this plan format."
                )


            # =================================================
            # WEEKLY SUMMARY
            # =================================================

            st.subheader(
                "📌 Weekly Summary"
            )


            pending_count = len(
                weekly_tasks
            )


            total_weekly_hours = (
                weekly_tasks["hours"]
                .astype(float)
                .sum()
            )


            summary1, summary2, summary3 = (
                st.columns(3)
            )


            summary1.metric(
                "📚 Pending Tasks",
                pending_count
            )


            summary2.metric(
                "⏰ Required Study Hours",
                f"{total_weekly_hours:.1f}"
            )


            summary3.metric(
                "🎯 Optimization Score",
                f"{weekly_score:.2f}/100"
            )


            # =================================================
            # AI EXPLANATION
            # =================================================

            st.subheader(
                "🧠 AI Weekly Planning Explanation"
            )


            st.info(
                """
The weekly planner uses heuristic search and
Hill Climbing to distribute academic tasks across
available study periods.

The optimization considers:

• 🚨 Deadline urgency
• ⭐ Task priority
• 🧠 Difficulty
• 📚 Task type
• ⏰ Required study hours
• ⚖️ Workload balance
• ☕ Break allocation
• 📅 Available study time

The initial solution is generated using heuristic
prioritization.

Hill Climbing then explores neighboring schedules
and attempts to improve the overall weekly score.

The final score is normalized to a scale of 0–100,
where a higher score represents a better optimized
study plan.
"""
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🎓 StudyPilot | AI-Powered Academic Study Planner | "
    "Heuristic Search + Hill Climbing"
)