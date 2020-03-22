from django.urls import path

from .views import TaskListView, TaskView, CreateTaskView, EditTaskView, FinishTaskView, ParticipateTaskView

urlpatterns = [
    path('', TaskListView.as_view()),
    path('create', CreateTaskView.as_view()),
    path('<int:id>', TaskView.as_view()),
    path('<int:id>/edit', EditTaskView.as_view()),
    path('<int:id>/finish', FinishTaskView.as_view()),
    path('<int:id>/participate', ParticipateTaskView.as_view())
]
