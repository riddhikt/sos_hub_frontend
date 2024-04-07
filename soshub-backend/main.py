import requests
import json
from fireworks.client import Fireworks
import openai
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, support_credentials=True)

FIREWORKS_API_KEY = "zLvHIvRZLnEmAGCGYbCzSYx9sqHidDmOkYLBDwvB7MbdWFCl"
NEURELO_API_URL = "https://us-west-2.aws.neurelo.com/rest/user_requests"
NEURELO_API_KEY = ("neurelo_9wKFBp874Z5xFw6ZCfvhXTGX5vYS/bbD99o3iuuYi5OaN1YNcm8X/wP6BK5rCoxsnuCzU"
                   "+DSWWnA2HTr1SbRNSDU6O2Dzyby/QShv4i2z203kMppHx6i5B5WkVdFZDhZ3Lkdy7CgzY/RCLRSCNhqqrskqwlvRPQupV2lkO"
                   "+aMaBVVTJtYZt13rQBC12HmnsA_WFbrbBk4B0Y6h9Lffmt6sagkxoD+xVnn4D5UJBX7t6Q=")


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_recommendations(image_base64, prompt):
    client = openai.OpenAI(
        base_url="https://api.fireworks.ai/inference/v1",
        api_key=FIREWORKS_API_KEY
    )
    response = client.chat.completions.create(
        model="accounts/fireworks/models/firellava-13b",
        messages=[{
            "role": "user",
            "content": [{
                "type": "text",
                "text": prompt,
            }, {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                },
            }, ],
        }],
    )
    if response.choices:
        return response.choices[0].message.content
    else:
        print("Error: No response from model.")
        return "Error processing image."


def analyze_data(firellava_analysis):
    client = openai.OpenAI(
        base_url="https://api.fireworks.ai/inference/v1",
        api_key=FIREWORKS_API_KEY
    )

    prompt = (f"<s>[INST] <<SYS>>Analyze this text and return the following data in JSON format-1. Severity of the "
              f"Emergency, 2. Which Authorities to be alerted, 3. What is the emergency (this should be a small text "
              f"as this involves emergency and 911 operators need to review it quickly) 4. Confidence percentage of "
              f"the analysis. Make sure that you only return the data in JSON format and no explanation or extra text "
              f"is needed. If the text says that there's no emergency then in the field 'what is the emergency' put "
              f"the text- 'From the image this emergency isn't clear or wrong image has been attached. Please call us "
              f"or re-submit the photo'<</SYS>>{firellava_analysis}[/INST]")
    response = client.completions.create(
        model="accounts/fireworks/models/llama-v2-70b-chat",
        max_tokens=512,
        temperature=0.1,
        prompt=prompt
    )

    if response.choices:
        return response.choices[0].text
    else:
        print("Error: No response from model.")
        return "Error processing data."


def analyze_user_data(firellava_analysis, user_category, user_description):
    client = openai.OpenAI(
        base_url="https://api.fireworks.ai/inference/v1",
        api_key=FIREWORKS_API_KEY
    )

    prompt_llama = (f"<s>[INST] <<SYS>>Your task is to review the following information and provide a response in JSON "
                    f"format:- AI Analysis: A text analysis of an emergency image by an AI model, identifying the "
                    f"type of emergency, recommended first responders, and severity.- User Category: An optional "
                    f"category entered by the user to describe the emergency.- User Description: An optional textual "
                    f"description of the emergency provided by the user. If the AI Analysis and user-entered data ("
                    f"Category and Description) do not match or if the image is unclear, return the following JSON "
                    f"data:'severity': low,'responders': [],'emergency': 'From the image this emergency isn't clear "
                    f"or wrong image has been attached. Please call us or re-submit the photo','confidence': 90. "
                    f"Otherwise, return a JSON object with the following fields:- severity: The severity of the "
                    f"emergency (e.g., low, medium, high)- responders: A list of recommended first responders (e.g., "
                    f"police, firefighters, EMTs, paramedics)- emergency: A brief description of the emergency - "
                    f"confidence: A percentage indicating the confidence level of the analysis. Example JSON "
                    f"output-'severity': 'high','responders': ['firefighters', 'paramedics'],'emergency': 'House fire "
                    f"with potential casualties','confidence': 85. Make sure that you ONLY return the data in JSON "
                    f"format and NO explanation or extra text or header is needed.<</SYS>>Input:AI Analysis: "
                    f"{firellava_analysis} , User Category: {user_category}, User Description: {user_description}["
                    f"/INST]")
    response = client.completions.create(
        model="accounts/fireworks/models/llama-v2-70b-chat",
        max_tokens=512,
        temperature=0.1,
        prompt=prompt_llama
    )

    if response.choices:
        return response.choices[0].text
    else:
        print("Error: No response from model.")
        return "Error processing data."


def analyze_recommendations(firellava_analysis, llama_analysis):
    client = openai.OpenAI(
        base_url="https://api.fireworks.ai/inference/v1",
        api_key=FIREWORKS_API_KEY
    )

    prompt_llamav2 = (f"<s>[INST] <<SYS>>]You are an AI assistant specialized in providing emergency response "
                      f"recommendations. Your task is to analyze the text, which describes an emergency situation "
                      f"identified from an image given in INPUT. Based on the provided text, you need to generate two "
                      f"lists: 1. A list of 5- 'Do's' - Actions or steps that the affected person(s) or bystanders "
                      f"should take while waiting for the first responders to arrive. 2. A list of 5- 'Donts' - "
                      f"Actions or steps that the affected person(s) or bystanders should avoid while waiting for the "
                      f"first responders to arrive. Your recommendations should be concise, clear, and tailored to "
                      f"the specific emergency situation described in the text. The goal is to provide practical and "
                      f"potentially life-saving guidance to help mitigate the situation until professional help "
                      f"arrives. Please format your response as follows: Do's: 1. [Action 1] 2. [Action 2] 3. [Action "
                      f"3] 4. [Action 4] 5. [Action 5]. Don'ts: 1. [Action 1] 2. [Action 2] 3. [Action 3] 4. [Action "
                      f"4] 5. [Action 5]Remember, your recommendations should be based solely on the information "
                      f"provided in the text and should not include any additional context or assumptions. Please "
                      f"format your response as a JSON object with the following structure: 'dos': [Action 1,"
                      f"Action 2,Action 3,Action 4,Action 5],'donts': [Action 1,Action 2,Action 3,Action 4,"
                      f"Action 5]. Remember, your recommendations should be based solely on the information provided "
                      f"in the JSON data and should not include any additional context or assumptions. Also MAKE "
                      f"SURE, if the text suggests that there is NO EMERGENCY, then return BLANK Dos and Donts in the "
                      f"JSON format mentioned above.Make sure that you ONLY return the data in JSON format and NO "
                      f"explanation or extra text is needed.<</SYS>>INPUT: {firellava_analysis}[/INST]")
    response = client.completions.create(
        model="accounts/fireworks/models/llama-v2-70b-chat",
        max_tokens=512,
        temperature=0.1,
        prompt=prompt_llamav2
    )

    if response.choices:
        return response.choices[0].text
    else:
        print("Error: No response from model.")
        return "Error processing data."


def analyze_emergency(image_base64, prompt):
    client = openai.OpenAI(
        base_url="https://api.fireworks.ai/inference/v1",
        api_key=FIREWORKS_API_KEY
    )
    response = client.chat.completions.create(
        model="accounts/fireworks/models/firellava-13b",
        messages=[{
            "role": "user",
            "content": [{
                "type": "text",
                "text": prompt,
            }, {
                "type": "image_url",
                "image_url": {
                    "url": image_base64
                },
            }, ],
        }],
    )
    if response.choices:
        return response.choices[0].message.content
    else:
        print("Error: No response from model.")
        return "Error processing image."


def store_analysis_results_in_db(data):
    headers = {
        "X-API-KEY": NEURELO_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(NEURELO_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        print("Data successfully stored in Neurelo database.")
    else:
        print(
            f"Failed to store data in Neurelo database. Status code: {response.status_code}, Response: {response.text}")


@app.route('/analyze', methods=['POST'])
@cross_origin(supports_credentials=True)
def analyze():
    data = request.json
    image_base64 = data.get('image_base64')
    if not image_base64:
        return jsonify({"error": "image_base64 is required"}), 400
    user_category = data.get('category', '')
    user_description = data.get('description', '')
    location = data.get('location', '')

    prompt = ("Prompt- You are a First Responder Analyst and your job is to view the image and "
              "analyze what kind of incident has happened. Also classify which of the first "
              "responders (police, firefighters, emergency medical technicians-EMTs, "
              "and paramedics) should be deployed based on the image. You need to make sure that "
              "the image is actually of an emergency, consider this image as part of a 911 call. "
              "So, analyze and classify if the image is of an emergency and also assign severity of "
              "the emergency. If the image doesn't seem like an emergency, you need to return a "
              "message saying -'From the image this emergency isn't clear or wrong image has been "
              "attached. Please call us or re-submit the photo'. Also give the confidence of your "
              "analysis in NUMERIC percentage always.")

    firellava_analysis = analyze_emergency(image_base64, prompt)

    if user_category and user_description:
        llama_analysis = analyze_user_data(firellava_analysis, user_category, user_description)
    else:
        llama_analysis = analyze_data(firellava_analysis, user_category, user_description)

    recommendations = analyze_recommendations(firellava_analysis, llama_analysis)

    data_to_store = [{
        "image_analysis": firellava_analysis,
        "llama_analysis": json.loads(llama_analysis) if llama_analysis else None,
        "recommendations": json.loads(recommendations) if recommendations else None,
        "location": location,
        "image_base64": image_base64,
        "category": user_category,
        "desc": user_description
    }]

    # Call the function to store data in the Neurelo database
    store_analysis_results_in_db(data_to_store)

    return jsonify(data_to_store)


if __name__ == '__main__':
    app.run(debug=True)
