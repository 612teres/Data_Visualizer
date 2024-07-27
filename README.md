# Data Visualizer

**Author:** Fabian Teres

## Overview

DataViz Showcase is an intuitive web application designed to enable users to upload CSV files, create interactive visualizations, and manage these visualizations seamlessly. With this tool, data analysis becomes visually engaging and accessible to everyone.

## Features

- **Upload CSV Datasets:** Easily upload and manage your datasets in CSV format.
- **Interactive Visualizations:** Create bar and line visualizations with simple input.
- **Real-time Data Insights:** View and interact with your data visualizations directly in the browser.
- **Save and Share:** Save your visualization configurations for future use and share insights with others.

## Technologies Used

- **Backend:** Flask, SQLAlchemy, Pandas
- **Frontend:** React, Axios
- **Styling:** CSS

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

Ensure you have the following software installed:

- Python 3.8+
- Node.js and npm

### Installation

#### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install the required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database:**
   ```python
   python
   >>> from app import app
   >>> from models import db
   >>> db.create_all(app=app)
   >>> exit()
   ```

4. **Run the backend server:**
   ```bash
   python app.py
   ```

#### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install the required Node packages:**
   ```bash
   npm install
   ```

3. **Run the frontend development server:**
   ```bash
   npm start
   ```

4. **Open your browser and go to `http://localhost:3000` to view the application.**

## Usage Guide

### Uploading a Dataset

1. Click on the "Upload CSV" button.
2. Choose a CSV file from your computer.
3. Provide a brief description of the dataset.
4. Click the "Upload" button to submit.

### Viewing Uploaded Datasets

- Navigate to the "Uploaded Datasets" section.
- Here you will see a list of all datasets you have uploaded along with their descriptions.

### Creating a Visualization

1. Go to the "Create Visualization" section.
2. Select the dataset you want to visualize by its ID.
3. Choose the type of visualization (Bar or Line).
4. Specify the columns for the X and Y axes.
5. Click the "Create Visualization" button to generate and view the chart.

### Saving Visualizations

- After creating a visualization, you can save it for future reference.
- Visualizations are stored with their configurations, allowing you to reload and share them easily.


## Project Structure

```
DataVizShowcase/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── views.py
│   ├── requirements.txt
│   └── config.py
├── frontend/
│   ├── public/
│   │   ├── index.html
│   └── src/
│       ├── App.js
│       ├── index.js
│       ├── components/
│       │   ├── DatasetUpload.js
│       │   ├── DatasetList.js
│       │   ├── Visualization.js
│       └── styles/
│           ├── App.css
│           └── Visualization.css
└── README.md
```

## Contributing

Contributions are welcome! Please fork this repository and submit pull requests for any features, improvements, or bug fixes.

## License

This project is licensed under the MIT License.

---
