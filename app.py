# Importing required libraries
from flask import Flask, request, render_template, redirect, url_for, flash
import numpy as np
import pandas as pd
from sklearn import metrics 
import warnings
import pickle
import os
# from dotenv import load_dotenv
from feature import FeatureExtraction
from predictor import predict_url
import logging
logging.basicConfig(level=logging.INFO)
# load_dotenv()

# Suppress warnings for cleaner logs
warnings.filterwarnings('ignore')

# Load the pre-trained model
with open("model.pkl", "rb") as file:
    gbc = pickle.load(file)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key123" 
# app.secret_key = os.getenv("SECRET_KEY") # Recommended for secure sessions
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # Limit file upload size to 2MB

# Routes
@app.route('/')
@app.route('/first')
def first():
    return render_template('first.html')

@app.route('/performance')
def performance():
    return render_template('performance.html')

@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/login')
def login():
    return render_template('login.html')

# @app.route('/upload')
# def upload():
#     return render_template('upload.html')
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        try:
            file = request.files['datasetfile']
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)  # ✅ Read the uploaded CSV as a DataFrame
                df_view = df.head(10)  # ✅ Preview the first 10 rows
                html_table = df.to_html(classes='table table-bordered')  # Optional styling
                return render_template('upload.html', table=html_table)
            else:
                return render_template('upload.html', error='Invalid file type. Please upload a CSV.')
        except Exception as e:
            return render_template('upload.html', error=f"Error processing CSV: {str(e)}")
    return render_template('upload.html')

# @app.route('/preview', methods=["POST"])
# def preview():
#     if request.method == 'POST':
#         try:
#             dataset = request.files['datasetfile']
#             # if not dataset:
#             #     flash("No file selected", "error")
#             #     return redirect(url_for('upload'))
#             if not dataset.filename.endswith('.csv'):
#                flash("Please upload a CSV file only.", "error")
#                return redirect(url_for('upload'))
            
#             # Load dataset and prepare for preview
#             df = pd.read_csv(dataset, encoding='unicode_escape')
#             df.set_index('Id', inplace=True)
#             return render_template("preview.html", df_view=df.to_html(classes='table table-striped'))
#         except Exception as e:
#             logging.error(f"Prediction Error: {e}")
#             flash("There was an error analyzing the URL.", "error")
#             return redirect(url_for('upload'))

# @app.route('/preview', methods=["POST"])
# def preview():
#     if request.method == 'POST':
#         try:
#             dataset = request.files.get('datasetfile')
#             if not dataset:
#                 flash("No file selected!", "danger")
#                 return redirect(url_for('upload'))

#             # Try reading as CSV
#             df = pd.read_csv(dataset, encoding='unicode_escape')

#             if df.empty:
#                 flash("Uploaded CSV is empty!", "warning")
#                 return redirect(url_for('upload'))

#             if 'Id' in df.columns:
#                 df.set_index('Id', inplace=True)
#             else:
#                 flash("CSV must contain 'Id' column.", "danger")
#                 return redirect(url_for('upload'))

#             return render_template("preview.html", df_view=df.to_html(classes='table table-bordered', border=0))

#         except Exception as e:
#             flash(f"Error processing CSV: {e}", "danger")
#             return redirect(url_for('upload'))

from flask import render_template, request, flash, redirect, url_for
import pandas as pd

@app.route('/preview', methods=['POST'])
def preview():
    try:
        file = request.files['datasetfile']
        if file.filename == '':
            flash(('danger', 'No file selected'))
            return redirect(request.url)
        
        # Read CSV file into pandas DataFrame
        df = pd.read_csv(file)

        # Take only the first 10 rows
        preview_df = df.head(10)

        # Convert DataFrame to HTML table
        table = preview_df.to_html(classes='table table-striped', index=False)

        # Render template with the table
        return render_template('preview.html', table=table)
    
    except Exception as e:
        flash(('danger', f'Error processing CSV: {str(e)}'))
        return redirect(url_for('upload'))



@app.route('/index')
def index():
    return render_template('index.html')

@app.route("/posts", methods=["GET", "POST"])
def posts():
    if request.method == "POST":
        try:
            url = request.form["url"]
            obj = FeatureExtraction(url)
            
            # x = np.array(obj.getFeaturesList()).reshape(1, 30)

            # y_pred = gbc.predict(x)[0]
            # y_pro_phishing = gbc.predict_proba(x)[0, 0]
            # y_pro_non_phishing = gbc.predict_proba(x)[0, 1]
            y_pred, proba = predict_url(url, gbc)
            y_pro_phishing, y_pro_non_phishing = proba[0], proba[1]

            # pred = f"It is {y_pro_phishing * 100:.2f}% safe to go"
            if y_pred == 1:
                 result_msg = "⚠️ Warning: This URL appears to be *phishing*."
            else:
                 result_msg = "✅ Safe: This URL appears to be *legitimate*."

            return render_template('result.html', xx=round(y_pro_non_phishing, 2), url=url, result_msg=result_msg)
        except Exception as e:
            flash(f"Error processing request: {e}", "error")
            return redirect(url_for('index'))
    return render_template("result.html", xx=-1)

if __name__ == "__main__":
    app.run(debug=True)
