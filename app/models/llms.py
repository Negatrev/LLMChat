from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from app.common.config import OPENAI_API_KEY

from app.models.llm_tokenizers import BaseTokenizer, LlamaTokenizer, OpenAITokenizer


@dataclass
class LLMModel:
    name: str  # model name
    max_total_tokens: int
    max_tokens_per_request: int
    token_margin: int
    tokenizer: BaseTokenizer


@dataclass
class LlamaCppModel(LLMModel):
    model_path: str  # The path to the Llama model file.
    lora_base: Optional[str] = None  # The path to the Llama LoRA base model.
    lora_path: Optional[str] = None  # The path to the Llama LoRA. If None, no LoRa is loaded.
    n_parts: int = (
        -1
    )  # Number of parts to split the model into. If -1, the number of parts is automatically determined.
    n_gpu_layers: int = 32  # Number of layers to keep on the GPU. If 0, all layers are kept on the GPU.
    seed: int = -1  # Seed. If -1, a random seed is used.
    f16_kv: bool = True  # Use half-precision for key/value cache.
    logits_all: bool = False  # Return logits for all tokens, not just the last token.
    vocab_only: bool = False  # Only load the vocabulary, no weights.
    use_mlock: bool = False  # Force system to keep model in RAM.
    n_batch: int = 512  # Number of tokens to process in parallel. Should be a number between 1 and n_ctx.
    last_n_tokens_size: int = 64  # The number of tokens to look back when applying the repeat_penalty.
    use_mmap: bool = True  # Whether to use memory mapping for the model.
    streaming: bool = True  # Whether to stream the results, token by token.
    cache: bool = True  # The size of the cache in bytes. Only used if cache is True.
    echo: bool = True  # Whether to echo the prompt.
    cache_size: Optional[int] = 2 << 30  # The size of the cache in bytes. Only used if cache is True.
    n_threads: Optional[
        int
    ] = None  # Number of threads to use. If None, the number of threads is automatically determined.
    suffix: Optional[str] = None  # A suffix to append to the generated text. If None, no suffix is appended.
    temperature: Optional[float] = 0.8  # The temperature to use for sampling.
    top_p: Optional[float] = 0.95  # The top-p value to use for sampling.
    logprobs: Optional[int] = None  # The number of logprobs to return. If None, no logprobs are returned.
    stop: Optional[list[str]] = field(
        default_factory=lambda: ["\u200b"]
    )  # A list of strings to stop generation when encountered.
    repeat_penalty: Optional[float] = 1.1  # The penalty to apply to repeated tokens.
    top_k: Optional[int] = 40  # The top-k value to use for sampling.
    description: Optional[str] = None  # A prefix to prepend to the generated text. If None, no prefix is prepended.

    def __post_init__(self):
        if self.description is not None:
            self.description_tokens = self.tokenizer.tokens_of(self.description)


@dataclass
class OpenAIModel(LLMModel):
    api_url: str = "https://api.openai.com/v1/chat/completions"
    api_key: str | None = field(repr=False, default=None)


class LLMModels(Enum):  # gpt models for openai api
    gpt_3_5_turbo = OpenAIModel(
        name="gpt-3.5-turbo",
        max_total_tokens=4096,
        max_tokens_per_request=2048,
        token_margin=8,
        tokenizer=OpenAITokenizer("gpt-3.5-turbo"),
        api_url="https://api.openai.com/v1/chat/completions",
        api_key=OPENAI_API_KEY,
    )
    gpt_3_5_turbo_proxy = OpenAIModel(
        name="gpt-3.5-turbo",
        max_total_tokens=4096,
        max_tokens_per_request=2048,
        token_margin=8,
        tokenizer=OpenAITokenizer("gpt-3.5-turbo"),
        api_url="https://whocars123-oai-proxy.hf.space/proxy/openai/v1/chat/completions",
        api_key="SOME_API_KEY",
    )

    gpt_4 = OpenAIModel(
        name="gpt-4",
        max_total_tokens=8192,
        max_tokens_per_request=4096,
        token_margin=8,
        tokenizer=OpenAITokenizer("gpt-4"),
        api_url="https://api.openai.com/v1/chat/completions",
        api_key=OPENAI_API_KEY,
    )

    gpt_4_proxy = OpenAIModel(
        name="gpt-4",
        max_total_tokens=8192,
        max_tokens_per_request=4096,
        token_margin=8,
        tokenizer=OpenAITokenizer("gpt-4"),
        api_url="https://whocars123-oai-proxy.hf.space/proxy/openai/v1/chat/completions",
        api_key="SOME_API_KEY",
    )

    vicuna = LlamaCppModel(
        name="wizard-vicuna-13B-ggml-q5-1",
        max_total_tokens=2048,  # context tokens (n_ctx)
        max_tokens_per_request=1024,  # The maximum number of tokens to generate.
        token_margin=8,
        tokenizer=LlamaTokenizer("junelee/wizard-vicuna-13b"),
        model_path="./llama_models/ggml/wizard-vicuna-13B.ggml.q5_1.bin",
        description="""The following is a friendly conversation between a {user} and an {ai}. The {ai} is talkative and provides lots of specific details from its context. If the {ai} does not know the answer to a question, it truthfully says it does not know:\n""",
    )
    vicunaunc = LlamaCppModel(
        name="Wizard-Vicuna-13B-Uncensored-GGML",
        max_total_tokens=2048,  # context tokens (n_ctx)
        max_tokens_per_request=1024,  # The maximum number of tokens to generate.
        token_margin=8,
        tokenizer=LlamaTokenizer("junelee/wizard-vicuna-13b"),
        model_path="./llama_models/ggml/ggml-model-q4_1.bin",
        description="""The following is a conversation between a {user} and an {ai}. The {ai} is talkative and provides lots of specific details from its context. If the {ai} does not know the answer to a question, it truthfully says it does not know:\n""",
    )
    gpt4x = LlamaCppModel(
        name="gpt4-x-vicuna-13B-GGML",
        max_total_tokens=2048,  # context tokens (n_ctx)
        max_tokens_per_request=1024,  # The maximum number of tokens to generate.
        token_margin=8,
        tokenizer=LlamaTokenizer("junelee/wizard-vicuna-13b"),
        model_path="./llama_models/ggml/gpt4-x-vicuna-13B.ggml.q4_0.bin",
        description="""The following is a conversation between a {user} and an {ai}. The {ai} is talkative and provides lots of specific details from its context. If the {ai} does not know the answer to a question, it truthfully says it does not know:\n""",
    )
    wizardlmunc = LlamaCppModel(
        name="WizardLM-13B-Uncensored-Q5_1-GGML",
        max_total_tokens=2048,  # context tokens (n_ctx)
        max_tokens_per_request=1024,  # The maximum number of tokens to generate.
        token_margin=8,
        tokenizer=LlamaTokenizer("junelee/wizard-vicuna-13b"),
        model_path="./llama_models/ggml/WizardML-Unc-13b-Q5_1.bin",
        description="""The following is a conversation between a {user} and an {ai}. The {ai} is talkative and provides lots of specific details from its context. If the {ai} does not know the answer to a question, it truthfully says it does not know:\n""",
    )
    wizardmega = LlamaCppModel(
        name="wizard-mega-13B-GGML",
        max_total_tokens=2048,  # context tokens (n_ctx)
        max_tokens_per_request=1024,  # The maximum number of tokens to generate.
        token_margin=8,
        tokenizer=LlamaTokenizer("junelee/wizard-vicuna-13b"),
        model_path="./llama_models/ggml/wizard-mega-13B.ggml.q4_0.bin",
        stop=field(default_factory=lambda: ["\u200b", "</s>"]),
        description="""The following is a conversation between a {user} and an {ai}. The {ai} is talkative and provides lots of specific details from its context. If the {ai} does not know the answer to a question, it truthfully says it does not know:\n""",
    )

    @classmethod
    def find_model_by_name(cls, name) -> LLMModel | None:
        for model in cls:
            if model.value.name == name:
                return model.value
        return None
