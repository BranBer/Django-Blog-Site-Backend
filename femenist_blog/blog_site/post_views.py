from django.shortcuts import render
from django.http import JsonResponse
from blog_site.models import *
from blog_site.serializers import *
from rest_framework.decorators import api_view
from datetime import datetime

from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import random
import string

from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from django.contrib.auth.decorators import user_passes_test


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active and user.is_superuser)
def Create_Blog_Post(request):
    #Get the token header
    authToken = request.headers.get('Authorization')[6:] if request.headers.get('Authorization') else ''
    user = Token.objects.filter(key = authToken)
    
    if(user.count() > 0):
        data = request.data
        images = []

        date = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S")

        blog_post = Blog_Post(
            post_title = data['post_title'], 
            author = data['author'],
            post_content = data['post_content'],
            date = date
            )

        blog_post.save()
       
        #Sift through images in data and create a blog post image for each 
        for key in data.keys():
            if(key[0:5] == 'image'):
                if(data[key] is not None):
                    img = Blog_Post_Image(blog_post = blog_post, image = data[key])
                    img.save()

         #Send newsletter to all subscribed users
        port = 465
        context = ssl.create_default_context()
        account = os.environ['SMTP_ACCOUNTS'].split(',')[0].split(':')

        sender = account[0]
        password = account[1]

        #Get subscribed users
        subbedUsers = User.objects.filter(subscribed = True)

        if(subbedUsers.exists()):
            for user in subbedUsers:
                recepient = user.email

                date = blog_post.date

                msg = MIMEMultipart('alternative')
                msg['Subject'] = "Newsletter Subscription: New Post! " + user.username
                msg['From'] = sender
                msg['To'] = recepient
                url = '/post/' + str(blog_post.id) +"/"

                html = """
                    <html>
                        <head>
                            <style>
                                body{{
                                    display: flex;
                                    flex-direction: column;
                                    align-items: center;
                                    background-image: linear-gradient(to bottom, #FF6565, rgba(0,0,0,0.0));
                                    color: black;
                                }}

                                .header
                                {{
                                    background-color = #FF6565;
                                    color: white;
                                    font-size: 24px;
                                    font-weight: bold;
                                    text-align: center;
                                }}

                                label{{
                                    font-weight: bold;     
                                    text-decoration: underline;                           
                                }}
                            </style>
                        </head>

                        <body>
                            <div className = 'header'>
                                <h2>New Post!</h2>
                            </div>
                            <p>Dear {},</p>
                            <br/>
                            <br/>
                            <p>Check out my new post! You can find this post at <a href = "{}">{}</a>. Be sure to give it a like! </p>
                            <br/>
                            <br/>
                            <p>Sincerely,</p>
                            <br/>
                            <p>Sarah</p>
                            <br/>
                            <sub>{}</sub>
                        </body>

                    </html>
                """.format(user.display_name, url, url, date)

                part1 = MIMEText(html, 'html')
                msg.attach(part1)

                with smtplib.SMTP_SSL("smtp.gmail.com", port, context = context) as server:
                    server.login(sender, password)
                    server.sendmail(sender, recepient, msg.as_string())

        return JsonResponse(Blog_Post_Ser(blog_post, many = False).data, safe = False)
    else:
        return JsonResponse("Login first", safe = False)

@api_view(['POST'])
def Create_Blog_Post_By_You(request):
    data = request.data
    data._mutable = True

    if('post_content' not in data.keys()):
        return JsonResponse("Must include post_content in body", safe = False, status = 401)
    elif(data['post_content'] == ''):
        return JsonResponse("Must include post_content in body", safe = False, status = 401)

    if('post_title' not in data.keys()):
        return JsonResponse("Must include post_title in body", safe = False, status = 401)
    elif(data['post_title'] == ''):
        return JsonResponse("Must include post_title in body", safe = False, status = 401)
        
    if('author' not in data.keys()):
        data['author'] = 'anonymous'

    date = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S")

    blog_post = Blog_Post(
        post_title = data['post_title'], 
        author = data['author'],
        post_content = data['post_content'],
        date = date,
        isMainPost = False,
        isVisible = False,
        )

    blog_post.save()

    return JsonResponse(Blog_Post_Ser(blog_post, many = False).data, safe = False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active)
def UpdateBlogPostVisibility(request):
    data = request.data

    if('id' in data.keys()):
        try:
            authtoken = request.headers.get('Authorization')[6:] if request.headers.get('Authorization') else ''
            isSuperUser = Token.objects.get(key = authtoken).user.isSuperUser

            if(isSuperUser):
                blog_post = Blog_Post.objects.get(id = int(request.data['id']))
                blog_post.isVisible = not blog_post.isVisible
                blog_post.save(update_fields=['isVisible'])
            else:
                return JsonResponse('Not Authorized', safe = False, status = 401)

            return JsonResponse('Successfully Updated Post Visibility', safe = False)
        except Blog_Post.DoesNotExist:
            return JsonResponse('No Posts Found', safe = False)
        except Token.DoesNotExist:
            return JsonResponse('Not Authorized', safe = False, status = 401)

    return JsonResponse('Must include id in body')

@api_view(['POST'])
def Login(request):
    if('username' in request.data.keys() and 'password' in request.data.keys()):
        user = authenticate(username = request.data['username'], 
                            password = request.data['password'])

        if(user is not None):
            token = Token.objects.get(user = user).key

            return JsonResponse( {
                'username': user.username,
                'token': token
            }, safe = False)
        else:
            return JsonResponse("Invalid Credentials", safe = False, status = 401)

    return JsonResponse("Must Input Username and Password!", safe = False)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active)
def DeletePost(request):
    try:
        if('id' not in request.data.keys()):
            return JsonResponse("Invalid Credentials", safe = False)

        authtoken = request.headers.get('Authorization')[6:] if request.headers.get('Authorization') else ''
        
        isSuperUser = Token.objects.get(key = authtoken).user.isSuperUser
        
        if(isSuperUser):
            Blog_Post.objects.get(id = request.data['id']).delete()
            return JsonResponse("Successfully Deleted Post", safe = False)
        else:
            return JsonResponse("Not Authorized", safe = False, status = 401)
    except Blog_Post.DoesNotExist:
        return JsonResponse("Invalid ID", safe = False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active)
def Create_Comment(request):
    authtoken = request.headers.get('Authorization')[6:] if request.headers.get('Authorization') else ''
    now = datetime.now()

    try:
        user = Token.objects.get(key = authtoken).user

        if('id' in request.data.keys() and 'comment' in request.data.keys()):
            user_has_posted = True if Blog_Post_Comments.objects.filter(user = user, blog_post = request.data['id']).count() > 0 else False

            #Check if user posted in this thread already
            if(user_has_posted == False):
                comment = Blog_Post_Comments.objects.create(blog_post = Blog_Post.objects.get(id = int(request.data['id'])), user = user, comment = request.data['comment'], date_posted = now)
                ser = Blog_Post_Comments_Serializer(comment)

                return JsonResponse(ser.data, safe = False, status = 200)
        elif('comment_id' in request.data.keys() and 'comment' in request.data.keys()):
            parent_comment = Blog_Post_Comments.objects.get(id = int(request.data['comment_id']))
            
            #Check to see if a user has already replied to this comment
            user_has_replied = True if Blog_Post_Comments.objects.filter(parent = parent_comment, user = user, comment = request.data['comment_id']).count() > 0 else False

            if(user_has_replied == False):
                reply = Blog_Post_Comments.objects.create(user = user, comment = request.data['comment'], parent = parent_comment, date_posted = now)

                ser = Blog_Post_Comments_Serializer(reply, many = False)

                return JsonResponse(ser.data, safe = False, status = 200)

        return JsonResponse("You can only comment once per post, and reply once per comment", safe = False, status = 500)
    except Token.DoesNotExist:
        return JsonResponse("Login first to comment", safe = False, status = 401)
    except Blog_Post.DoesNotExist:
        return JsonResponse("Invalid Blog Post ID", safe = False, status = 401)
    except Blog_Post_Comments.DoesNotExist:
        return JsonResponse("Invalid Comment ID", safe = False, status = 401)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active)
def Delete_Comment(request):
    authtoken = request.headers.get('Authorization')[6:] if request.headers.get('Authorization') else ''

    try:
        user = Token.objects.get(key = authtoken).user
        
        if(user.is_superuser): #If user is a superuser, they can delete any comment
            if('id' in request.data.keys()):
                deleted_comment = Blog_Post_Comments.objects.get(id = int(request.data['id'])).delete()

                return JsonResponse("Successfully Deleted Comment", safe = False)
            else: #If user is owner of comment, they can delete it
                comment =  Blog_Post_Comments.objects.get(id = int(request.data['id']))
                if(user.id == comment.user.id):
                    comment.delete() 
                    return JsonResponse("Successfully Deleted Comment", safe = False)           

        return JsonResponse("Not Authorized", safe = False, status = 401)
    except Token.DoesNotExist:
        return JsonResponse("Invalid Token", safe = False, status = 401)
    except Blog_Post_Comments.DoesNotExist:
        return JsonResponse("Comment does not exist", safe = False, status = 401)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active)
def Vote_On_Comment(request):
    authtoken = request.headers.get('Authorization')[6:] if request.headers.get('Authorization') else ''
    try:
        user = Token.objects.get(key = authtoken).user
        
        if('id' in request.data.keys()):
            comment = Blog_Post_Comments.objects.get(id = request.data['id'])
            #Has to check if user has voted on comment already. If the user has already voted then reject the request. 
            #However, if the user's new vote is different than the current, update that user's vote.
            
            if('vote_type' in request.data.keys()): #vote_type = true is an upvote, vote_type = false is a downvote
                user_vote = comment.blog_post_comment_vote_set.filter(user = user)
                vote = True if request.data['vote_type'].lower() == 'true' else False

                #If a user has previously voted on this comment
                if(user_vote.count() > 0):
                    this_vote = user_vote[0]
                    
                    if(vote != user_vote[0].vote_type):
                        this_vote.vote_type = not this_vote.vote_type
                        this_vote.save(update_fields = ['vote_type'])

                        return JsonResponse(
                            Blog_Post_Comments_Serializer(comment, many = False).data,
                            safe = False,
                            status = 200
                        )
                    else:
                        return JsonResponse("Can only vote once per comment, or change your vote.", safe = False, status = 500)
                else:
                    #Create a new vote for the requesting user
                    vote = Blog_Post_Comment_Vote.objects.create(
                        vote_type = request.data['vote_type'],
                        user = user,
                        comment = comment
                    )

                    return JsonResponse(
                        Blog_Post_Comments_Serializer(comment, many = False).data,
                        safe = False,
                        status = 200
                    )
            else:
                return JsonResponse("Must Include vote_type", safe = False, status = 401)
        return JsonResponse('Something went wrong', safe = False, status = 401)
    except Token.DoesNotExist:
        return JsonResponse("Invalid Token", safe = False, status = 401)
    except Blog_Post_Comments.DoesNotExist:
        return JsonResponse("Invalid Comment", safe = False, status = 401)



@api_view(['POST'])
def SendRegistrationCode(request):
    if('email' not in request.data.keys()):
        return JsonResponse('Must include email', safe = False, status = 401)
    if('username' not in request.data.keys()):
        return JsonResponse('Must include username', safe = False, status = 401)

    email = request.data['email'].lower()
    username = request.data['username']
    email_exists = User.objects.filter(email = email).exists()
    user_exists = User.objects.filter(username = username).exists()

    return JsonResponse('Registration code send', safe = False, status = 200)
    #Check if username or email is already in the system
    if(email_exists):
        return JsonResponse('A user is associated with that email', safe = False, status = 401)
    if(user_exists):
        return JsonResponse('A user is associated with that username', safe = False, status = 401)
    

    #This is tries to delete any entries if the user needs to resend the code to their email
    try:
        EmailCodes.objects.get(email = email).delete()
    except EmailCodes.DoesNotExist:
        pass    

    port = 465
    account = os.environ['SMTP_ACCOUNTS'].split(',')[0].split(':')
    sender = account[0]
    password = account[1]

    context = ssl.create_default_context()

    #Creates a random code
    code = ''.join(random.choice(string.digits + string.ascii_letters + string.digits) for i in range(6))

    #Create the email message
    content = "Your code is: " + code
    msg = MIMEText(content)
    msg['Subject'] = 'Your Registration Code'
    msg['From'] = sender

    EmailCodes.objects.create(code = code, email = email)

     #Sends the code
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, email, msg.as_string())

    del password

    return JsonResponse("Code Successfuly Sent!", safe = False)

@api_view(['POST'])
def AuthorizeRegistrationCode(request):
    if('email' not in request.data.keys()):
        return JsonResponse('Must include email', safe = False, status = 401)
    if('username' not in request.data.keys()):
        return JsonResponse('Must include username', safe = False, status = 401)
    if('password' not in request.data.keys()):
        return JsonResponse('Must include email', safe = False, status = 401)
    if('dob' not in request.data.keys()):
        return JsonResponse('Must include date of birth', safe = False, status = 401)
    if('code' not in request.data.keys()):
        return JsonResponse('Must include code', safe = False, status = 401)
    if('display_name' not in request.data.keys()):
        return JsonResponse('Must include display name', safe = False, status = 401)

    
    # Get the authcode
    code = EmailCodes.objects.filter(
        email = request.data['email'].lower(),
        code = request.data['code']
    )

    existing_user = User.objects.filter()

    # Trying to enforce one email per account
    if(code.count() > 1):
        return JsonResponse('This email is already in use', safe = False, status = 500)
    elif(code.count() == 1):

        # Confirm the code then create the user, if the code does not exists, return a 
        # response saying that the code is invalid.
        try:
            code = EmailCodes.objects.get(email = request.data['email'].lower(), code = request.data['code'])

            User.objects.create_user(
                email = request.data['email'],
                username = request.data['username'],
                password = request.data['password'],
                date_of_birth = request.data['dob'],
                display_name = request.data['display_name']
            )

            #Delete the code so that no one can use it to create more accounts 
            code.delete()

            return JsonResponse("Successfully Created New User!", safe = False)
        except EmailCodes.DoesNotExist:
            return JsonResponse('Invalid code, try again', safe = False, status = 401)

    return JsonResponse("Code not found...how did you get here?", safe = False, status = 401)

        
#If the user forgot their password, this sends a code to the user's email that can be used to change their password        
@api_view(['POST'])
def SendForgotPasswordCode(request):
    if('email' not in request.data.keys()):
        return JsonResponse('Must include email', safe = False, status = 401)

    user = User.objects.filter(email = request.data['email'])

    if(user.exists()):
        username = user[0].username

        #if a code already exists, delete it so that it can be resent
        current_code = ChangePasswordCodes.objects.filter(user = user[0])
        if(current_code.exists()):
            current_code[0].delete()
            
        port = 465
        context = ssl.create_default_context()

        account = os.environ['SMTP_ACCOUNTS'].split(',')[0].split(':')
        sender = account[0]
        password = account[1]

        code = ''.join(random.choice(string.digits + string.ascii_letters + string.digits) for i in range(6))

        msg = MIMEText('The code to reset your password for user ' + username + ' is ' + code)
        msg['Subject'] = 'Password Reset'
        msg['From'] = sender

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context = context) as server:
            #Create the code and send the email
            ChangePasswordCodes.objects.create(user = user[0], code = code)
            server.login(sender, password)
            server.sendmail(sender, user[0].email, msg.as_string())

        del password

        return JsonResponse('Code sent', safe = False, status = 200)     
    else:
        return JsonResponse('No user found', safe = False, status = 401)

#Changes the password given that the user enters a code that was sent to their email and is currently in the system
@api_view(['POST'])
def ChangePassword(request):
    if('code' not in request.data.keys()):
        return JsonResponse('Must include code', safe = False, status = 401)

    if('password' not in request.data.keys()):
        return JsonResponse('Must include password', safe = False, status = 401)
    try:
        code = ChangePasswordCodes.objects.get(code = request.data['code'])
        user = code.user
        user.set_password(request.data['password'])
        user.save()

        #Delete the code so that no one can exploit the code to change that user's password
        code.delete()

        return JsonResponse('Successfully changed user ' + user.username + '\'s password', safe = False, status = 200)

    except ChangePasswordCodes.DoesNotExist:
        return JsonResponse('Invalid Code', safe = False, status = 401)


#Function that allows a logged in user to update their display name and email
@api_view(['POST'])
@user_passes_test(lambda user: user.is_active)
@permission_classes([IsAuthenticated])
def UpdateUser(request):
    try: 
        user = Token.objects.get(key = request.headers.get('Authorization')[6:]).user
        data = request.data

        #This makes it so that the user can only update their email and display_name
        for key in data.keys():
            if(key.lower() == 'email' and data[key] is not ''):   
                #If the new email is the same as the old email, don't do anything
                if(user.email is not data[key]):
                    #Delete any existing email codes
                    codes = ChangeEmailCodes.objects.filter(user = user, new_email = data[key])

                    if(codes.exists()):
                        codes.delete()

                    #Send an email confirmation code here
                    #Generate random code of 6 characters
                    chars = string.digits + string.ascii_letters + string.digits
                    code = ''.join(random.choice(chars) for char in range(6))
                    
                    e_code = ChangeEmailCodes.objects.create(new_email = data[key], code = code, user = user)

                    #Send email
                    port = 465
                    
                    account = os.environ['SMTP_ACCOUNTS'].split(',')[0]
                    sender = account.split(':')[0]
                    password = account.split(':')[1]
                    
                    msg = MIMEText('Your code to change your email is: ' + code)
                    msg['Subject'] = "Email Change Auth Code"
                    msg['From'] = sender

                    context = ssl.create_default_context()

                    with smtplib.SMTP_SSL("smtp.gmail.com", port, context = context) as server:
                        server.login(sender, password)
                        server.sendmail(sender, data[key], msg.as_string())

            if(key.lower() == 'display_name' and data[key] is not ''):
                user.display_name = data[key]   
            if(key.lower() == 'subscribed'):
                user.subscribed = True if data[key].lower() == 'true' else False

        user.save()     

        return JsonResponse(User_Serializer(user).data, safe = False, status = 200)
    except User.DoesNotExist:
        return JsonResponse("User not found", safe = False, status = 401)
    except Token.DoesNotExist:
        return JsonResponse("Invalid Token", safe = False, status = 401)

#Function that allows a logged in user to update their email given that they supply the correct code
@api_view(['POST'])
@user_passes_test(lambda user: user.is_active)
@permission_classes([IsAuthenticated])
def UpdateUserEmail(request):
    if('code' not in request.data.keys()):
        return JsonResponse("Must Include Code", safe = False, status = 401)

    try:
        user = Token.objects.get(key = request.headers.get('Authorization')[6:]).user
        code = request.data['code']

        #The user must be logged in to change the code. That way you need more than just 
        #the code to change a user's email
        emailCode = ChangeEmailCodes.objects.get(code = code, user = user)
        if(User.objects.filter(email = emailCode.new_email).exists()):
            return JsonResponse('The email you want is already being used', safe = False, status = 500)

        myUser = emailCode.user

        myUser.email = emailCode.new_email
        myUser.save()

        emailCode.delete()

        return JsonResponse(User_Serializer(myUser).data, safe = False, status = 200)
    except Token.DoesNotExist:
        return JsonResponse("Invalid Token", safe = False, status = 401)
    except User.DoesNotExist:
        return JsonResponse("User not found", safe = False, status = 401)
    except ChangeEmailCodes.DoesNotExist:
        return JsonResponse("Invalid Code", safe = False, status = 401)

#This view allows a user to send an email to a moderator email given that
#the user supplies the comment id and the reason for reporting said comment
@api_view(['POST'])
@user_passes_test(lambda user: user.is_active)
@permission_classes([IsAuthenticated])
def ReportComment(request):
    if('id' not in request.data.keys()):
        return JsonResponse("Must include comment id", safe = False, status = 401)
    if('reason' not in request.data.keys()):
        return JsonResponse("Must include reason", safe = False, status = 401)

    try:
        user = Token.objects.get(key = request.headers.get('Authorization')[6:]).user
        comment = Blog_Post_Comments.objects.get(id = request.data['id'])

        port = 465
        context = ssl.create_default_context()
        account = os.environ['SMTP_ACCOUNTS'].split(',')[0].split(':')

        sender = account[0]
        password = account[1]

        recepient = 'disabledfeminist@gmail.com'

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Comment Report by " + user.username
        msg['From'] = sender
        msg['To'] = recepient

        html = """
            <html>

                <head>
                    <style>
                        body{{
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                        }}

                        label{{
                            font-weight: bold;     
                            text-decoration: underline;                           
                        }}
                    </style>
                </head>

                <body>
                    <label>Comment ID</label>
                    <p> {} </p>

                    <label>Reason</label>
                    <p>
                        {}
                    </p>
      
                    <label>Comment Creator</label>
                    <p> 
                        {} 
                    </p>

                    <label>Comment Content</label>
                    <p>
                        {}
                    </p>

                </body>

            </html>
        """.format(request.data['id'], request.data['reason'], comment.user.username, comment.comment)

        part1 = MIMEText(html, 'html')
        msg.attach(part1)

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context = context) as server:
            server.login(sender, password)
            server.sendmail(sender, recepient, msg.as_string())

        return JsonResponse('Report Submitted', safe = False, status = 200)
    except Token.DoesNotExist:
        return JsonResponse('Invalid Token', safe = False, status = 401)
    except User.DoesNotExist:
        return JsonResponse('Invalid User', safe = False, status = 401)
    except Blog_Post_Comments.DoesNotExist:
        return JsonResponse('Invalid Comment', safe = False, status = 401)

#This view allows super users to delete comments
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active)
def DeleteComment(request):
    if('id' not in request.data.keys()):
        return JsonResponse("Must include comment id", safe = False, status = 401)

    try:
        user = Token.objects.get(key = request.headers.get('Authorization')[6:]).user
        if(user.is_superuser):
            Blog_Post_Comments.objects.get(id = request.data['id']).delete()

            return JsonResponse('Comment Deleted', safe = False, status = 200)
        

        return JsonResponse('Unauthorized', safe = False, status = 401)
    except Token.DoesNotExist:
        return JsonResponse('Invalid Token', safe = False, status = 401)
    except User.DoesNotExist:
        return JsonResponse('Invalid User', safe = False, status = 401)
    except Blog_Post_Comments.DoesNotExist:
        return JsonResponse('Invalid Comment', safe = False, status = 401)

#This view allows a superuser to disable a user's account
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active and user.is_superuser)
def DisableUser(request):
    if('username' not in request.data.keys()):
        return JsonResponse('Must include username', safe = False, status = 401)
    try:
        user = Token.objects.get(key = request.headers.get('Authorization')[6:]).user

        disabledUser = User.objects.get(username = request.data['username'])
        disabledUser.is_active = False
        disabledUser.save()

        return JsonResponse('User ' + disabledUser.username + ' has been disabled', safe = False, status = 200)
    except Token.DoesNotExist:
        return JsonResponse('Invalid Token', safe = False, status = 401)
    except User.DoesNotExist:
        return JsonResponse('Invalid User', safe = False, status = 401)
    except Blog_Post_Comments.DoesNotExist:
        return JsonResponse('Invalid Comment', safe = False, status = 401)

#This view allows a superuser to enable a user's account
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active and user.is_superuser)
def EnableUser(request):
    if('username' not in request.data.keys()):
        return JsonResponse('Must include username', safe = False, status = 401)
    try:
        user = Token.objects.get(key = request.headers.get('Authorization')[6:]).user

        enabledUser = User.objects.get(username = request.data['username'])
        enabledUser.is_active = True
        enabledUser.save()

        return JsonResponse('User ' + enabledUser.username + ' has been enabled', safe = False, status = 200)
    except Token.DoesNotExist:
        return JsonResponse('Invalid Token', safe = False, status = 401)
    except User.DoesNotExist:
        return JsonResponse('Invalid User', safe = False, status = 401)
    except Blog_Post_Comments.DoesNotExist:
        return JsonResponse('Invalid Comment', safe = False, status = 401)

#This view allows a logged in user to like a blog post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active)
def LikePost(request):
    if('id' not in request.data.keys()):
        return JsonResponse('Must include id', safe = False, status = 401)

    try:
        user = Token.objects.get(key = request.headers.get('Authorization')[6:]).user
        post = Blog_Post.objects.get(id = request.data['id'])

        #Check if user has liked post already
        #If they already liked the post, then delete to like
        #This allows the user to unlike the post
        if(post.userpostlikes_set.filter(user = user).exists()):
            UserPostLikes.objects.get(user = user, post = post).delete()
            return JsonResponse({'CurrentLikes': post.userpostlikes_set.filter().count(),
                                 'Liked': False}, safe = False, status = 200)

        UserPostLikes.objects.create(user = user, post = post)
        return JsonResponse({'CurrentLikes': post.userpostlikes_set.filter().count(), 'Liked': True}, safe = False, status = 200)
    except Token.DoesNotExist:
        return JsonResponse('Invalid Token', safe = False, status = 401)
    except User.DoesNotExist:
        return JsonResponse('Invalid User', safe = False, status = 401)
    except Blog_Post.DoesNotExist:
        return JsonResponse('Invalid Post ID', safe = False, status = 401)


#This checks if a user has liked a post already
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active)
def HasLiked(request):
    if('id' not in request.data.keys()):
        return JsonResponse('Must include id', safe = False, status = 401)

    try:
        user = Token.objects.get(key = request.headers.get('Authorization')[6:]).user
        post = Blog_Post.objects.get(id = request.data['id'])

        #Check if user has liked post already
        #If they already liked the post, then they cannot like it again
        if(post.userpostlikes_set.filter(user = user).exists()):
            return JsonResponse({'HasLiked': True}, safe = False, status = 200)

        return JsonResponse({'HasLiked': False}, safe = False, status = 200)
    except Token.DoesNotExist:
        return JsonResponse('Invalid Token', safe = False, status = 401)
    except User.DoesNotExist:
        return JsonResponse('Invalid User', safe = False, status = 401)
    except Blog_Post.DoesNotExist:
        return JsonResponse('Invalid Post ID', safe = False, status = 401)

#This allows a super user to create a new welcome message
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda user: user.is_active and user.is_superuser)
def CreateWelcomeMessage(request):
    if('message' not in request.data.keys()):
        return JsonResponse('Must include message', safe = False, status = 401)

    WelcomeMessage.objects.create(date_posted = datetime.now(), message = request.data['message'])

    return JsonResponse('Successfully created message', safe = False, status = 200)
