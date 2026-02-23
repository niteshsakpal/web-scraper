from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TranslationResponse:
    translated_text: str
    engine: str


class TranslationService(ABC):
    @abstractmethod
    def translate(self, text: str, source_language: str, target_language: str = "en") -> TranslationResponse:
        raise NotImplementedError


class DummyTranslationService(TranslationService):
    def translate(self, text: str, source_language: str, target_language: str = "en") -> TranslationResponse:
        if source_language.lower().startswith("en"):
            return TranslationResponse(translated_text=text, engine="dummy-noop")
        return TranslationResponse(
            translated_text=f"[Translated {source_language}->{target_language}]\n{text}",
            engine="dummy-prefix",
        )
