from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework import status
from django.db import connection
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
import jwt, datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password

@api_view(['POST'])
def sign_up(request):
    if request.method == 'POST':
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        hashed_password = make_password(password)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, password, first_name, last_name, is_superuser, is_staff, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [username, email, hashed_password, first_name, last_name, False, False, True]
            )
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def sign_in(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE users.username = %s", [username])
            user_data = cursor.fetchone()
        if user_data:
            user_id, stored_password = user_data[0], user_data[1]
            if check_password(password, stored_password):
                # Passwords match, authentication successful
                return Response({'message': 'Authentication successful', 'userId': user_id}, status=200)
            else:
                # Passwords do not match
                return Response({'error': 'Invalid credentials'}, status=400)
        else:
            # User not found
            return Response({'error': 'Invalid credentials'}, status=403)
    else:
        return Response({'error': 'Invalid request method'}, status=400)

@api_view(['POST'])
def get_user(request):
    user_id = int(request.data.get('userId'))
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE users.user_id = %s", [user_id])
        user_data = cursor.fetchone()
        user = {
            'memberId': user_data[0],
            'username': user_data[4],
            'first_name': user_data[5],
            'last_name': user_data[6],
        }
        return Response({'user' : user}, status=200)

@api_view(['POST'])
def search_users(request):
    query = request.data.get('query')
    # Check if the query is a number (integer) or a string
    try:
        user_id = int(query)
        # If it's a number, search based on project_id
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users "
                "WHERE user_id = %s",
                [user_id]
            )
            users = cursor.fetchall()
            users_data = [
                 {
                'memberId': user[0],
                'username': user[4],
                'first_name': user[5],
                'last_name': user[6],
            }
                for user in users
            ]

        return Response({"users": users_data}, status=status.HTTP_200_OK)
    except ValueError:
        # If it's not a number, treat it as a string and search based on project_title
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users "
                "WHERE LOWER(username) LIKE LOWER(%s)",
                [f'%{query}%']
            )
            users = cursor.fetchall()
            users_data = [
                {
                    'memberId': user[0],
                    'username': user[4],
                    'first_name': user[5],
                    'last_name': user[6],
                    'email': user[7]
                }
                for user in users
            ]

        return Response({"users": users_data}, status=status.HTTP_200_OK)




