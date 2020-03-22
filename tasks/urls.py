from django.urls import path

from .views import TaskListView, TaskView, CreateTaskView, EditTaskView

urlpatterns = [
    path('', TaskListView.as_view()),
    path('create', TaskView.as_view()),
    path('<int:id>', TaskView.as_view()),
    path('<int:id>/edit', EditTaskView.as_view())
]
