from flask import Flask, jsonify, request
from threading import Thread

from predict import Predictor

import tensorflow as tf


graph = tf.get_default_graph()
model = None
application = Flask(__name__, static_url_path='')
application.config['JSON_AS_ASCII'] = False


def init(model_path):
    global model
    with graph.as_default():
        model = Predictor(model_path=model_path)
    print('Initialized the model!', flush=True)


t = Thread(target=init, args=('model.pkl',))
t.start()


@application.route('/')
def index():
    return application.send_static_file('index.html')


@application.route('/process', methods=['POST'])
def process():
    if model is None:
        raise Exception('Model not initialized yet')

    text = request.get_data(as_text=True)
    with graph.as_default():  # Needed to avoid exception (tensor doesn't belong to this graph)
        prediction = model.predict_raw(input_text=str(text))
    return jsonify(prediction)


if __name__ == '__main__':
    application.run()
