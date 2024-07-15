from Asn1Parser import Asn1Parser
from Asn1TreeElement import Asn1TreeElement

class Asn1Tree:
    def __init__(self) -> None:
        self.root = None
        self.next_uid = 0

    def import_from_file(self, file_path: str) -> None:
        with open(file_path, "rb") as f:
            data = f.read()

        # try:
        #     data = base64.b64decode(data)
        # except Exception as exp:
        #     pass

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


    def insert_node_before(self, cur_node: Asn1TreeElement, new_node: str) -> None:
        new_node_bytes = bytes.fromhex(new_node)

        offset = 0
        # offset - 1 - length_len if length_len else offset - 2
        cur_elem = cur_node.get_parrent()
        childs = cur_elem.get_childs()
        index = childs.index(cur_node)
        first_new_elem = None

        if index:
            last_element = childs[index - 1]
        else:
            last_element = cur_elem

        new_global_offset = cur_node.get_offset()
        # print(cur_node.get_length(), cur_node.get_offset())

        while offset < len(new_node_bytes):
            new_offset, displayed_offset, tag_type, length, value, decoded_value, __constructed, encode_info = Asn1Parser.decode(new_node_bytes, offset)
            is_primitive = True if value is not None or tag_type == "OCTET STRING" else False

            new_element = Asn1TreeElement(
                cur_elem,
                decoded_value,
                value, tag_type,
                length,
                new_global_offset + displayed_offset,
                self.next_uid,
                is_primitive,
                *encode_info
            )

            if first_new_elem is None:
                first_new_elem = new_element
                # print(first_new_elem.get_length(), first_new_elem.get_offset())

            if index is not None:
                childs.insert(index, new_element)
                index = None
                childs = None
            elif cur_elem is not None:
                cur_elem.add_child(new_element)

            self.next_uid += 1
            cur_elem = new_element

            if not __constructed:
                while self.__is_parent_level_traversal_needed(cur_elem):
                    cur_elem = cur_elem.get_parrent()
                if cur_elem.get_parrent() is not None:
                    cur_elem = cur_elem.get_parrent()

            offset = new_offset

        was_elems = list()


        offset_changes = len(new_node_bytes)
        additional_offset = 0
        # print(first_new_elem.get_uid())

        was_element = False
        nodes_to_visit = [self.root]
        visited_nodes = set()

        while nodes_to_visit:
            current_node = nodes_to_visit.pop(0)

            if current_node.get_uid() == first_new_elem.get_uid():
                was_element = True

                # tmp_nodes = [first_new_elem]

                # while tmp_nodes:
                #     tmp_current_node = tmp_nodes.pop(0)
                #     tmp_current_node.set_offset(tmp_current_node.get_offset() + additional_offset)
                #     for child in reversed(tmp_current_node.get_childs()):
                #         tmp_nodes.insert(0, child)

                continue
            # print(current_node.get_uid(), was_element)
            if self.__is_grand_parrent(current_node, first_new_elem.get_uid()): # Элементы выше и включают в себя "наш" элемент
                additional_offset += self.check_length_len_parrents(current_node, offset_changes, visited_nodes)
            elif was_element: # элементы ниже "нашего" элемента
                if current_node.get_uid() in visited_nodes:
                    current_node.set_offset(current_node.get_offset() + offset_changes)
                else:
                    current_node.set_offset(current_node.get_offset() + offset_changes + additional_offset)

                # print(current_node.get_tag_type())
            else:  # элементы выше и НЕ включают в себя "наш" элемент
                # current_node.set_offset(current_node.get_offset() + additional_offset)
                pass

            for child in reversed(current_node.get_childs()):
                nodes_to_visit.insert(0, child)


    def check_length_len_parrents(self, cur_node: Asn1TreeElement, offset_len: Asn1TreeElement, visited_nodes: set) -> int:
        if cur_node is None: return 0

        additional_offset = 0
        new_length = cur_node.get_length() + offset_len
        offset = Asn1Parser.get_length_len(new_length) - Asn1Parser.get_length_len(cur_node.get_length())
        cur_node.set_length(new_length)

        if offset:
            self.add_childs_offset(cur_node, offset, visited_nodes)

        # for child in cur_node.get_childs():
        #     child.set_offset(child.get_offset() + offset)

        # cur_node.set_offset(cur_node.get_offset() + offset)
        additional_offset += offset

        parrent = cur_node.get_parrent()

        while parrent is not None:
            additional_offset += self.check_length_len_parrents(parrent, offset, visited_nodes)
            parrent = parrent.get_parrent()
            

        return additional_offset
    
    def add_childs_offset(self, cur_node: Asn1TreeElement, change_offset: Asn1TreeElement, visited_nodes: set) -> None:
        for child in cur_node.get_childs():
            visited_nodes.add(child.get_uid())
            child.set_offset(child.get_offset() + change_offset)
            self.add_childs_offset(child, change_offset, visited_nodes)


    def insert_node_after(self, cur_node: Asn1TreeElement, new_node: str) -> None:
        new_node_bytes = bytes.fromhex(new_node)

        offset = 0
        # offset - 1 - length_len if length_len else offset - 2
        cur_elem = cur_node.get_parrent()
        childs = cur_elem.get_childs()
        index = childs.index(cur_node)
        first_new_elem = None

        if index + 1 < len(childs):
            new_global_offset = childs[index + 1].get_offset()
        else:
            new_global_offset = cur_node.get_offset() + len(self.get_full_encoded_item(cur_node))
        # print(cur_node.get_length(), cur_node.get_offset())

        while offset < len(new_node_bytes):
            new_offset, displayed_offset, tag_type, length, value, decoded_value, __constructed, encode_info = Asn1Parser.decode(new_node_bytes, offset)
            is_primitive = True if value is not None or tag_type == "OCTET STRING" else False

            new_element = Asn1TreeElement(
                cur_elem,
                decoded_value,
                value, tag_type,
                length,
                new_global_offset + displayed_offset,
                self.next_uid,
                is_primitive,
                *encode_info
            )

            if first_new_elem is None:
                first_new_elem = new_element
                # print(first_new_elem.get_length(), first_new_elem.get_offset())

            if index is not None:
                childs.insert(index + 1, new_element)
                index = None
                childs = None
            elif cur_elem is not None:
                cur_elem.add_child(new_element)

            self.next_uid += 1
            cur_elem = new_element

            if not __constructed:
                while self.__is_parent_level_traversal_needed(cur_elem):
                    cur_elem = cur_elem.get_parrent()
                if cur_elem.get_parrent() is not None:
                    cur_elem = cur_elem.get_parrent()

            offset = new_offset

        offset_changes = len(new_node_bytes)
        additional_offset = 0
        # print(first_new_elem.get_uid())

        was_element = False
        nodes_to_visit = [self.root]

        while nodes_to_visit:
            current_node = nodes_to_visit.pop(0)

            if current_node.get_uid() == first_new_elem.get_uid():
                was_element = True
                continue
            # print(current_node.get_uid(), was_element)
            if self.__is_grand_parrent(current_node, new_element.get_uid()): # Элементы выше и включают в себя "наш" элемент
                new_length = current_node.get_length() + offset_changes
                offset = Asn1Parser.get_length_len(current_node.get_length()) - Asn1Parser.get_length_len(new_length)
                additional_offset += offset
                current_node.set_length(new_length)
            elif was_element: # элементы ниже "нашего" элемента
                current_node.set_offset(current_node.get_offset() + offset_changes + additional_offset)
                # print(current_node.get_tag_type())
            else:  # элементы выше и НЕ включают в себя "наш" элемент
                current_node.set_offset(current_node.get_offset() + additional_offset)

            for child in reversed(current_node.get_childs()):
                nodes_to_visit.insert(0, child)

            
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
            # print(current_node.get_tag_type())

            for child in reversed(current_node.get_childs()):
                nodes_to_visit.insert(0, (child, level + 1))

        f_out.close()


    def export_node_to_file(self, file_path: str, element: Asn1TreeElement) -> None:
        f_out = open(file_path, "wb")
        nodes_to_visit = [(element, 0)]

        while nodes_to_visit:
            current_node, level = nodes_to_visit.pop(0)

            # if current_node.get_tag_type() == "OBJECT IDENTIFIER":
            # print('aboba',current_node.get_offset(), current_node.get_encode_tag_number())

            constructed = True if not current_node.is_primitive() and current_node.get_tag_type() != "OCTET STRING" else False

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


    def get_full_encoded_item(self, element: Asn1TreeElement) -> bytes:
        nodes_to_visit = [element]
        answer = bytes()

        while nodes_to_visit:
            current_node = nodes_to_visit.pop(0)

            constructed = True if not current_node.is_primitive() and current_node.get_tag_type() != "OCTET STRING" else False

            answer += Asn1Parser.encode(
                current_node.get_length(),
                current_node.get_encode_tag_number(),
                current_node.get_encode_class(),
                current_node.get_decode_value(),
                constructed
            )

            for child in reversed(current_node.get_childs()):
                nodes_to_visit.insert(0, child)

        return answer


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
            new_value = new_value.replace(" ", "")
            new_encode_value = bytes.fromhex(new_value)
            new_value = Asn1Parser.decode_primitive_value(element.get_tag_type(), new_encode_value, len(new_encode_value))
        else:
            new_encode_value = Asn1Parser.encode_value(new_value, element.get_tag_type())
        # print(new_value, new_encode_value)
        element.set_value(new_value)
        element.set_length(len(new_encode_value))
        element.set_encode_value(new_encode_value)

        offset_changes = element.get_length() - old_length +\
            Asn1Parser.get_length_len(element.get_length()) - Asn1Parser.get_length_len(old_length)

        additional_offset = 0

        was_element = False
        nodes_to_visit = [self.root]

        while nodes_to_visit:
            current_node = nodes_to_visit.pop(0)

            if current_node.get_uid() == element.get_uid():
                was_element = True
                continue

            if self.__is_grand_parrent(current_node, element.get_uid()): # Элементы выше и включают в себя "наш" элемент
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
