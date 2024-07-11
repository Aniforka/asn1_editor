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
            new_offset, displayed_offset, tag_type, length, value, decoded_value, __constructed, encode_info = Asn1Parser.decode(data, offset)

            new_element = Asn1TreeElement(
                cur_elem,
                decoded_value,
                value, tag_type,
                length,
                displayed_offset,
                self.count_of_elements,
                *encode_info
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


    def export_to_file(self, file_path: str) -> None:
        f_out = open(file_path, "wb")
        nodes_to_visit = [(self.root, 0)]

        while nodes_to_visit:
            current_node, level = nodes_to_visit.pop(0)

            # if current_node.get_tag_type() == "OBJECT IDENTIFIER":
            # print('aboba',current_node.get_offset(), current_node.get_encode_tag_number())

            constructed = True if current_node.get_childs() and current_node.get_tag_type() != "OCTET STRING" else False

            f_out.write(
                Asn1Parser.encode(
                    current_node.get_length(),
                    current_node.get_encode_tag_number(),
                    current_node.get_encode_class(),
                    current_node.get_decode_value(),
                    constructed
                )
            )

            for child in reversed(current_node.get_childs()):
                nodes_to_visit.insert(0, (child, level + 1))

        f_out.close()

    def remove_node(self, element: Asn1TreeElement) -> None:
        offset_changes = 0

    
        offset_changes = 1 + element.get_length() + Asn1Parser.get_length_len(element.get_length())
        print(offset_changes)

        nodes_to_visit = [(self.root, 0)]
        was_element = False

        while nodes_to_visit:
            current_node, level = nodes_to_visit.pop(0)

            if was_element:
                current_node.set_offset(current_node.get_offset() - offset_changes)
            else:
                new_length = current_node.get_length() - offset_changes
                offset = Asn1Parser.get_length_len(current_node.get_length()) - Asn1Parser.get_length_len(new_length)
                offset_changes += offset
                current_node.set_length(new_length)

            for child in reversed(current_node.get_childs()):
                if child.get_uid() == element.get_uid():
                    
                    current_node.get_childs().remove(element)
                    was_element = True
                else:
                    nodes_to_visit.insert(0, (child, level + 1))


    def add_node(element: Asn1TreeElement, uid: int) -> None:
        pass

    def get_root(self) -> Asn1TreeElement:
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

            for child in reversed(current_node.get_childs()):
                nodes_to_visit.insert(0, (child, level + 1))

        return answer
