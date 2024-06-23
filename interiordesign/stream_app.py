
import streamlit as st
from dotenv import load_dotenv
from digiotai.digiotai_jazz import Agent, Task, OpenAIModel, SequentialFlow, InputType, OutputType
import os
from openai import OpenAI
load_dotenv()

#openai_api_key = os.getenv("OPENAI_API_KEY")

openai_api_key = st.secrets["OPENAI_API_KEY"]

#Define agent properties
expertise = "Interior Desinger"
task = Task("Image Generation")
input_type = InputType("Text")
output_type = OutputType("Image")
agent = Agent(expertise, task, input_type, output_type)
api_key = openai_api_key
model = OpenAIModel(api_key=api_key,model="dall-e-2")
sequential_flow = SequentialFlow(agent, model)

# Main page content
st.title("DIGIOTAI")
st.subheader("Interior Designer")
st.write("")  # Placeholder for the generated image

# Sidebar content
st.sidebar.title("Welcome to interior designer")


# Dropdown for interior design styles
styles = ["Modern", "Contemporary", "Minimalist", "Industrial", "Scandinavian", "Traditional", "Bohemian"]
selected_style = st.sidebar.selectbox("Select an interior design style:", styles)

# Dropdown for types of rooms
rooms = ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Dining Room", "Home Office", "Kids Room"]
selected_room = st.sidebar.selectbox("Select a room type:", rooms)

# Input box for further instructions
additional_instructions = st.sidebar.text_area("Any further instructions:")

# Submit button
if st.sidebar.button("Submit"):
    # Combine all user inputs to form a prompt
    prompt = f"Generate a Realistic looking Interior design with the following instructions style: {selected_style}, Room type: {selected_room}, Instructions: {additional_instructions}"

    # Generate image using the prompt
    image_url = sequential_flow.execute(prompt)
    
    # Display the generated image on the main page
    st.image(image_url, caption="")


