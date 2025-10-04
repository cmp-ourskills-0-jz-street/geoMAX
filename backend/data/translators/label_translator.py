from domain.entities.label import Label

class LabelTranslator:
    def to_document(self, label: Label) -> dict:
        return label.model_dump()
    
    def from_document(self, document: dict) -> Label:
        return Label(**document)