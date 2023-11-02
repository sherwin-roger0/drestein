import streamlit as st
from pymongo import MongoClient
from streamlit_local_storage import LocalStorage
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import os
from math import sqrt

global embed
embed = hub.KerasLayer(os.getcwd())

class TensorVector(object):

    def __init__(self, FileName=None):
        self.FileName = FileName

    def process(self):

        img = tf.io.read_file(self.FileName)
        img = tf.io.decode_jpeg(img, channels=3)
        img = tf.image.resize_with_pad(img, 224, 224)
        img = tf.image.convert_image_dtype(img,tf.float32)[tf.newaxis, ...]
        features = embed(img)
        feature_set = np.squeeze(features)
        return list(feature_set)
    
class TensorVector1(object):

    def __init__(self):
        pass

    def process(self, uploaded_image):
        # Convert the uploaded image to bytes
        image_bytes = uploaded_image.read()

        # Decode the image bytes
        img = tf.image.decode_image(image_bytes, channels=3)
        img = tf.image.resize_with_pad(img, 224, 224)
        img = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]

        # Assuming you have the 'embed' function defined elsewhere
        features = embed(img)
        feature_set = np.squeeze(features)
        return list(feature_set)
    
def cosineSim(a1,a2):
    sum = 0
    suma1 = 0
    sumb1 = 0
    for i,j in zip(a1, a2):
        suma1 += i * i
        sumb1 += j*j
        sum += i*j
    cosine_sim = sum / ((sqrt(suma1))*(sqrt(sumb1)))
    return cosine_sim

client = MongoClient("mongodb+srv://sherwinroger:tronster@cluster0.vvp2vpz.mongodb.net/?retryWrites=true&w=majority")
db = client["drestin"]
users_collection = db["users"]
image_collection=db["image"]

image_number=image_collection.find_one()["image"]
print(image_number)

def LocalStorageManager():
    return LocalStorage()
localS = LocalStorageManager()

st.session_state.value=localS.getItem("value",key="valuezz")

st.session_state.page=localS.getItem("user",key="bye")
            
if st.session_state.page["storage"]==None:
    
    st.title("User Registration Page")

    user_name = st.text_input("Enter your username:")

    if st.button("Register") and user_name:          
        user_data = {
            "username": user_name,
        }

        users_collection.insert_one(user_data)
        st.success(f"Registration successful for {user_name}!")
        localS.setItem("user", user_name)
        st.session_state.page = localS.getItem("user",key="hi")
    
else: 
    uploaded_file1 = st.file_uploader("Choose an image...", type="png")
    st.image(f"img{image_number}.png")

    if uploaded_file1:
        st.image(uploaded_file1)
        if st.session_state.value["storage"]==None:
            st.session_state.value["storage"]={"value":0}
        helper = TensorVector(f"img{image_number}.png")
        vector = helper.process()
        
        helper1 = TensorVector1()
        vector2 = helper1.process(uploaded_file1)
            
        answer = cosineSim(vector,vector2)
        
        if answer>st.session_state.value["storage"]["value"]:
            localS.setItem("value",answer)
            filter={"username":st.session_state.page["storage"]["value"]}
            users_collection.update_one(filter, {"$set": {"score": answer}})
        st.session_state.value["storage"]["value"]=answer
    try:    
        st.write(st.session_state.value["storage"]["value"])    
    except:
        st.write(0)
        


st.text("© 2023 Jayashree Rao, Someasvar, Vignesh, Lokesh,Raghav,Sherwin Roger,Mr. Dhinesh Kumar and Mr. Ramachandra (Prompt ur Way Thru). All rights reserved.")
