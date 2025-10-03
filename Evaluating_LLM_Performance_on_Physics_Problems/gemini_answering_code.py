GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

physics_data_path = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Dataset/chapter_10_answers.txt"
with open(physics_data_path, "r", encoding="utf-8") as file:
    physics_data = json.load(file)

# Solve questions with Gemini 1.5 Flash
model_name = 'gemini-1.5-flash'
flash_model = genai.GenerativeModel(model_name)
flash_answers = []
out_dir = f"/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Outputs/{model_name}_answers.json"
for item in physics_data:
    question_id = item['question_id']
    question_text = item['question']
    image_desc = item['image_description']

    # Construct the prompt
    prompt = f"Please solve the following physics question in a step-by-step manner.\n\nQuestion: {question_text}"
    if image_desc:
        prompt += f"\n\nContext from an image: {image_desc}"

    print(f"Processing Question ID: {question_id}...")
    
    response = flash_model.generate_content(prompt)
    model_answer = response.text

    flash_answers.append({
        "question_id": question_id,
        f"{model_name}_answer": model_answer
    })

with open(out_dir,"w", encoding="utf-8") as f:
    json.dump(flash_answers, f, ensure_ascii=False, indent=2)