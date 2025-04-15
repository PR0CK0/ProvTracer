import time, random, csv, os, base64
from openai import OpenAI

api_key = "sk-proj-mSqGOS6drMEaRmBctboZT3BlbkFJ4NRuLnaqscGRMa8JSJaK" 
client = OpenAI(api_key=api_key)

model = "gpt-4o-mini"
num_runs_per_prompt = 25
screenshot_path = os.path.join(os.path.dirname(__file__), "screenshot.png")

def encode_image(image_path):
	with open(image_path, "rb") as img_file:
		return base64.b64encode(img_file.read()).decode("utf-8")

image_data = encode_image(screenshot_path)

def create_gpt_message(text, image):
	return [
		{
			"role": "user",
			"content": [
				{"type": "text", "text": text},
				{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image}", "detail": "auto"}}
			]
		}
	]

prompts = [
	"Describe this image.",
	"Describe this image of a user's screen.",
	"Describe the contents of the user's screen, focusing on text elements.",
	"Describe all visible elements in the image, including text, icons, and buttons.",
	"Describe this image as if explaining it to someone visually impaired, including layout and features.",
	"Analyze the image and list all visible application windows, icons, and prominent UI elements like buttons.",
	"Provide a detailed breakdown of the user’s screen, specifying the applications, menus, and any readable text.",
	"Describe this image in great detail, including any visible buttons, toolbars, status indicators, and background elements.",
	"Identify and explain the function of any visible software applications, toolbars, graphical elements, and user actions in the image.",
	"Analyze the image as if preparing a digital accessibility report, listing each visual element, its function, and how it interacts with other elements."
]

response_times = {prompt: [] for prompt in prompts}

for prompt in prompts:
	for i in range(num_runs_per_prompt):
		start_time = time.time()
		try:
			response = client.chat.completions.create(
				model=model,
				messages=create_gpt_message(prompt, image_data),
				max_tokens=200,
				temperature=0.7,
				n=1
			)
			end_time = time.time()
			elapsed_time = end_time - start_time
			response_times[prompt].append(elapsed_time)
			print(f"Run {i+1}/{num_runs_per_prompt} for prompt {prompts.index(prompt)+1}: {elapsed_time:.2f}s")
			time.sleep(random.uniform(1,7))
		except Exception as e:
			print(f"Error on run {i+1} for prompt {prompts.index(prompt)+1}: {e}")
			response_times[prompt].append(None)

csv_filename = os.path.join(os.path.dirname(__file__), "gpt4o_mini_response_times.csv")
with open(csv_filename, mode="w", newline="") as file:
	writer = csv.writer(file)
	writer.writerow(["Run"] + [f"Prompt {i+1}" for i in range(len(prompts))])
	for i in range(num_runs_per_prompt):
		writer.writerow([i+1] + [response_times[prompt][i] for prompt in prompts])

print(f"Benchmarking complete. Results saved in {csv_filename}.")
