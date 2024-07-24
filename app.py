import os
import random
import pandas as pd
import json
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import base64
import io
import plotly.express as px

# Flask setup
server = Flask(__name__)
server.secret_key = os.urandom(24)
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_random_profile_pic():
    return f"https://avatars.dicebear.com/api/avataaars/{random.randint(1, 1000)}.svg"

@server.route('/')
def index():
    return render_template('login.html')

@server.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

    # Check if the username or email is already taken
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already taken'})
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already registered'})

    hashed_password = generate_password_hash(password, method='sha256')
    profile_pic = generate_random_profile_pic()
    new_user = User(username=username, email=email, password=hashed_password, profile_pic=profile_pic)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return jsonify({'success': True})

@server.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@server.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@server.route('/dashboard')
@login_required
def dashboard():
    return redirect('/dash')

# Dash setup
class DataVisualizerDash:
    def __init__(self, flask_app):
        self.datasets = {}
        self.visualizations = {}
        self.base_path = "./data"

        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

        self.app = dash.Dash(__name__, server=flask_app, url_base_pathname='/dash/', external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.build_layout()

    def build_layout(self):
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col(html.H1("Data Visualizer", style={
                    'text-align': 'center',
                    'font-weight': 'bold',
                    'text-transform': 'uppercase',
                    'background-color': 'black',
                    'color': 'white',
                    'padding': '10px'
                }), width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Img(id='profile-pic', src=current_user.profile_pic if current_user.is_authenticated else "https://via.placeholder.com/150", style={'border-radius': '50%', 'width': '100px', 'margin': 'auto'}),
                        html.H2(id='user-name', children=current_user.username if current_user.is_authenticated else "User", style={'text-align': 'center'}),
                        html.P(id='login-status', children="Logged In" if current_user.is_authenticated else "Logged Out", style={'text-align': 'center'}),
                        dbc.Button('Logout', id='logout-btn', color='black', className="mb-2", style={'display': 'block', 'margin': '10px auto', 'background-color': 'black', 'color': 'white'})
                    ], style={'text-align': 'center', 'padding': '20px'}),
                    html.H3("Side Panel"),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px',
                            'background-color': '#f9f9f9',
                        },
                        multiple=False
                    ),
                    html.Div(id='output-data-upload'),
                    html.H3("Datasets"),
                    html.Div(id='dataset-list'),
                    html.H3("Create Visualization"),
                    dbc.Input(id='dataset-id', placeholder='Enter Dataset ID', type='number', className="mb-2"),
                    dbc.Input(id='viz-type', placeholder='Enter visualization type (bar/line)', type='text', className="mb-2"),
                    dbc.Input(id='x-col', placeholder='Enter X-axis column', type='text', className="mb-2"),
                    dbc.Input(id='y-col', placeholder='Enter Y-axis column', type='text', className="mb-2"),
                    dbc.Input(id='x-label', placeholder='Enter X-axis label', type='text', className="mb-2"),
                    dbc.Input(id='y-label', placeholder='Enter Y-axis label', type='text', className="mb-2"),
                    dbc.Button('Create Visualization', id='create-viz-btn', n_clicks=0, color="primary"),
                    html.Div(id='visualization-output'),
                    html.H3("Save Visualization"),
                    dbc.Input(id='viz-id', placeholder='Enter Visualization ID', type='number', className="mb-2"),
                    dbc.Button('Save Visualization', id='save-viz-btn', n_clicks=0, color="primary"),
                    html.Div(id='save-viz-output'),
                    html.H3("Document Name"),
                    dbc.Input(id='document-name', placeholder='Enter Document Name', type='text', className="mb-2"),
                    html.H3("Manage Documents"),
                    dbc.Button('Add Document', id='add-document-btn', n_clicks=0, color="success", className="mb-2"),
                    dbc.Button('Switch Document', id='switch-document-btn', n_clicks=0, color="info", className="mb-2"),
                    html.Div(id='document-list'),
                ], width=3, style={
                    'background-color': '#e3f2fd',
                    'padding': '20px',
                    'border-radius': '5px'
                }),
                dbc.Col([
                    html.H3("Main Panel"),
                    html.Div(id='document-title', style={'text-align': 'center', 'font-weight': 'bold', 'margin-bottom': '20px'}),
                    dash_table.DataTable(
                        id='table-editing-simple',
                        columns=[{"name": i, "id": i} for i in ['Year', 'Sales', 'Profit']],
                        data=[{'Year': 2016, 'Sales': 150, 'Profit': 30},
                            {'Year': 2017, 'Sales': 200, 'Profit': 50},
                            {'Year': 2018, 'Sales': 250, 'Profit': 60},
                            {'Year': 2019, 'Sales': 300, 'Profit': 70},
                            {'Year': 2020, 'Sales': 350, 'Profit': 80},
                            {'Year': 2021, 'Sales': 400, 'Profit': 90}],
                        editable=True,
                        row_deletable=True,
                        style_table={'height': '300px', 'overflowY': 'auto'},
                        style_cell={'textAlign': 'center'},
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }
                        ]
                    ),
                    dcc.Graph(id='main-graph'),
                ], width=9)
            ]),
        ], fluid=True)

        self.app.callback(
            Output('output-data-upload', 'children'),
            Input('upload-data', 'contents'),
            State('upload-data', 'filename')
        )(self.upload_csv)

        self.app.callback(
            Output('dataset-list', 'children'),
            Input('upload-data', 'contents')
        )(self.list_datasets)

        self.app.callback(
            Output('visualization-output', 'children'),
            Output('main-graph', 'figure'),
            Input('create-viz-btn', 'n_clicks'),
            State('dataset-id', 'value'),
            State('viz-type', 'value'),
            State('x-col', 'value'),
            State('y-col', 'value'),
            State('x-label', 'value'),
            State('y-label', 'value')
        )(self.create_visualization)

        self.app.callback(
            Output('save-viz-output', 'children'),
            Input('save-viz-btn', 'n_clicks'),
            State('viz-id', 'value')
        )(self.save_visualization)

        self.app.callback(
            Output('document-list', 'children'),
            Output('document-title', 'children'),
            Input('add-document-btn', 'n_clicks'),
            State('document-name', 'value'),
            State('table-editing-simple', 'data')
        )(self.add_document)

        self.app.callback(
            Output('table-editing-simple', 'data'),
            Output('document-title', 'children'),
            Input('switch-document-btn', 'n_clicks'),
            State('document-name', 'value')
        )(self.switch_document)

    def upload_csv(self, contents, filename):
        if contents is None:
            return html.Div()

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            dataset_id = len(self.datasets) + 1
            dataset_name = filename
            self.datasets[dataset_id] = {
                "name": dataset_name,
                "data": df,
                "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "file_path": filename
            }
            return html.Div([html.H5(f"Dataset {dataset_name} uploaded successfully with ID {dataset_id}.")])
        except Exception as e:
            return html.Div([html.H5(f"Failed to upload {filename}. Error: {str(e)}")])

    def list_datasets(self, _):
        if not self.datasets:
            return html.Div([html.H5("No datasets uploaded.")])

        datasets_info = [html.P(f"ID: {dataset_id}, Name: {info['name']}, Uploaded At: {info['uploaded_at']}") for dataset_id, info in self.datasets.items()]
        return html.Div(datasets_info)

    def create_visualization(self, n_clicks, dataset_id, viz_type, x_col, y_col, x_label, y_label):
        if n_clicks == 0:
            return html.Div(), {}

        if dataset_id not in self.datasets:
            return html.Div([html.H5(f"Dataset with ID {dataset_id} does not exist.")]), {}

        dataset = self.datasets[dataset_id]
        df = dataset["data"]

        if x_col not in df.columns or y_col not in df.columns:
            return html.Div([html.H5(f"Invalid columns: {x_col}, {y_col}")]), {}

        fig = None
        if viz_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, labels={x_col: x_label, y_col: y_label})
        elif viz_type == "line":
            fig = px.line(df, x=x_col, y=y_col, labels={x_col: x_label, y_col: y_label})
        else:
            return html.Div([html.H5(f"Unsupported visualization type: {viz_type}")]), {}

        viz_id = len(self.visualizations) + 1
        self.visualizations[viz_id] = {
            "dataset_id": dataset_id,
            "type": viz_type,
            "x_col": x_col,
            "y_col": y_col,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return html.Div([html.H5(f"Visualization {viz_type} created successfully with ID {viz_id}.")]), fig

    def save_visualization(self, n_clicks, viz_id):
        if n_clicks == 0:
            return html.Div()

        if viz_id not in self.visualizations:
            return html.Div([html.H5(f"Visualization with ID {viz_id} does not exist.")])

        viz = self.visualizations[viz_id]
        viz_file_path = os.path.join(self.base_path, f"visualization_{viz_id}.json")

        with open(viz_file_path, "w") as file:
            json.dump(viz, file)

        return html.Div([html.H5(f"Visualization {viz_id} saved successfully at {viz_file_path}.")])

    def add_document(self, n_clicks, document_name, table_data):
        if n_clicks == 0 or not document_name:
            return [], "No document selected"

        document_id = len(self.datasets) + 1
        df = pd.DataFrame(table_data)
        self.datasets[document_id] = {
            "name": document_name,
            "data": df,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        documents = [html.P(f"ID: {document_id}, Name: {document_name}, Created At: {self.datasets[document_id]['created_at']}")]
        return documents, f"Current Document: {document_name}"

    def switch_document(self, n_clicks, document_name):
        if n_clicks == 0 or not document_name:
            return [], "No document selected"

        for document_id, info in self.datasets.items():
            if info["name"] == document_name:
                data = info["data"].to_dict("records")
                return data, f"Current Document: {document_name}"

        return [], "Document not found"

    def run(self):
        self.app.run_server(debug=True)

if __name__ == "__main__":
    app = DataVisualizerDash()
    with server.app_context():
        db.create_all()
    app.run()
