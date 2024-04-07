from flask import Flask, request, jsonify
from fireworks.client import Fireworks
import base64
from io import BytesIO
import os
from datetime import datetime
import requests
import json

app = Flask(__name__)

# Firework AI API URL and credentials
FIREWORK_API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
FIREWORK_API_KEY = "zLvHIvRZLnEmAGCGYbCzSYx9sqHidDmOkYLBDwvB7MbdWFCl"
LLAMA_API_URL = "https://api.fireworks.ai/inference/v1/completions"  # URL for the LLaMA 2 model
LLAMA_MODEL = "accounts/fireworks/models/llama-v2-13b-chat"  # Specify the correct LLaMA model

uploads_dir = os.path.join(app.root_path, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)  # Create uploads directory if it doesn't exist


def save_image(base64_str, file_path):
    """
    Decode a Base64 string and save the image to a file.
    Strips any potential metadata prefix (e.g., 'data:image/jpeg;base64,') before decoding.
    """
    # Check if the string contains ';base64,' which indicates the presence of a metadata prefix.
    if ";base64," in base64_str:
        # Split the string on ";base64," and take the part after it, which is the actual Base64-encoded data.
        base64_str = base64_str.split(";base64,")[1]
    # Decode the Base64-encoded data to get the original binary image data.
    image_data = base64.b64decode(base64_str)
    # Write the binary image data to a file at the specified path.
    with open(file_path, 'wb') as file:
        file.write(image_data)


def analyze_emergency(image_path):
    with open(image_path, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    firework_payload = {
        "model": "accounts/fireworks/models/llava-yi-34b",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Prompt- You are a First Responder Analyst and your job is to view the image and "
                                "analyze what kind of incident has happened. Also classify which of the first "
                                "responders (police, firefighters, emergency medical technicians-EMTs, "
                                "and paramedics) should be deployed based on the image. You need to make sure that "
                                "the image is actually of an emergency, consider this image as part of a 911 call. "
                                "So, analyze and classify if the image is of an emergency and also assign severity of "
                                "the emergency. If the image doesn't seem like an emergency, you need to return a "
                                "message saying -'From the image this emergency isn't clear or wrong image has been "
                                "attached. Please call us or re-submit the photo'. Also give the confidence of your "
                                "analysis in NUMERIC percentage always."

                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIREWORK_API_KEY}"
    }

    # Make the request to Firework AI API
    response = requests.post(FIREWORK_API_URL, headers=headers, json=firework_payload)
    if response.status_code == 200:
        # Process and return the response from Firework AI here
        response = response.json(), 200
    else:
        response = jsonify({'error': 'Failed to get a response from Firework AI API',
                            'status_code': response.status_code}), response.status_code
    # print(response)
    vision_description = response[0]["choices"][0]["message"]["content"]
    return vision_description


def analyze_data_with_llama(firellava_analysis):
    prompt = (f"<s>[INST] <<SYS>>Analyze this text and return the following data in JSON format-1. Severity of the "
              f"Emergency, 2. Which Authorities to be alerted, 3. What is the emergency (this should be a small text "
              f"as this involves emergency and 911 operators need to review it quickly) 4. Confidence percentage of "
              f"the analysis. Make sure that you only return the data in JSON format and no explanation or extra text "
              f"is needed. If the text says that there's no emergency then in the field 'what is the emergency' put "
              f"the text- 'From the image this emergency isn't clear or wrong image has been attached. Please call us "
              f"or re-submit the photo'<</SYS>>{firellava_analysis}[/INST]"
              )

    llama_payload = {
        "model": LLAMA_MODEL,
        "max_tokens": 512,
        "temperature": 0.1,
        "prompt": prompt
    }

    llama_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIREWORK_API_KEY}"  # Use your Firework API key
    }

    llama_response = requests.post(LLAMA_API_URL, json=llama_payload, headers=llama_headers)

    if llama_response.status_code == 200:
        # Process and return the response from Firework AI LLaMA here
        return llama_response.json()
    else:
        return {'error': 'Failed to get a response from Firework AI LLaMA API',
                'status_code': llama_response.status_code}


def analyze_user_data_with_llama(firellava_analysis, category, description):
    prompt = (f"<s>[INST] <<SYS>>Your task is to review the following information and provide a response in JSON "
              f"format:- AI Analysis: A text analysis of an emergency image by an AI model, identifying the type of "
              f"emergency, recommended first responders, and severity.- User Category: An optional category entered "
              f"by the user to describe the emergency.- User Description: An optional textual description of the "
              f"emergency provided by the user. If the AI Analysis and user-entered data (Category and Description) "
              f"do not match or if the image is unclear, return the following JSON data:'severity': low,'responders': "
              f"[],'emergency': 'From the image this emergency isn't clear or wrong image has been attached. Please "
              f"call us or re-submit the photo','confidence': 90. Otherwise, return a JSON object with the following "
              f"fields:- severity: The severity of the emergency (e.g., low, medium, high)- responders: A list of "
              f"recommended first responders (e.g., police, firefighters, EMTs, paramedics)- emergency: A brief "
              f"description of the emergency - confidence: A percentage indicating the confidence level of the "
              f"analysis. Example JSON output-'severity': 'high','responders': ['firefighters', 'paramedics'],"
              f"'emergency': 'House fire with potential casualties','confidence': 85. Make sure that you ONLY return "
              f"the data in JSON format and NO explanation or extra text or header is needed.<</SYS>>Input:AI "
              f"Analysis: {firellava_analysis} , User Category: {category}, User Description: "
              f"{description}[/INST]"
              )

    llama_payload = {
        "model": LLAMA_MODEL,
        "max_tokens": 512,
        "temperature": 0.1,
        "prompt": prompt
    }

    llama_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIREWORK_API_KEY}"  # Use your Firework API key
    }

    llama_response = requests.post(LLAMA_API_URL, json=llama_payload, headers=llama_headers)

    if llama_response.status_code == 200:
        # Process and return the response from Firework AI LLaMA here
        return llama_response.json()
    else:
        return {'error': 'Failed to get a response from Firework AI LLaMA API',
                'status_code': llama_response.status_code}


def analyze_recommendations(firellava_analysis):
    prompt = (f"<s>[INST] <<SYS>>You are an AI assistant specialized in providing emergency response "
              f"recommendations. Your task is to analyze the text, which describes an emergency situation "
              f"identified from an image given in INPUT. Based on the provided text, you need to generate two "
              f"lists: 1. A list of 5- 'Do's' - Actions or steps that the affected person(s) or bystanders "
              f"should take while waiting for the first responders to arrive. 2. A list of 5- 'Donts' - "
              f"Actions or steps that the affected person(s) or bystanders should avoid while waiting for the "
              f"first responders to arrive. Your recommendations should be concise, clear, and tailored to "
              f"the specific emergency situation described in the text. The goal is to provide practical and "
              f"potentially life-saving guidance to help mitigate the situation until professional help "
              f"arrives. Please format your response as follows: Do's: 1. [Action 1] 2. [Action 2] 3. [Action "
              f"3] 4. [Action 4] 5. [Action 5]. Donts: 1. [Action 1] 2. [Action 2] 3. [Action 3] 4. [Action "
              f"4] 5. [Action 5]Remember, your recommendations should be based solely on the information "
              f"provided in the text and should not include any additional context or assumptions. Please "
              f"format your RESPONSE AS A JSON OBJECT with the following structure: 'dos': [Action 1,"
              f"Action 2,Action 3,Action 4,Action 5],'donts': [Action 1,Action 2,Action 3,Action 4,"
              f"Action 5]. Remember, your recommendations should be based solely on the information provided "
              f"in the JSON data and should not include any additional context or assumptions. Also MAKE "
              f"SURE, if the text suggests that there is NO EMERGENCY, then return BLANK Dos and Donts in the "
              f"JSON format mentioned above.MOST IMPORTANT- Make sure that you ONLY return the data in JSON format and NO "
              f"explanation or extra text or HEADER is needed.<</SYS>>INPUT: {firellava_analysis}[/INST]")

    llama_payload = {
        "model": LLAMA_MODEL,
        "max_tokens": 512,
        "temperature": 0.1,
        "prompt": prompt
    }

    llama_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIREWORK_API_KEY}"  # Use your Firework API key
    }

    llama_response = requests.post(LLAMA_API_URL, json=llama_payload, headers=llama_headers)

    if llama_response.status_code == 200:
        # Process and return the response from Firework AI LLaMA here
        return llama_response.json()
    else:
        return {'error': 'Failed to get a response from Firework AI LLaMA API',
                'status_code': llama_response.status_code}


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    base64_str = data['base64_str']
    category = data.get('category', '')
    description = data.get('description', '')

    # Generate a unique filename for the image
    filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.png'
    file_path = os.path.join(uploads_dir, filename)

    # Save the decoded image to the uploads directory
    save_image(base64_str, file_path)

    # Create a local URL for the saved image
    image_url = 'uploads/' + filename

    firellava_analysis = analyze_emergency(image_url)

    # Assuming firellava_analysis needs to be passed as is. Adjust if needed.
    if category and description:
        llama_analysis = analyze_user_data_with_llama(firellava_analysis, category, description)
    else:
        llama_analysis = analyze_data_with_llama(firellava_analysis)
    recommendations = analyze_recommendations(firellava_analysis)

    # Splitting the entry into the two sections: Do's and Dont's
    parts = recommendations['choices'][0]['text'].split("Dont's:\n\n")

    # Further splitting to isolate the Do's and Dont's lists
    dos_text = parts[0].split("Do's:\n\n")[1]
    donts_text = parts[1].split("5")[0]

    # Splitting each section into individual points and trimming whitespace
    dos_list = [point.strip() for point in dos_text.strip().split("\n") if point.strip()]
    donts_list = [point.strip() for point in donts_text.strip().split("\n") if
                  point.strip() and not point.startswith("Please note")]

    # Creating a dictionary to hold the separated lists
    separated_lists = {
        "Dos": dos_list,
        "Donts": donts_list,
        "Disclaimer": "Please note that these recommendations are based solely on the information provided in the text "
                      "and should not be taken as professional advice. In case of any emergency, always prioritize "
                      "your safety and the safety of others, and follow the instructions of the trained first "
                      "responders."
    }

    return jsonify({
        "FireLLaVA Analysis": firellava_analysis,
        "Llama Analysis": json.loads(llama_analysis['choices'][0]['text']),
        "recommendations": separated_lists
    })


if __name__ == '__main__':
    app.run(debug=True)
