from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = Path(__file__).with_name("growlog.db")


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    with connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS employees (
                employee_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                division TEXT NOT NULL,
                team TEXT NOT NULL,
                job TEXT NOT NULL,
                level TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS goals (
                goal_id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                purpose TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                planned_hours REAL NOT NULL CHECK (planned_hours > 0),
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            );

            CREATE TABLE IF NOT EXISTS activities (
                activity_id TEXT PRIMARY KEY,
                goal_id TEXT NOT NULL,
                employee_id TEXT NOT NULL,
                activity_date TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                hours REAL NOT NULL CHECK (hours > 0 AND hours <= 24),
                memo TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (goal_id) REFERENCES goals(goal_id),
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            );
            """
        )


def is_empty() -> bool:
    with connect() as connection:
        count = connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    return count == 0


def load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    with connect() as connection:
        employees = pd.read_sql_query(
            """
            SELECT employee_id, name, email, division, team, job, level, created_at
            FROM employees
            ORDER BY created_at, name
            """,
            connection,
        )
        goals = pd.read_sql_query(
            """
            SELECT goal_id, employee_id, title, category, purpose, start_date,
                   end_date, planned_hours, status, created_at
            FROM goals
            ORDER BY created_at
            """,
            connection,
        )
        activities = pd.read_sql_query(
            """
            SELECT activity_id, goal_id, employee_id, activity_date, activity_type,
                   hours, memo, created_at
            FROM activities
            ORDER BY activity_date, created_at
            """,
            connection,
        )
    return employees, goals, activities


def insert_seed_data(
    employees: pd.DataFrame, goals: pd.DataFrame, activities: pd.DataFrame
) -> None:
    seed_employees = employees.copy()
    if "email" not in seed_employees.columns:
        seed_employees["email"] = (
            seed_employees["employee_id"].str.lower() + "@growlog.local"
        )
    seed_employees["created_at"] = pd.Timestamp.now().isoformat()

    with connect() as connection:
        seed_employees[
            [
                "employee_id",
                "name",
                "email",
                "division",
                "team",
                "job",
                "level",
                "created_at",
            ]
        ].to_sql("employees", connection, if_exists="append", index=False)

        work_goals = goals.copy()
        for column in ("start_date", "end_date", "created_at"):
            work_goals[column] = work_goals[column].astype(str)
        work_goals.to_sql("goals", connection, if_exists="append", index=False)

        if not activities.empty:
            work_activities = activities.copy()
            for column in ("activity_date", "created_at"):
                work_activities[column] = work_activities[column].astype(str)
            work_activities.to_sql(
                "activities", connection, if_exists="append", index=False
            )


def add_employee(employee: dict) -> None:
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO employees (
                employee_id, name, email, division, team, job, level, created_at
            ) VALUES (
                :employee_id, :name, :email, :division, :team, :job, :level, :created_at
            )
            """,
            employee,
        )


def add_goal(goal: dict) -> None:
    payload = {key: str(value) if key in {"start_date", "end_date", "created_at"} else value
               for key, value in goal.items()}
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO goals (
                goal_id, employee_id, title, category, purpose, start_date,
                end_date, planned_hours, status, created_at
            ) VALUES (
                :goal_id, :employee_id, :title, :category, :purpose, :start_date,
                :end_date, :planned_hours, :status, :created_at
            )
            """,
            payload,
        )


def add_activity(activity: dict) -> None:
    payload = {
        key: str(value) if key in {"activity_date", "created_at"} else value
        for key, value in activity.items()
    }
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO activities (
                activity_id, goal_id, employee_id, activity_date, activity_type,
                hours, memo, created_at
            ) VALUES (
                :activity_id, :goal_id, :employee_id, :activity_date, :activity_type,
                :hours, :memo, :created_at
            )
            """,
            payload,
        )


def reset_database(
    employees: pd.DataFrame, goals: pd.DataFrame, activities: pd.DataFrame
) -> None:
    with connect() as connection:
        connection.execute("DELETE FROM activities")
        connection.execute("DELETE FROM goals")
        connection.execute("DELETE FROM employees")
    insert_seed_data(employees, goals, activities)
