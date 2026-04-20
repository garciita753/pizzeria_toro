from flask import request, Blueprint
from flask_restful import Api, Resource
import re
from .schemas import UsuariosSchema
from ..models import Usuario, Role
from flask_jwt_extended import create_access_token, jwt_required, current_user
from werkzeug.security import generate_password_hash

usuarios_v1_0_bp = Blueprint('films_v1_0_bp', __name__)
usuarios_schema = UsuariosSchema()
api = Api(usuarios_v1_0_bp)

class Registro_Resource(Resource):
    def post(self):
        try:
            data=request.get_json()
            campos_requeridos=['nombre', 'correo', 'contra', 'codigo', 'cedula','rol_id']
            if not data or not all(k in data for k in campos_requeridos):
                return {'error':'Faltan Datos'}, 400
            nombre = data['nombre'].strip()
            correo = data['correo'].strip()
            contra = data['contra']
            if not contra or not isinstance(contra, str) or contra.strip() == '':
                return {'error': 'La contraseña es requerida y no puede estar vacía'}, 400
            
            rol_id=int(data['rol_id'])
            codigo = data['codigo'].strip()
            cedula = data['cedula'].strip()
            if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', nombre):
                return {'error': 'El nombre completo debe contener solo letras'}, 400
            if not re.match(r'^[0-9]{5,10}$', codigo):
                return {'error':'Codigo debe contener solo numeros menor a 10 digitos y mayor a 4'},400
            if Usuario.get_by_email(correo):
                return {'error': f'El Email {correo} ya esta siendo utilizado por otra persona'}, 409
            
            user = Usuario(nombre=nombre, correo=correo, contra=contra, rol_id=rol_id, cedula=cedula, codigo=codigo)
            user.save()
            user_data = usuarios_schema.dump(user)
            return {'message': 'Trabajador Creado Exitosamente', 'user': user_data}, 201
        except Exception as e:
            return {'error': f'Error Interno del servidor: {str(e)}'}, 500
class Login_Resource(Resource):
    def post(self):
        try:
            data = request.get_json()
            
            campos_requeridos = ['correo', 'contra']
            if not data or not all(k in data for k in campos_requeridos):
                return {"error": "Faltan datos "}, 400
            
            correo = data['correo'].strip()
            contra = data['contra']
            usuarios = Usuario.get_by_email(correo)
            
            if usuarios is not None and usuarios.activo and usuarios.check_password(contra):
                rol = usuarios.rol.nombre if usuarios.rol else None
                nombre = usuarios.nombre
                token = create_access_token(identity=str(usuarios.id), additional_claims={"role": rol})
                #token = create_access_token(identity=usuarios.id, additional_claims={"role": rol})
                return {'access_token': token, 'message': 'Iniciado correctamente', 'rol': rol,
                        'nombre': nombre, 'id':           usuarios.id}, 200
            else:
                return {'error': 'Credenciales incorrectas o usuario inactivo'}, 401
        except Exception as e:
            return {'error': f'Error interno del servidor: {str(e)}'}, 500


class Usuario_Resource(Resource):
    @jwt_required()
    def get(self):
        try:
            user = current_user
            if not user:
                return {'error': 'Usuario no encontrado'}, 404
            return {'user': usuarios_schema.dump(user)}, 200
        except Exception as e:
            return {'error': f'Error interno del servidor: {str(e)}'}, 500


class UsuarioEdit_Resource(Resource):
    @jwt_required()
    def put(self, usuario_id):
        try:
            data = request.get_json()
            user = Usuario.query.get_or_404(usuario_id)
            current_user_obj = current_user
            

            if current_user_obj.id != user.id and (not current_user_obj.rol or current_user_obj.rol.nombre != 'admin'):
                return {'error': 'No tienes permisos para editar este usuario'}, 403
            

            if 'nombre' in data:
                nombre = data['nombre'].strip()
                if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', nombre):
                    return {'error': 'El nombre completo debe contener solo letras'}, 400
                user.nombre = nombre
            
            if 'rol_id' in data:
                rol_id = int(data['rol_id'])
                role = Role.query.get(rol_id)
                if not role:
                    return {'error': 'Rol no encontrado'}, 404
                user.rol_id = rol_id
            
            if 'codigo' in data:
                codigo = data['codigo'].strip()
                if not re.match(r'^[0-9]{5,10}$', codigo):
                    return {'error': 'Código debe contener solo números, menor a 10 dígitos y mayor a 4'}, 400
                user.codigo = codigo
            
            if 'activo' in data:
                # Solo admin puede cambiar activo
                if not current_user_obj.rol or current_user_obj.rol.nombre != 'admin':
                    return {'error': 'Solo administradores pueden cambiar el estado activo'}, 403
                activo = data['activo']
                if isinstance(activo, bool):
                    user.activo = activo
                else:
                    return {'error': 'activo debe ser true o false'}, 400
            
            user.save()
            user_data = usuarios_schema.dump(user)
            return {'message': 'Usuario actualizado exitosamente', 'user': user_data}, 200
        except Exception as e:
            return {'error': f'Error interno del servidor: {str(e)}'}, 500


class CambiarContrasena_Resource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            campos_requeridos = ['contra_actual', 'contra_nueva']
            if not data or not all(k in data for k in campos_requeridos):
                return {'error': 'Faltan datos: contra_actual y contra_nueva'}, 400
            
            contra_actual = data['contra_actual']
            contra_nueva = data['contra_nueva']
            
            if not contra_nueva or contra_nueva.strip() == '':
                return {'error': 'La nueva contraseña no puede estar vacía'}, 400
            
            user = current_user
            if not user.check_password(contra_actual):
                return {'error': 'La contraseña actual es incorrecta'}, 401
            
            user.set_password(contra_nueva)
            user.save()
            return {'message': 'Contraseña cambiada exitosamente'}, 200
        except Exception as e:
            return {'error': f'Error interno del servidor: {str(e)}'}, 500


class UsuariosList_Resource(Resource):
    def get(self):
        try:
            query = Usuario.query
            rol_nombre = request.args.get('rol')
            activo_str = request.args.get('activo')
            
            if rol_nombre:
                role = Role.query.filter_by(nombre=rol_nombre).first()
                if role:
                    query = query.filter_by(rol_id=role.id)
                else:
                    return {'error': f'Rol {rol_nombre} no encontrado'}, 404
            
            if activo_str is not None:
                if activo_str.lower() == 'true':
                    activo = True
                elif activo_str.lower() == 'false':
                    activo = False
                else:
                    return {'error': 'activo debe ser true o false'}, 400
                query = query.filter_by(activo=activo)
            
            usuarios = query.all()
            return {'users': usuarios_schema.dump(usuarios, many=True)}, 200
        except Exception as e:
            return {'error': f'Error interno del servidor: {str(e)}'}, 500

api.add_resource(Registro_Resource, '/api/v1.0/registrar/', '/Registro_Resource')
api.add_resource(Login_Resource, '/api/v1.0/login/', '/Login_Resource')
api.add_resource(Usuario_Resource, '/me')
api.add_resource(UsuarioEdit_Resource, '/api/v1.0/usuarios/<int:usuario_id>')
api.add_resource(CambiarContrasena_Resource, '/api/v1.0/cambiar_contrasena')
api.add_resource(UsuariosList_Resource, '/api/v1.0/list')
