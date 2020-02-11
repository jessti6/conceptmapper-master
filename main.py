import os

# from django.core.files import File
from flask import flash, request, redirect, render_template, make_response, send_from_directory
# from pip._vendor import requests
from werkzeug.utils import secure_filename

import mm_comparator
from app import app
from lib.flask import Response

Extensions = 'mm'
Allowed_extensions = set([Extensions])



diffs = ""
file_name = ''
# out_directory = os.path.expanduser('~').replace('\\', '\\\\')

key_file_sav = {''}
key_file_name_sav = ''

student_file_name_sav = ''
student_filenames = ''

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
    context = {'repeated': q_repeated, 'key_file': key_file_name_sav, 'student_file': student_file_name_sav,
               'filenames': student_filenames}
    return render_template('upload.html', context=context)


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        global key_file_sav, key_file_name_sav, student_file_name_sav
        key_file = request.files['key_file']
        key_file.save(os.path.join(app.config['UPLOAD_FOLDER'], key_file.filename))
        student_file = request.files.getlist("student_file[]")
        for i in student_file:
            i.save(os.path.join(app.config['UPLOAD_FOLDER'], i.filename))

        for i in student_file:
            if check_inputs(key_file, i) != '':
                flash(check_inputs(key_file, i))
                return redirect(request.url)

        # good to go, run the comparison
        global diffs, file_name
        # if key_file.filename != key_file_name_sav and key_file.filename == '':
        #     key_file = key_file_sav
        # else:
        #     key_file_sav = key_file
        #     key_file_name_sav = key_file.filename

        for i in student_file:
            # student_file_name_sav = i.filename
            # diffs = ''
            diffs = mm_comparator.return_diffs(key_file, key_file.filename, i, i.filename)
            # temp_print(diffs)
            # diffs = ''
            # temp_print(diffs)
            # diffs = mm_comparator.return_diffs('',key_file.filename, '', i.filename)
            # temp_print(diffs)
            # file_name = mm_comparator.set_output_path(key_file_name_sav, i.filename)
            file_name = mm_comparator.set_output_path(key_file.filename,i.filename)

        return redirect('/out')



@app.route("/out")
def get():
    # global q_repeated
    # q_repeated = True
    mm_comparator.clear2()
    return render_template('download.html')


# def temp_print(x):
#     y = 0
#     for i in x:
#         y = y + 1



@app.route("/getDownload")
def getDownload():
    global diffs
    with open(file_name, 'w') as f:
        empty = os.stat(file_name).st_size == 0
        if empty:
            print(diffs)
            for i in diffs:
                f.write(i)
                f.write('\n')
            f.close()
            del diffs
        else:
            file_name.seek(0)
            file_name.truncate()
            with open(file_name, 'w') as f:
                for i in diffs:
                    f.write(i)
                    f.write('\n')
            f.close()
    # f.close()

    with open(file_name, 'r') as f1:
        diff = f1.read()
        f1.close()
    return Response(
        diff,
        mimetype="text",
        headers={"Content-disposition":
                     "attachment; filename=diff.txt"})




if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
    #app.run()
