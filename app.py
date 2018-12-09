from flask import Flask, jsonify, request
from threading import Thread

from predict import Predictor

import tensorflow as tf


graph = tf.get_default_graph()
model = None
app = Flask(__name__, static_url_path='')
app.config['JSON_AS_ASCII'] = False


def init(model_path):
    global model
    model = Predictor(model_path=model_path)
    print('Initialized the model!', flush=True)


t = Thread(target=init, args=('model.pkl',))
t.start()


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/process', methods=['POST'])
def process():
    if model is None:
        raise Exception('Model not initialized yet')

    text = request.get_data(as_text=True)
    with graph.as_default():  # Needed to avoid exception (tensor doesn't belong to this graph)
        prediction = model.predict_raw(input_text=str(text))
    return jsonify(prediction)


if __name__ == '__main__':
    app.run()
