"""
AI Infrastructure Generator - Main Application
"""
from flask import Flask, request, jsonify, render_template
from config.settings import Config
from generators.terraform import TerraformGenerator
from generators.kubernetes import KubernetesGenerator
from utils.stats import track_generation, get_stats

app = Flask(__name__)
app.config.from_object(Config)

# Initialize generators
terraform_gen = TerraformGenerator()
kubernetes_gen = KubernetesGenerator()


@app.route('/')
def home():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/generate/terraform', methods=['POST'])
def generate_terraform():
    print("Generating terraform code...")
    try:
        data = request.json
        requirements = data.get('requirements', '')

        if not requirements:
            return jsonify({'error': 'No requirements provided'}), 400

        result = terraform_gen.generate(requirements)
        track_generation('terraform')

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate/kubernetes', methods=['POST'])
def generate_kubernetes():
    print("Generating Kubernetes manifests...")
    try:
        data = request.json
        requirements = data.get('requirements', '')

        if not requirements:
            return jsonify({'error': 'No requirements provided'}), 400

        result = kubernetes_gen.generate(requirements)
        track_generation('kubernetes')

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/stats')
def stats():
    """Get usage statistics"""
    return jsonify(get_stats())


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    print("🚀 Starting AI Infrastructure Generator...")
    print(f"📍 Open http://localhost:{Config.PORT} in your browser")
    print(f"🤖 Using {Config.AI_PROVIDER} provider")

    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )