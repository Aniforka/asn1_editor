from Asn1Parser import Asn1Parser
from Asn1TreeElement import Asn1TreeElement

class Asn1Tree:
    def __init__(self) -> None:
        root = list()
        count_of_elements = 0

    def import_from_file(self, file_path: str) -> None:
        pass

    def export_from_file(self, file_path: str) -> None:
        pass

    def remove_node(self, uid: int) -> None:
        pass

    def add_node(element: Asn1TreeElement, uid: int) -> None:
        pass

    def get_root(self) -> Asn1TreeElement | None:
        return self.root
