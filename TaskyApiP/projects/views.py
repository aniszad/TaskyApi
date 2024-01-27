from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, date
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.shortcuts import get_object_or_404
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import transaction
from django.db import IntegrityError
from django.db import OperationalError

@api_view(['POST'])
def get_my_projects(request):
    user_id = request.data.get('userId')  # Ensure user_id is an integer
    raw_query = """
            SELECT *
            FROM projects
            WHERE owner_id = %s
        """
    with connection.cursor() as cursor:
        cursor.execute(raw_query, [user_id])
        projects = cursor.fetchall()
        print("projects", projects)

    project_data = [
        {
            'projectId': project[0],
            'ownerId': project[1],
            'title': project[2],
            'description': project[3],
            'priority': project[4],
            'status': project[5],
            'start_date': project[6],
            'end_date': project[7],
            'color': project[8],
            'tasks': []
        }
        for project in projects
    ]
    for project in project_data:
        tasks = get_tasks_statuses_for_project(project['projectId'])
        project['tasks'] = tasks

    return Response({'projects_with_tasks': project_data})

def get_tasks_statuses_for_project(project_id):
    raw_query_tasks = """
        SELECT status
        FROM tasks
        WHERE project_id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(raw_query_tasks, [project_id])
        task_statuses = cursor.fetchall()

    task_statuses_list = [status[0] for status in task_statuses]
    return task_statuses_list

@api_view(['POST'])
def create_project(request):
    owner_id = request.data.get('userId')
    data = request.data.get('project')
    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority')
    project_status = data.get('status')
    color = data.get('color')
    start_date = data.get('start_date', date(2023, 1, 1))
    end_date = data.get('end_date', date(2023, 12, 12))
    members = data.get('members', [])

    with connection.cursor() as cursor:
        # Insert project
        cursor.execute(
            """
            INSERT INTO projects (owner_id, title, description, priority, status, start_date, end_date, color)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING project_id
            """,
            [owner_id, title, description, priority, project_status, start_date, end_date, color]
        )
        # Get the project ID of the newly created project
        project_id = cursor.fetchone()[0]
        # Insert members
        for member_id in members:
            cursor.execute(
                """
                INSERT INTO projects_members (project_id, user_id)
                VALUES (%s, %s)
                """,
                [project_id, member_id]
            )

    return Response({'message': 'Project created successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def get_project_members(request):
    projectId = int(request.data.get('projectId'))
    with transaction.atomic():
        with connection.cursor() as cursor:
            # Update task status
            cursor.execute(
                """
                SELECT users.user_id, users.username, users.first_name, users.last_name
                FROM users
                INNER JOIN projects_members ON users.user_id = projects_members.user_id
                WHERE projects_members.project_id = %s;
                """,
                [projectId]
            )
            # Fetch all rows from the query result
            result = cursor.fetchall()
        # Build a list of dictionaries for each user's information
        users_list = [{'memberId': row[0],'username': row[1], 'first_name': row[2], 'last_name': row[3]} for row in result]

    return Response({'project_members': users_list}, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_member_to_project(request):
    try:
        projectId = int(request.data.get('projectId'))
        memberId = int(request.data.get('memberId'))
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Check if the member already exists in the project
                cursor.execute(
                    """
                    SELECT 1
                    FROM projects_members
                    WHERE project_id = %s AND user_id = %s
                    """,
                    [projectId, memberId]
                )
                member_exists = cursor.fetchone()
                if member_exists:
                    # Member already exists in the project, raise IntegrityError
                    return Response({'error': 'Member Already Exists'})
                # If member doesn't exist, insert into the junction table
                cursor.execute(
                    """
                    INSERT INTO projects_members (project_id, user_id)
                    VALUES (%s, %s)
                    """,
                    [projectId, memberId]
                )

        return Response({'message': 'Member added to project successfully'})

    except IntegrityError as e:
        # Handle cases where the same member is added to the project multiple times
        return Response({'error': str(e)}, status=400)

    except Exception as e:
        # Handle other unexpected errors
        return Response({'error': f'An error occurred: {str(e)}'}, status=500)

@api_view(['POST'])
def delete_project_member(request):
    try:
        memberId = int(request.data.get('memberId'))
        projectId = int(request.data.get('projectId'))
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Delete task_assignees entry
                cursor.execute(
                    """
                    DELETE FROM projects_members
                    WHERE user_id = %s AND project_id = %s
                    """,
                    [memberId, projectId]
                )
        return Response({'message': 'Member deleted successfully'}, status=status.HTTP_200_OK)

    except OperationalError as e:
        # Handle database connection issues
        return Response({'error': 'Database connection error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except IntegrityError as e:
        # Handle database integrity errors, such as unique constraint violations
        return Response({'error': 'Integrity error.'},
                        status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Handle other unexpected errors
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def get_involved_projects(request):
    user_id = int(request.data.get('userId'))
    raw_query = """
                SELECT projects.*
                FROM projects
                JOIN projects_members ON projects.project_id = projects_members.project_id
                WHERE projects_members.user_id = %s
            """
    with connection.cursor() as cursor:
        cursor.execute(raw_query, [user_id])
        projects = cursor.fetchall()

    # Map the raw SQL result to a format similar to your provided function
    project_data = [
        {
            'projectId': project[0],
            'ownerId': project[1],
            'title': project[2],
            'description': project[3],
            'priority': project[4],
            'status': project[5],
            'start_date': project[6],
            'end_date': project[7],
            'color': project[8],
            'tasks':[]
            # Add more fields as needed
        }
        for project in projects
    ]
    # Use a separate function to retrieve tasks for each project
    for project in project_data:
        tasks = get_tasks_statuses_for_project(project['projectId'])
        project['tasks'] = tasks

    return Response({'projects': project_data})

@api_view(['POST'])
def get_project_owner(request):
    project_owner_id = request.data.get('projectOwnerId')

    with connection.cursor() as cursor:
        # Use raw SQL to retrieve the project owner from the 'users' table
        sql_query = """
            SELECT * FROM users WHERE user_id = %s
        """
        cursor.execute(sql_query, [project_owner_id])
        user_data = cursor.fetchone()

    if user_data:
        # Assuming your User model has fields like 'id', 'username', etc.
        user_dict = {
            'id': user_data[0],
            'username': user_data[4],
            'first_name': user_data[5],
            'last_name': user_data[6],
            'email': user_data[7],
            # Add other fields as needed
        }
        return Response({"project_owner": user_dict})
    else:
        return Response(null, status=404)


@api_view(['POST'])
def delete_project(request):
    projectId = int(request.data.get('projectId'))

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM tasks_assignees
                WHERE task_id IN (SELECT task_id FROM tasks WHERE project_id = %s);

                DELETE FROM tasks
                WHERE project_id = %s;

                DELETE FROM projects_members
                WHERE project_id = %s;
                
                DELETE FROM requests_user_project
                WHERE project_id = %s;

                DELETE FROM projects
                WHERE project_id = %s;
                """,
                [projectId, projectId, projectId, projectId, projectId]
            )

    return Response({'message': 'Project deleted successfully'},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
def update_project(request):
    if request.method == 'POST':
        # Assuming you have the necessary data in the request
        project_description = request.data.get('description', '')
        project_priority = request.data.get('priority', '')
        project_status = request.data.get('status', '')
        project_id = request.data.get('projectId', '')
        start_date = request.data.get('startDate', None)
        end_date = request.data.get('endDate', None)

        # Construct your SQL update query
        if(start_date and end_date):
            sql = """
                UPDATE projects
                SET description = %s,
                    priority = %s,
                    status = %s,
                    start_date = %s,
                    end_date = %s
                WHERE project_id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(sql, [project_description, project_priority, project_status,start_date, end_date ,project_id])
        else:
            sql = """
                UPDATE projects
                SET description = %s,
                    priority = %s,
                    status = %s
                    WHERE project_id = %s
                """
            with connection.cursor() as cursor:
                cursor.execute(sql, [project_description, project_priority, project_status, project_id])


        return Response({'message': 'Project updated successfully'})

    return Response({'error': 'Invalid request method'}, status=405)

@api_view(['POST'])
def search_project(request):
    query = request.data.get('query')
    # Check if the query is a number (integer) or a string
    try:
        project_id = int(query)
        # If it's a number, search based on project_id
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM projects "
                "WHERE project_id = %s",
                [project_id]
            )
            projects = cursor.fetchall()
            project_data = [
                {
                    'projectId': project[0],
                    'ownerId': project[1],
                    'title': project[2],
                    'description': project[3],
                    'priority': project[4],
                    'status': project[5],
                    'start_date': project[6],
                    'end_date': project[7],
                    'color': project[8],
                    'members': []
                }
                for project in projects
            ]
            for project in projects_data :
                members = get_project_members_ids(project['projectId'])
                project['members'] = members

        return Response({"projects": project_data}, status=status.HTTP_200_OK)
    except ValueError:
        # If it's not a number, treat it as a string and search based on project_title
        with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM projects "
                    "WHERE LOWER(title) LIKE LOWER(%s)",
                    [f'%{query}%']
                )
                projects = cursor.fetchall()
        project_data = [
            {
                'projectId': project[0],
                'ownerId': project[1],
                'title': project[2],
                'description': project[3],
                'priority': project[4],
                'status': project[5],
                'start_date': project[6],
                'end_date': project[7],
                'color': project[8],
                'tasks': []
            }
            for project in projects
        ]
        for project in project_data:
            members = get_project_members_ids(project['projectId'])
            project['members'] = members
        return Response({"projects": project_data}, status=status.HTTP_200_OK)



def get_project_members_ids(projectId):
    with transaction.atomic():
        with connection.cursor() as cursor:
            # Update task status
            cursor.execute(
                """
                SELECT users.user_id
                FROM users
                INNER JOIN projects_members ON users.user_id = projects_members.user_id
                WHERE projects_members.project_id = %s;
                """,
                [projectId]
            )
            # Fetch all rows from the query result
            result = cursor.fetchall()
            print("hhehehhehehe", str(result))
        # Build a list of dictionaries for each user's information
        user_ids = [row[0] for row in result]
        print("hhehehhehehe", str(user_ids))

    return user_ids





















