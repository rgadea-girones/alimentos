# LSTM for sequence classification in the IMDB dataset
import tensorflow as tf
from tensorflow.keras.datasets import imdb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Embedding
from tensorflow.keras.preprocessing import sequence

new_model = tf.keras.models.load_model('Modelo_Paola_linux')
new_model.summary()

new_model.save('saved_model/Modelo_Paola_windows')
