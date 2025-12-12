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
    """Health check endpoint - verifica SOLO el estado de microservicio2"""
    # NO verificar microservicio1 aquí para que el pod pueda estar ready
    return jsonify({
        'status': 'healthy',
        'service': APP_NAME,
        'version': API_VERSION
    }), 200
 
@app.route('/health/full', methods=['GET'])
def health_full():
    """Health check completo - verifica estado y conectividad con microservicio1"""
    microservicio1_status = 'unknown'
    microservicio1_reachable = False
    try:
        # Verificar conectividad con microservicio1
        response = requests.get(
            f'{MICROSERVICIO1_URL}/health',
            timeout=5
        )
        if response.status_code == 200:
            microservicio1_status = 'healthy'
            microservicio1_reachable = True
        else:
            microservicio1_status = 'unhealthy'
            microservicio1_reachable = False
    except requests.exceptions.Timeout:
        microservicio1_status = 'timeout'
        logger.warning("Timeout connecting to microservicio1")
    except requests.exceptions.ConnectionError:
        microservicio1_status = 'unreachable'
        logger.warning("Cannot connect to microservicio1")
    except Exception as e:
        microservicio1_status = f'error: {str(e)}'
        logger.error(f"Error checking microservicio1: {str(e)}")
    return jsonify({
        'status': 'healthy',
        'service': APP_NAME,
        'version': API_VERSION,
        'microservicio1': {
            'status': microservicio1_status,
            'reachable': microservicio1_reachable,
            'url': MICROSERVICIO1_URL
        }
    }), 200
 
@app.route('/productos', methods=['GET'])
def get_productos():
    """GET endpoint - obtiene productos de microservicio1"""
    try:
        logger.info(f"Attempting to fetch products from {MICROSERVICIO1_URL}/productos")
        response = requests.get(
            f'{MICROSERVICIO1_URL}/productos',
            timeout=10
        )
        if response.status_code == 200:
            productos = response.json()
            logger.info(f"Successfully fetched {len(productos)} products")
            return jsonify({
                'source': 'microservicio1',
                'productos': productos,
                'count': len(productos)
            }), 200
        else:
            logger.error(f"Error response from microservicio1: {response.status_code}")
            return jsonify({
                'error': 'Error al obtener productos desde microservicio1',
                'status_code': response.status_code,
                'details': response.text
            }), response.status_code
    except requests.exceptions.Timeout:
        logger.error(f"Timeout connecting to {MICROSERVICIO1_URL}")
        return jsonify({
            'error': 'Timeout al conectar con microservicio1',
            'service_url': MICROSERVICIO1_URL
        }), 504
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to microservicio1: {str(e)}")
        return jsonify({
            'error': 'No se puede conectar con microservicio1',
            'service_url': MICROSERVICIO1_URL,
            'details': str(e)
        }), 503
    except Exception as e:
        logger.error(f"Unexpected error in get_productos: {str(e)}")
        return jsonify({
            'error': 'Error inesperado',
            'details': str(e)
        }), 500
 
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
        logger.info(f"Creating product: {data.get('nombre')}")
        # Reenviar solicitud a microservicio1
        response = requests.post(
            f'{MICROSERVICIO1_URL}/productos',
            json=data,
            timeout=10
        )
        if response.status_code == 201:
            producto = response.json()
            logger.info(f"Product created successfully: {producto.get('id')}")
            return jsonify({
                'source': 'microservicio1',
                'producto': producto,
                'created': True
            }), 201
        else:
            logger.error(f"Error creating product: {response.status_code}")
            return jsonify({
                'error': 'Error al crear producto en microservicio1',
                'status_code': response.status_code,
                'details': response.text
            }), response.status_code
    except requests.exceptions.Timeout:
        logger.error(f"Timeout connecting to {MICROSERVICIO1_URL}")
        return jsonify({
            'error': 'Timeout al conectar con microservicio1',
            'service_url': MICROSERVICIO1_URL
        }), 504
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to microservicio1: {str(e)}")
        return jsonify({
            'error': 'No se puede conectar con microservicio1',
            'service_url': MICROSERVICIO1_URL,
            'details': str(e)
        }), 503
    except Exception as e:
        logger.error(f"Unexpected error in create_producto: {str(e)}")
        return jsonify({
            'error': 'Error inesperado',
            'details': str(e)
        }), 500
 
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
    logger.info(f"Starting {APP_NAME} v{API_VERSION}")
    logger.info(f"Microservicio1 URL: {MICROSERVICIO1_URL}")
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=DEBUG
    )