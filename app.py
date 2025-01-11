from flask import Flask, render_template, request, jsonify
from utils.git_handler import GitHandler
from utils.markdown_generator import MarkdownGenerator
import os
import shutil
from werkzeug.serving import run_simple
import time

app = Flask(__name__)
app.config['EXTRA_FILES'] = []  # Disable file watching

# Initialize handlers
git_handler = GitHandler()
markdown_generator = MarkdownGenerator()

def force_remove_directory(path):
    """Force remove a directory and its contents, handling Windows file locks."""
    if not os.path.exists(path):
        return
    
    try:
        # First try using shutil
        shutil.rmtree(path, ignore_errors=True)
        time.sleep(0.5)  # Short wait
        
        # If directory still exists, try system commands
        if os.path.exists(path):
            if os.name == 'nt':  # Windows
                os.system(f'rmdir /S /Q "{path}"')
                time.sleep(0.5)
                # If still exists, try with del command
                if os.path.exists(path):
                    os.system(f'del /F /Q /S "{path}\\*.*"')
                    os.system(f'rmdir /S /Q "{path}"')
            else:  # Linux/Mac
                os.system(f'rm -rf "{path}"')
            time.sleep(0.5)
        
        # If still exists, try one last time with Python
        if os.path.exists(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    try:
                        os.unlink(os.path.join(root, name))
                    except:
                        pass
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except:
                        pass
            try:
                os.rmdir(path)
            except:
                pass
            
    except Exception as e:
        app.logger.error(f"Error in force_remove_directory: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cleanup', methods=['DELETE'])
def cleanup_repository():
    try:
        if os.path.exists('my_repo'):
            force_remove_directory('my_repo')
            return jsonify({'message': 'Repository directory cleaned up successfully'})
        return jsonify({'message': 'Repository directory does not exist'})
    except Exception as e:
        app.logger.error(f"Error cleaning up repository: {str(e)}")
        return jsonify({'error': 'Failed to clean up repository directory'}), 500

@app.route('/clone', methods=['POST'])
def clone_repository():
    try:
        repo_url = request.form.get('repo_url')
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400

        # Validate repository URL format
        if not repo_url.startswith(('http://', 'https://', 'git://')):
            return jsonify({'error': 'Invalid repository URL format'}), 400

        # Force remove the my_repo directory and all its contents
        try:
            force_remove_directory('my_repo')
        except Exception as e:
            app.logger.error(f"Failed to remove directory: {str(e)}")
            return jsonify({'error': 'Failed to clean up existing repository'}), 500

        try:
            # Clone repository
            repo_path = git_handler.clone_repository(repo_url, 'my_repo')
            
            # Generate markdown content
            markdown_content = markdown_generator.generate_markdown(repo_path)
            
            return jsonify({'markdown': markdown_content})
        except Exception as e:
            app.logger.error(f"Error during clone or markdown generation: {str(e)}")
            return jsonify({'error': f'Repository processing failed: {str(e)}'}), 500
    
    except Exception as e:
        app.logger.error(f"Error processing repository: {str(e)}")
        return jsonify({'error': 'Failed to process repository. Please check the URL and try again.'}), 500

if __name__ == '__main__':
    run_simple('0.0.0.0', 5000, app, use_reloader=True, use_debugger=True, 
              reloader_type='stat', extra_files=[
                  f for f in os.listdir('.')
                  if os.path.isfile(f) and not f.startswith('my_repo')
              ])
