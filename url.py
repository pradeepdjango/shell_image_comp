from django.conf.urls.static import static

urlpatterns = [

    ######################### Productions ####################################
    path('home/', home, name='home'),
    path('upload/', FileUpload, name='upload'),
    path('process_duplicates/', process_selected_duplicates, name='process_selected_duplicates'),
    path('tracker_production/', tracker_production, name='tracker_production'),
    path('continueButton/', continueButton, name='continueButton'),
    path('cancel/', cancel, name='cancel'),

    path('upc/', upc, name='upc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
