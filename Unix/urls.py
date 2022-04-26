from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginPage, name='login'),
    path('signup/', views.signupPage, name='signup'),
    path('ServerDetails/', views.serverData, name='serverData'),
    path('logout/', views.logoutPage, name='logout'),
    path('index/', views.index, name='index'),
    path('Backup/', views.backup, name='backupArchive'),
    path('Processes/', views.process, name='processes'),
    path('Users/', views.users, name='manageUser'),
    path('DiskSpace/', views.diskSpace, name='diskSpace'),
    path('GraphicaAnalysis', views.graphicalAnalysis, name='graphicalAnalysis'),
    path('RunCommand/', views.runCommand, name='runCommand'),
    path('Error/', views.error, name='error')
]