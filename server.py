from app import server, DataVisualizerDash, generate_random_password
from flask import jsonify

@server.route('/generate-password')
def generate_password():
    password = generate_random_password()
    return jsonify({'password': password})

if __name__ == "__main__":
    app = DataVisualizerDash(server)
    with server.app_context():
        db.create_all()
    app.run()
