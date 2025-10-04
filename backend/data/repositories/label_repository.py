from typing import List, Optional
from data.datasource import DictionaryManager
from domain.entities.label import Label
from data.translators.label_translator import LabelTranslator


class LabelRepository:
    def __init__(self, db_path: str = "dictionaries.db"):
        self._manager = DictionaryManager(db_path)
        self.translator = LabelTranslator()

    def add(self, label: Label) -> bool:
        document = self.translator.to_document(label=label)
        return self._manager.insert_dictionary(document)

    def add_all(self, labels: List[Label]) -> bool:
        documents = [self.translator.to_document(model) for model in labels]
        return self._manager.insert_dictionaries(documents)

    def get_by_id(self, label_id: int) -> Optional[Label]:
        raw = self._manager.get_dictionary_by_id(label_id)
        if raw is None:
            return None
        return self.translator.from_document(raw)

    def get_all(self) -> List[Label]:
        raw_list = self._manager.get_all_dictionaries()
        return [
            self.translator.from_document(item)
            for item in raw_list
        ]

    def update(self, label: Label) -> bool:
        document = self.translator.to_document(label)
        return self._manager.update_dictionary(document)

    def delete(self, dict_id: int) -> bool:
        return self._manager.delete_dictionary(dict_id)

    def count(self) -> int:
        return self._manager.get_dictionaries_count()

    def clear(self) -> bool:
        return self._manager.clear_all_dictionaries()