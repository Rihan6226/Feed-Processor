from flask import Flask, render_template, request, make_response
import requests
from parse_feeder import parse_feed
from save_feeds import article_save
from fetch_feeds import fetch_feeds_from_db
import csv

app = Flask(__name__)

# Sample sum function (replace with your actual function)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        url = request.form['link']
        articles = parse_feed(url)
        article_save(articles)
        return render_template('index.html', result=result)

    return render_template('index.html', result=result)

@app.route('/data', methods=['GET'])
def data():
    data,columns,error = fetch_feeds_from_db()
    return render_template('data.html', data=data, columns=columns)

@app.route('/download', methods=['GET'])
def download():
    data,columns,error = fetch_feeds_from_db()
    output_file = './output.csv'
    with open(output_file, 'w+', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)  # Write the column headers
        writer.writerows(data)     # Write the data rows

    # Prepare the response for downloading the CSV file
    response = make_response(open(output_file, 'r', encoding='utf-8').read())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={output_file}'
    return response

if __name__ == '__main__':
    app.run(debug=True)
