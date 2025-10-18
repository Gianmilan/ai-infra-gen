"""
AI Infrastructure Generator - Main Application
"""
import subprocess
import logging

from flask import Flask, request, jsonify, render_template
from config.settings import Config
from generators.terraform import TerraformGenerator
from generators.kubernetes import KubernetesGenerator
from utils.stats import track_generation, get_stats
from utils.cache import cache

# Setup logging first
Config.setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize generators
logger.info("Initializing infrastructure generators...")
terraform_gen = TerraformGenerator()
kubernetes_gen = KubernetesGenerator()
logger.info("Generators initialized successfully")


@app.route('/')
def home():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/generate/terraform', methods=['POST'])
def generate_terraform():
    logger.info("=== Terraform generation request received ===")
    try:
        data = request.json
        requirements = data.get('requirements', '')

        if not requirements:
            logger.warning("Terraform generation rejected: no requirements provided")
            return jsonify({'error': 'No requirements provided'}), 400

        logger.info(f"Processing Terraform request (requirements length: {len(requirements)} chars)")
        result = terraform_gen.generate(requirements)
        track_generation('terraform')
        logger.info("Terraform generation completed successfully")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Terraform generation failed: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/generate/kubernetes', methods=['POST'])
def generate_kubernetes():
    logger.info("=== Kubernetes generation request received ===")
    try:
        data = request.json
        requirements = data.get('requirements', '')

        if not requirements:
            logger.warning("Kubernetes generation rejected: no requirements provided")
            return jsonify({'error': 'No requirements provided'}), 400

        logger.info(f"Processing Kubernetes request (requirements length: {len(requirements)} chars)")
        result = kubernetes_gen.generate(requirements)
        track_generation('kubernetes')
        logger.info("Kubernetes generation completed successfully")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Kubernetes generation failed: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/generate/auto', methods=['POST'])
def generate_auto():
    logger.info("=== Auto-detect generation request received ===")
    try:
        data = request.json
        requirements = data.get('requirements', '')

        if not requirements:
            logger.warning("Auto-detect generation rejected: no requirements provided")
            return jsonify({'error': 'No requirements provided'}), 400

        req_lower = requirements.lower()

        k8s_keywords = ['kubernetes', 'k8s', 'pod', 'deployment', 'service',
                        'namespace', 'configmap', 'secret', 'ingress',
                        'statefulset', 'daemonset', 'helm']

        tf_keywords = ['terraform', 'aws', 'azure', 'gcp', 'ec2', 's3',
                       'rds', 'lambda', 'cloudfront', 'elasticache', 'vpc']

        k8s_score = sum(1 for kw in k8s_keywords if kw in req_lower)
        tf_score = sum(1 for kw in tf_keywords if kw in req_lower)

        if k8s_score > tf_score:
            logger.info(f"Auto-detected: Kubernetes (k8s_score={k8s_score}, tf_score={tf_score})")
            result = kubernetes_gen.generate(requirements)
            result['detected_type'] = 'kubernetes'
            track_generation('kubernetes')

        else:
            logger.info(f"Auto-detected: Terraform (k8s_score={k8s_score}, tf_score={tf_score})")
            result = terraform_gen.generate(requirements)
            result['detected_type'] = 'terraform'
            track_generation('terraform')

        logger.info("Auto-detect generation completed successfully")
        return jsonify(result)

    except Exception as e:
        logger.error(f"Auto-detect generation failed: {str(e)}", exc_info=True)
        return jsonify({'error': f'Could not detect Kubernetes nor Terraform keywords from prompt: {str(e)}'}), 500


@app.route('/stats')
def stats():
    """Get usage statistics"""
    return jsonify(get_stats())


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


@app.route('/cache/info')
def cache_info():
    """Get cache information"""
    logger.info("Cache info requested")
    return jsonify(cache.info())


@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache (debug mode only)"""
    if not Config.DEBUG:
        logger.warning("Cache clear attempt rejected (not in debug mode)")
        return jsonify({'error': 'Cache clearing only available in debug mode'}), 403

    logger.info("Cache clear requested")
    count = cache.clear()
    return jsonify({
        'success': True,
        'items_cleared': count,
        'message': f'Cache cleared ({count} items removed)'
    })


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting AI Infrastructure Generator...")
    logger.info(f"Server URL: http://{Config.HOST}:{Config.PORT}")
    logger.info(f"AI Provider: {Config.AI_PROVIDER}")
    logger.info(f"Debug Mode: {Config.DEBUG}")
    logger.info(f"Validation: {'Enabled' if Config.ENABLE_VALIDATION else 'Disabled'}")
    logger.info(f"Caching: {'Enabled' if Config.ENABLE_CACHE else 'Disabled'}")
    logger.info(f"Log Level: {Config.LOG_LEVEL}")
    logger.info(f"Log File: {Config.CACHE_DIR / 'app.log'}")
    logger.info("=" * 60)

    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )