import os
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import base64
import io
import plotly.express as px

class DataVisualizerDash:
    def __init__(self):
        self.datasets = {}
        self.visualizations = {}
        self.base_path = "./data"

        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.build_layout()

    def build_layout(self):
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col(html.H1("Data Visualizer Studio V-1.0", style={
                    'text-align': 'center',
                    'font-weight': 'bold',
                    'text-transform': 'uppercase',
                    'background-color': 'white',
                    'color': 'black',
                    'padding': '10px'
                }), width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    html.H3("Dashboard"),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'none',
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
                ], width=3, style={
                    'background-color': '#e3f2fd',
                    'padding': '20px',
                    'border-radius': '5px'
                }),
                dbc.Col([
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

    def run(self):
        self.app.run_server(debug=True)

if __name__ == "__main__":
    app = DataVisualizerDash()
    app.run()
