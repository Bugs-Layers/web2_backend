import os
import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model
from PIL import Image, ImageFile
import gradio as gr

ImageFile.LOAD_TRUNCATED_IMAGES = True

new_model = tf.keras.models.load_model('tree-not-tree.keras')

def TreeOrNotTree(img):
    # Convert PIL image to a numpy array (RGB format)
    img_array = np.array(img)

    # Resize the image to the expected input size (128x128) using cv2
    img_array = cv2.resize(img_array, (128, 128))

    # Normalize the image
    img_array = img_array / 255.0
    
    # Reshape to add batch dimension (1, 128, 128, 3)
    img_array = np.expand_dims(img_array, axis=0)
    
    # Make prediction
    prediction = new_model.predict(img_array)
    
    # Round the prediction to get the class
    pred_round = prediction.round()
    
    # Determine the predicted class
    pred_class = 'Not Tree' if pred_round == 0 else 'Tree'
    
    return pred_class

def classify_image(input_image):
    return TreeOrNotTree(input_image)

# Create Gradio interface
interface = gr.Interface(fn=classify_image, 
                         inputs=gr.Image(),
                         outputs="text", 
                         title="Tree or Not Tree Classifier",
                         description="Upload an image to classify if it's a Tree or Not Tree.")

interface.launch()

    