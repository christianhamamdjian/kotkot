import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from flask import Flask, render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, \
    current_user
from werkzeug.utils import secure_filename
from . import auth
from .. import db
from ..models import User, ToDo
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm, PaivitaKayttaja, UusiKayttaja
from datetime import datetime
import cloudinary.uploader

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'app/uploads'


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Virheellinen sähköpostiosoite tai salasana.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Olet kirjautunut ulos.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Vahvista tilisi.',
                   'auth/email/confirm', user=user, token=token)
        flash('Vahvistusviesti on lähetetty sinulle sähköpostitse.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('Olet vahvistanut tilisi. Kiitos!')
    else:
        flash('Vahvistuslinkki on virheellinen tai on vanhentunut.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('Sähköpostilla on lähetetty uusi vahvistusviesti sähköpostitse.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Salasanasi on päivitetty.')
            return redirect(url_for('main.index'))
        else:
            flash('Virheellinen salasana.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Nollaa salasana',
                       'auth/email/reset_password',
                       user=user, token=token)
        flash('Sähköposti, jossa on ohjeet salasanan vaihtamiseksi,  '
              'on lähetetty sinulle.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Salasanasi on päivitetty.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Vahvista sähköpostiosoitteesi',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('Sähköposti, jossa on ohjeet uuden sähköpostiosoitteesi vahvistamiseksi,  '
                  'on lähetetty sinulle.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Sähköpostiosoitteesi on päivitetty.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))

def upload_to_cloudinary(filename):
            # To Cloudinary
            cloudinary.config(
                cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
                api_key=os.getenv("CLOUDINARY_API_KEY"),
                api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            )
            upload_result = cloudinary.uploader.upload(os.path.join(app.config['UPLOAD_PATH'], filename))
            return upload_result
            # Cloudinary End

@auth.route('/kayttaja_profiili/<username>', methods=['GET', 'POST'])
@login_required
def kayttaja_profiili(username):
    user = User.query.filter_by(username = username).first_or_404()
    return render_template('auth/users/kayttaja_profiili.html', user = user) 


@auth.route('/paivita_kayttaja', methods=['GET', 'POST'])
@login_required
def paivita_kayttaja():
    if request.method == "POST":
            uploaded_file = request.files['kuva']
            filename = secure_filename(uploaded_file.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                file_info = upload_to_cloudinary(filename)
                file_url = file_info['url']

                user = User.query.get(request.form.get("id"))
                user.kuva = file_url
                user.username = request.form["username"]
                user.email = request.form["email"]
                db.session.commit()
                flash("Käyttäjä päivitetty onnistuneesti.")
                token = user.generate_confirmation_token()

            else:
                user = User.query.get(request.form.get("id"))
                user.kuva = 'http://res.cloudinary.com/dzgrmafak/image/upload/v1620127841/qya7suptxee7x8ri6wau.png'
                user.username = request.form["username"]
                user.email = request.form["email"]
                db.session.add(user)
                db.session.commit()
                token = user.generate_confirmation_token()

                # user = User.query.get(request.form.get("id"))
                # user.kuva = request.files["kuva"]
                # user.username = request.form["username"]
                # user.email = request.form["email"]
                # db.session.commit()
                # flash("Käyttäjä päivitetty onnistuneesti.")
                
    # if form.validate_on_submit():
    #     uploaded_file = request.files['file']
    #     filename = secure_filename(uploaded_file.filename)
    #     if filename != '':
    #         file_ext = os.path.splitext(filename)[1]
    #         if file_ext not in app.config['UPLOAD_EXTENSIONS']:
    #             abort(400)
    #         uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        
    #         file_info = upload_to_cloudinary(filename)
    #         file_url = file_info['url']
    #         user = User(email=form.email.data.lower(),
    #                             username=form.username.data,
    #                             password=form.password.data,
    #                             kuva=file_url)
    #         db.session.add(user)
    #         db.session.commit()
    #         token = user.generate_confirmation_token()

    #     else:
    #         user = User(email=form.email.data.lower(),
    #                 username=form.username.data,
    #                 password=form.password.data,
    #                 kuva= 'app/uploads/img-placeholder.png')
    #         db.session.add(user)
    #         db.session.commit()
    #         token = user.generate_confirmation_token()


        # send_email(user.email, 'Confirm Your Account',
        #            'auth/email/confirm', user=user, token=token)
        # flash('Vahvistusviesti on lähetetty sinulle sähköpostitse.')

        # return redirect(url_for('auth.login'))
    # return render_template('auth/profile.html', form=form)

    # user = User.query.filter_by(username = username).first_or_404()
    form = UusiKayttaja()
    kayttajat = User.query.order_by(User.id.asc()).all()
    return render_template('auth/users/kayttajat.html', kayttajat=kayttajat, form=form )


@auth.route('/uusi_kayttaja', methods=['GET', 'POST'])
@login_required
def uusi_kayttaja():
    form = UusiKayttaja()
    if form.validate_on_submit():
            uploaded_file = request.files['file']
            filename = secure_filename(uploaded_file.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            
                file_info = upload_to_cloudinary(filename)
                file_url = file_info['url']
                user = User(email=form.email.data.lower(),
                                    username=form.username.data,
                                    password=form.password.data,
                                    kuva=file_url)
                db.session.add(user)
                db.session.commit()
                token = user.generate_confirmation_token()

            else:
                user = User(email=form.email.data.lower(),
                        username=form.username.data,
                        password=form.password.data,
                        kuva= 'http://res.cloudinary.com/dzgrmafak/image/upload/v1620127841/qya7suptxee7x8ri6wau.png')
                db.session.add(user)
                db.session.commit()
                token = user.generate_confirmation_token()

            return redirect(url_for('auth.login'))

    # user = User.query.filter_by(username = username).first_or_404()
    return render_template("auth/users/uusi_kayttaja.html", form=form) 

@auth.route('/uusi_tehtava', methods=['GET', 'POST'])
@login_required
def uusi_tehtava():
    if request.method == "POST":
        # Taking Form Data To Add A Task
        task_title = request.form["title"]
        task_description = request.form["description"]

        # Storing Data In ToDo Model
        new_task = ToDo(title = task_title, description = task_description)
        new_task.user_id = current_user.id
        new_task.is_completed = False

        # Adding In DB
        try:
            db.session.add(new_task)
            db.session.commit()
            flash("Tehtäväsi on luotu onnistuneesti!")
            return redirect(url_for("auth.tehtavat"))
        except:
            flash("Oli ongelma lisäämällä tehtävääsi! Yritä uudelleen myöhemmin.")


@auth.route('/paivita_tehtava', methods=['GET', 'POST'])
@login_required
def paivita_tehtava():
    if request.method == "POST":
            task = ToDo.query.get(request.form.get("item_id"))
            task.title = request.form["title"]
            task.description = request.form["description"]
            task.date_updated = datetime.utcnow()

            db.session.commit()
            flash("Tehtävä päivitetty onnistuneesti.")
            return redirect(url_for("auth.tehtavat"))


@auth.route('/poista', methods=['GET', 'POST'])
@login_required
def poista():
    id = request.form.get('id')
    task_to_delete = ToDo.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    flash(f"Tehtävä {task_to_delete.nimi} on poistettu.") 
    response = jsonify(success=True)
    response.status_code = 200
    return response
    
@auth.route('/poista_kayttaja', methods=['GET', 'POST'])
@login_required
def poista_kayttaja():
    id = request.form.get('id')
    user_to_delete = User.query.get_or_404(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f"Käyttäjä {user_to_delete.username} on poistettu.") 
    response = jsonify(success=True)
    response.status_code = 200
    return response

@auth.route('/kayttajat', methods=['GET', 'POST'])
@login_required
def kayttajat():
    form=UusiKayttaja()
    if form.validate_on_submit():
            uploaded_file = request.files['file']
            filename = secure_filename(uploaded_file.filename)
                
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            
                file_info = upload_to_cloudinary(filename)
                file_url = file_info['url']
                user = User(email=form.email.data.lower(),
                                    username=form.username.data,
                                    password=form.password.data,
                                    kuva=file_url)
                db.session.add(user)
                db.session.commit()
                token = user.generate_confirmation_token()

            else:
                user = User(email=form.email.data.lower(),
                        username=form.username.data,
                        password=form.password.data,
                        kuva= 'app/uploads/img-placeholder.png')
                db.session.add(user)
                db.session.commit()
                token = user.generate_confirmation_token()

            # return redirect(url_for('auth.login'))
    # if 'id' in request.args:
    #         id = request.args.get('id')
    #         user= User.query.get_or_404(id)
    #         form = PaivitaKayttaja(obj=user)
            
    kayttajat = User.query.order_by(User.id.asc()).all()
    return render_template('auth/users/kayttajat.html', kayttajat=kayttajat, form=form ) 


@auth.route('/tehtavat', methods=['GET', 'POST'])
@login_required
def tehtavat():
    todoitems = ToDo.query.filter_by(user_id = current_user.id).order_by(ToDo.date_created.desc()).all()
    return render_template('auth/tasks/tehtavat.html', todoitems=todoitems) 


@auth.route('/tehtava', methods=['GET', 'POST'])
@login_required
def tehtava():

    return render_template('auth/tehtava.html') 


# @auth.route("/poistaa/<int:id>", methods=['POST'])
# def poistaa(id):
#     task_to_delete = ToDo.query.get_or_404(id)

#     try:
#         db.session.delete(task_to_delete)
#         db.session.commit()
#         return redirect(url_for("auth.tehtavat"))
#     except:
#         flash("Oli ongelma poistaa tämä tehtävä! Yritä uudelleen myöhemmin.")


# User Profile Edit Form
# class EditProfileForm(FlaskForm):
#     username = StringField("Username", validators = [DataRequired(message="Käyttäjätunnus on pakollinen")])
#     firstName = StringField("First Name", validators = [DataRequired(message="Etunimi vaaditaan")])
#     lastName = StringField("Last Name", validators = [DataRequired(message="Sukunimi vaaditaan")])
#     submit = SubmitField("Lähetä")

#     def __init__(self, original_username, *args, **kwargs):
#         super(EditProfileForm, self).__init__(*args, **kwargs)
#         self.original_username = original_username

#     def validate_username(self, username):
#         if username.data != self.original_username:
#             user = User.query.filter_by(username = self.username.data).first()
#             if user is not None:
#                 raise ValidationError("Käytä toista käyttäjänimeä.")


# @app.route("/add", methods = ["POST"])
# def add_task():
#     if request.method == "POST":
#         # Taking Form Data To Add A Task
#         task_title = request.form["title"]
#         task_description = request.form["description"]

#         # Storing Data In ToDo Model
#         new_task = ToDo(title = task_title, description = task_description)
#         new_task.user_id = current_user.id
#         new_task.is_completed = False

#         # Adding In DB
#         try:
#             db.session.add(new_task)
#             db.session.commit()
#             flash("Tehtäväsi on luotu onnistuneesti!")
#             return redirect(url_for("index"))
#         except:
#             flash("Oli ongelma lisäämällä tehtävääsi! Yritä uudelleen myöhemmin.")


# Edit User Profile Information
# @auth.route("/editProfile", methods = ["GET", "POST"])
# @login_required
# def editProfile():
#     form = EditProfileForm(current_user.username)
#     # if form.validate_on_submit():
#     #     current_user.username = form.username.data
#     #     current_user.firstName = form.firstName.data
#     #     current_user.lastName = form.lastName.data
#     #     db.session.commit()
#     #     flash(_("Your changes have been saved"))
#     #     return redirect(url_for("editProfile"))
#     # elif request.method == "GET":
#     #     form.username.data = current_user.username
#     #     form.firstName.data = current_user.firstName
#     #     form.lastName.data = current_user.lastName
#     return render_template("auth/users/editProfile.html", form = form)