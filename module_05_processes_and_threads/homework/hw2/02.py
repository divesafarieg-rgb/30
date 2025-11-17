from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)


@app.route('/execute', methods=['POST'])
def execute_code():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    code = data.get('code')
    timeout = data.get('timeout')

    if not code:
        return jsonify({'error': 'Missing code'}), 400

    if timeout is None:
        return jsonify({'error': 'Missing timeout'}), 400

    try:
        timeout = int(timeout)
        if not 1 <= timeout <= 30:
            return jsonify({'error': 'Timeout must be between 1 and 30 seconds'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Timeout must be a number'}), 400

    try:
        process = subprocess.Popen(
            ['python', '-c', code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return jsonify({
                'success': True,
                'output': stdout,
                'error': stderr,
                'return_code': process.returncode
            })

        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return jsonify({
                'success': False,
                'error': f'Execution timed out after {timeout} seconds',
                'partial_output': stdout
            }), 408

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Execution failed: {str(e)}'
        }), 500


@app.route('/')
def home():
    return '''
    <h1>Python Code Execution API</h1>
    <p>Use POST /execute with JSON:</p>
    <pre>
    {
        "code": "print('Hello World')",
        "timeout": 5
    }
    </pre>
    '''


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
