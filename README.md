# Market Mingle

Welcome to Market Mingle, an eCommerce project designed to provide a seamless online shopping experience. Developed using Django, Market Mingle allows users to purchase a wide range of products. Key features include Razorpay payment gateway integration, email notifications, login verification, user account creation with email authentication, a cart page, and a payment receipt page.

## Features

- **Product Purchase**: Browse and buy a wide range of products.
- **Razorpay Payment Gateway**: Secure and reliable payment processing.
- **Email Notifications**: Receive order and account-related notifications via email.
- **Login Verification**: Secure login process with email verification.
- **User Creation with Email Authentication**: Register and authenticate users via email.
- **Cart Page**: View and manage selected products before purchase.
- **Payment Receipt Page**: View and download payment receipts after completing a purchase.

## Technologies Used

- **Python**
- **Django**
- **SQLite**
- **HTML**
- **CSS**
- **JavaScript**
- **Bootstrap**
- **gmail (smtp)**


## Getting Started

### Prerequisites

- Python 3.x
- Django 3.x or higher
- SQLite
- Razorpay Python SDK
- Pillow (Python Imaging Library)

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/Thamaraiselvan16/Market_Mingle
    cd Market_Mingle
    ```

2. **Create a virtual environment and activate it:**
    ```sh
    pip install virtualenv
    python -m venv venv_name
    source venv_name\Scripts\activate  # On Windows, use `venv_name/bin/activate`
    ```

3. **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```


5. **Run migrations:**
    ```sh
    python manage.py migrate
    ```

6. **Add Razorpay keys**
    ```sh
    source ecommerce/ecommerceapp/keys.py
    `RAZORPAY_KEY_ID = 'your key'`
    `RAZORPAY_KEY_SECRET = 'your secret key'`
    go to this website and login with your account `https://dashboard.razorpay.com/?screen=sign_in`

6. **Start the development server:**
    ```sh
    cd ecommerce
    python manage.py runserver


    ```

### Usage

1. **Register an Account**: Create a new user account with email authentication.
2. **Login**: Log in with your verified account.
3. **Browse Products**: Explore and select products to purchase.
4. **Add to Cart**: Add desired products to the cart.
5. **Checkout**: Proceed to checkout and complete the payment using Razorpay.
6. **Receive Notifications**: Get email notifications for order confirmations and updates.
7. **View Payment Receipt**: Access and download the payment receipt from the payment receipt page.


## Acknowledgments

- Thanks to the open-source community for their tools and resources.
- Special thanks to the Django, Razorpay, and Pillow communities for their excellent tools and documentation.

---

We hope you enjoy using Market Mingle. If you have any questions or feedback, feel free to open an issue or contact us.
