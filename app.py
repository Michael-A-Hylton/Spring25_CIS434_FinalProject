from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from model import db, bcrypt, User, Message
from forms import LoginForm, RegisterForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt.init_app(app)

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
        print("Form is being submitted!")  # Should print no matter what
        print("Form data:", request.form)  # Raw data
        print("Validation errors:", form.errors)  # Show why it failed

    if form.validate_on_submit():
        print("Form validated!")
        print("Password ")
        print(request.form.password.data)
        print(request.form.password)
        print(form.password.data)


        if request.form.password != request.form.confirm_password:
            flash('Passwords do not match! Please try again.', 'danger')
            return render_template('register.html', form=form)

        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)

        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
