# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import dialogflow
import os
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Order
import argparse
import uuid
from django.contrib.auth.forms import UserCreationForm 
#from dialogflow_v2 import dialogflow_v2 as Dialogflow
# Create your views here.
from django.contrib import messages 
from .forms import UserRegistrationForm
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.auth.forms import User
@require_http_methods(['GET'])
def index_view(request):
    return render(request, 'chathome.html')

def home_view(request):
    return render(request, 'home.html')

def reg_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # user.profile.email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            messages.success(request,"Account Created for %s is created. Login!" %username)
            return redirect('login') 
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form':form})

def convert(data):
    if isinstance(data, bytes):
        return data.decode('ascii')
    if isinstance(data, dict):
        return dict(map(convert, data.items()))
    if isinstance(data, tuple):
        return map(convert, data)

    return data

# @csrf_exempt
# @require_http_methods(['POST'])
# def webhook(request):
#     # build a request object
#     # input_dict = convert(request.body)
#     # print(input_dict)
#     print("efsghfeh")
#     input_text = json.loads(request.body)
#     print(input_text)
    
#     order_id = input_text['queryResult']['parameters']['orderid']
#     if(order_id != ''):
#         order_id = int(order_id)
#     print(order_id)
#     order = Order.objects.filter(orderid = order_id).first()
#     context_name = input_text['queryResult']['outputContexts'][0]['name']

#     print(context_name)
#     # get action from json
#     # action = request.get('queryResult').get('action')
#     # return a fulfillment message
#     # order = Order.objects.get(orderid = input_text)
#     # print(type(order))
#     # print(order.orderid) 
#     # print(order_reply)
#     # ff_response = fulfillment_response()
#     if(order != None):
#         reply = {
#                 "fulfillmentMessages": [
#                     {
#                     "text": {
#                         "text": [
                            
#                             'Order ID: ' + order.orderid + '\nOrder Name: ' + order.name + '\nOrder Details: ' + order.details + '\nOrder Status: ' + order.status + '\nOrder Date: ' + str(order.date_ordered) 

#                         ]
#                     }
#                     }
#                 ]
#                 }
#     else:

#         reply = ' order id you enetered is not valid. Please enter a valid order id'
     
#         reply = {
#                 "fulfillmentMessages": [
#                     {
#                     "text": {
#                         "text": [
                            
#                             'The' + reply

#                         ]
#                     }
#                     }
#                 ]
#                 }
#     print(reply)
#     return JsonResponse(reply, safe = False)

@csrf_exempt
@require_http_methods(['POST'])
def chat_view(request):
    if request.user.is_authenticated:
        print('Body', request.body)
        input_dict = convert(request.body)
        input_text = json.loads(input_dict)['text']

        GOOGLE_AUTHENTICATION_FILE_NAME = "AppointmentScheduler.json"
        current_directory = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(current_directory, GOOGLE_AUTHENTICATION_FILE_NAME)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

        GOOGLE_PROJECT_ID = "ivr-bot-goug"
        session_id = "1234567891"
        context_short_name = "does_not_matter"

        context_name = "projects/" + GOOGLE_PROJECT_ID + "/agent/sessions/" + session_id + "/contexts/" + \
                context_short_name.lower()

        parameters = dialogflow.types.struct_pb2.Struct()
        #parameters["foo"] = "bar"

        context_1 = dialogflow.types.context_pb2.Context(
            name=context_name,
            lifespan_count=2,
            parameters=parameters
        )
        # print(context_1)
        query_params_1 = {"contexts": [context_1]}

        language_code = 'en'
        
        response = detect_intent_with_parameters(
            project_id=GOOGLE_PROJECT_ID,
            session_id=session_id,
            query_params=query_params_1,
            language_code=language_code,
            user_input=input_text
        )
        print("hfeifbfrif")
        print(response)
        print(response.query_result.parameters.fields["orderid"].number_value)
        order_id = int(response.query_result.parameters.fields["orderid"].number_value)
        # if(response.query.fullfillment_text == "order id"):
        print(order_id)
        if(order_id !=  0):
            order = Order.objects.filter(orderid = order_id).first()
            if(order != None):
                print(type(order))
                print(order.orderid)
                order_reply = 'Order ID: ' + order.orderid + '\nOrder Name: ' + order.name + '\nOrder Details: ' + order.details + '\nOrder Status: ' + order.status + '\nOrder Date: ' + str(order.date_ordered)
                response.query_result.fulfillment_messages[0].text.text[0] = order_reply
                # print(order_reply)
                # return HttpResponse(order_reply, status=200)
            else:
                order_reply = 'The order id you enetered is not valid. Please enter a valid order id'
                response.query_result.fulfillment_messages[0].text.text[0] = order_reply
                # return HttpResponse(order_reply, status=200)
        if(response.query_result.intent.display_name == "appointment schedule - yes"):
            print(response.query_result.output_contexts[0].parameters.fields["time"].string_value)
            subject = 'A meeting scheduled with a client'
            message = render_to_string('mail.html', {
                'time': response.query_result.output_contexts[0].parameters.fields["time"].string_value[11:-6], 
                'date': response.query_result.output_contexts[0].parameters.fields["date"].string_value[0:10], 
                'user' : User.objects.filter(username = request.user.username).first().username
            })
            print(User.objects.filter(username = request.user.username).first().username)
            if(response.query_result.output_contexts[0].parameters.fields["department"].string_value == "IT"):
                to_email = 'ivrtestit123@gmail.com'
            else:
                to_email = 'canbecreated@gmail.com'
            email_user = EmailMessage(subject, message, to=[to_email])
            email_user.send()
        print(response.query_result.fulfillment_messages[0].text.text[0])

        return HttpResponse(response.query_result.fulfillment_messages[0].text.text[0], status=200)
    else:
        return HttpResponse("Please Login to continue", status=200)

def detect_intent_with_parameters(project_id, session_id, query_params, language_code, user_input):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversaion."""
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session))

    #text = "this is as test"
    text = user_input

    text_input = dialogflow.types.TextInput(
        text=text, language_code=language_code)

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
        session=session, query_input=query_input,
        query_params=query_params
    )

    print('=' * 20)
    print('Query text: {}'.format(response.query_result.query_text))
    print('Detected intent: {} (confidence: {})\n'.format(
        response.query_result.intent.display_name,
        response.query_result.intent_detection_confidence))
    print('Fulfillment text: {}\n'.format(
        response.query_result.fulfillment_text))

    return response

    

def about(request):
    return render(request, 'chat/about.html')
