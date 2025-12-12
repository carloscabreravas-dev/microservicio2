from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)

# Configuración
MICROSERVICIO1_URL = os.getenv('MICROSERVICIO1_URL', 'http://localhost:5000')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
APP_NAME = os.getenv('APP_NAME', 'Microservicio2 API')
API_VERSION = os.getenv('API_VERSION', '1.0.0')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint - verifica estado de microservicio2 y conectividad con microservicio1"""
    try:
        # Verificar conectividad con microservicio1
        response = requests.get(
            f'{MICROSERVICIO1_URL}/health',
            timeout=5
        )
        microservicio1_status = response.json() if response.status_code == 200 else {'status': 'unreachable'}
        
        return jsonify({
            'status': 'healthy',
            'service': APP_NAME,
            'version': API_VERSION,
            'microservicio1': microservicio1_status
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'microservicio1': 'unreachable'
        }), 500

@app.route('/productos', methods=['GET'])
def get_productos():
    """GET endpoint - obtiene productos de microservicio1"""
    try:
        response = requests.get(
            f'{MICROSERVICIO1_URL}/productos',
            timeout=10
        )
        
        if response.status_code == 200:
            productos = response.json()
            return jsonify({
                'source': 'microservicio1',
                'productos': productos,
                'count': len(productos)
            }), 200
        else:
            return jsonify({
                'error': 'Error al obtener productos desde microservicio1',
                'status_code': response.status_code
            }), response.status_code
    except requests.exceptions.ConnectionError:
        logger.error("Connection error to microservicio1")
        return jsonify({
            'error': 'No se puede conectar con microservicio1',
            'service_url': MICROSERVICIO1_URL
        }), 503
    except Exception as e:
        logger.error(f"Error in get_productos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/productos', methods=['POST'])
def create_producto():
    """POST endpoint - crea un nuevo producto en microservicio1"""
    try:
        data = request.get_json()
        
        # Validar datos
        if not data or 'nombre' not in data or 'descripcion' not in data:
            return jsonify({
                'error': 'nombre y descripcion son requeridos'
            }), 400
        
        # Reenviar solicitud a microservicio1
        response = requests.post(
            f'{MICROSERVICIO1_URL}/productos',
            json=data,
            timeout=10
        )
        
        if response.status_code == 201:
            producto = response.json()
            return jsonify({
                'source': 'microservicio1',
                'producto': producto,
                'created': True
            }), 201
        else:
            return jsonify({
                'error': 'Error al crear producto en microservicio1',
                'status_code': response.status_code,
                'details': response.text
            }), response.status_code
    except requests.exceptions.ConnectionError:
        logger.error("Connection error to microservicio1")
        return jsonify({
            'error': 'No se puede conectar con microservicio1',
            'service_url': MICROSERVICIO1_URL
        }), 503
    except Exception as e:
        logger.error(f"Error in create_producto: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint - información sobre el servicio"""
    return jsonify({
        'service': APP_NAME,
        'version': API_VERSION,
        'status': 'running',
        'microservicio1_url': MICROSERVICIO1_URL
    }), 200

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=DEBUG
    )
