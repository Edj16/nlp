from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

model_name = "facebook/opt-125m"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="cpu", low_cpu_mem_usage=True)

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

prompt = "Generate a simple partnership contract between Alice and Bob for one year."
output = generator(prompt, max_new_tokens=200)

print(output[0]['generated_text'])
