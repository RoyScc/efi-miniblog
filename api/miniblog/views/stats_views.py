from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from ..extensions import db
from ..models import Usuario, Post, Comentario 

stats_bp = Blueprint('stats_views', __name__)

@stats_bp.route('/api/stats', methods=['GET'])
@jwt_required()
def get_stats():
    claims = get_jwt()
    user_role = claims.get("role")
    current_user_id = get_jwt_identity()

   
    if user_role == 'admin':
        total_users = Usuario.query.count()
        total_posts = Post.query.count()
        total_comments = Comentario.query.count()
        
        return jsonify({
            "rol": "admin",
            "estadisticas": {
                "total_usuarios": total_users,
                "total_posts": total_posts,
                "total_comentarios": total_comments
            }
        }), 200

    
    elif user_role == 'mod':
        try:
            pending_posts = Post.query.filter_by(is_published=False).count()
        except Exception:
            pending_posts = 0

        return jsonify({
            "rol": "mod",
            "estadisticas": {
                "posts_pendientes": pending_posts
            }
        }), 200

     
    elif user_role == 'user':
        current_user_id_int = int(current_user_id) 
        
        user_posts_count = Post.query.filter_by(autor_id=current_user_id_int).count()
        user_comments_count = Comentario.query.filter_by(autor_id=current_user_id_int).count() # Asumiendo que Comentario también usa autor_id
        
        return jsonify({
            "rol": "user",
            "estadisticas": {
                "mis_posts": user_posts_count,
                "mis_comentarios": user_comments_count
            }
        }), 200
        
    
    else:
        return jsonify({
            "rol": user_role,
            "msg": "Acceso denegado. No hay estadísticas definidas para tu rol."
        }), 403