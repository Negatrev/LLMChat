from abc import ABC, abstractmethod
from typing import Type

from tiktoken import Encoding, encoding_for_model
from transformers import LlamaTokenizer as _LlamaTokenizer

from app.utils.chat.llama_cpp import LlamaTokenizerAdapter

from app.utils.logger import api_logger
from app.shared import Shared


class BaseTokenizer(ABC):
    @abstractmethod
    def encode(self, message: str) -> list[int]:
        ...

    @abstractmethod
    def tokens_of(self, message: str) -> int:
        ...


class OpenAITokenizer(BaseTokenizer):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._tokenizer: Encoding | None = None

    def encode(self, message: str, /) -> list[int]:
        return self.tokenizer.encode(message)

    def tokens_of(self, message: str) -> int:
        return len(self.encode(message))

    @property
    def vocab_size(self) -> int:
        return self.tokenizer.n_vocab

    @property
    def tokenizer(self) -> Encoding:
        if self._tokenizer is None:
            print("Loading tokenizer: ", self.model_name)
            self._tokenizer = encoding_for_model(self.model_name)
        return self._tokenizer


class LlamaTokenizer(BaseTokenizer):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._tokenizer: Encoding | None = None

    def encode(self, message: str, /) -> list[int]:
        return self.tokenizer.encode(message)

    def tokens_of(self, message: str) -> int:
        return len(self.encode(message))

    @property
    def vocab_size(self) -> int:
        return self.tokenizer.n_vocab

    @property
    def tokenizer(self) -> Encoding:
        if self._tokenizer is None:
            split_str = self.model_name.split("/")

            if len(split_str) == 2:
                root_path = self.model_name
                subfolder = None
            elif len(split_str) > 2:
                root_path = "/".join(split_str[:2])
                subfolder = "/".join(split_str[2:])
            else:
                print(split_str)
                raise ValueError("Input string is not in the correct format")
            try:
                self._tokenizer = _LlamaTokenizer.from_pretrained(root_path, subfolder=subfolder)
            except Exception as e:
                api_logger.error(f"Error loading tokenizer: {self.model_name}", exc_info=True)
                raise e
            print("Tokenizer loaded:", self.model_name)
        return self._tokenizer


class LlamaTokenizerSlow(BaseTokenizer):
    def __init__(self, llama_cpp_model_name: str):
        self.llama_cpp_model_name = llama_cpp_model_name

    def encode(self, message: str, /) -> list[int]:
        from app.models.llms import LLMModels
        from app.models.llms import LlamaCppModel

        llama_cpp_model = LLMModels.find_model_by_name(self.llama_cpp_model_name)
        assert isinstance(llama_cpp_model, LlamaCppModel), type(llama_cpp_model)
        return (
            Shared()
            .process_pool_executor.submit(
                self.tokenizer.encode,
                text=message,
                llama_cpp_model=llama_cpp_model,
            )
            .result()
        )

    def tokens_of(self, message: str) -> int:
        return len(self.encode(message))

    @property
    def tokenizer(self) -> Type[LlamaTokenizerAdapter]:
        return LlamaTokenizerAdapter
