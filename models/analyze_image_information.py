from groq import Groq

def analyze_image_information(image_description, ocr_results, yolo_results, emotions):
    prompt = f"""
    Analyze the following image information and provide insights based on the criteria given below:

    Image Description:
    {image_description}

    OCR Results:
    {ocr_results}

    Yolo Results:
    {yolo_results}

    Emotions:
    {emotions}

    Criteria:
    1. Setup Context: Determine the scene context in the picture
    - You should response: "The scene context is xxx" with xxx is bar, restaurant, grocery store, supermarket, boozer or something like that
    2. People: Describe the number of people, their activities, and emotions.
    - You should response: "There are(is) xxx people in the picture" with xxx is the number of people. You must know exactly how many people in this picture.
    - You should response: "There are(is) yyy people who are drinking beer" with yyy is the number of people who are drinking beer. You must know exactly how many people who are drinking in the picture.
    3. Brand Detection: Identify any brand mentioned in the image, description or OCR results (Heineken, Tiger, Bia Viet, Larue, Bivina, Edelweiss and Strongbow, etc).
    - You should response: "There are(is) xxx brand in the picture: yyy, yyy, yyy" with xxx is the number of brands and yyy is the name of brand logos such as Heineken, Tiger, Bia Viet, Larue, Bivina, Edelweiss and Strongbow, etc
    4. Products: Mention any products such as beer kegs and bottles.
    - How many beer bottles, beer kegs of each brand?
    5. Promotional Materials: Identify any posters, banners, and billboards.


    Insights:

    If you don't know clearly, don't say false information.
    """

    # Replace with your Groq API key

    client = Groq(
        # This is the default and can be omitted
        api_key="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",
    )


    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}]
    }

    chat_completion = client.chat.completions.create(**data)
    return chat_completion.choices[0].message.content