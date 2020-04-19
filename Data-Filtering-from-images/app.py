import os
import os.path
import zipfile
import io
import pathlib
from flask import * 
import urllib.request
from werkzeug.utils import secure_filename
from classification import classify_data
from data_cleaning import clean_image_data, delete_generated_data

def create_directories(*args):
    for files in args:
        if os.path.isdir("./{}".format(files)):
            pass
        else:
            os.mkdir(os.path.join("./", files))

source_path = "test_images"
destination_path = "tested"
text_path = "text"

UPLOAD_FOLDER = './test_images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)   

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024



@app.route("/") 
def home():     
    delete_generated_data(source_path, destination_path, text_path)
    create_directories(source_path,destination_path, text_path)
    return render_template("home.html")   

@app.route("/download") 
def download():     
    return render_template("download.html")   

@app.route("/download-csv") 
def request_csv():     
    if os.path.isfile('bill_info.csv'):
        download_path="bill_info.csv"
        return send_file(download_path, as_attachment=True)
    else:
        return redirect(url_for('download'))

@app.route("/download-zip")
def request_zip():
    if not os.listdir('./text'):
        return redirect(url_for('download')) 
    else:
        base_path = pathlib.Path('./text/')
        data = io.BytesIO()
        with zipfile.ZipFile(data, mode='w') as z:
            for f_name in base_path.iterdir():
                z.write(f_name)
        data.seek(0)
        return send_file(
            data,
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename='text.zip'
            )    

@app.route("/converter") 
def converter():     
    clean_image_data(source_path, destination_path, text_path)
    classify_data()
    return redirect(url_for('download'))  


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if request.files['files[]'].filename == '':
            # flash('No selected file')
            return redirect(url_for('home'))
        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        # flash('File(s) successfully uploaded')
        return redirect(url_for('converter'))

if __name__ == "__main__":     
    app.run(debug=True)

