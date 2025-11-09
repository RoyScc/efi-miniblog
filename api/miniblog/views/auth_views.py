from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_login import login_user, current_user, login_required, logout_user
from ..models import db, Usuario, UserCredentials 
from ..schemas import user_schema

auth_bp = Blueprint('auth_views', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = Usuario.query.filter_by(nombre=username).first()

    if not user or not user.credentials or not check_password_hash(
        pwhash=user.credentials.password_hash, 
        password=password
    ):
        return jsonify({"error": "Credenciales inválidas"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "email": user.correo}
    )
    
    return jsonify({
        "mensaje": "Login exitoso",
        "token": access_token,
        "user": user_schema.dump(user) 
    }), 200

@auth_bp.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Faltan datos (username, email o password)"}), 400
    existing_user = Usuario.query.filter_by(correo=email).first()
    if existing_user:
        return jsonify({"error": "El email ya está registrado"}), 409

    hashed_password = generate_password_hash(password)
    try:
        new_user = Usuario(nombre=username, correo=email)
        new_credentials = UserCredentials(password_hash=hashed_password, user=new_user)
        db.session.add(new_user)
        db.session.add(new_credentials)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al guardar en la base de datos", "detalle": str(e)}), 500

    return jsonify({
        "mensaje": "Usuario registrado exitosamente",
        "usuario": { "id": new_user.id, "username": new_user.nombre, "email": new_user.correo }
    }), 201

# Ruta de Template para Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
     if current_user.is_authenticated:
         return redirect(url_for('index')) # 'index' debe estar en otro blueprint
     if request.method == 'POST':
         username = request.form.get('username')
         password = request.form.get('password')
         user = Usuario.query.filter_by(nombre=username).first()
         if user and user.credentials and check_password_hash(
             pwhash=user.credentials.password_hash, 
             password=password
         ):
             login_user(user)
             next_page = request.args.get('next') 
             # 'index' se referenciará como 'main.index' (blueprint.función)
             return redirect(next_page or url_for('main.index')) 
         else: 
             flash('Usuario o contraseña inválidos.', 'danger')
     return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('index'))