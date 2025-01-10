from flask import Flask, render_template, request, jsonify
from utils.git_handler import GitHandler
from utils.markdown_generator import MarkdownGenerator
import os
import shutil

app = Flask(__name__)

# Initialize handlers
git_handler = GitHandler()
markdown_generator = MarkdownGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clone', methods=['POST'])
def clone_repository():
    try:
        repo_url = request.form.get('repo_url')
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400

        # Validate repository URL format
        if not repo_url.startswith(('http://', 'https://', 'git://')):
            return jsonify({'error': 'Invalid repository URL format'}), 400

        # Create my_repo directory if it doesn't exist
        if os.path.exists('my_repo'):
            shutil.rmtree('my_repo')
        os.makedirs('my_repo')

        try:
            # Clone repository
            repo_path = git_handler.clone_repository(repo_url, 'my_repo')
            
            # Generate markdown content
            markdown_content = markdown_generator.generate_markdown(repo_path)
            
            return jsonify({'markdown': markdown_content})
        except Exception as e:
            # Clean up the directory in case of failure
            if os.path.exists('my_repo'):
                shutil.rmtree('my_repo')
            raise e
    
    except Exception as e:
        app.logger.error(f"Error processing repository: {str(e)}")
        return jsonify({'error': 'Failed to process repository. Please check the URL and try again.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
