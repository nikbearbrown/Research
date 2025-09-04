# # GPT 5 answering code
# model_name = "gpt-5"
# answers = []
# for item in physics_data:
#     qid = item["question_id"]
#     qtext = item["question"]
#     img = item.get("image_description") or ""

#     prompt = (
#         "Solve step-by-step, be concise but correct.\n\n"
#         f"Question: {qtext}\n"
#         + (f"\nContext from image: {img}\n" if img else "")
#     )

#     print(f"Processing Question ID: {qid}...")
#     resp = client.responses.create(
#         model=model_name,
#         reasoning={"effort": "low"},
#         text={"verbosity": "low"},
#         input=prompt,
#     )
#     answer_text = resp.output_text

#     answers.append({
#         "question_id": qid,
#         f"{model_name}_answer": answer_text
#     })

# # --- write output ---
# out_dir = "/Users/akshaysyal/Medhavi_LLM_Eval/Research/Evaluating_LLM_Performance_on_Physics_Problems/Outputs"
# out_path = os.path.join(out_dir, f"{model_name}_answers_low_reasoning_low_verbosity.json")
# with open(out_path, "w", encoding="utf-8") as f:
#     json.dump(answers, f, ensure_ascii=False, indent=2)