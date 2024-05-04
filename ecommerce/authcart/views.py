from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utils import TokenGenerator,generate_token
# from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from django.contrib import messages
# from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError, force_text
# from django.utils.encoding import force_bytes, force_text
from django.utils.encoding import force_bytes
# from six import text_type as force_text
from django.utils.encoding import smart_str

from django.utils.http import urlsafe_base64_decode

from django.core.mail import EmailMessage
from django.conf import settings

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate,login,logout
# Create your views here.
def signup(request):
    if request.method=="POST":
        email=request.POST['email']
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        if password!=confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,'signup.html')                   
        try:
            if User.objects.get(username=email):
                # return HttpResponse("email already exist")
                messages.info(request,"Email is Taken")
                return render(request,'signup.html')
        except Exception as identifier:
            pass
        user = User.objects.create_user(email,email,password)
        user.is_active=False
        user.save()
        email_subject="Registration - Activate Your Account - Market Mingle"
        message=render_to_string('activate.html',{
            'user':user,
            'domain':'127.0.0.1:2000',   #this id domain name to change hosting time
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)

        })

        email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
        email_message.send()
        # messages.success(request,f"Activate Your Account by clicking the link in your gmail {message}")
        messages.success(request,f"Activate Your Account by clicking the link in your gmail")
        return redirect('/auth/login/')
    return render(request,"signup.html")


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as e:
            messages.error(request, "Activation link is invalid or expired.")
            return render(request, 'activatefail.html')

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Account activated successfully. You can now log in.")
            return redirect('/auth/login')
        else:
            messages.error(request, "Activation link is invalid or expired.")
            return render(request, 'activatefail.html')


from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.conf import settings

def handlelogin(request):
    if request.method == "POST":
        username = request.POST['email']
        userpassword = request.POST['pass1']
        myuser = authenticate(username=username, password=userpassword)

        if myuser is not None:
            login(request, myuser)
            messages.success(request, "Login Success")
            
            # Send notification email
            email_subject = "Login Successful - Market Mingle"
            message = render_to_string('login_notification.html', {'user': myuser})
            email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [myuser.email])
            email_message.send()

            return redirect('/')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('/auth/login')

    return render(request, 'login.html')


# def handlelogin(request):
#     if request.method=="POST":

#         username=request.POST['email']
#         userpassword=request.POST['pass1']
#         myuser=authenticate(username=username,password=userpassword)

#         if myuser is not None:
#             login(request,myuser)
#             messages.success(request,"Login Success")
#             return redirect('/')

#         else:
#             messages.error(request,"Invalid Credentials")
#             return redirect('/auth/login')

#     return render(request,'login.html')  






def handlelogout(request):
    logout(request)
    messages.info(request,"Logout Success")
    return redirect('/auth/login')


class RequestResetEmailView(View):
    def get(self,request):
        return render(request,'request-reset-email.html')
    
    def post(self,request):
        email=request.POST['email']
        user=User.objects.filter(email=email)

        if user.exists():
            # current_site=get_current_site(request)
            email_subject='Reset Your Password - Market Mingle'
            message=render_to_string('reset-user-password.html',{
                'domain':'127.0.0.1:2000',
                'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token':PasswordResetTokenGenerator().make_token(user[0])
            })

            email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
            email_message.send()

            # messages.info(request,f"WE HAVE SENT YOU AN EMAIL WITH INSTRUCTIONS ON HOW TO RESET THE PASSWORD {message} " )
            messages.info(request,f"We have sent you an email with instructions on how to reset the password" )
            # messages.info(request,f"WE HAVE SENT YOU AN EMAIL WITH INSTRUCTIONS ON HOW TO RESET THE PASSWORD {message} " )
            return render(request,'request-reset-email.html')






from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import smart_str, force_bytes
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views import View
from django.conf import settings

class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.warning(request, "Password Reset Link is Invalid")
                return render(request, 'request-reset-email.html')

        except Exception as e:
            pass

        return render(request, 'set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']
        if password != confirm_password:
            messages.warning(request, "Password is Not Matching")
            return render(request, 'set-new-password.html', context)

        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            # Send email notification
            email_subject = "Password Reset Successful - Market Mingle"
            message = render_to_string('password_reset_success_email.html', {'user': user})
            email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
            email_message.send()

            messages.success(request, "Password Reset Success. Please login with the new password.")
            return redirect('/auth/login/')

        except Exception as e:
            messages.error(request, "Something Went Wrong")
            return render(request, 'set-new-password.html', context)

        return render(request, 'set-new-password.html', context)























# class SetNewPasswordView(View):
#     def get(self,request,uidb64,token):
#         context = {
#             'uidb64':uidb64,
#             'token':token
#         }
#         try:
#             user_id=smart_str(urlsafe_base64_decode(uidb64))
#             user=User.objects.get(pk=user_id)

#             if  not PasswordResetTokenGenerator().check_token(user,token):
#                 messages.warning(request,"Password Reset Link is Invalid")
#                 return render(request,'request-reset-email.html')

#         except DjangoUnicodeDecodeError as identifier:
#             pass

#         return render(request,'set-new-password.html',context)

#     def post(self,request,uidb64,token):
#         context={
#             'uidb64':uidb64,
#             'token':token
#         }
#         password=request.POST['pass1']
#         confirm_password=request.POST['pass2']
#         if password!=confirm_password:
#             messages.warning(request,"Password is Not Matching")
#             return render(request,'set-new-password.html',context)
        
#         try:
#             user_id=smart_str(urlsafe_base64_decode(uidb64))
#             user=User.objects.get(pk=user_id)
#             user.set_password(password)
#             user.save()
#             messages.success(request,"Password Reset Success Please Login with NewPassword")
#             return redirect('/auth/login/')

#         except DjangoUnicodeDecodeError as identifier:
#             messages.error(request,"Something Went Wrong")
#             return render(request,'set-new-password.html',context)

#         return render(request,'set-new-password.html',context)
