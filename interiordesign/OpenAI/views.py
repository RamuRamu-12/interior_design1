from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from digiotai.digiotai_jazz import Agent, Task, OpenAIModel, SequentialFlow, InputType, OutputType
from .form import CreateUserForm
import io
import json
import base64
import pandas as pd
from dotenv import load_dotenv
import os
from openai import OpenAI



load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)
expertise = "Interior Desinger"
task = Task("Image Generation")
input_type = InputType("Text")
output_type = OutputType("Image")
agent = Agent(expertise, task, input_type, output_type)
api_key = OPENAI_API_KEY


@csrf_exempt
def testing(request):
    return HttpResponse("Application is up")


def get_csv_metadata(df):
    metadata = {
        "columns": df.columns.tolist(),
        "data_types": df.dtypes.to_dict(),
        "null_values": df.isnull().sum().to_dict(),
        "example_data": df.head().to_dict()
    }
    return metadata

@csrf_exempt
def loginpage(request):
    """ if user submits the credentials  then it check if they are valid or not
                    if it is valid then it redirects to user home page """
    if request.user.is_authenticated:
        return redirect('demo:home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse("Login Success")
            else:
                print('User Name or Password is incorrect')
        context = {}
        return HttpResponse("Login failed")

@csrf_exempt
# logout method
def logoutpage(request):
    try:
        logout(request)
        request.session.clear()  # deleting the session of user
        return redirect('demo:login')  # redirecting to login page
    except Exception as e:
        return e  # redirect('demo:')  # redirecting to login page

@csrf_exempt
def register(request):
    if request.user.is_authenticated:
        return HttpResponse("Registration Failed")
    else:
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            try:
                if form.is_valid():
                    print("test2")
                    form.save()
                    user = form.cleaned_data.get('username')
                    return HttpResponse("Registration Success")
                else:
                    print(form.errors)
                    return HttpResponse("Registration failed")
            except Exception as e:
                print(e)

        return HttpResponse("Registration Failed")


@csrf_exempt
def upload_data(request):
    if request.method == "POST":
        files = request.FILES['file']
        if len(files) < 1:
            return HttpResponse('No files uploaded')
        else:
            content = files.read().decode('utf-8')
            csv_data = io.StringIO(content)
            df = pd.read_csv(csv_data)
            df.to_csv('data.csv',index=False)
            return HttpResponse("Success")
    else:
        return HttpResponse("Failure")

@csrf_exempt
def genAIPrompt(request):
    if request.method == "POST":
        df = pd.read_csv("data.csv")
        csv_metadata = get_csv_metadata(df)
        metadata_str = ", ".join(csv_metadata["columns"])
        query = request.POST["query"]
        prompt_eng = (
            f"You are graphbot. If the user asks to plot a graph, you only reply with the Python code of Matplotlib to plot the graph and save it as graph.png. "
            f"The data is in data.csv and its attributes are: {metadata_str}. If the user does not ask for a graph, you only reply with the answer to the query. "
            f"The user asks: {query}"
        )

        code = generate_code(prompt_eng)
        if 'import matplotlib' in code:
            try:
                exec(code)
                with open("graph.png", 'rb') as image_file:
                    return HttpResponse(json.dumps({"graph": base64.b64encode(image_file.read()).decode('utf-8')}),
                                        content_type="application/json")
            except Exception as e:
                prompt_eng = f"There has occurred an error while executing the code, please take a look at the error and strictly only reply with the full python code do not apologize or anything just give the code {str(e)}"
                code = generate_code(prompt_eng)
                try:
                    exec(code)
                    with open("graph.png", 'rb') as image_file:
                        return HttpResponse(json.dumps({"graph": base64.b64encode(image_file.read()).decode('utf-8')}),
                                            content_type="application/json")
                except Exception as e:
                    return HttpResponse("Failed to generate the chart. Please try again")
        else:
            return HttpResponse(code)


@csrf_exempt
def genAIPrompt2(request):
    if request.method == "POST":
        model = OpenAIModel(api_key=api_key, model="dall-e-3")
        sequential_flow = SequentialFlow(agent, model)
        selected_style = request.POST["selected_style"]
        selected_room_color = request.POST["selected_room_color"]
        selected_room_type = request.POST["selected_room_type"]
        number_of_room_designs = request.POST["number_of_room_designs"]
        additional_instructions = request.POST["additional_instructions"]
        prompt = f"Generate a Realistic looking Interior design with the following instructions style: {selected_style}, Room Color: {selected_room_color},Room type: {selected_room_type},Number of designs:{number_of_room_designs} ,Instructions: {additional_instructions}"
        image_url = sequential_flow.execute(prompt)
        print(image_url)
        return HttpResponse(image_url)
    

@csrf_exempt
def generate_code(prompt_eng):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_eng}
        ]
    )
    all_text = ""

    # Display generated content dynamically
    for choice in response.choices:
        print(f"Debug - choice structure: {choice}")  # Debugging line
        message = choice.message
        print(f"Debug - message structure: {message}")  # Debugging line
        chunk_message = message.content if message else ''
        all_text += chunk_message

    code_start = all_text.find("```python") + 9
    code_end = all_text.find("```", code_start)
    code = all_text[code_start:code_end]
    return code


@csrf_exempt
def genAIPrompt3(request):
        df = pd.read_csv("data.csv")
        prompt_eng = (
            f"You are analytics_bot. Analyse the data: {df} and give description of the columns"
        )
        code = generate_code(prompt_eng)
        prompt_eng1 = (
            f"Give sample questions based for that data"
        )
        code1 = generate_code(prompt_eng1)
        print(code1)
        return HttpResponse(code1)




# # Converting the three images in to the single image
@csrf_exempt
def generateCombinedImage(request):
    if request.method == "POST":
        try:
            # Initialize OpenAIModel and SequentialFlow
            model = OpenAIModel(api_key=api_key, model="dall-e-3")
            agent = Agent(expertise="Interior Designer", task=Task("Image Generation"), 
                          input_type=InputType("Images"), output_type=OutputType("Image"))
            sequential_flow = SequentialFlow(agent=agent, model=model)

            # Retrieve input values from POST data
            selected_style = request.POST["selected_style"]
            selected_room_color = request.POST["selected_room_color"]
            selected_room_type = request.POST["selected_room_type"]
            number_of_room_designs = request.POST["number_of_room_designs"]

            # Construct prompt with input values
            prompt = f"Generate a final image based on the provided input: Style: {selected_style}, Room Color: {selected_room_color}, Room Type: {selected_room_type}, Number of Designs: {number_of_room_designs}"

            # Execute SequentialFlow to generate final image
            image_url = sequential_flow.execute(prompt)

            # Return the image URL as a response
            return HttpResponse(image_url)

        except Exception as e:
            # Handle exceptions as needed
            return HttpResponse(f"Error: {str(e)}")

    else:
        # Handle GET requests or other methods if needed
        return HttpResponse("Method not allowed")


