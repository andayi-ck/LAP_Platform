import os
import smtplib
import ssl
from email.message import EmailMessage
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

import sqlite3
from datetime import datetime

from flask import (flash, get_flashed_messages, jsonify, redirect, render_template, request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from market import app, bcrypt, db
from market.forms import LoginForm, PurchaseItemForm, RegisterForm
from market.models import Illness, Item, User, Veterinary

#@app.route('/')
# def hello_world():
#    return '<h1>Home Page</h1>'

@app.route('/')
def welcome_page():
    return render_template('welcome-page.html')


@app.route('/home')
def home_page():
    return render_template('home.html')
    #  we went on to call the home.html file as can be seen above.
    # 'render_template()' basically works by rendering files.


#@login_required
#below list of dictionaries is sent to the market page through the market.html
#       but we are going to look for a way to store information inside an organized
#       DATABASE which can be achieved through configuring a few things in our flask
#       application
# WE ARE THUS GOING TO USE SQLITE3 is a File WHich allows us to store information and we are going to
#   connect it to the Flask APplication.We thus have to install some flask TOOL THAT ENABLES THIS through the terminal


# Email configuration
EMAIL_SENDER = 'magero833@gmail.com'
EMAIL_PASSWORD = "gdtd gmuk bddl retb"  # App-specific password for Gmail

# Token generator for email verification
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def send_verification_email(email_receiver, username, token):
    verification_url = url_for('verify_email', token=token, _external=True)
    subject = 'Verify Your Email to Create Your Account'
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                padding: 20px 0;
                background-color: #D2B48C;
                color: white;
                border-radius: 8px 8px 0 0;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 20px;
                color: #333;
            }}
            .content p {{
                line-height: 1.6;
                margin: 10px 0;
            }}
            .button {{
                display: inline-block;
                padding: 12px 25px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                text-align: center;
            }}
            .button:hover {{
                background-color: #45a049;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                font-size: 12px;
                color: #777;
            }}
            .link {{
                word-break: break-all;
                color: #4CAF50;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://livestockanalytics.com/hs-fs/hubfs/Logos%20e%20%C3%ADconos/livestock.png?width=115&height=70&name=livestock.png" alt="Livestock Management" style="max-width: 150px;">
                <h1>Welcome to Livestock Management</h1>
            </div>
            <div class="content">
                <p>Hello {username},</p>
                <p>Thank you for joining the Livestock Management System! To complete your account creation, please verify your email by clicking the button below:</p>
                <p style="text-align: center;">
                    <a href="{verification_url}" class="button">Create Account</a>
                </p>
                <p>If the button doesn’t work, copy and paste this link into your browser:</p>
                <p><a href="{verification_url}" class="link">{verification_url}</a></p>
                <p>This link expires in 1 hour.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Livestock Management System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    em = EmailMessage()
    em['From'] = EMAIL_SENDER
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body, subtype='html')  # Ensure HTML subtype is set

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_SENDER, email_receiver, em.as_string())
        print(f"Verification email sent to {email_receiver}")
    except Exception as e:
        print(f"Email error: {str(e)}")


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        # Create user but don’t activate yet
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password_hash=form.password1.data,  # Hash in production
            email_verified=False  # Initially unverified
        )
        db.session.add(user_to_create)
        db.session.commit()

        # Generate verification token
        token = s.dumps({'user_id': user_to_create.id, 'email': user_to_create.email_address}, salt='email-verify')
        
        # Send verification email
        send_verification_email(user_to_create.email_address, user_to_create.username, token)
        
        # Redirect to the verification pending page instead of register_page
        return redirect(url_for('verify_pending', email=user_to_create.email_address))
        flash("A verification email has been sent. Please check your inbox (and spam) to complete registration.", category='info')

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
            
            
    return render_template('register.html', form=form)


@app.route('/verify-pending/<email>')
def verify_pending(email):
    return render_template('verify_pending.html', email=email)


@app.route('/resend-verification/<email>')
def resend_verification(email):
    user = User.query.filter_by(email_address=email, email_verified=False).first()
    if user:
        token = s.dumps({'user_id': user.id, 'email': user.email_address}, salt='email-verify')
        send_verification_email(user.email_address, user.username, token)
        flash("A new verification email has been sent!", category='info')
    else:
        flash("No unverified account found for this email.", category='danger')
    return redirect(url_for('verify_pending', email=email))

@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        # Verify token (expires in 3600 seconds = 1 hour)
        data = s.loads(token, salt='email-verify', max_age=3600)
        user_id = data['user_id']
        email = data['email']
        
        # Find user and verify email matches
        user = User.query.get(user_id)
        if user and user.email_address == email and not user.email_verified:
            user.email_verified = True
            db.session.commit()
            login_user(user)
            flash(f"Email verified! Welcome, {user.username}!", category='success')
            return redirect(url_for('welcome_page'))
        else:
            flash("Invalid or already verified account.", category='danger')
    except SignatureExpired:
        flash("The verification link has expired. Please register again.", category='danger')
    except BadSignature:
        flash("Invalid verification link.", category='danger')
    
    return redirect(url_for('register_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('livestock_dashboard'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

#added this code for the search bar at the navbar in 'base.html'
@app.route('/search', methods=['GET'])
def search_results():
    query = request.args.get('animal', '').strip()

    if not query:
        return render_template('livestock_dashboard.html', error="Please enter an animal name.")

    conn = get_db_connection()
    cur = conn.cursor()

    # Get animal ID
    cur.execute("SELECT id FROM Animals WHERE LOWER(name) = LOWER(?)", (query,))
    animal = cur.fetchone()
    if not animal:
        conn.close()
        return render_template('livestock_dashboard.html', error=f"No data found for {query}.", animal=query)
    animal_id = animal['id']

    # Fetch static data (no age range)
    cur.execute("SELECT name AS species_name FROM Species WHERE animal_id = ?", (animal_id,))
    species = cur.fetchone()

    cur.execute("SELECT preferred_conditions AS habitat, temperature_range FROM Habitat WHERE animal_id = ?", (animal_id,))
    habitat = cur.fetchone()

    cur.execute("SELECT product_type AS produce FROM Produce WHERE animal_id = ?", (animal_id,))
    produce = cur.fetchone()

    # Fetch age-specific data
    cur.execute("SELECT age_range, feed_type, quantity_per_day FROM Feed WHERE animal_id = ?", (animal_id,))
    feeds = cur.fetchall()

    cur.execute("SELECT age_range, vaccine_name FROM VaccinationSchedule WHERE animal_id = ?", (animal_id,))
    vaccines = cur.fetchall()

    cur.execute("SELECT age_range, disease_name FROM Diseases WHERE animal_id = ?", (animal_id,))
    diseases = cur.fetchall()

    cur.execute("SELECT age_range, average_weight FROM WeightTracking WHERE animal_id = ?", (animal_id,))
    weights = cur.fetchall()

    cur.execute("SELECT age_range, supplement_name, dosage FROM AdditivesAndMinerals WHERE animal_id = ?", (animal_id,))
    supplements = cur.fetchall()

    conn.close()

    # Group age-specific data
    grouped_results = {}
    for table_data, key in [
        (feeds, 'feeds'), (vaccines, 'vaccines'), (diseases, 'diseases'),
        (weights, 'weights'), (supplements, 'supplements')
    ]:
        for row in table_data:
            age = row['age_range'] or 'Unknown'
            if age not in grouped_results:
                grouped_results[age] = {
                    'species_name': species['species_name'] if species else 'Not Available',
                    'habitat': habitat['habitat'] if habitat else 'Not Available',
                    'temperature_range': habitat['temperature_range'] if habitat else 'Not Available',
                    'produce': produce['produce'] if produce else 'Not Available',
                    'feeds': [], 'vaccines': [], 'diseases': [], 'weights': [], 'supplements': []
                }
            if key == 'feeds':
                grouped_results[age]['feeds'].append({'feed_type': row['feed_type'], 'quantity_per_day': row['quantity_per_day']})
            elif key == 'vaccines':
                grouped_results[age]['vaccines'].append(row['vaccine_name'])
            elif key == 'diseases':
                grouped_results[age]['diseases'].append(row['disease_name'])
            elif key == 'weights':
                grouped_results[age]['weights'].append(row['average_weight'])
            elif key == 'supplements':
                grouped_results[age]['supplements'].append({'supplement_name': row['supplement_name'], 'dosage': row['dosage']})

    if not grouped_results:
        return render_template('livestock_dashboard.html', error=f"No detailed data found for {query}.", animal=query)

    return render_template('livestock_dashboard.html', grouped_results=grouped_results, animal=query)
# Function to connect to SQLite
def get_db_connection():
    conn = sqlite3.connect('C:/Users/ADMIN/.vscode/.vscode/FlaskMarket/market.db')
    conn.row_factory = sqlite3.Row  # Allows fetching results as dictionaries
    return conn


# Age Calculator Route
@app.route('/livestock_dashboard/age_calculator', methods=['POST'])
def age_calculator():
    try:
        # Get form data
        dob_str = request.form['dob']
        calc_date_str = request.form['calc_date']
        format_choice = request.form['format_choice']

        # Convert strings to datetime objects
        dob = datetime.strptime(dob_str, '%Y-%m-%d')
        calc_date = datetime.strptime(calc_date_str, '%Y-%m-%d')

        # Validate dates
        if calc_date < dob:
            return jsonify({"error": "Calculate date must be after date of birth."})

        # Use relativedelta for precise age calculation
        delta = relativedelta(calc_date, dob)

        # Format result based on choice
        if format_choice == 'days':
            total_days = (calc_date - dob).days
            result = f"{total_days} days"
        elif format_choice == 'weeks':
            total_days = (calc_date - dob).days
            weeks = total_days // 7
            result = f"{weeks} weeks"
        elif format_choice == 'months':
            months = delta.years * 12 + delta.months
            result = f"{months} months"
        elif format_choice == 'years':
            years = delta.years
            result = f"{years} years"
        elif format_choice == 'ymd':
            result = f"{delta.years} years, {delta.months} months, {delta.days} days"

        return jsonify({"result": result})

    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})




def get_animal_info(animal_name):
    conn = sqlite3.connect('C:/Users/ADMIN/.vscode/.vscode/FlaskMarket/market.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM animals WHERE LOWER(name) = LOWER(?)", (animal_name,))
    animal = cursor.fetchone()
    conn.close()
    return animal


@app.route('/Privacy_page')
def Privacy_page():
    return render_template('Privacy_page.html')

@app.route('/nearby-vets')
def nearby_vets():
    return render_template('nearby-vets.html')


@app.route('/home2_page')
def home2_page():
    return render_template('home2.html')


@app.route('/livestock_dashboard')
def livestock_dashboard():
    return render_template('livestock_dashboard.html')

@app.route('/near-veterinaries')
def near_veterinaries():
    return render_template('near-veterinaries.html')



@app.route('/symptom-checker', methods=['GET', 'POST'])
def symptom_checker():
    form = SymptomCheckerForm()
    result = None
    recommended_vet = None

    if form.validate_on_submit():
        user_symptoms = [symptom.strip().lower() for symptom in form.symptoms.data.split(',')]
        illnesses = Illness.query.all()
        best_match = None
        max_matches = 0

        for illness in illnesses:
            illness_symptoms = [symptom.strip().lower() for symptom in illness.symptoms.split(',')]
            matches = len(set(user_symptoms) & set(illness_symptoms))
            if matches > max_matches:
                max_matches = matches
                best_match = illness

        if best_match and max_matches > 0:
            result = {
                'illness': best_match.name,
                'matched_symptoms': max_matches,
                'total_symptoms': len(best_match.symptoms.split(',')),
                'required_specialist': best_match.required_specialist
            }
            recommended_vet = Veterinary.query.filter_by(specialty=best_match.required_specialist).first()
            if not recommended_vet:
                flash("No veterinary found for this specialty.", category='warning')
        else:
            flash("No matching illness found for the given symptoms.", category='danger')

    return render_template('symptom_checker.html', form=form, result=result, recommended_vet=recommended_vet)


@app.route('/connect-farmers')
def connect_farmers():
    farmers = Farmer.query.all()
    return render_template('connect-farmers.html', farmers=farmers)


@app.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    try:
        data = request.get_json()
        vet_id = data.get('vetId')
        vet_name = data.get('vetName')
        appointment_date = data.get('appointmentDate')
        appointment_time = data.get('appointmentTime')
        animal_type = data.get('animalType')
        owner_name = data.get('ownerName')
        owner_email = data.get('ownerEmail')

        # Validate required fields
        if not all([vet_id, vet_name, appointment_date, appointment_time, animal_type, owner_name, owner_email]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Save the appointment
        appointment = Appointment(
            vet_id=int(vet_id),
            vet_name=vet_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            animal_type=animal_type,
            owner_name=owner_name,
            owner_email=owner_email,
            user_id=current_user.id
        )
        db.session.add(appointment)

        # Create a notification for the user
        notification = Notification(
            content=f"Appointment booked with {vet_name} on {appointment_date} at {appointment_time} for your {animal_type}",
            category='appointment',
            user_id=current_user.id
        )
        db.session.add(notification)
        db.session.commit()

        # Send confirmation email
        send_appointment_email(owner_email, vet_name, appointment_date, appointment_time, animal_type, owner_name)

        return jsonify({'message': 'Appointment booked successfully'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error booking appointment: {str(e)}")
        return jsonify({'error': str(e)}), 500


def send_vet_confirmation_email(email_receiver, vet_name):
    subject = 'Vet Profile Added - Livestock Management System'
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                padding: 20px 0;
                background-color: #D2B48C;
                color: white;
                border-radius: 8px 8px 0 0;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 20px;
                color: #333;
            }}
            .content p {{
                line-height: 1.6;
                margin: 10px 0;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                font-size: 12px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://livestockanalytics.com/hs-fs/hubfs/Logos%20e%20%C3%ADconos/livestock.png?width=115&height=70&name=livestock.png" alt="Livestock Management" style="max-width: 150px;">
                <h1>Livestock Management System</h1>
            </div>
            <div class="content">
                <p>Hello {vet_name},</p>
                <p>Your vet profile has been successfully added to the Livestock Management System!</p>
                <p>You can now be discovered by farmers and pet owners looking for veterinary services. Log in to manage your profile and appointments.</p>
            </div>
            <div class="footer">
                <p>© 2025 Livestock Management System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body, subtype='html')

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, EMAIL_PASSWORD)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        app.logger.info(f"Vet confirmation email sent to {email_receiver}")
    except Exception as e:
        app.logger.error(f"Email error: {str(e)}")
        raise


    
@app.route('/add_vet', methods=['GET', 'POST'])
@login_required
def add_vet():
    if current_user.role != 'vet':
        flash('Only vets can add profiles.', 'error')
        return redirect(url_for('nearby_vets_4'))
    
    form = VetForm()
    if form.validate_on_submit():
        vet_id = f"vet_{current_user.id}_{uuid4().hex[:8]}"
        while Vet.query.filter_by(vet_id=vet_id).first():
            vet_id = f"vet_{current_user.id}_{uuid4().hex[:8]}"

        # Compute the rating string
        rating_score = form.rating_score.data
        review_count = form.review_count.data
        rating = f"{rating_score} ({review_count} reviews)"

        vet = Vet(
            vet_id=vet_id,
            user_id=current_user.id,
            name=form.name.data,
            specialty=form.specialty.data,
            clinic=form.clinic.data,
            experience=int(form.experience.data),
            availability=form.availability.data,
            accepting=form.accepting.data,
            rating=rating,  # Store computed rating
            rating_score=rating_score,
            review_count=review_count,
            price=0,
            image_url=form.image_url.data or "https://via.placeholder.com/300x150",
            reviews=form.reviews.data or ""
        )
        db.session.add(vet)
        db.session.commit()

        vet_notification = Notification(
            content=f"Vet profile added: {vet.name}",
            category='vet_added',
            user_id=current_user.id
        )
        db.session.add(vet_notification)

        other_users = User.query.filter(User.id != current_user.id).all()
        for user in other_users:
            user_notification = Notification(
                content=f"New vet added: {vet.name}",
                category='new_vet',
                user_id=user.id
            )
            db.session.add(user_notification)
            try:
                send_vet_confirmation_email(user.email, vet.name, user.username)
            except Exception as e:
                app.logger.error(f"Failed to send new vet notification to {user.email}: {str(e)}")

        db.session.commit()

        try:
            send_vet_confirmation_email(form.email.data, vet.name)
        except Exception as e:
            app.logger.error(f"Failed to send vet confirmation email to {form.email.data}: {str(e)}")
            flash('Vet profile added successfully, but failed to send confirmation email.', 'warning')
        else:
            flash('Vet profile added successfully! A confirmation email has been sent.', 'success')

        return redirect(url_for('nearby_vets'))
    
    return render_template('add_vet.html', form=form)
    


    
@app.route('/edit_vet/<vet_id>', methods=['GET', 'POST'])
@login_required
def edit_vet(vet_id):
    vet = Vet.query.filter_by(vet_id=vet_id, user_id=current_user.id).first()
    if not vet:
        flash('Vet profile not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('vet_dashboard'))

    form = VetForm(obj=vet)
    if form.validate_on_submit():
        vet.name = form.name.data
        vet.specialty = form.specialty.data
        vet.clinic = form.clinic.data
        vet.experience = int(form.experience.data)
        vet.availability = form.availability.data
        vet.accepting = form.accepting.data
        vet.rating_score = form.rating_score.data
        vet.review_count = form.review_count.data
        vet.rating = f"{form.rating_score.data} ({form.review_count.data} reviews)"  # Update rating string
        vet.image_url = form.image_url.data or "https://via.placeholder.com/300x150"
        vet.reviews = form.reviews.data or ""

        db.session.commit()
        flash('Vet profile updated successfully!', 'success')
        return redirect(url_for('list_vets'))

    return render_template('edit_vet.html', form=form, vet=vet)


@app.route('/list_vets', defaults={'page': 1})
@app.route('/list_vets/<int:page>')
def list_vets(page):
    per_page = 6
    vets = Vet.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('nearby-vets-4.html', vets=vets, current_user=current_user)



# Define synonyms for animal types
ANIMAL_SYNONYMS = {
    'cow': ['cow', 'cattle', 'calf', 'bovine'],
    'cattle': ['cow', 'cattle', 'calf', 'bovine'],
    'calf': ['cow', 'cattle', 'calf', 'bovine'],
    'bovine': ['cow', 'cattle', 'calf', 'bovine'],
    'goat': ['goat', 'kid'],
    'sheep': ['sheep', 'lamb', 'ewe'],
    'pig': ['pig', 'swine', 'hog', 'boar', 'sow'],
    'swine': ['pig', 'swine', 'hog', 'boar', 'sow'],
    'chicken': ['chicken', 'poultry', 'hen', 'rooster'],
    'poultry': ['chicken', 'poultry', 'hen', 'rooster'],
    'horse': ['horse', 'mare', 'stallion', 'foal'],
    'donkey': ['donkey', 'ass', 'mule'],
    'cat': ['cat', 'kitten', 'feline'],
    'dog': ['dog', 'puppy', 'canine'],
    'rabbit': ['rabbit', 'bunny'],
    'camel': ['camel', 'dromedary', 'bactrian']
}


# Predefined symptom synonyms (from previous implementation)
SYMPTOM_SYNONYMS = {
    "high temperature": "fever",
    "elevated temperature": "fever",
    "coughing": "cough",
    "runny nose": "nasal discharge",
    "sneezing": "nasal discharge",
    "tiredness": "lethargy",
    "weakness": "lethargy",
    "breathing difficulty": "respiratory distress",
    "lameness": "limping",
    "rapid breathing": "respiratory distress",
    "weight loss": "emaciation",
    "swollen udder": "painful udder",
    "milk clots": "reduced milk yield",
    "redness of udder": "painful udder"
}


    
