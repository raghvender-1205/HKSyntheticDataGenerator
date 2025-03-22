from enum import Enum

class DatasetType(str, Enum):
    QA = "qa"
    INSTRUCTION = "instruction"
    CONVERSATION = "conversation"
    CLASSIFICATION = "classification"
    TEXT = "text"