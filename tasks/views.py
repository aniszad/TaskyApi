from django.shortcuts import render

# Create your views here.

from datetime import datetime, date
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.shortcuts import get_object_or_404
from django.db import connection
from rest_framework.permissions import AllowAny
from django.db import IntegrityError
from django.db.utils import OperationalError
from django.utils import timezone
from django.db import transaction
from datetime import datetime


@api_view(['POST'])
def get_project_tasks(request):
    # Assuming you are passing the projectId in the request
    project_id = int(request.data.get('projectId'))  # Ensure project_id is an integer

    # Use raw SQL to retrieve tasks with the specified projectId
    raw_query = """
        SELECT *
        FROM tasks
        WHERE project_id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(raw_query, [project_id])
        tasks = cursor.fetchall()

    # You can then serialize the tasks and return them as JSON
    task_data = []
    for task in tasks:
        print(task)
        task_members = get_task_members(task[0])  # Assuming task[5] is the taskId
        task_info = {
            'taskId': task[0],
            'projectId': task[1],
            'content': task[2],
            'status': task[3],
            'priority': task[4],
            'start_date': task[5],
            'end_date': task[6],
            'task_members': task_members
        }
        task_data.append(task_info)
        print("tasks hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh", task_data)

    return Response({'tasks': task_data})

def get_task_members(task_id):
        with connection.cursor() as cursor:
            # Update task status
            cursor.execute(
                """
                SELECT users.username, users.first_name, users.last_name, users.user_id
                FROM users
                INNER JOIN tasks_assignees ON users.user_id = tasks_assignees.user_id
                WHERE tasks_assignees.task_id = %s;
                """,
                [task_id]
            )

            # Fetch all rows from the query result
            result = cursor.fetchall()

            # Build a list of dictionaries for each user's information
            users_list = [{'username': row[0], 'first_name': row[1], 'last_name': row[2], 'id':row[3]} for row in result]

            return users_list

@api_view(['POST'])
def create_task(request):
    try:
        data = request.data
        content = data.get('content')
        projectId = data.get('projectId')
        priority = data.get('priority')
        task_status = data.get('status')
        start_date = data.get('start_date', timezone.now().date())
        end_date = data.get('end_date', timezone.now().date())
        members = data.get('membersIds', [])

        with transaction.atomic():
            with connection.cursor() as cursor:
                # Insert project and assignees in a single query
                cursor.execute(
                    """
                    WITH inserted_task AS (
                        INSERT INTO tasks (content, status, start_date, end_date, project_id, priority)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING task_id
                    )
                    INSERT INTO tasks_assignees (task_id, user_id)
                    SELECT task_id, unnest(%s::int[])
                    FROM inserted_task;
                    """,
                    [content, task_status, start_date, end_date, projectId, priority, members]
                )

        return Response({'message': 'Task created successfully'}, status=status.HTTP_201_CREATED)

    except OperationalError as e:
        # Handle database connection issues
        return Response({'error': 'Database connection error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except IntegrityError as e:
        # Handle database integrity errors, such as unique constraint violations
        print("hehehe", str(e))
        return Response({'error': 'Integrity error. Make sure projectId is valid and membersIds are valid users.'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Handle other unexpected errors
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def delete_task(request):
    try:
        taskId = int(request.data.get('taskId'))
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Delete task_assignees entry
                cursor.execute(
                    """
                    DELETE FROM tasks_assignees
                    WHERE task_id = %s
                    """,
                    [taskId]
                )
                # Delete task
                cursor.execute(
                    """
                    DELETE FROM tasks
                    WHERE task_id = %s
                    """,
                    [taskId]
                )
        return Response({'message': 'Task deleted successfully'}, status=status.HTTP_200_OK)

    except OperationalError as e:
        # Handle database connection issues
        return Response({'error': 'Database connection error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except IntegrityError as e:
        # Handle database integrity errors, such as unique constraint violations
        return Response({'error': 'Integrity error. Make sure projectId is valid and membersIds are valid users.'},
                            status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Handle other unexpected errors
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_task(request):
    try:
        taskId = request.data.get('taskId')
        task_status = request.data.get('status')

        with transaction.atomic():
            with connection.cursor() as cursor:
                # Update task status
                cursor.execute(
                    """
                    UPDATE tasks
                    SET status = %s
                    WHERE task_id = %s
                    """,
                    [task_status, taskId]
                )

        return Response({'message': 'Task updated successfully'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def get_completed_tasks(request):
    # Assuming you are passing the projectId in the request
    userId = int(request.data.get('userId'))  # Ensure project_id is an integer
    raw_query = """
                SELECT tasks.*
                FROM tasks
                JOIN tasks_assignees ON tasks.task_id = tasks_assignees.task_id
                WHERE tasks_assignees.user_id = %s AND tasks.status = 'Completed'
    """
    with connection.cursor() as cursor:
        cursor.execute(raw_query, [userId])
        tasks = cursor.fetchall()

    # You can then serialize the tasks and return them as JSON
    task_data = []
    for task in tasks:
        task_members = get_task_members(task[0])  # Assuming task[5] is the taskId
        task_info = {
            'taskId': task[0],
            'projectId': task[1],
            'content': task[2],
            'status': task[3],
            'priority': task[4],
            'start_date': task[5],
            'end_date': task[6],
            'task_members': task_members
        }
        task_data.append(task_info)


    return Response({'completed_tasks': task_data})


from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def search_tasks(request):
    userId = int(request.data.get('userId'))
    query = request.data.get('query')

    # Constructing the SQL query dynamically based on the provided parameters
    raw_query = """
                SELECT tasks.*
                FROM tasks
                JOIN tasks_assignees ON tasks.task_id = tasks_assignees.task_id
                WHERE tasks_assignees.user_id = %s
                AND tasks.status = 'Completed'
    """

    params = [userId]

    # Check if the query is in the format "year-month-day" (date)
    if validate_date_format(query):
        print("its a date", query)
        raw_query += " AND %s BETWEEN tasks.start_date AND tasks.end_date"
        params.append(query)
    else:
        print("its a query", query)
        raw_query += " AND tasks.content ILIKE %s"
        params.append(f"%{query}%")

    with connection.cursor() as cursor:
        cursor.execute(raw_query, params)
        tasks = cursor.fetchall()

    task_data = []
    for task in tasks:
        task_members = get_task_members(task[0])  # Assuming task[5] is the taskId
        task_info = {
            'taskId': task[0],
            'projectId': task[1],
            'content': task[2],
            'status': task[3],
            'priority': task[4],
            'start_date': task[5],
            'end_date': task[6],
            'task_members': task_members
        }
        task_data.append(task_info)
        print("returned data", task_data)

    return Response({'task_search': task_data})

def validate_date_format(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False



