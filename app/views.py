from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
import cv2
import numpy as np
import pytesseract
import os
import io
from django.urls import reverse
from pdf2image import convert_from_bytes
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from skimage.registration import phase_cross_correlation
import imutils
import tempfile
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from .forms import RegisterForm
from .models import CustomUserManager, CustomUser
from django.contrib.auth.models import User 
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy



# Create your views here.

def home_view(request):
    return render(request, 'home.html')

def review_view(request):
    return render(request, 'review/review_application.html')

from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import CustomUser

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = CustomUser.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                address=form.cleaned_data['address'],
                phone_number=form.cleaned_data['phone_number'],
                password=form.cleaned_data['password1']
            )
            user.save()
            return redirect('home/')
    else:
        form = RegisterForm()
    return render(request, 'registration/sign_up.html', {'form': form})


def cert_choice(request):
    return render(request, 'cert_choice.html')

def review_app(request):
    return render(request, 'review/review_application.html')

maxFeatures = 500
keepPercent=0.2
debug = False
@login_required
def ocr_view_birth(request):
    if request.method == 'POST':

        uploaded_file = request.FILES['image']
        file_extension = os.path.splitext(uploaded_file.name)[1]
        
        if file_extension == '.pdf':
            # Convert the PDF to an image
            with tempfile.TemporaryDirectory() as tempdir:
                pdf_bytes = uploaded_file.read()
                pdf_images = convert_from_bytes(pdf_bytes, output_folder=tempdir)
                if not pdf_images:
                    return HttpResponseBadRequest('Failed to convert PDF to image')
                image = np.array(pdf_images[0])
        else:
            # Load the image from the POST request
            image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

        # Load the template image
        template = cv2.imread('/Users/TA/Downloads/Ta W Mduluza Birth-NatID 1_page-0001(temp).jpg')

        # Resize the images
        image = cv2.resize(image, (773, 1000), fx = 0.5, fy =0.5)
        template = cv2.resize(template, (773, 1000), fx = 0.5, fy = 0.5)

        # Convert both images to grayscale
        imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Extract keypoints and features using ORB
        orb = cv2.ORB_create(maxFeatures)
        (kpsA, descsA) = orb.detectAndCompute(imageGray, None)
        (kpsB, descsB) = orb.detectAndCompute(templateGray, None)

        # Match the features using a brute-force Hamming distance matcher
        method = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
        matcher = cv2.DescriptorMatcher_create(method)
        matches = matcher.match(descsA, descsB, None)

        # Sort the matches by their distance and keep only the top matches
        matches = sorted(matches, key=lambda x:x.distance)
        keep = int(len(matches) * keepPercent)
        matches = matches[:keep]

        # Allocate memory for the keypoints coordinates and compute the homography matrix
        ptsA = np.zeros((len(matches), 2), dtype="float")
        ptsB = np.zeros((len(matches), 2), dtype="float")
        for (i, m) in enumerate(matches):
            ptsA[i] = kpsA[m.queryIdx].pt
            ptsB[i] = kpsB[m.trainIdx].pt

        (H, mask) = cv2.findHomography(ptsA, ptsB, method=cv2.RANSAC)

        # Use the homography matrix to align the images
        (h, w) = template.shape[:2]
        aligned = cv2.warpPerspective(image, H, (w, h))
        aligned = cv2.resize(aligned, (773, 1000), fx = 0.5, fy = 0.5)

        # Define the ROIs
        roi1 = aligned[280:300, 155:450] 
        roi2 = aligned[290:340, 220:390] 
        roi3 = aligned[260:390, 510:600]

        # Perform OCR on each ROI
        text1 = pytesseract.image_to_string(roi1)
        text2 = pytesseract.image_to_string(roi2)
        text3 = pytesseract.image_to_string(roi3)

        # Pass the OCR results to the template
        context = {
            'text1': text1,
            'text2': text2,
            'text3': text3,
        }
        return render(request, 'ocr output/ocr_output_birth.html', context)

    return render(request, 'birth_cert.html')

@login_required
def ocr_view_olevel(request):
    template = cv2.imread('/Users/TA/Downloads/Ta W Mduluza Birth-NatID 1_page-0001(temp).jpg', cv2.IMREAD_GRAYSCALE)
    if request.method == 'POST':
        #Check if image was uploaded
        if 'image' not in request.FILES:
            error_message = 'Please select an image to upload'
            if request.is_ajax():
                return JsonResponse({'error_message': error_message}, status=400)
            else:
                return render(request, 'olevel.html', {'error_message': error_message})
          
        uploaded_file = request.FILES['image']
        file_extension = os.path.splitext(uploaded_file.name)[1]
        
        if file_extension == '.pdf':
            # Convert the PDF to an image
            with tempfile.TemporaryDirectory() as tempdir:
                pdf_bytes = uploaded_file.read()
                pdf_images = convert_from_bytes(pdf_bytes, output_folder=tempdir)
                if not pdf_images:
                    return HttpResponseBadRequest('Failed to convert PDF to image')
                image = np.array(pdf_images[0])
        else:
        # Load the image from the POST request
            image = cv2.imdecode(np.fromstring(request.FILES['image'].read(), np.uint8), cv2.IMREAD_UNCHANGED)

        # Resize the image
        image = cv2.resize(image, (773, 1000), fx=0.5, fy=0.5)
        
        # Define the ROIs
        roi1 = image[270:330, 240:355] 
        roi2 = image[330:380, 50:290] 
        roi3 = image[370:420, 80:490]
        roi4 = image[480:510, 10:610]
        roi5 = image[500:525, 10:640]
        roi6 = image[500:525, 10:640]

        # Perform OCR on each ROI
        text1 = pytesseract.image_to_string(roi1)
        text2 = pytesseract.image_to_string(roi2)
        text3 = pytesseract.image_to_string(roi3)
        text4 = pytesseract.image_to_string(roi4)
        text5 = pytesseract.image_to_string(roi5)
        text6 = pytesseract.image_to_string(roi6)

        

        # Pass the OCR results to the template
        context = {
            'text1': text1,
            'text2': text2,
            'text3': text3,
            'text4': text4,
            'text5': text5,
            'text6': text6,
            'image': uploaded_file,

        }
        print(context['image'])  # Check the value of 'image'
        return render(request, 'ocr output/ocr_output_olevel_cam.html', context)
    return render(request, 'olevel_cam.html')

@login_required
def ocr_view_olevel_zim(request):
    template = cv2.imread('/Users/TA/Downloads/Ta W Mduluza Birth-NatID 1_page-0001(temp).jpg', cv2.IMREAD_GRAYSCALE)
    if request.method == 'POST':
        #Check if image was uploaded
        if 'image' not in request.FILES:
            error_message = 'Please select an image to upload'
            if request.is_ajax():
                return JsonResponse({'error_message': error_message}, status=400)
            else:
                return render(request, 'olevel.html', {'error_message': error_message})
          
        uploaded_file = request.FILES['image']
        file_extension = os.path.splitext(uploaded_file.name)[1]
        
        if file_extension == '.pdf':
            # Convert the PDF to an image
            with tempfile.TemporaryDirectory() as tempdir:
                pdf_bytes = uploaded_file.read()
                pdf_images = convert_from_bytes(pdf_bytes, output_folder=tempdir)
                if not pdf_images:
                    return HttpResponseBadRequest('Failed to convert PDF to image')
                image = np.array(pdf_images[0])
        else:
        # Load the image from the POST request
            image = cv2.imdecode(np.fromstring(request.FILES['image'].read(), np.uint8), cv2.IMREAD_UNCHANGED)

        # Resize the image
        image = cv2.resize(image, (773, 1000), fx=0.5, fy=0.5)
        
        # Define the ROIs
        roi1 = image[340:420, 90:290] 
        roi2 = image[340:430, 250:510] 
        roi3 = image[340:420, 500:690]
        roi4 = image[390:490, 90:290]
        roi5 = image[440:520, 90:690]

        # Perform OCR on each ROI
        text1 = pytesseract.image_to_string(roi1)
        text2 = pytesseract.image_to_string(roi2)
        text3 = pytesseract.image_to_string(roi3)
        text4 = pytesseract.image_to_string(roi4)
        text5 = pytesseract.image_to_string(roi5)


        # Pass the OCR results to the template
        context = {
            'text1': text1,
            'text2': text2,
            'text3': text3,
            'text4': text4,
            'text5': text5,

        }
        return render(request, 'ocr output/ocr_output_olevel_zim.html', context) 
    return render(request, 'olevel_zim.html')

@login_required
def ocr_view_alevel(request):
    template = cv2.imread('/Users/TA/Downloads/Ta Wiseman Mduluza A-O Cert 1_page-0001.jpg', cv2.IMREAD_GRAYSCALE)
    if request.method == 'POST':
          
        uploaded_file = request.FILES['image']
        file_extension = os.path.splitext(uploaded_file.name)[1]
        
        if file_extension == '.pdf':
            # Convert the PDF to an image
            with tempfile.TemporaryDirectory() as tempdir:
                pdf_bytes = uploaded_file.read()
                pdf_images = convert_from_bytes(pdf_bytes, output_folder=tempdir)
                if not pdf_images:
                    return HttpResponseBadRequest('Failed to convert PDF to image')
                image = np.array(pdf_images[0])
        else:
        # Load the image from the POST request
            image = cv2.imdecode(np.fromstring(request.FILES['image'].read(), np.uint8), cv2.IMREAD_UNCHANGED)

        # Resize the image
        image = cv2.resize(image, (773, 1000), fx=0.5, fy=0.5)
        
        # Define the ROIs
        roi1 = image[270:330, 240:355] 
        roi2 = image[330:380, 50:290] 
        roi3 = image[370:420, 80:490]
        roi4 = image[480:670, 10:610]

        # Perform OCR on each ROI
        text1 = pytesseract.image_to_string(roi1)
        text2 = pytesseract.image_to_string(roi2)
        text3 = pytesseract.image_to_string(roi3)
        text4 = pytesseract.image_to_string(roi4)

        lines4 = text4.split('\n')

        # Pass the OCR results to the template
        context = {
            'text1': text1,
            'text2': text2,
            'text3': text3,
            'text4': lines4,

        }
        return render(request, 'ocr output/ocr_output_alevel_cam.html', context)

    return render(request, 'alevel_cam.html')

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def review(request, app_customuser_id):
    details = CustomUser.objects.get(pk=app_customuser_id)
    return render(request, 'review/review_application.html', {'details': details})

@login_required
def alldata(request):
    user = request.user
    custom_user = CustomUser.objects.get(id=user.id)
    user_data = {
        'first_name': custom_user.first_name,
        'last_name': custom_user.last_name,
        'email': custom_user.email,
    }
    return render(request, 'review/review_application.html', {'user_data': user_data})

@login_required
def application_status(request):
    # Define the stages and their order
    stages = [
        {'name': 'Stage 1', 'completed': True},
        {'name': 'Stage 2', 'completed': False},
        {'name': 'Stage 3', 'completed': False},
        {'name': 'Stage 4', 'completed': False},
    ]
    
    # Count the number of completed stages
    completed_stages = sum(stage['completed'] for stage in stages)
    
    # Calculate the progress as a percentage
    progress = int(completed_stages / len(stages) * 100)
    
    # Render the template with the stages and progress
    return render(request, 'review/track_application.html', {'stages': stages, 'progress': progress})

class AdminLoginView(LoginView):
    template_name = 'admin/login.html'  # path to your login template
    redirect_authenticated_user = True  # redirect to index page if already authenticated
    success_url = reverse_lazy('admin:index')  # URL to redirect to after successful login
