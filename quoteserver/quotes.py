import logging
from elasticsearch import Elasticsearch
from flask import Flask, request, send_from_directory, render_template

app = Flask(__name__)

client = Elasticsearch([{'host':'localhost','port':9200}])

index = 'quotes'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.route('/css/<path:path>')
def css(path):
    return send_from_directory(app.static_folder + '/css/', path, mimetype='text/css')
@app.route('/images/<path:path>')
def image(path):
    return send_from_directory(app.static_folder + '/images/', path, mimetype='image/jpg')

@app.route('/quotes/sayHello', methods=['GET'])
def sayHello():
    docId = request.args.get('id')
    return 'hello ' + docId

@app.route('/quotes/byId', methods=['GET'])
def getById():
    docId = request.args.get('id')
    quote = client.get(index=index, id=docId)
    return render_template('quote.html',quote=quote)

if __name__ == "__main__":
    app.logger.disabled = True
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.run(host='localhost', port=9996, debug=False, threaded=True)

