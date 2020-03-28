from django.urls import path

from .views import MyTaskListView, TaskListView, TaskView, CreateTaskView, EditTaskView, FinishTaskView, ApplyTaskView, OpenOffersListView, AcceptedOffersListView, DeclinedOffersListView, AcceptTaskOfferView, DeclineTaskOfferView

urlpatterns = [
    path('', TaskListView.as_view()),
    path('offers', OpenOffersListView.as_view()),
    path('offers/accepted', AcceptedOffersListView.as_view()),
    path('offers/declined', DeclinedOffersListView.as_view()),
    path('offers/<int:id>/accept', AcceptTaskOfferView.as_view()),
    path('offers/<int:id>/decline', DeclineTaskOfferView.as_view()),
    path('my-task-list', MyTaskListView.as_view()),
    path('create', CreateTaskView.as_view()),
    path('<int:id>', TaskView.as_view()),
    path('<int:pk>/edit', EditTaskView.as_view()),
    path('<int:id>/finish', FinishTaskView.as_view()),
    path('<int:id>/apply', ApplyTaskView.as_view())
]
