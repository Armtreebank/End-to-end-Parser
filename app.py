from flask import Flask, jsonify, request

from predict import Predictor

import tensorflow as tf


graph = tf.get_default_graph()
model = Predictor(model_path='model.pkl')
app = Flask(__name__, static_url_path='')
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/process', methods=['POST'])
def process():
    text = request.get_data(as_text=True)
    with graph.as_default():  # Needed to avoid exception (tensor doesn't belong to this graph)
        prediction = model.predict_raw(input_text=str(text))
    return jsonify(prediction)


if __name__ == '__main__':
    app.run()
