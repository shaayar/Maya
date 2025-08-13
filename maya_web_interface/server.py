from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Routes
@app.route('/')
def index():
    """Render the landing page."""
    return render_template('landing.html')

@app.route('/app')
def app_route():
    """Render the main chat application."""
    return render_template('index.html')

@app.route('/search')
def search():
    """Handle search queries."""
    query = request.args.get('q', '')
    # Here you would typically process the search query
    # For now, we'll just redirect to the main app with the query
    return redirect(url_for('app_route', q=query))

# API Endpoints
@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Here you would typically process the message with your AI model
        # For now, we'll return a simple response
        response = {
            'message': f"I received your message: {user_message}",
            'timestamp': 'just now',
            'status': 'success'
        }
        
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f'Error in chat endpoint: {str(e)}')
        return jsonify({'error': 'An error occurred', 'status': 'error'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part', 'status': 'error'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file', 'status': 'error'}), 400
        
        if file:
            # Secure the filename to prevent directory traversal
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure the upload directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save the file
            file.save(filepath)
            
            # Return success response
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'url': f'/static/uploads/{filename}',
                'status': 'success'
            })
            
    except Exception as e:
        app.logger.error(f'Error uploading file: {str(e)}')
        return jsonify({
            'error': 'Failed to upload file',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
    
    # Run the server
    app.run(debug=True, port=5000)
