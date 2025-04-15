import time, csv, os, base64
from openai import OpenAI

api_key = 'sk-proj-mSqGOS6drMEaRmBctboZT3BlbkFJ4NRuLnaqscGRMa8JSJaK'
client = OpenAI(api_key=api_key)

models = ['gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini']
prompt_text = 'Describe the content of this image in detail.'
screenshot_path = os.path.join(os.path.dirname(__file__), 'screenshot.png')
response_times = {model: [] for model in models}
num_runs = 50

def encode_image(image_path):
	with open(image_path, 'rb') as img_file:
		return base64.b64encode(img_file.read()).decode('utf-8')

image_data = encode_image(screenshot_path)

def create_gpt_message(text, image):
	return [
		{
			'role': 'user',
			'content': [
				{'type': 'text', 'text': text},
				{'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{image}', 'detail': 'auto'}}
			]
		}
	]

for model in models:
	for i in range(num_runs):
		start_time = time.time()
		try:
			response = client.chat.completions.create(
				model=model,
				messages=create_gpt_message(prompt_text, image_data),
				max_tokens=100,
				temperature=0.7,
				n=1
			)
			end_time = time.time()
			elapsed_time = end_time - start_time
			response_times[model].append(elapsed_time)
			print(f'Run {i+1}/{num_runs} for {model}: {elapsed_time:.2f}s')
			#print(response.choices[0].message.content + '\n')
		except Exception as e:
			print(f'Error on {model} run {i+1}: {e}')
			response_times[model].append(None)

csv_filename = os.path.join(os.path.dirname(__file__), 'response_times.csv')
with open(csv_filename, mode='w', newline='') as file:
	writer = csv.writer(file)
	writer.writerow(['Run', 'GPT-4-Turbo', 'GPT-4o', 'GPT-4o-mini'])
	for i in range(num_runs):
		writer.writerow([i+1, response_times['gpt-4-turbo'][i], response_times['gpt-4o'][i], response_times['gpt-4o-mini'][i]])

print(f'Benchmarking complete. Results saved in {csv_filename}.')