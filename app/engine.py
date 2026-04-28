import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class InferenceEngine:
    def __init__(self, model_id="microsoft/Phi-3-mini-4k-instruct"):
        self.model_id = model_id
        self.generator = None

    def load_model(self):
        """Loads the model into memory. In Azure, this happens at container startup."""
        print(f"Loading model: {self.model_id}...")
        
        # Use CPU if GPU is not available (common in Free Tiers)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model = AutoModelForCausalLM.from_pretrained(
            self.model_id, 
            device_map=device, 
            torch_dtype="auto", 
            trust_remote_code=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        
        self.generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
        print("Model loaded successfully.")

    def generate_text(self, prompt: str, max_length: int = 200):
        messages = [{"role": "user", "content": prompt}]
        output = self.generator(messages, max_new_tokens=max_length, return_full_text=False)
        return output[0]['generated_text']

# Singleton instance
engine = InferenceEngine()