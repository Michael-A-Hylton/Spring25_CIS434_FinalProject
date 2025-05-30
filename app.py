from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from model import db, bcrypt, User, Message
from forms import LoginForm, RegisterForm
from config import Config
from flask_mail import Mail, Message as MailMessage


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt.init_app(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    sent_ids = db.session.query(Message.receiver_id).filter_by(sender_id=current_user.id)
    received_ids = db.session.query(Message.sender_id).filter_by(receiver_id=current_user.id)
    user_ids = sent_ids.union(received_ids).distinct()
    conversations = User.query.filter(User.id.in_(user_ids)).filter(User.id != current_user.id).all()
    return render_template('home.html', conversations=conversations, selected_user=None, messages=[])


@app.route('/message/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def message(receiver_id):
    selected_user = User.query.get_or_404(receiver_id)

    if request.method == 'POST':
        content = request.form.get('message')
        if content:
            msg = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('message', receiver_id=receiver_id))

    # All conversations
    sent_ids = db.session.query(Message.receiver_id).filter_by(sender_id=current_user.id)
    received_ids = db.session.query(Message.sender_id).filter_by(receiver_id=current_user.id)
    user_ids = sent_ids.union(received_ids).distinct()
    conversations = User.query.filter(User.id.in_(user_ids)).filter(User.id != current_user.id).all()

    # Conversation with selected user
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()

    return render_template('home.html', conversations=conversations, selected_user=selected_user, messages=messages)
# 🔍 Search for user to start new chat
@app.route('/search_user', methods=['GET', 'POST'])
@login_required
def search_user():
    query = request.args.get('q', '')
    if query:
        users = User.query.filter(User.username.ilike(f'%{query}%')).filter(User.id != current_user.id).all()
    else:
        users = []

    return render_template('search_user.html', users=users, query=query)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if request.method == 'POST':
        print("Form is being submitted!")
        print("Form data:", request.form)
        print("Validation errors:", form.errors)

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)

        user = User(
            username=form.username.data,
            email=form.email.data,
            public_key=request.form.get('public_key')
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))  # ← was wrongly indented before

    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            user.generate_2fa_code()
            db.session.commit()

            msg = MailMessage('Your 2FA Code', recipients=[user.email])
            msg.body = f'Your verification code is: {user.two_factor_code}'
            mail.send(msg)

            session['pending_2fa_user_id'] = user.id
            flash('A verification code has been sent to your email.', 'info')
            return redirect(url_for('verify_2fa'))

        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/search_api')
@login_required
def search_api():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    users = User.query.filter(User.username.ilike(f"%{query}%")).limit(10).all()
    return jsonify([{'id': u.id, 'username': u.username} for u in users])

@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'pending_2fa_user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['pending_2fa_user_id'])

    if request.method == 'POST':
        code = request.form.get('code')

        if user:
            valid, message, commit_required = user.verify_2fa_code(code)

            if commit_required:
                db.session.commit()

            if valid:
                login_user(user)
                session.pop('pending_2fa_user_id', None)
                user.two_factor_code = None
                user.two_factor_expiry = None
                db.session.commit()
                return redirect(url_for('home'))
            else:
                flash(message, 'danger')
                return render_template('verify_2fa.html')

    return render_template('verify_2fa.html')

@app.route('/2fa', methods=['GET', 'POST'])
def two_factor():
    user_id = session.get('pre_2fa_user_id')
    if not user_id:
        flash('Session expired. Please log in again.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        entered_code = ''.join(request.form.get(f'code{i}') for i in range(6))
        user = User.query.get(user_id)

        if user and entered_code == user.two_factor_code:
            # Verification passed — log the user in
            login_user(user)
            session.pop('pre_2fa_user_id', None)
            return redirect(url_for('dashboard'))  # or whatever your post-login page is

        flash('Invalid 2FA code.', 'danger')

    return render_template('two_factor.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
