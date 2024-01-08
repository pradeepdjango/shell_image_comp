from django.shortcuts import render
from django.http import HttpResponse ,  JsonResponse
import zipfile
import os
import shutil
import numpy as np 
import cv2
from django.middleware.csrf import get_token

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
            zip_image = cv2.imdecode(zip_image_array, cv2.IMREAD_GRAYSCALE)

            for dest_image_path in all_files_destination:
                dest_image = cv2.imread(dest_image_path, cv2.IMREAD_GRAYSCALE)

                if are_images_same(zip_image, dest_image, threshold):
                    matched_image_names.append((zip_image_name, os.path.basename(dest_image_path)))

    return matched_image_names


def upload_zip(request):
    if request.method == 'POST':
        # Extracting the uploaded zip file
        uploaded_file = request.FILES['zip_file']
        project_path = os.path.dirname(os.path.abspath(__file__))

        django_app_folder = os.path.join(project_path, 'my_django_app')

        destination_folder = django_app_folder+'\extracted_folder'

        with open('temp.zip', 'wb') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

        
        result = compare_images_in_zip('temp.zip', destination_folder)


        # Return the result as JSON for JavaScript to handle
        return JsonResponse({'message': result})


    csrf_token = get_token(request)


    html_content = f"""
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


    return HttpResponse(html_content)

# def are_images_same(img1, img2, threshold=0.8):

#     orb = cv2.ORB_create()
#     keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
#     keypoints2, descriptors2 = orb.detectAndCompute(img2, None)


#     if not keypoints1 or not keypoints2:
#         return False

   
#     bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
#     matches = bf.match(descriptors1, descriptors2)

   
#     matches = sorted(matches, key=lambda x: x.distance)

 
#     good_matches = [match for match in matches if match.distance < threshold * min(len(keypoints1), len(keypoints2))]
    
   
#     return len(good_matches) / min(len(keypoints1), len(keypoints2)) > threshold

# def compare_images_in_zip(zip_file_path, destination_folder, threshold=0.8):
   
#     all_files_destination = []
#     for root, dirs, files in os.walk(destination_folder):
#         for file in files:
#             all_files_destination.append(os.path.join(root, file))

  
#     zip_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), zip_file_path)

    
#     with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
#         zip_file_images = zip_ref.namelist()

        
#         for zip_image_name in zip_file_images:
#             zip_image_data = zip_ref.read(zip_image_name)
#             zip_image_array = np.frombuffer(zip_image_data, np.uint8)
#             zip_image = cv2.imdecode(zip_image_array, cv2.IMREAD_GRAYSCALE)

#             for dest_image_path in all_files_destination:
#                 dest_image = cv2.imread(dest_image_path, cv2.IMREAD_GRAYSCALE)

               
#                 if are_images_same(zip_image, dest_image, threshold):
#                     print(f"The images {zip_image_name} and {os.path.basename(dest_image_path)} are the same.")


# project_path = os.path.dirname(os.path.abspath(__file__))

# django_app_folder = os.path.join(project_path, 'my_django_app')


# zip_file_path = django_app_folder+'\zipfile.zip' 
# destination_folder = django_app_folder+'\extracted_folder'
# compare_images_in_zip(zip_file_path, destination_folder)
