"""
URL configuration for TaskyApi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from TaskyApiP.users import views as users_views
from TaskyApiP.projects import views as projects_views
from TaskyApiP.tasks import views as tasks_views
from TaskyApiP.request import views as request_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sign_up/', users_views.sign_up, name="sign_up"),
    path('sign_in/', users_views.sign_in, name="sign_in"),
    path('get_user/', users_views.get_user, name="get_user"),
    path('search_users/', users_views.search_users, name="search_users"),
    path('create_project/', projects_views.create_project, name="create_project"),
    path('get_my_projects/', projects_views.get_my_projects, name="get_my_projects"),
    path('get_project_owner/', projects_views.get_project_owner, name="get_project_owner"),
    path('get_involved_projects/', projects_views.get_involved_projects, name="get_involved_projects"),
    path('delete_project/', projects_views.delete_project, name="delete_project"),
    path('update_project/', projects_views.update_project, name="update_project"),
    path('get_project_members/', projects_views.get_project_members, name="get_project_members"),
    path('get_my_project_tasks/', tasks_views.get_project_tasks, name="get_project_tasks"),
    path('create_task/', tasks_views.create_task, name="create_task"),
    path('get_completed_tasks/', tasks_views.get_completed_tasks, name="get_completed_tasks"),
    path('update_task/', tasks_views.update_task, name="update_task"),
    path('delete_task/', tasks_views.delete_task, name="delete_task"),
    path('get_task_members/', tasks_views.get_task_members, name="get_task_members"),
    path('search_tasks/', tasks_views.search_tasks, name="search_tasks"),
    path('add_member_to_project/', projects_views.add_member_to_project, name="add_member_to_project"),
    path('delete_project_member/', projects_views.delete_project_member, name="delete_project_member"),
    path('create_project_request/', request_views.create_project_request, name="create_project_request"),
    path('accept_request/', request_views.accept_request, name="accept_request"),
    path('delete_request/', request_views.delete_request, name="delete_request"),
    path('get_requests_by_project/', request_views.get_requests_by_project, name="get_requests_by_project"),
    path('get_requests_by_user/', request_views.get_requests_by_user, name="get_requests_by_user"),
    path('search_project/', projects_views.search_project, name="search_project")
]
