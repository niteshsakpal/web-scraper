from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SummaryResponse:
    summary_text: str
    model_name: str
    prompt_version: str
    temperature: float
    token_usage: int


class SummarizationService(ABC):
    @abstractmethod
    def summarize(self, text: str) -> SummaryResponse:
        raise NotImplementedError


class DummySummarizationService(SummarizationService):
    def summarize(self, text: str) -> SummaryResponse:
        max_chars = 650
        snippet = text[:max_chars]
        summary = f"Executive summary:\n{snippet}"
        return SummaryResponse(
            summary_text=summary,
            model_name="dummy-llm-v1",
            prompt_version="v1.0.0",
            temperature=0.2,
            token_usage=max(1, len(snippet.split())),
        )
