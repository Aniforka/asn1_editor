class Asn1TreeElement:
    def __init__(
            self,
            parent=None,
            decode_value=None,
            encode_value=None, tag_type=None,
            length=None,
            offset=None,
            uid=None)-> None:
        
        self.parent = parent
        self.childs = None
        self.decode_value = decode_value
        self.encode_value = encode_value
        self.tag_type = tag_type
        self. length = length
        self.offset = offset
        self.uid = uid

    def add_child(self, element) -> None:
        if self.childs is None:
            self.childs = list()

        self.child.append(element)