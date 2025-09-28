from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
# ⚠️ CRITICAL: REPLACE THIS WITH A LONG, RANDOM, SECURE KEY FOR PRODUCTION
app.secret_key =  '662ace46ee00ef6e1fc014491f06f3dc157cf0590ea3a49a'

# ---------------- APPLICATION & EMAIL CONFIGURATION ----------------
app.config['SHOP_NAME'] = "Natural Healing Center"
app.config['HEALER_NAME'] = "Healer TarunKumar UN"
app.config['SHOP_CITY'] = "Davangere"
app.config['SHOP_ADDRESS'] = "Kirwadi Layout,1st Main,1st Cross,Lenin Nagara,Nituvalli Main Road,Davanagere 577008"
app.config['OWNER_PHONE'] = "+919741367959"
app.config['OWNER_EMAIL'] = "tarunun11@gmail.com"

# Email setup for sending mails
app.config['MAIL_USERNAME'] = "tarunun11@gmail.com"
app.config['MAIL_PASSWORD'] = "dbqwdfuzavtmjzrq" # Your 16-character App Password

# ---------------- ADMIN LOGIN CREDENTIALS ----------------
# NOTE: CHANGE THESE TO YOUR SECURE LOGIN CREDENTIALS
ADMIN_USERNAME = "NHC_TarunBoss2025" 
ADMIN_PASSWORD = "T@runHeals#051!Dbgn" 
# -----------------------------------------------------------------

# ---------------- GOOGLE SHEETS SETUP ----------------
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

# IMPORTANT: Ensure this path is correct on your production server
creds = Credentials.from_service_account_file(r"E:\tarunproject\credentials.json", scopes=scope)
client_gs = gspread.authorize(creds)

sheet = client_gs.open_by_url(
    "https://docs.google.com/spreadsheets/d/15Y0AVv682PQr9DoNk2PLCzE2VEw7eFdfFwjhKYGzk6I/edit?usp=sharing"
).sheet1


# ---------------- EMAIL HELPER FUNCTIONS ----------------
def send_email(to_email, subject, body, is_html=False):
    """Helper function to send email."""
    try:
        msg = MIMEMultipart()
        msg["From"] = app.config['MAIL_USERNAME']
        msg["To"] = to_email
        msg["Subject"] = subject
        
        if is_html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(app.config['MAIL_USERNAME'], to_email, msg.as_string())
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email failed to {to_email}: {e}")

def create_customer_email_body_html(name, booking_date, slot):
    """Generates the HTML content for the customer's confirmation email."""
    
    google_maps_query = app.config['SHOP_ADDRESS'].replace(' ', '+').replace(',', '%2C')
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={google_maps_query}"
    call_link = f"tel:{app.config['OWNER_PHONE']}"

    # NOTE: The email HTML body (omitted here for brevity, but retained from your previous code)
    # is assumed to be correct and unchanged for the public facing email.
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 0; border: 1px solid #ddd; border-radius: 8px; }}
            .header {{ background-color: #f4f4f4; padding: 20px; text-align: center; border-bottom: 1px solid #ddd; border-radius: 8px 8px 0 0; }}
            .content {{ padding: 20px; line-height: 1.6; }}
            .button-group {{ text-align: center; padding: 10px 0 20px 0; }}
            .button {{ display: inline-block; padding: 10px 20px; margin: 5px; background-color: #007BFF; color: #fff; text-decoration: none; border-radius: 5px; font-weight: bold; }}
            .call-button {{ background-color: #28a745; }}
            .footer {{ text-align: center; margin-top: 10px; padding: 10px 20px; font-size: 0.8em; color: #777; border-top: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Appointment Confirmed!</h2>
            </div>
            <div class="content">
                <p>Dear {name},</p>
                <p>Your appointment with <strong>{app.config['HEALER_NAME']}</strong> is confirmed. We look forward to seeing you!</p>
                <p><strong>Date:</strong> {booking_date}</p>
                <p><strong>Time:</strong> {slot}</p>
                <p><strong>Location:</strong> {app.config['SHOP_ADDRESS']}</p>
                <p>Please use the buttons below for directions or to contact the healer directly.</p>
                
                <div class="button-group">
                    <a href="{google_maps_url}" class="button" target="_blank" style="background-color: #007BFF;">View on Google Maps</a>
                    <a href="{call_link}" class="button call-button" style="background-color: #28a745; color: white; text-decoration: none;">Long Press To Call Now</a>
                </div>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# ---------------- SECURE ROUTES (LOGIN/LOGOUT/DASHBOARD) ----------------

@app.route("/admin_login")
def admin_login_page():
    """Renders the admin login form (admin_login.html)."""
    return render_template("admin_login.html")

@app.route("/login", methods=["POST"])
def login():
    """Handles login form submission, redirects to dashboard on success."""
    username = request.form.get("username")
    password = request.form.get("password")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        # NOTE: Using the provided admin_dashboard.html, assuming it renders the sheet data
        return redirect(url_for('admin_dashboard')) 
    else:
        # Re-render the login page with an error. 
        # (This is a simplified approach, using flash messages is better for production)
        return render_template("admin_login.html", error="Invalid credentials")

@app.route("/dashboard")
def admin_dashboard():
    """Renders the secure admin dashboard (admin_dashboard.html)."""
    # SECURITY CHECK: If user is not logged in, redirect to login page
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('admin_login_page'))
    
    # Get all booking records for display
    try:
        # Note: This assumes your Google Sheet columns match the keys expected in admin_dashboard.html
        all_records = sheet.get_all_records()
    except Exception as e:
        all_records = []
        print(f"Error retrieving sheet records: {e}")
    
    # The 'records' variable will be used by admin_dashboard.html
    return render_template("admin_dashboard.html", records=all_records, app_config=app.config)

@app.route("/logout")
def logout():
    """Logs the user out and clears the session."""
    session.pop('logged_in', None)
    return redirect(url_for('admin_login_page'))


# ---------------- PUBLIC ROUTES (BOOKING) ----------------

@app.route("/")
def register_page():
    """Renders the initial registration page."""
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_customer():
    """Handles registration form submission and redirects to booking."""
    name = request.form.get("name")
    phone = request.form.get("phone")
    
    # Store customer info in the session
    session['name'] = name
    session['phone'] = phone
    
    return redirect(url_for('booking_page'))

@app.route("/booking")
def booking_page():
    """Renders the booking page after a successful registration."""
    if 'name' not in session:
        return redirect(url_for('register_page'))
    
    shop_data = {
        "shop_name": app.config['SHOP_NAME'],
        "healer_name": app.config['HEALER_NAME'],
        "shop_city": app.config['SHOP_CITY'],
        "shop_address": app.config['SHOP_ADDRESS'],
        "owner_phone": app.config['OWNER_PHONE'],
        "owner_email": app.config['OWNER_EMAIL'],
        "treatments_Provided": [
            "Single Seed Point", "Color Therapy", "Seed Therapy", "Meditation Guidance", 
            "Acupressure(Aricular Theropy)", "Colour Numerology",
        ],
        "slots": [
            "10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM", "2:00 PM - 3:00 PM", 
            "3:00 PM - 4:00 PM", "5:00 PM - 6:00 PM"
        ],
        "today": date.today().isoformat(),
        "registered_name": session.get('name'),
        "registered_phone": session.get('phone')
    }
    return render_template("index.html", **shop_data)

@app.route("/book", methods=["POST"])
def book():
    """Handles the appointment booking form submission."""
    try:
        name = request.form.get("name")
        phone = request.form.get("phone")
        
        if not phone.startswith("+"):
            phone = "+91" + phone 

        email = request.form.get("email")
        
        if not email:
             return jsonify({"success": False, "message": "Email is required."}), 400

        age = request.form.get("age")
        location = request.form.get("location")
        booking_date = request.form.get("date")
        slot = request.form.get("slot")

        sheet.append_row([name, phone, email, age, location, booking_date, slot])

        # Customer Email
        subject = "Your Appointment is Confirmed!"
        html_body = create_customer_email_body_html(name, booking_date, slot)
        send_email(email, subject, html_body, is_html=True)

        # Healer Notification Email
        healer_subject = "New Appointment Booking"
        healer_body = f"Hello {app.config['HEALER_NAME']},\n\nNew booking received:\n\nName: {name}\nPhone: {phone}\nEmail: {email}\nAge: {age}\nLocation: {location}\nDate: {booking_date}\nSlot: {slot}\n\nRegards,\nThe {app.config['SHOP_NAME']} System"
        send_email(app.config['OWNER_EMAIL'], healer_subject, healer_body)

        return jsonify({"success": True, "message": "Booking confirmed!"}), 200

    except Exception as e:
        print(f"❌ Error in booking: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    # ⚠️ REMEMBER: USE A PRODUCTION WSGI SERVER (LIKE GUNICORN) AND debug=False FOR LAUNCH
    app.run(debug=False)