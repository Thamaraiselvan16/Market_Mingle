from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import Contact,Product,OrderUpdate,Orders
from django.contrib import messages
from math import ceil
from . import keys
from django.conf import settings
import json
from django.views.decorators.csrf import  csrf_exempt

# Create your views here.
def index(request):

    allProds = []
    catprods = Product.objects.values('category','id')
    print(catprods)
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}

    return render(request,"index.html",params)



from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, product_id):
    # Retrieve the product details from the database
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'product_detail.html', {'product': product})



# views.py
from django.shortcuts import render
from .models import Product

def search(request):
    query = request.GET.get('q')
    if query:
        results = Product.objects.filter(product_name__icontains=query)
    else:
        results = None
    return render(request, 'search_results.html', {'results': results})


    
from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Contact

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        desc = request.POST.get("desc")
        pnumber = request.POST.get("pnumber")
        image = request.FILES.get("profile-pic")
        
        # Create a new Contact object and save it to the database
        myquery = Contact(name=name, email=email, desc=desc, phonenumber=pnumber, image=image)
        myquery.save()
        
        # Send a formal email with the details
        subject = 'New Contact Form Submission - Formal Notification'
        message = f'Dear Team,\n\nA new contact form submission has been received with the following details:\n\nName: {name}\nEmail: {email}\nDescription: {desc}\nPhone Number: {pnumber}\n\nBest Regards,\n{name}'
        recipient_list = [settings.EMAIL_HOST_USER]  # Change this to the email address where you want to receive the notification
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)
        
        messages.info(request, "We will get back to you soon..")
        return redirect("contact")  # Redirect to the contact page after submission

    return render(request, "contact.html")




# def about(request):
#     return render(request,"about.html")



# views.py
from django.shortcuts import render
from .models import Product, Orders, OrderUpdate
import razorpay

razorpay_client = razorpay.Client(auth=(keys.RAZORPAY_KEY_ID, keys.RAZORPAY_KEY_SECRET))

# Your other views...

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Orders, OrderUpdate
import razorpay
from . import keys

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = int(request.POST.get('amt')) * 100  # Amount in paise
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        
        # Create an order in Razorpay
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': 'receipt_order_{}'.format(name),
            'payment_capture': 1  # Auto-capture payment
        }
        razorpay_order = razorpay_client.order.create(data=order_data)
        razorpay_order_id = razorpay_order['id']

        Order = Orders(items_json=items_json, name=name, amount=amount/100, email=email, address1=address1, address2=address2,
                       city=city, state=state, zip_code=zip_code, phone=phone, oid=razorpay_order_id)
        Order.save()

        update = OrderUpdate(order_id=Order.order_id, update_desc="The order has been placed")
        update.save()

        # Send email with product details and price
        email_subject = "Order Confirmation - Market Mingle"
        email_message = render_to_string('order_confirmation_email.html', {'order': Order})
        email = EmailMessage(email_subject, email_message, to=[email])
        email.send()

        thank = True

        return render(request, 'razorpay.html', {'order_id': razorpay_order_id, 'amount': amount})

    return render(request, 'checkout.html')



from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import Orders
import razorpay
from . import keys

@csrf_exempt
def handlerequest(request):
    if request.method == 'POST':
        response = request.POST
        if response.get('razorpay_payment_id'):
            razorpay_payment_id = response['razorpay_payment_id']
            razorpay_order_id = response['razorpay_order_id']
            razorpay_signature = response['razorpay_signature']

            # Verify the payment signature
            client = razorpay.Client(auth=(keys.RAZORPAY_KEY_ID, keys.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            try:
                client.utility.verify_payment_signature(params_dict)
                # Payment successful, update your database accordingly
                # Fetch order details from database
                order = Orders.objects.get(oid=razorpay_order_id)
                
                # Send email notification for successful payment
                email_subject = "Payment Successful"
                email_message = render_to_string('payment_successful_email.html', {'order': order})
                email = EmailMessage(email_subject, email_message, to=[order.email])
                email.send()
                
                return render(request, 'paymentstatus.html', {'response': response, 'order': order})
            except razorpay.errors.SignatureVerificationError:
                # Payment failed due to signature mismatch
                error_description = "Signature verification failed"
                return render(request, 'paymentstatus.html', {'response': response, 'error_description': error_description})
        else:
            # Payment failed with no payment ID
            error_description = response.get('error_description', 'Unknown error')
            return render(request, 'paymentstatus.html', {'response': response, 'error_description': error_description})

    return HttpResponse(status=200)



# @csrf_exempt
# def handlerequest(request):
#     if request.method == 'POST':
#         response = request.POST
#         if response.get('razorpay_payment_id'):
#             razorpay_payment_id = response['razorpay_payment_id']
#             razorpay_order_id = response['razorpay_order_id']
#             razorpay_signature = response['razorpay_signature']

#             # Verify the payment signature
#             client = razorpay.Client(auth=(keys.RAZORPAY_KEY_ID, keys.RAZORPAY_KEY_SECRET))
#             params_dict = {
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': razorpay_payment_id,
#                 'razorpay_signature': razorpay_signature
#             }
#             try:
#                 client.utility.verify_payment_signature(params_dict)
#                 # Payment successful, update your database accordingly
#                 # Fetch order details from database
#                 order = Orders.objects.get(oid=razorpay_order_id)
#                 return render(request, 'paymentstatus.html', {'response': response, 'order': order})
#             except razorpay.errors.SignatureVerificationError:
#                 # Payment failed due to signature mismatch
#                 error_description = "Signature verification failed"
#                 return render(request, 'paymentstatus.html', {'response': response, 'error_description': error_description})
#         else:
#             # Payment failed with no payment ID
#             error_description = response.get('error_description', 'Unknown error')
#             return render(request, 'paymentstatus.html', {'response': response, 'error_description': error_description})

#     return HttpResponse(status=200)





















# def checkout(request):
#     if not request.user.is_authenticated:
#         messages.warning(request, "Login & Try Again")
#         return redirect('/auth/login')

#     if request.method == "POST":
#         items_json = request.POST.get('itemsJson', '')
#         name = request.POST.get('name', '')
#         amount = int(request.POST.get('amt')) * 100  # Amount in paise
#         email = request.POST.get('email', '')
#         address1 = request.POST.get('address1', '')
#         address2 = request.POST.get('address2', '')
#         city = request.POST.get('city', '')
#         state = request.POST.get('state', '')
#         zip_code = request.POST.get('zip_code', '')
#         phone = request.POST.get('phone', '')
        
#         # Create an order in Razorpay
#         order_data = {
#             'amount': amount,
#             'currency': 'INR',
#             'receipt': 'receipt_order_{}'.format(name),
#             'payment_capture': 1  # Auto-capture payment
#         }
#         razorpay_order = razorpay_client.order.create(data=order_data)
#         razorpay_order_id = razorpay_order['id']

#         Order = Orders(items_json=items_json, name=name, amount=amount/100, email=email, address1=address1, address2=address2,
#                        city=city, state=state, zip_code=zip_code, phone=phone, oid=razorpay_order_id)
#         Order.save()

#         update = OrderUpdate(order_id=Order.order_id, update_desc="The order has been placed")
#         update.save()

#         thank = True

#         return render(request, 'razorpay.html', {'order_id': razorpay_order_id, 'amount': amount})

#     return render(request, 'checkout.html')

# # views.py

# # Your other views...
# # views.py
# # views.py

# @csrf_exempt
# def handlerequest(request):
#     if request.method == 'POST':
#         response = request.POST
#         if response.get('razorpay_payment_id'):
#             razorpay_payment_id = response['razorpay_payment_id']
#             razorpay_order_id = response['razorpay_order_id']
#             razorpay_signature = response['razorpay_signature']

#             # Verify the payment signature
#             client = razorpay.Client(auth=(keys.RAZORPAY_KEY_ID, keys.RAZORPAY_KEY_SECRET))
#             params_dict = {
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': razorpay_payment_id,
#                 'razorpay_signature': razorpay_signature
#             }
#             try:
#                 client.utility.verify_payment_signature(params_dict)
#                 # Payment successful, update your database accordingly
#                 # Fetch order details from database
#                 order = Orders.objects.get(oid=razorpay_order_id)
#                 return render(request, 'paymentstatus.html', {'response': response, 'order': order})
#             except razorpay.errors.SignatureVerificationError:
#                 # Payment failed due to signature mismatch
#                 error_description = "Signature verification failed"
#                 return render(request, 'paymentstatus.html', {'response': response, 'error_description': error_description})
#         else:
#             # Payment failed with no payment ID
#             error_description = response.get('error_description', 'Unknown error')
#             return render(request, 'paymentstatus.html', {'response': response, 'error_description': error_description})

#     return HttpResponse(status=200)


# def profile(request):
#     if not request.user.is_authenticated:
#         messages.warning(request,"Login & Try Again")
#         return redirect('/auth/login')
#     currentuser=request.user.username
#     items=Orders.objects.filter(email=currentuser)
#     rid=""
#     for i in items:
#         print(i.oid)
#         # print(i.order_id)
#         myid=i.oid
#         rid=myid.replace("ShopyCart","")
#         print(rid)
#     status=OrderUpdate.objects.filter(order_id=int(rid))
#     for j in status:
#         print(j.update_desc)

   
#     context ={"items":items,"status":status}
#     # print(currentuser)
#     return render(request,"profile.html",context)


from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Orders

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login and try again.")
        return redirect('/auth/login')
    
    current_user = request.user.username
    items = Orders.objects.filter(email=current_user)
    
    context = {"items": items}
    return render(request, "profile.html", context)

