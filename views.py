from django.shortcuts import render
from django.http import HttpResponse ,  JsonResponse
import zipfile
import os
import shutil
import numpy as np 
import cv2
from django.middleware.csrf import get_token
from django.template import Template, Context
from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

def members(request):
    return HttpResponse("Hello world!")





def are_images_same(img1, img2, threshold=0.8):

    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(img2, None)

 
    if not keypoints1 or not keypoints2:
        return False


    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)


    matches = sorted(matches, key=lambda x: x.distance)

    good_matches = [match for match in matches if match.distance < threshold * min(len(keypoints1), len(keypoints2))]
    

    return len(good_matches) / min(len(keypoints1), len(keypoints2)) > threshold



def compare_images_in_zip(zip_file, destination_folder, threshold=0.8):
    matched_image_names = []

    all_files_destination = []
    for root, dirs, files in os.walk(destination_folder):
        for file in files:
            all_files_destination.append(os.path.join(root, file))

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_file_images = zip_ref.namelist()

        for zip_image_name in zip_file_images:
            zip_image_data = zip_ref.read(zip_image_name)
            zip_image_array = np.frombuffer(zip_image_data, np.uint8)

            try:
                zip_image = cv2.imdecode(zip_image_array, cv2.IMREAD_GRAYSCALE)
            except cv2.error as e:
                print(f"Error decoding image {zip_image_name}: {str(e)}")
                continue

            for dest_image_path in all_files_destination:
                dest_image = cv2.imread(dest_image_path, cv2.IMREAD_GRAYSCALE)

                try:
                    if are_images_same(zip_image, dest_image, threshold):
                        matched_image_names.append((zip_image_name, os.path.basename(dest_image_path)))
                except cv2.error as e:
                    print(f"Error comparing images {zip_image_name} and {os.path.basename(dest_image_path)}: {str(e)}")
                    continue

    return matched_image_names



def upload_zip(request):
    if request.method == 'POST':
        # Extracting the uploaded zip file
        uploaded_file = request.FILES['zip_file']
        project_path = os.path.dirname(os.path.abspath(__file__))

        django_app_folder = os.path.join(project_path, 'my_django_app')

        destination_folder = os.path.join(BASE_DIR, 'media\extracted_folder')



        with open('temp.zip', 'wb') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

        result = compare_images_in_zip('temp.zip', destination_folder)

        print(result,'###########################')

        image_data = [{'folder_path': destination_folder, 'image_name': os.path.basename(dest),'image_': os.path.basename(_)} for _, dest in result]




        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Matched Images</title>
        </head>
        <body>

        <h2>Matched Images</h2>

        {% for image in image_data %}
            <div>
                <p>Folder Path: {{ image.folder_path }}</p>
                <p>Image Name: {{ image.image_name }}</p>
                <img src="/media/extracted_folder/{{ image.image_name }}" alt="Matched Image" height="200px" width="200px">
                <img src="/media/extracted_folder/{{ image.image_name }}" alt="Matched Image" height="200px" width="200px">
            </div>
        {% endfor %}

        </body>
        </html>
        """

        html_content = Template(html_template).render(Context({'image_data': image_data}))

        return HttpResponse(html_content)

    csrf_token = get_token(request)

    original_html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload Zip</title>
    </head>
    <body>

    <h2>Upload Zip</h2>

    <form method="post" enctype="multipart/form-data">
        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
        <input type="file" name="zip_file" accept=".zip" required>
        <button type="submit">Upload</button>
    </form>

    </body>
    </html>
    """
    
    return HttpResponse(original_html_content)
