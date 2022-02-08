from jinja2 import Template
import sys
import csv
import matplotlib.pyplot as plt

 
templates='''<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>{{title}}</title>
</head>
<body>
	--data--
</body>
</html>'''


with open('data.csv', mode='r') as inp:
    reader = csv.reader(inp)
    dict_from_csv = [[r.strip() for r in rows] for rows in reader]



def studentDetail(position, value):
	header=dict_from_csv[0]
	data=[]
	total_marks = 0
	for row in dict_from_csv[1:]:
		if row[position] == value:
			data.append(row)
			total_marks += float(row[-1])
	total_marks = int(total_marks)
	if not data:
		return wrongInput()
	htmldata ='''
	<div>
		<h1>{{title}}</h1> 
		<table border ="1px">
			<tr >
				{% for h in header %}
				<th>{{h}}</th>
				{% endfor %}
			</tr>
			{% for row in data %}
				<tr >
					{% for d in row %}
					<td>{{d}}</td>
					{% endfor %}
				</tr>
			{% endfor %}
			<tr>
				<td colspan="2">Total Marks</td>
				<td>{{total_marks}}</td>
			</tr>
		</table>
	</div>
	'''
	html = templates.replace('--data--',htmldata)
	my_statement = Template(html)
	out = my_statement.render(header=header, data=data,total_marks=total_marks, title = 'Student Details' )
	return out


def courseDetail(position, value):
	header=dict_from_csv[0]
	total_courses = 0
	Max = 0
	avg = 0
	l=[]

	for row in dict_from_csv[1:]:
		if row[position] == value:
			l.append(float(row[-1]))
	if not l:
		return wrongInput()
	avg = round(sum(l)/len(l),1)
	Max = int(max(l))
	plt.hist(sorted(l))
	plt.ylabel('Frequency')
	plt.xlabel('Marks')
	plt.savefig('img.png')
	# plt.show()

	htmldata ='''
	<div>
		<h1>{{title}}</h1> 
		<table border ="1px">
			<tr >
				<th>Average Marks</th>
				<th>Maximum Marks</th>
			</tr>
			<tr>
				<td >{{avg}}</td>
				<td>{{Max}}</td>
			</tr>
		</table>
		<img src="img.png" >
	</div>
	'''
	html = templates.replace('--data--',htmldata)
	my_statement = Template(html)
	out = my_statement.render(title = 'Student Details',avg=avg, Max=Max )
	return out



def wrongInput():
	htmldata ='''
	<div>
		<h1>{{title}}</h1> 
		<p>Somthing went wrong</p>
	</div>
	'''
	html = templates.replace('--data--',htmldata)
	my_statement = Template(html)
	out = my_statement.render(title = 'Wrong Inputs' )
	return out


ref = {'-s':'Student id','-c':'Course id'}
i = sys.argv
try:
	if i[1].lower() == '-s':
		indx =dict_from_csv[0].index('Student id')
		output = studentDetail(indx,i[2])
	elif i[1].lower() == '-c':
		indx =dict_from_csv[0].index('Course id')
		output = courseDetail(indx,i[2])
	else:
		output = wrongInput()
except:
	output = wrongInput()



with open('output.html','w') as f:
	f.write(output)