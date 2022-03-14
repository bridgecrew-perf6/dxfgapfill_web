from flask import Flask, render_template, request , session, redirect
from script import upated_file
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "Youwillnever guess"

basdir = os.path.abspath(os.path.dirname(__file__))
Upload_dir = basdir + "/static/temp/"

@app.route("/")
def index():
	try:
		directory = os.fsencode(Upload_dir)
		for file in os.listdir(directory):
			filename = os.fsdecode(file)
			if filename.endswith(".dxf"):
				print(filename)
				print("file name===================")
				print(session['filename'])
				if filename == session['filename']:
					print("yes---------------------------")					
					os.remove(os.path.join(Upload_dir,session['filename']))
					print("removed_________________________________")
					session['filename'] = ""
	except Exception as e:
		print(e)
	return render_template("index.html")


@app.route("/upload_file" , methods=["POST","GET"])
def upload_file():
	if request.method == "POST":
		file = request.files['fileUpload']
		filename = secure_filename(file.filename)
		filename_ =  "edited" + filename
		session['filename'] = filename_
		file.save(os.path.join(basdir, str(filename)))
		upated_file(filename)

	return render_template("upload.html", f=session['filename'])



# @app.after_request
# def delte():
# 	print(filename_)
# 	directory = os.fsencode(Upload_dir)
# 	for file in os.listdir(directory):
# 		filename = os.fsdecode(file)
# 		if filename.endswith(".dxf"):
# 			print(filename)
# 			print("file name===================")
# 			print(filename_)
# 			if filename ==filename_:
# 				print("yes---------------------------")
# 				os.remove(os.path.join(basdir,"edited"+filename_))





if __name__ == "__main__":
	app.run(debug=True)