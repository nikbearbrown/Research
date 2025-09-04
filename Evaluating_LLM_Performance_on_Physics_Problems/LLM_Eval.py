import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from pathlib import Path
from openai import OpenAI
import base64, mimetypes

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 

if not OPENAI_API_KEY:
    raise ValueError("Set OPENAI_API_KEY not in your .env")
client = OpenAI(api_key=OPENAI_API_KEY)

# Loading QA Data
physics_data_path = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Dataset/chapter_10_answers.txt"
with open(physics_data_path, "r", encoding="utf-8") as f:
    physics_data = json.load(f)


# # Judge with Gemini 2.5 Pro
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=GOOGLE_API_KEY)
# judge_verdicts = []
# print("Judging Answers with Gemini 2.5 Pro")
# judge_model = genai.GenerativeModel('gemini-2.5-pro')
# gpt_5_answer_path = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Outputs/gpt-5_answers_low_reasoning_low_verbosity.json"

# with open(gpt_5_answer_path, "r", encoding="utf-8") as file:
#     gpt_5_answers = json.load(file)

# ## Eval Loop 

# for i in range(len(physics_data)):
#     model_output = gpt_5_answers[i]['gpt-5_answer']
#     actual_solution = physics_data[i]['solution']
#     question_id = gpt_5_answers[i]['question_id']
    
#     # Construct the prompt for the judge
#     judge_prompt = f"""
# You are an expert physics professor. Compare the 'Ground Truth Answer' with the 'Model Generated Answer' for the same physics question.
# Determine if the model's answer is substantially similar or correct compared to the ground truth.
# Your response must be a single integer: 1 if they are similar/correct, and 0 if they are not.

# Ground Truth Answer:
# "{actual_solution}"

# Model Generated Answer:
# "{model_output}"

# Verdict (1 for similar, 0 for not):
# """
    
#     print(f"Judging Question ID: {question_id}...")
#     response = judge_model.generate_content(judge_prompt)
#     try:
#         verdict = int(response.text.strip())
#     except ValueError:
#         print(f"Warning: Judge returned a non-integer value for question {question_id}. Defaulting to 0.")
#         verdict = 0
    
#     judge_verdicts.append({
#         "question_id": question_id,
#         "answerVerdict": verdict
#     })


# out_dir = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Outputs"
# out_path = os.path.join(out_dir, f"Eval_gpt_5_low_verbosity_low_reasoning_judge_Gemini_2.5_pro.json")
# with open(out_path, "w", encoding="utf-8") as f:
#     json.dump(judge_verdicts, f, ensure_ascii=False, indent=2)

# Loading Eval Dataset
# physics_data_path = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Outputs/Eval_gpt_5_low_verbosity_low_reasoning_judge_Gemini_2.5_pro.json"
# with open(physics_data_path, "r", encoding="utf-8") as f:
#     eval_data = json.load(f)
# print(eval_data[62])
# for i in range(len(eval_data)):
#     questionId,answerVerdict = eval_data[i]['question_id'],eval_data[i]['answerVerdict']
#     if answerVerdict == 0:
#         print(questionId) 

# 13: Question not processed properly 
# 39: Image description not processed properly
# 48: Image description not processed properly
# 62: Answered incorrectly

# Prompting gpt 5 model with question images
client = OpenAI(api_key=OPENAI_API_KEY)

# Your local image
imgs = [13,39,48,62]
ans = []
for img in imgs:
    q_img_path = f"/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Dataset/{img}.png"
    mime, _ = mimetypes.guess_type(q_img_path)
    mime = mime or "image/png"
    with open(q_img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    data_url = f"data:{mime};base64,{b64}"

    response = client.responses.create(
        model="gpt-5",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text",
                "text": "Solve step-by-step, be concise but correct. Give the final numeric answer at the end."},
                {"type": "input_image",
                "image_url": data_url}
            ]
        }],
        reasoning={"effort": "low"},     # keep reasoning light
        text={"verbosity": "low"},       # keep outputs terse
    )
    ans.append({"question":img,"answer":response.output_text})
out_dir = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Outputs"
out_path = os.path.join(out_dir, f"Eval_gpt_5_low_verbosity_low_reasoning_judge_manual.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(ans, f, ensure_ascii=False, indent=2)


    