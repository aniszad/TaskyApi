from django.shortcuts import render

from django.db import connection
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponseServerError

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

@api_view(['POST'])
def create_project_request(request):
    project_id = int(request.data.get('project_id'))
    user_id = int(request.data.get('user_id'))

    # Get project title from projects table
    with connection.cursor() as cursor:
        cursor.execute(
            """INSERT INTO requests_user_project (user_id, project_id, username, project_title)
            VALUES (%s, %s, (SELECT username FROM users WHERE user_id = %s),
            (SELECT title FROM projects WHERE project_id = %s))""",
            [user_id, project_id, user_id, project_id]
        )

    return Response({"message": "Project request created successfully"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def accept_request(request):

        projectId = int(request.data.get('project_id'))
        memberId = int(request.data.get('user_id'))
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
        transaction.commit()
        delete_request_fun(projectId, memberId)
        return Response({'message': 'Member added to project successfully'})


def delete_request_fun(projectId, memberId):
    with transaction.atomic():
        with connection.cursor() as cursor:
            # Check if the member already exists in the project
            cursor.execute(
                """
                DELETE FROM requests_user_project
                WHERE project_id = %s AND user_id = %s
                """,
                [projectId, memberId]
            )
    transaction.commit()

@api_view(['POST'])
def delete_request(request):
    projectId = int(request.data.get('project_id'))
    memberId = int(request.data.get('user_id'))
    with transaction.atomic():
        with connection.cursor() as cursor:
            # Check if the member already exists in the project
            cursor.execute(
                """
                DELETE FROM requests_user_project
                WHERE project_id = %s AND user_id = %s
                """,
                [projectId, memberId]
            )
    transaction.commit()
    return Response({'message': 'Request deleted successfully'})




@api_view(['POST'])
def get_requests_by_project(request):
    project_id = int(request.data.get('project_id'))

    # Execute raw SQL to retrieve requests from requests_user_project table for a specific project_id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM requests_user_project WHERE project_id = %s", [project_id])
        requests = cursor.fetchall()

    # Format the data as needed
    requests_data = [{'user_id': row[0], 'project_id': row[1], 'username': row[2], 'project_title': row[3]} for row in requests]

    return Response({"requests": requests_data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_requests_by_user(request):
    user_id = int(request.data.get('user_id'))

    # Execute raw SQL to retrieve requests from requests_user_project table for a specific project_id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM requests_user_project WHERE user_id = %s", [user_id])
        requests = cursor.fetchall()

    # Format the data as needed
    requests_data = [{'user_id': row[0], 'project_id': row[1], 'username': row[2], 'project_title': row[3]} for row in requests]

    return Response({"requests": requests_data}, status=status.HTTP_200_OK)






