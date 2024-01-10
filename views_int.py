import os
from zipfile import ZipFile
import zipfile
import numpy as np
import cv2
# from aifc import _File
from django.middleware.csrf import get_token
from django.db.models import *
from django.core.files import File
from django.core.files.base import ContentFile
import tempfile
from django.shortcuts import render
import csv
from django.db import transaction
import pandas as pd
import json
from django.http import HttpResponseRedirect, JsonResponse
from .models import *
from shell.settings import MEDIA_ROOT

# Create your views here.
global_temp_filepath_1 = None
global_temp_filepath_2 = None
global_temp_filepath_3 = None

def FileUpload(request):
    global global_temp_filepath_1, global_temp_filepath_2, global_temp_filepath_3

    if request.method == 'POST':
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as trackerfile_temp:
                trackerfile = request.FILES.get('trackerfile')
                trackerfile_temp.write(trackerfile.read())
                global_temp_filepath_1 = trackerfile_temp.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as pdf_temp:
                planogram_pdfs = request.FILES.get('planogram_pdf')
                pdf_temp.write(planogram_pdfs.read())
                global_temp_filepath_2 = pdf_temp.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as image_temp:
                planogram_image = request.FILES.get('planogram_image')
                image_temp.write(planogram_image.read())
                global_temp_filepath_3 = image_temp.name

            print(global_temp_filepath_1, global_temp_filepath_2, global_temp_filepath_3)

            duplicate_images = compare_temp_image(global_temp_filepath_3,MEDIA_ROOT)
                
            # if not duplicate_images:
            return render(request, 'pages/comp.html', {'duplicate_images': duplicate_images})


            result = FileUploa(global_temp_filepath_1, global_temp_filepath_2, global_temp_filepath_3)

            if result == 1:
                return render(request, 'pages/upload.html')

        except Exception as er:
            print(er)
            responseData = {'status': 'failed', 'result': "Error processing files"}
            return JsonResponse(responseData)

    else:
        return render(request, 'pages/upload.html')


def loginView(request):
    if request.method == 'POST':     
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username,password)

        if username == "admin" and password == "admin":
            return render(request, 'index.html')  
        
        elif username == "user" and password == "user":
            return HttpResponseRedirect('/userpage/')
        else:  
            return render(request, 'pages/registration/login.html')        
    else:
        return render(request, 'pages/registration/login.html')
    
def logoutView(request):
    request.session.flush()
    request.session.clear()
    request.session.clear_expired()
    return HttpResponseRedirect('/dash/')


def home(request):
    return render(request, 'index.html')

def cancel(request):
    return render(request, 'pages/upload.html')

def continueButton(request):

    if request.method == 'GET':
         FileUploa(global_temp_filepath_1,global_temp_filepath_2,global_temp_filepath_3)
         return render(request, 'pages/upload.html')

def FileUploa(global_temp_filepath_1,global_temp_filepath_2,global_temp_filepath_3)  :

        print(global_temp_filepath_1,global_temp_filepath_2,global_temp_filepath_3)

        pdf_zip_ref = ZipFile(global_temp_filepath_1, 'r')
        pdf_file_infos = pdf_zip_ref.infolist()
        

        imgs_zip_ref = ZipFile(global_temp_filepath_2, 'r')
        imgs_file_infos = imgs_zip_ref.infolist()

        excel_data = pd.read_csv(global_temp_filepath_3)
        to_dict = excel_data.to_dict('records')
        try:
            with transaction.atomic():
                last_RECD = Trackerfile_data.objects.order_by('-id').first()
                if last_RECD:
                    last_id = int(last_RECD.cycle[5:])
                    new_id = last_id + 1
                else:
                    new_id = 1
                cycle = f'CYCLE{new_id:05}'
                cyclename = cycle + '/'

                for PdfFIle in pdf_file_infos:
                    pdf_filename = PdfFIle.filename
                    pdf_FileNames = pdf_filename.split("/")[-1]
                    movedPDFfilename = cyclename + 'PlanogramPDF/' + \
                            str(pdf_FileNames)
                    if pdf_filename.endswith('.pdf'):
                        pdf_file = pdf_zip_ref.read(pdf_filename)
                        pdf_instance = PlanogramePDF.objects.create(
                                planograme_pdf=ContentFile(pdf_file, name=movedPDFfilename)
                            )
                        for i in to_dict:
                            if i['Planogram Name'] in pdf_FileNames:
                                trackerid = Trackerfile_data.objects.create(
                                        cycle = cycle,
                                        store_number = i.get('Store Number',None),
                                        four_digit_store_number = i.get('4 - Digit Store Number',None),
                                        store_name = i.get('Store Name',None),
                                        department_name = i.get('Department Name',None),
                                        planogram_type = i.get('Planogram Type',None),
                                        planogram_name = i.get('Planogram Name',None),
                                        no_of_skus = i.get('No. of SKUs',None),
                                        # no_of_missing_skus = i.get('No. of Missing SKUs',None),
                                        # incorrectly_placed_skus = i.get('Incorrectly placed SKUs',None),
                                        # workable_non_workable = i.get('Workable/Non-Workable',None),
                                        # Image_Qualified_for_Compliance = i.get('Image Qualified for Compliance',None),
                                        # No_of_Bays = i.get('No. of Bays',None),
                                        # No_of_Shelves = i.get('No. of Shelves',None),
                                        # Size_of_Bays = i.get('Size of Bays',None),
                                        # Status = i.get('Status',None),
                                        # Remarks = i.get('Remarks',None),

                                        Completed_Date = i.get('Completed Date',None),
                                        Allocation = i.get('Allocation',None),
                                        planograme_pdf_id = pdf_instance.id
                                    )
                                
                                for img_file_info in imgs_file_infos:
                                    img_filename = img_file_info.filename   
                                    img_FileNames = img_filename.split("/")[-1]
                                    foldername = img_filename.split("/")[1]
                                    base_path = img_filename.split("/")[0]
                                    moved_img_filename = f"{cyclename}{'Store-Images/'}{img_filename[len(base_path):]}"
                                    if img_filename.endswith('.jpg') and str(i['Planogram Type']) in foldername and str(i['4 - Digit Store Number']) in img_FileNames:
                                        img_file =  imgs_zip_ref.read(img_filename)
                                        storeImages.objects.create(
                                            trackerfile_id=trackerid.id,planogram_id = pdf_instance.id,
                                            store_images=ContentFile(img_file, name=moved_img_filename)
                                        )

                responseData = {'status': 'success',
                                'result': 'Data Upload Successfully'}
                return 1
        except Exception as er:
            print(er)
            responseData = {'status': 'failed',
                            'result': ",File Already Exist"}
            return JsonResponse(responseData)

    
def tracker_production(request):
    if request.method == 'POST':
        idval = request.POST.get('idval')
        no_of_missing_skus = request.POST.get('no_of_missing_skus')
        incorrectly_placed_skus = request.POST.get('incorrectly_placed_skus')
        workable_non_workable = request.POST.get('workable_non_workable')
        Image_Qualified_for_Compliance = request.POST.get('Image_Qualified_for_Compliance')
        No_of_Bays = request.POST.get('No_of_Bays')
        No_of_Shelves = request.POST.get('No_of_Shelves')
        Size_of_Bays = request.POST.get('Size_of_Bays')
        Status = request.POST.get('Status')
        Remarks = request.POST.get('Remarks')
        print(idval,no_of_missing_skus,incorrectly_placed_skus,workable_non_workable,Image_Qualified_for_Compliance,No_of_Bays,No_of_Shelves,Size_of_Bays,Status,Remarks)
        Trackerfile_data.objects.filter(id = idval).update(no_of_missing_skus = no_of_missing_skus,
                                            incorrectly_placed_skus = incorrectly_placed_skus,
                                            workable_non_workable = workable_non_workable,
                                            Image_Qualified_for_Compliance = Image_Qualified_for_Compliance,
                                            No_of_Bays = No_of_Bays,
                                            No_of_Shelves = No_of_Shelves,
                                            Size_of_Bays = Size_of_Bays,
                                            Status = Status,
                                            Remarks = Remarks,production_status = "completed")
    else:
        with transaction.atomic():
            instance = Trackerfile_data.objects.select_for_update(skip_locked=True).filter(
                            Q(status='picked') | Q(status='not_picked')).values('id','store_number','four_digit_store_number','department_name', 'planogram_type','planogram_name','no_of_skus','planograme_pdf_id').order_by('-production_status','store_number').exclude(status='one').first()
            Trackerfile_data.objects.filter(id = instance['id']).update(production_status = "picked")
            planogrampdf = PlanogramePDF.objects.filter(id=instance['planograme_pdf_id']).values('planograme_pdf')
            storeimg = storeImages.objects.filter(trackerfile_id = instance['id'],planogram_id = instance['planograme_pdf_id']).values('store_images')

        return render(request, 'pages/tracker_production.html',{'trackingdata':instance,'planogrampdf':planogrampdf,'storeimg':storeimg})

def userpage(request):
    return render(request, 'pages/userpage.html')


def compare_temp_image(temp_image_path, media_root):
    duplicate_images = None

    with zipfile.ZipFile(temp_image_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        zip_data = {name: zip_ref.read(name) for name in file_list}

    duplicate_images = find_duplicate_images(zip_data, media_root)

    return duplicate_images
    
def find_duplicate_images(zip_data, directory):
    duplicate_images = []

    
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)

            
            for zip_filename, zip_file_content in zip_data.items():
                if compare_images_opencv(zip_file_content, path):
                    duplicate_images.append((zip_filename, path))

    return duplicate_images

def compare_images_opencv(zip_image_content, existing_image_path):
    
    existing_image = cv2.imread(existing_image_path)
    
    if existing_image is None:
        return False  

    try:
        
        zip_image = cv2.imdecode(np.frombuffer(zip_image_content, np.uint8), -1)
    except cv2.error as e:
        print(f"Error decoding image: {e}")
        return False

   
    if zip_image is not None and zip_image.size != 0:
        
        if existing_image.shape == zip_image.shape:
            difference = cv2.subtract(existing_image, zip_image)
            b, g, r = cv2.split(difference)
            if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                return True  

    return False

def process_selected_duplicates(request):
    if request.method == 'POST':
        selected_images = request.POST.getlist('selected_images[]')
        print("Selected Images:", selected_images)
        return JsonResponse({'status': selected_images})

    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
