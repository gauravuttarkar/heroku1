"""
Different functions required for angular
"""
#import uuid

#from django.conf import settings
import json
from django.http import HttpResponse
from django.shortcuts import render
from yellowant import YellowAnt
#from django.urls import reverse
from yellowant_api.models import UserIntegration, azure
#from .forms import UserForm
#from django.contrib.auth import authenticate, login


#import requests
# Create your views here.


def index(request, path):
    """Index of the user Integration."""
    context = {
        "user_integrations": []
    }
    print("Inside index")
    if request.user.is_authenticated:
        user_integrations = UserIntegration.objects.filter(user=request.user)
        print(user_integration)
        for user_integration in user_integrations:
            print(user_integration," inside for loop")
            context["user_integrations"].append(user_integration)
    print("returning from index")
    return render(request, "home.html", context)

def userdetails(request):
    """
    Returns the details of each user in a list.
    """
    user_integrations_list = []
    if request.user.is_authenticated:

        user_integrations = UserIntegration.objects.filter(user=request.user)
        print('Got user integrations from userdetails function')
        for user_integration in user_integrations:
            print (user_integration.yellowant_integration_invoke_name)
            print (user_integration.id)

            try:
                smut = azure.objects.get(user_integration_id=user_integration.id)
                user_integrations_list.append(
                    {"user_invoke_name":user_integration.yellowant_integration_invoke_name,
                     "id":user_integration.id,
                     "app_authenticated":True, "is_valid":smut.AZURE_update_login_flag})
            except: #user_integration.DoesNotExist:
                user_integrations_list.append({"user_invoke_name": user_integration.yellowant_integration_invoke_name,
                                               "id": user_integration.id, "app_authenticated":False})
    print("User integration list",user_integrations_list)
    return HttpResponse(json.dumps(user_integrations_list), content_type="application/json")

def delete_integration(request, id=None):
    """Function to delete an integration."""
    print("In delete_integration")
    #print(id)
    access_token_dict = UserIntegration.objects.get(id=id)
    access_token = access_token_dict.yellowant_integration_token
    user_integration_id = access_token_dict.yellowant_integration_id
    #print(user_integration_id)
    #"https://api.yellowant.com/api/user/integration/%s" % (user_integration_id)
    yellowant_user = YellowAnt(access_token=access_token)
    yellowant_user.delete_user_integration(id=user_integration_id)
    UserIntegration.objects.get(yellowant_integration_token=access_token).delete()
    #print(response_json)
    return HttpResponse("successResponse", status=200)


def view_integration(request, id=None):
    """
    Function to View an integration when it is clicked.
    """
    print("In view_integration")
    #print(id)
    access_token_dict = UserIntegration.objects.get(id=id)
    access_token = access_token_dict.yellowant_integration_token
    user_integration_id = access_token_dict.yellowant_integration_id
    print(user_integration_id)
    url = "https://api.yellowant.com/api/user/integration/%s" % (user_integration_id)
    yellowant_user = YellowAnt(access_token=access_token)
    yellowant_user.delete_user_integration(id=user_integration_id)
    #print(response_json)
    return HttpResponse("successResponse", status=200)
