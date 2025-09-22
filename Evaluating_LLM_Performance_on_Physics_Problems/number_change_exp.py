import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from pathlib import Path
from openai import OpenAI
from anthropic import Anthropic
import base64, mimetypes
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
# QUESTION IDs to evaluate
# Q39 (includes Diagram), 63, 61, 60, 59, 58, 57, 56, 55, 54, 53, 51, 50, 49, 47

# OPEN AI CODE
openAIClient = OpenAI(api_key=OPENAI_API_KEY)
gpt5_answers = []
claude_answers = []
# Loop through the 14 questions ; one question is image based
# Loading QA Data
modified_physics_questions = []
modified_physics_questions_path = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Dataset/Modified_Questions.txt"
with open(modified_physics_questions_path, "r", encoding="utf-8") as f:
    modified_physics_questions = json.load(f)

# 14 TEXT-ONLY Questions (GPT)
# for i in range(1,len(modified_physics_questions)):
#     question_id = modified_physics_questions[i]['question_id']
#     question = modified_physics_questions[i]['modified_question']
#     # Get output of gpt
#     prompt = (
#     "Solve step-by-step, be concise but correct. "
#     "Give the final numeric answer at the end.\n\n"
#     f"{question}"
#     )
#     response = openAIClient.responses.create(
#         model="gpt-5",
#         input=[{
#             "role": "user",
#             "content": [
#                 {"type": "input_text",
#                 "text": prompt},
#             ]
#         }],
#         reasoning={"effort": "low"},     
#         text={"verbosity": "low"},       
#     )
#     gpt5_answers.append({"question_id": question_id, "answer": response.output_text})
#     out_dir = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Outputs"
#     out_path = os.path.join(out_dir, f"Modified_Q_gpt_5_low_verbosity_low_reasoning.json")

# with open(out_path, "w", encoding="utf-8") as f:
#     json.dump(gpt5_answers, f, ensure_ascii=False, indent=2)

# 1 IMG-BASED Question (GPT)
# diagram_path = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Dataset/Q39 Diagram.png"
# mime, _ = mimetypes.guess_type(diagram_path)
# mime = mime or "image/png"
# with open(diagram_path, "rb") as f:
#     b64 = base64.b64encode(f.read()).decode("utf-8")
# data_url = f"data:{mime};base64,{b64}"

# prompt = (
#     "Solve step-by-step, be concise but correct. "
#     "Give the final numeric answer at the end.\n\n"
#     f"{modified_physics_questions[0]}"
#     )
# response = openAIClient.responses.create(
#     model="gpt-5",
#     input=[{
#         "role": "user",
#         "content": [
#             {"type": "input_text",
#             "text": prompt},
#             {"type": "input_image",
#             "image_url": data_url}
#             ]
#         }],
#         reasoning={"effort": "low"},     
#         text={"verbosity": "low"},       
# )
# print(response.output_text)

# - Get output of claude


# -  Loop though answers of gpt and claude ; use gemini as judge. Output format
# {
# "question_id",
# "gpt_anwer_verdict",
# "claude_answer_verdict"
# }

## CLAUDE CODE
# CLAUDE_MODEL = "claude-sonnet-4-0"  
# MAX_TOKENS = 2048                    
# THINKING_BUDGET = 1024               

# anthropicClient = Anthropic(api_key=ANTHROPIC_API_KEY)

# modified_physics_questions_path = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Dataset/Modified_Questions.txt"
# with open(modified_physics_questions_path, "r", encoding="utf-8") as f:
#     modified_physics_questions = json.load(f)

# # 14 TEXT-ONLY Questions (Claude 4)
# for i in range(1, len(modified_physics_questions)):  # your original index pattern
#     question_id = modified_physics_questions[i]["question_id"]
#     question = modified_physics_questions[i]["modified_question"]

#     prompt = (
#         "Solve step-by-step, be concise but correct. "
#         "Give the final numeric answer at the end.\n\n"
#         f"{question}"
#     )

#     msg = anthropicClient.messages.create(
#         model=CLAUDE_MODEL,
#         max_tokens=MAX_TOKENS,
#         thinking={"type": "enabled", "budget_tokens": THINKING_BUDGET},  # extended thinking ~ low effort
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": prompt},
#                 ],
#             }
#         ],
#     )

#     # Claude responses come back as content blocks; stitch text parts together
#     text_out = "".join(
#         block.text for block in msg.content if getattr(block, "type", None) == "text"
#     )
#     claude_answers.append({"question_id": question_id, "answer": text_out})

# # Write Claude text answers 
# out_dir = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Outputs"
# os.makedirs(out_dir, exist_ok=True)
# out_path = os.path.join(out_dir, "Modified_Q_claude_4_low_thinking.json")
# with open(out_path, "w", encoding="utf-8") as f:
#     json.dump(claude_answers, f, ensure_ascii=False, indent=2)

# # 1 IMG-BASED Question (Claude 4)
# diagram_path = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Dataset/Q39 Diagram.png"
# mime, _ = mimetypes.guess_type(diagram_path)
# mime = mime or "image/png"
# with open(diagram_path, "rb") as f:
#     b64 = base64.b64encode(f.read()).decode("utf-8")

# img_prompt = (
#     "Solve step-by-step, be concise but correct. "
#     "Give the final numeric answer at the end.\n\n"
#     f"{modified_physics_questions[0]}"
# )

# msg_img = anthropicClient.messages.create(
#     model=CLAUDE_MODEL,
#     max_tokens=MAX_TOKENS,
#     thinking={"type": "enabled", "budget_tokens": THINKING_BUDGET},
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "image",
#                     "source": {"type": "base64", "media_type": mime, "data": b64},
#                 },
#                 {"type": "text", "text": img_prompt},
#             ],
#         }
#     ],
# )

# img_out = "".join(
#     block.text for block in msg_img.content if getattr(block, "type", None) == "text"
# )
# print(img_out)

# GEMINI JUDGE
judge_verdicts = [] #[{"question_id", "gpt_anwer_verdict", "claude_answer_verdict"}
print("Judging Answers with Gemini 2.5 Pro")
judge_model = genai.GenerativeModel('gemini-2.5-pro')

gpt_5_answer_path = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Outputs/Modified_Q_gpt_5_low_verbosity_low_reasoning.json"
with open(gpt_5_answer_path, "r", encoding="utf-8") as file:
    gpt_5_answers = json.load(file)

anthropic_answer_path = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Outputs/Modified_Q_claude_4_low_thinking.json"
with open(anthropic_answer_path, "r", encoding="utf-8") as file:
    anthropic_answers = json.load(file)

# ## Eval Loop 
for i in range(len(modified_physics_questions)):
    question_id = modified_physics_questions[i]['question_id']
    groud_truth = modified_physics_questions[i]['modified_question_solution']
    gpt_5_answer = gpt_5_answers[i]['answer']
    anthropic_answer = anthropic_answers[i]['answer']
    gpt5JudgePrompt = f"""
        You are an expert physics professor. 
        Compare the 'Ground Truth Answer' with the 'Model Generated Answer' 
        for the same physics question.
        Determine if the model's answer is substantially similar 
        or correct compared to the ground truth.
        Your response must be a single integer: 1 if they are similar/correct, 
        and 0 if they are not.

        Ground Truth Answer:
        "{groud_truth}"

        Model Generated Answer:
        "{gpt_5_answer}"

        Verdict (1 for similar, 0 for not):
    """
    anthropicJudgePrompt = f"""
        You are an expert physics professor. 
        Compare the 'Ground Truth Answer' with the 'Model Generated Answer' 
        for the same physics question.
        Determine if the model's answer is substantially similar 
        or correct compared to the ground truth.
        Your response must be a single integer: 1 if they are similar/correct, 
        and 0 if they are not.

        Ground Truth Answer:
        "{groud_truth}"

        Model Generated Answer:
        "{anthropic_answer}"

        Verdict (1 for similar, 0 for not):
    """
    
    print(f"Judging Question ID: {question_id}...")
    gpt5_response = judge_model.generate_content(gpt5JudgePrompt)
    anthropic_response = judge_model.generate_content(anthropicJudgePrompt)
    try:
        gpt5Verdict = int(gpt5_response.text.strip())
    except ValueError:
        print(f"Warning: Judge returned a non-integer value for question {question_id} for GPT 5. Defaulting to 0.")
        gpt5Verdict = 0
    
    try:
        anthropicVerdict = int(anthropic_response.text.strip())
    except ValueError:
        print(f"Warning: Judge returned a non-integer value for question {question_id} for Anthropic. Defaulting to 0.")
        anthropicVerdict = 0
    
    judge_verdicts.append({
        "question_id": question_id,
        "gpt5Verdict": gpt5Verdict,
        "sonnet4Verdict":anthropicVerdict
    })


out_dir = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Outputs"
out_path = os.path.join(out_dir, f"Eval_modified_q_sonnet4_gpt5.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(judge_verdicts, f, ensure_ascii=False, indent=2)