from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from multiprocessing import Manager
from multiprocessing.managers import SyncManager

import openai
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.summarize import load_summarize_chain, stuff_prompt
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import TokenTextSplitter

from app.common.config import OPENAI_API_KEY, ChatConfig, SingletonMetaClass, config
from app.common.constants import SummarizationTemplates


@dataclass
class Shared(metaclass=SingletonMetaClass):
    process_manager: SyncManager = field(default_factory=Manager)
    process_pool_executor: ProcessPoolExecutor = field(
        default_factory=ProcessPoolExecutor
    )
    openai_embeddings: OpenAIEmbeddings = field(init=False)
    openai_llm: ChatOpenAI = field(init=False)
    map_reduce_summarize_chain: MapReduceDocumentsChain = field(init=False)
    stuff_summarize_chain: StuffDocumentsChain = field(init=False)
    token_text_splitter: TokenTextSplitter = field(init=False)

    def __post_init__(self):
        self.openai_embeddings = OpenAIEmbeddings(
            client=openai.Embedding,
            openai_api_key=OPENAI_API_KEY,
        )
        self.openai_llm = ChatOpenAI(
            client=None,
            model_name=ChatConfig.summarization_openai_model,
            openai_api_key=OPENAI_API_KEY,
        )
        self.map_reduce_summarize_chain = load_summarize_chain(  # type: ignore
            self.openai_llm,
            chain_type="map_reduce",
            map_prompt=stuff_prompt.PROMPT,
            combine_prompt=SummarizationTemplates.TEXT__MARKUP.value,
            verbose=config.debug,
        )
        self.stuff_summarize_chain = load_summarize_chain(  # type: ignore
            self.openai_llm,
            chain_type="stuff",
            prompt=SummarizationTemplates.TEXT__MARKUP.value,
            verbose=config.debug,
        )
        self.token_text_splitter = TokenTextSplitter(
            encoding_name="cl100k_base",
            chunk_size=ChatConfig.summarization_token_limit,
            chunk_overlap=ChatConfig.summarization_token_overlap,
        )
