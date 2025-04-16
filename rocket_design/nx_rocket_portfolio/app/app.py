"""
Flask web application for NX Rocket Portfolio.
Provides a web interface for creating, modifying, and viewing parametric rocket components.
"""

import os
import sys
import json
import logging
import uuid
import time
import traceback
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import NX API
# Add parent directory to sys.path to enable package imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Add the root project directory to enable absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # Use absolute import path
    from nx_rocket_portfolio.api import nx_model_api
    from nx_rocket_portfolio.services.ai_controller import ai_controller
    from nx_rocket_portfolio.app.ai_design_helpers import update_geometry_file
    nx_api_available = True
except ImportError as e:
    logger.error(f"Failed to import NX API: {e}")
    nx_api_available = False

# Create Flask app
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')

# Create required directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Dictionary to store user sessions
user_sessions = {}

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html', nx_available=nx_api_available)

@app.route('/components')
def components_page():
    """Render components catalog page"""
    components = []
    if nx_api_available:
        components = nx_model_api.get_available_components()
    return render_template('components.html', components=components)

@app.route('/editor/<component_id>')
def editor_page(component_id):
    """Render editor page for a specific component"""
    component_info = {}
    if nx_api_available:
        component_info = nx_model_api.get_component_parameters(component_id)
    return render_template('editor.html', component=component_info)

@app.route('/portfolio')
def portfolio_page():
    """Render portfolio page"""
    return render_template('portfolio.html')

@app.route('/stage-designer')
@app.route('/stage-designer/<component_id>')
def stage_designer_page(component_id=None):
    """Render rocket stage designer with real-world examples"""
    # No need to check NX availability for pure JavaScript designers
    # The rocket_presets.js file will handle the real-world examples
    return render_template('stage_designer.html', component_id=component_id)

@app.route('/structural-analysis')
def structural_analysis_page():
    """Render structural analysis tools for rocket components"""
    # This is a client-side tool that doesn't require NX API
    return render_template('structural_analysis.html')

@app.route('/ai-designer')
def ai_designer_page():
    """Render AI-assisted rocket design interface"""
    # This is an interactive design tool with AI assistance
    return render_template('ai_designer.html')

@app.route('/api/components', methods=['GET'])
def get_components():
    """API endpoint to get available components"""
    if not nx_api_available:
        return jsonify({"error": "NX API not available"}), 503
    
    components = nx_model_api.get_available_components()
    return jsonify(components)

@app.route('/api/parameters/<component_id>', methods=['GET'])
def get_parameters(component_id):
    """API endpoint to get parameters for a component type"""
    if not nx_api_available:
        return jsonify({"error": "NX API not available"}), 503
    
    params = nx_model_api.get_component_parameters(component_id)
    return jsonify(params)

@app.route('/api/models', methods=['POST'])
def create_model():
    """API endpoint to create a new model"""
    if not nx_api_available:
        return jsonify({"error": "NX API not available"}), 503
    
    data = request.json
    
    # Generate model ID if not provided
    model_id = data.get('model_id', str(uuid.uuid4()))
    component_id = data.get('component_id')
    parameters = data.get('parameters', {})
    
    if not component_id:
        return jsonify({"error": "Component ID required"}), 400
    
    # Create model
    result = nx_model_api.create_model(model_id, component_id, parameters)
    
    # Save to user session
    user_id = request.headers.get('X-User-ID', 'anonymous')
    if user_id not in user_sessions:
        user_sessions[user_id] = []
    
    user_sessions[user_id].append(model_id)
    
    return jsonify(result)

@app.route('/api/models/<model_id>', methods=['PUT'])
def update_model(model_id):
    """API endpoint to update model parameters"""
    if not nx_api_available:
        return jsonify({"error": "NX API not available"}), 503
    
    data = request.json
    parameters = data.get('parameters', {})
    
    result = nx_model_api.update_model_parameters(model_id, parameters)
    return jsonify(result)

@app.route('/api/models/<model_id>', methods=['DELETE'])
def delete_model(model_id):
    """API endpoint to delete a model"""
    if not nx_api_available:
        return jsonify({"error": "NX API not available"}), 503
    
    result = nx_model_api.delete_model(model_id)
    
    # Remove from user session
    user_id = request.headers.get('X-User-ID', 'anonymous')
    if user_id in user_sessions and model_id in user_sessions[user_id]:
        user_sessions[user_id].remove(model_id)
    
    return jsonify(result)

@app.route('/api/models/<model_id>/export', methods=['POST'])
def export_model(model_id):
    """API endpoint to export a model to NX"""
    if not nx_api_available:
        return jsonify({"error": "NX API not available"}), 503
    
    data = request.json
    file_path = data.get('file_path')
    
    # If no path specified, generate one in the output folder
    if not file_path:
        filename = f"{model_id}.prt"
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    result = nx_model_api.export_model_to_nx(model_id, file_path)
    return jsonify(result)

@app.route('/api/models/<model_id>/performance', methods=['GET'])
def get_performance(model_id):
    """API endpoint to get performance metrics for a model"""
    if not nx_api_available:
        return jsonify({"error": "NX API not available"}), 503
    
    result = nx_model_api.calculate_performance_metrics(model_id)
    return jsonify(result)

@app.route('/api/models/<model_id>/preview', methods=['GET'])
def get_preview(model_id):
    """API endpoint to get preview data for a model"""
    if not nx_api_available:
        return jsonify({"error": "NX API not available"}), 503
    
    result = nx_model_api.get_model_preview_data(model_id)
    return jsonify(result)

@app.route('/api/user/models', methods=['GET'])
def get_user_models():
    """API endpoint to get models for the current user"""
    user_id = request.headers.get('X-User-ID', 'anonymous')
    
    models = []
    if user_id in user_sessions:
        for model_id in user_sessions[user_id]:
            try:
                model = nx_model_api.get_model_preview_data(model_id)
                models.append(model)
            except Exception as e:
                logger.error(f"Error getting model {model_id}: {e}")
    
    return jsonify({"models": models})

@app.route('/api/samples', methods=['GET'])
def get_samples():
    """API endpoint to get sample models"""
    if not nx_api_available:
        return jsonify({"error": "NX API not available"}), 503
    
    samples = nx_model_api.export_sample_models()
    return jsonify({"samples": samples})

@app.route('/output/<path:filename>')
def download_file(filename):
    """Serve files from the output directory"""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

@app.route('/api/ai-design', methods=['POST'])
def ai_design():
    """API endpoint for AI-assisted design using OpenAI"""
    try:
        # Log the incoming request
        app.logger.info("Received AI design request")
        
        # Extract request data
        data = request.json
        if not data:
            app.logger.error("No JSON data in request")
            return jsonify({
                'status': 'error',
                'message': "Please provide design prompt and model data"
            }), 400
            
        prompt = data.get('prompt', '')
        current_model = data.get('currentModel', {})
        
        if not prompt:
            app.logger.error("No prompt provided")
            return jsonify({
                'status': 'error',
                'message': "Please provide a design prompt"
            }), 400
        
        # Log the processing attempt
        app.logger.info(f"Processing design prompt: {prompt[:50]}...")
        
        # Process the prompt using the AI controller with visualizations
        response = ai_controller.process_design_prompt(prompt, current_model)
        
        # Ensure response has all required fields
        if not isinstance(response, dict):
            app.logger.error(f"AI controller returned non-dict response: {type(response)}")
            response = {
                'message': "I've analyzed your design but encountered an internal error formatting the response.",
                'modelChanges': {}
            }
            
        if 'message' not in response:
            response['message'] = "I've analyzed your design but couldn't generate a proper message."
            
        if 'modelChanges' not in response:
            response['modelChanges'] = {}
            
        # Add status field if not present
        response['status'] = response.get('status', 'success')
        
        # Log success
        app.logger.info("Successfully processed AI design request")
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Error in AI design: {str(e)}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': "I encountered an error analyzing your design. Please try again with a different request.",
            'modelChanges': {}
        }), 200  # Return 200 instead of 500 to allow frontend to display the message

@app.route('/api/analyze-design', methods=['POST'])
def analyze_design():
    """API endpoint to analyze rocket design using OpenAI"""
    try:
        data = request.json
        model = data.get('model', {})
        
        # Analyze the design using the AI controller with enhanced visualizations
        analysis = ai_controller.analyze_rocket_design(model)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis
        })
    except Exception as e:
        app.logger.error(f"Error analyzing design: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error analyzing design: {str(e)}"
        }), 500

@app.route('/api/update-model-geometry', methods=['POST'])
def update_model_geometry():
    """API endpoint to update STEP file based on model changes"""
    try:
        data = request.json
        model_data = data.get('model', {})
        filename = data.get('filename', 'updated_rocket_model.step')
        
        # Update the geometry file
        result = update_geometry_file(model_data, filename)
        
        return jsonify({
            'status': 'success',
            'message': 'Geometry updated successfully',
            'fileUrl': result.get('fileUrl')
        })
    except Exception as e:
        app.logger.error(f"Error updating geometry: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error updating geometry: {str(e)}"
        }), 500

@app.route('/api/interpret-step', methods=['POST'])
def interpret_step_file():
    """API endpoint to interpret a STEP file using AI"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        if not file.filename.endswith('.step') and not file.filename.endswith('.stp'):
            return jsonify({
                'status': 'error',
                'message': 'File must be a STEP file (.step or .stp)'
            }), 400
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Interpret the STEP file using AI
        analysis = ai_controller.interpret_rocket_design(file_path)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis
        })
    except Exception as e:
        app.logger.error(f"Error interpreting STEP file: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error interpreting STEP file: {str(e)}"
        }), 500

@app.route('/api/optimize-design', methods=['POST'])
def optimize_design():
    """API endpoint to start a design optimization process"""
    try:
        data = request.json
        base_model = data.get('model', {})
        goal = data.get('goal', 'Optimize overall performance')
        
        # Start the optimization process
        run_id = ai_controller.optimize_design(base_model, goal)
        
        return jsonify({
            'status': 'success',
            'run_id': run_id,
            'message': 'Optimization process started'
        })
    except Exception as e:
        app.logger.error(f"Error starting design optimization: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error starting design optimization: {str(e)}"
        }), 500

@app.route('/api/optimization-status/<run_id>', methods=['GET'])
def get_optimization_status(run_id):
    """API endpoint to check the status of an optimization run"""
    try:
        # Get the current status
        status = ai_controller.get_optimization_status(run_id)
        
        return jsonify({
            'status': 'success',
            'optimization_status': status
        })
    except Exception as e:
        app.logger.error(f"Error getting optimization status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error getting optimization status: {str(e)}"
        }), 500

@app.route('/api/enhance-structural-analysis', methods=['POST'])
def enhance_structural_analysis():
    """API endpoint to enhance structural analysis with AI insights"""
    try:
        data = request.json
        model = data.get('model', {})
        basic_analysis = data.get('basic_analysis', {})
        
        # Enhance the analysis with AI
        enhanced_analysis = ai_controller.enhance_structural_analysis(model, basic_analysis)
        
        return jsonify({
            'status': 'success',
            'enhanced_analysis': enhanced_analysis
        })
    except Exception as e:
        app.logger.error(f"Error enhancing structural analysis: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error enhancing structural analysis: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Create sample models
    if nx_api_available:
        try:
            nx_model_api.export_sample_models()
            logger.info("Sample models created")
        except Exception as e:
            logger.error(f"Failed to create sample models: {e}")
    
    # Run development server
    app.run(debug=True, host='0.0.0.0', port=5000)
