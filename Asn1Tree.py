from Asn1Parser import Asn1Parser
from Asn1TreeElement import Asn1TreeElement

class Asn1Tree:
    def __init__(self) -> None:
        self.root = None
        self.next_uid = 0

    def import_from_file(self, file_path: str) -> None:
        with open(file_path, "rb") as f:
            data = f.read()

        offset = 0
        # offset - 1 - length_len if length_len else offset - 2
        cur_elem = None

        while offset < len(data):
            new_offset, displayed_offset, tag_type, length, value, decoded_value, __constructed, encode_info = Asn1Parser.decode(data, offset)
            is_primitive = True if value is not None or tag_type == "OCTET STRING" else False

            new_element = Asn1TreeElement(
                cur_elem,
                decoded_value,
                value, tag_type,
                length,
                displayed_offset,
                self.next_uid,
                is_primitive,
                *encode_info
            )

            
            if cur_elem is not None:
                cur_elem.add_child(new_element)

            self.next_uid += 1
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
        if (element.get_uid() == self.root.get_uid()):
            del self.root
            self.root = None
            return

        offset_changes = 0
    
        offset_changes = 1 + element.get_length() + Asn1Parser.get_length_len(element.get_length())
        # print(offset_changes)
        additional_offset = 0

        was_element = False
        nodes_to_visit = [self.root]

        while nodes_to_visit:
            current_node = nodes_to_visit.pop(0)

            if current_node.get_uid() == element.get_uid():
                was_element = True
                current_node.get_parrent().get_childs().remove(element)
                continue

            if self.__is_grand_parrent(current_node, element.get_uid()): # Элементы выше и включают в себя "наш" элемент
                new_length = current_node.get_length() - offset_changes
                offset = Asn1Parser.get_length_len(current_node.get_length()) - Asn1Parser.get_length_len(new_length)
                additional_offset += abs(offset)
                current_node.set_length(new_length)
            elif was_element: # элементы ниже "нашего" элемента
                current_node.set_offset(current_node.get_offset() - offset_changes - additional_offset)
            else:  # элементы выше и НЕ включают в себя "наш" элемент
                current_node.set_offset(current_node.get_offset() - additional_offset)

            for child in reversed(current_node.get_childs()):
                nodes_to_visit.insert(0, child)

    def __is_grand_parrent(self, current_node: Asn1TreeElement, uid: int):
        nodes_to_visit = [current_node]

        while nodes_to_visit:
            current_node = nodes_to_visit.pop(0)

            if current_node.get_uid() == uid:
                return True

            for child in reversed(current_node.get_childs()):
                nodes_to_visit.insert(0, child)

        return False

    def add_node(self, parrent: Asn1TreeElement, tag: str) -> None:
        new_tag = int(tag, 16)
        tag_number, class_, constucted, tag_type, tag_class = Asn1Parser.get_tag_info(new_tag)

        if parrent.get_childs():
            last_element = parrent.get_childs()[-1]
        else:
            last_element = parrent

        new_offset = 1 + last_element.get_length() + last_element.get_offset() + Asn1Parser.get_length_len(last_element.get_length())

        new_element = Asn1TreeElement(
            parrent=parrent,
            tag_type=tag_type,
            length=0,
            offset=new_offset,
            uid=self.next_uid,
            primitive= not bool(constucted),
            encode_tag=new_tag,
            encode_tag_number=tag_number,
            encode_class=class_,
            encode_offset=new_offset + len(tag)
        )
        self.next_uid += 1

        parrent.add_child(new_element)

        offset_changes = 2
        additional_offset = 0

        was_element = False
        nodes_to_visit = [self.root]

        while nodes_to_visit:
            current_node = nodes_to_visit.pop(0)

            if current_node.get_uid() == new_element.get_uid():
                was_element = True
                continue

            if self.__is_grand_parrent(current_node, new_element.get_uid()): # Элементы выше и включают в себя "наш" элемент
                new_length = current_node.get_length() + offset_changes
                offset = Asn1Parser.get_length_len(current_node.get_length()) - Asn1Parser.get_length_len(new_length)
                additional_offset += offset
                current_node.set_length(new_length)
            elif was_element: # элементы ниже "нашего" элемента
                current_node.set_offset(current_node.get_offset() + offset_changes + additional_offset)
            else:  # элементы выше и НЕ включают в себя "наш" элемент
                current_node.set_offset(current_node.get_offset() + additional_offset)

            for child in reversed(current_node.get_childs()):
                nodes_to_visit.insert(0, child)

    def edit_node(self, element: Asn1TreeElement, new_value: str, is_hex=False) -> None:
        old_length = element.get_length()

        if is_hex:
            new_encode_value = bytes.fromhex(new_value.replace(" ", ""))
            new_value = Asn1Parser.decode_primitive_value(element.get_tag_type(), new_encode_value, len(new_encode_value))
        else:
            new_encode_value = Asn1Parser.encode_value(new_value, element.get_tag_type())

        element.set_value(new_value)
        element.set_length(len(new_encode_value))
        element.set_encode_value(new_encode_value)

        offset_changes = element.get_length() - old_length +\
            Asn1Parser.get_length_len(element.get_length()) - Asn1Parser.get_length_len(old_length)

        was_element = False
        nodes_to_visit = [(self.root, 0)]

        while nodes_to_visit:
            current_node, level = nodes_to_visit.pop(0)

            if current_node.get_uid() == element.get_uid():
                was_element = True
                continue

            if was_element:
                current_node.set_offset(current_node.get_offset() + offset_changes)
            else:
                new_length = current_node.get_length() + offset_changes
                offset = Asn1Parser.get_length_len(current_node.get_length()) - Asn1Parser.get_length_len(new_length)
                offset_changes += offset
                current_node.set_length(new_length)

            for child in reversed(current_node.get_childs()):
                nodes_to_visit.insert(0, (child, level + 1))


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
