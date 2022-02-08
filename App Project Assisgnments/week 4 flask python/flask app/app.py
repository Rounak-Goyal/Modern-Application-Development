import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route('/', methods = ["GET", "POST"])
def hello_world():
    if request.method == "GET":
        return render_template("index.html", template_folder="templates")
    elif request.method == "POST":
        id = request.form["ID"]
        b = request.form["id_value"]
        temp = []
        courses = []#
        students = []#
        marks = []
        fields = []
        all = []
        total_marks = 0
        average_marks = 0
        maximum_marks = 0
        
        with open("data.csv", 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            fields = next(csvreader)
            
            for row in csvreader:
                all.append(row)
                students.append(row[0])#
                courses.append(row[1].lstrip())#
    
        if b == "" or not b.isnumeric():
            return render_template("error.html", template_folder="templates")
        
        if id == "student_id":
            if b[0] != "1":
                return render_template("error.html", template_folder="templates")
            else:
                for i in all: 
                    if i[0] == b:
                        temp.append(i)
                        total_marks += int(i[2])
                return render_template("student.html", template_folder="templates", fields = fields, temp = temp, total_marks = total_marks)
                
        elif id == "course_id":

         if b[0] != "2":
             return render_template("error.html", template_folder="templates")
         else:
             for i in all:
                 if i[1].lstrip() == b:
                     temp.append(i)
                     total_marks += int(i[2])
                     marks.append(int(i[2]))
                     if maximum_marks < int(i[2]):
                         maximum_marks = int(i[2])
            
             if(len(temp) != 0):
                 average_marks = total_marks / len(temp)
             plt.hist(marks)
             plt.xlabel('Marks')
             plt.ylabel('Frequency')
             plt.savefig('static/hist.png')
             plt.clf()
             return render_template("course.html", template_folder="templates", average_marks = average_marks, maximum_marks = maximum_marks, plot = "static/hist.png")

	
if __name__ == "__main__":
    app.run()