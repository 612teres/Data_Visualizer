from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Create an 'uploads' folder for storing files

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

blog_posts = [
    {
        'title': 'Data Visualization with Plotly',
        'content': 'Learn how to create interactive and informative visualizations using Plotly in your Flask applications.',
    },
    {
        'title': 'File Handling in Flask',
        'content': 'Explore techniques for handling file uploads and processing in your Flask projects.',
    }
]

@app.route('/blog')
def blog():
    return render_template('blog.html', posts=blog_posts)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        # Check if the file has a filename
        if file.filename == '':
            return redirect(request.url)

        # Check if the file is allowed
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('visualize', filename=filename))

    return render_template('upload.html')

@app.route('/visualize/<filename>')
def visualize(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(file_path)

    # Basic visualization (you can customize this)
    fig = px.scatter(df, x=df.columns[0], y=df.columns[1])  # Assuming first two columns are numerical

    # Convert the Plotly figure to HTML for embedding
    graph_html = fig.to_html(full_html=False)

    return render_template('visualize.html', graph=graph_html)

if __name__ == '__main__':
    app.run(debug=True)