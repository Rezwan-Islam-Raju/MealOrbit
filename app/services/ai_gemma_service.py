import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class GemmaService:

    MODEL_PATH = ".AIModel/gemma"

    def __init__(self):

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.MODEL_PATH
        )

        # Load Gemma model
        self.model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=self.MODEL_PATH,
            dtype=torch.float32
        )

        # CPU
        self.model = self.model.to("cpu")

        # Inference mode
        self.model.eval()

    def generate_response(self, prompt: str) :

        message = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Convert prompt to model input
        input_token = self.tokenizer.apply_chat_template(
            message,
            tokenize=True,
            add_special_tokens=True,
            return_dict=True,
            return_tensors="pt"
        )

        # CPU
        input_token = {
            key: value.to("cpu")
            for key, value in input_token.items()
        }

        # Generate response
        with torch.no_grad():

            output_token = self.model.generate(
                **input_token,
                max_new_tokens=20
            )

        # Only decode newly generated tokens
        input_length = input_token["input_ids"].shape[-1]

        result = self.tokenizer.decode(
            output_token[0][input_length:],
            skip_special_tokens=True
        )

        return result


# Create service instance
gemma_service = GemmaService()