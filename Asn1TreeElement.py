class Asn1TreeElement:
    def __init__(
            self,
            parent=None,
            decode_value=None,
            encode_value=None, tag_type=None,
            length=-1,
            offset=-1,
            uid=-1)-> None:
        
        self.parent = parent
        self.childs = None
        self.decode_value = decode_value
        self.encode_value = encode_value
        self.tag_type = tag_type
        self.length = length
        self.offset = offset
        self.uid = uid

    def add_child(self, element) -> None:
        if self.childs is None:
            self.childs = list()

        self.child.append(element)

    def get_parrent(self):
        return self.parent

    def get_length(self) -> int:
        return self.length

    def get_offset(self) -> int:
        return self.offset