from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('articles/', views.articles_list, name="articles-list"),
    path('articles/<int:article_id>/', views.article_details, name="article-details"),
    path('create/', views.create_article, name="create-article"),
]