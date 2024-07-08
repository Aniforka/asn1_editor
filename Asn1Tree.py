from Asn1Parser import Asn1Parser
from Asn1TreeElement import Asn1TreeElement

class Asn1Tree:
    def __init__(self) -> None:
        self.root = None
        self.count_of_elements = 0

    def import_from_file(self, file_path: str) -> None:
        with open(file_path, "rb") as f:
            data = f.read()

        offset = 0
        # offset - 1 - length_len if length_len else offset - 2
        cur_elem = None

        while offset < len(data):
            new_offset, displayed_offset, tag_type, length, value, decoded_value, __constructed = Asn1Parser.decode(data, offset)

            new_element = Asn1TreeElement(
                cur_elem,
                decoded_value,
                value, tag_type,
                length,
                displayed_offset,
                self.count_of_elements
            )

            
            if cur_elem is not None:
                cur_elem.add_child(new_element)

            self.count_of_elements += 1
            cur_elem = new_element

            if self.root is None:
                self.root = new_element

            if not __constructed:
                while self.__is_parent_level_traversal_needed(cur_elem):
                    cur_elem = cur_elem.get_parrent()
                if cur_elem.get_parrent() is not None:
                    cur_elem = cur_elem.get_parrent()

            offset = new_offset

            
    def __is_parent_level_traversal_needed(self, cur_node: Asn1TreeElement) -> bool:
        parrent = cur_node.get_parrent()

        if parrent is None:
            return False

        return (parrent.get_length() + parrent.get_offset() <= cur_node.get_length() + cur_node.get_offset())


    def export_from_file(self, file_path: str) -> None:
        pass

    def remove_node(self, uid: int) -> None:
        pass

    def add_node(element: Asn1TreeElement, uid: int) -> None:
        pass

    def get_root(self) -> Asn1TreeElement | None:
        return self.root
    
    def __repr__(self) -> str:
        answer = ""

        nodes_to_visit = [(self.root, 0)]

        while nodes_to_visit:
            current_node, level = nodes_to_visit.pop(0)
    
            answer += "  " * level
            answer += f"({current_node.get_offset()}, {current_node.get_length()}) {current_node.get_tag_type()}"
            value = current_node.get_decode_value()

            if value is not None:
                answer += f": {value}"

            answer += '\n'

            for child in reversed(current_node.childs):
                nodes_to_visit.insert(0, (child, level + 1))

        return answer
