import os
import mm_comparator
from app import app
from flask import Flask, flash, request, redirect, render_template


Extensions = 'mm'
Allowed_extensions = set([Extensions])


diffs = ''
file_name = ''
out_directory = os.path.expanduser('~').replace('\\', '\\\\')

key_file_sav = {''}
key_file_name_sav = ''

q_repeated = False


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in Allowed_extensions


def check_inputs(file1, file2):
	if file1.filename == '' and key_file_name_sav == '':
		return 'No key file selected for uploading'
	elif file2.filename == '':
		return 'No student data file selected for uploading'
	elif not allowed_file(file1.filename) and key_file_name_sav == '':
		return 'Allowed key files have ' + Extensions + ' extension'
	elif not allowed_file(file2.filename):
		return 'Allowed student data files have ' + Extensions + ' extension'
	return ''


@app.route('/')
def upload_form():
	context = {'repeated': q_repeated, 'key_file': key_file_name_sav}
	return render_template('upload.html', context=context)


@app.route('/out')
def download_form():
	global out_directory
	context = {'out_directory': out_directory}
	return render_template('download.html', context=context)


@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		global key_file_sav, key_file_name_sav
		key_file = request.files['key_file']
		student_file = request.files['student_file']
		if check_inputs(key_file, student_file) != '':
			flash(check_inputs(key_file, student_file))
			return redirect(request.url)
		# good to go, run the comparison
		global diffs, file_name
		if key_file.filename != key_file_name_sav and key_file.filename != '':
			key_file_sav = key_file
			key_file_name_sav = key_file.filename
		diffs = mm_comparator.return_diffs(key_file_sav, student_file)
		file_name = mm_comparator.set_output_path(key_file_name_sav, student_file.filename)
		return redirect('/out')


@app.route('/out', methods=['POST'])
def download_file():
	if request.method == 'POST':
		global out_directory
		out_directory = request.form['out_path']
		if out_directory == '':
			flash('No directory selected for downloading')
			return redirect(request.url)
		# good to go, run the comparison
		save_it_out()
		flash('Comparison file successfully downloaded')
		global q_repeated
		q_repeated = True
		return redirect('/')


def save_it_out():
	global out_directory, file_name, diffs
	if out_directory[len(out_directory)-1] != '\\':
		out_directory += '\\'
	file = open(os.path.join(out_directory, file_name), 'w')
	for i in diffs:
		file.write(i)
		file.write('\n')
	file.close()
	return


if __name__ == "__main__":
	app.run()
