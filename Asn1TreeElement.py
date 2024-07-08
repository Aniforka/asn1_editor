class Asn1TreeElement:
    def __init__(
            self,
            parent=None,
            decode_value=None,
            encode_value=None,
            tag_type=None,
            length=-1,
            offset=-1,
            uid=-1)-> None:
        
        self.parent = parent
        self.childs = list()
        self.decode_value = decode_value
        self.encode_value = encode_value
        self.tag_type = tag_type
        self.length = length
        self.offset = offset
        self.uid = uid

    def add_child(self, element) -> None:
        self.childs.append(element)

    def get_length(self) -> int:
        return self.length

    def get_offset(self) -> int:
        return self.offset

    def get_decode_value(self) -> str:
        return self.decode_value
    
    def get_encode_value(self):
        return self.encode_value
    
    def get_tag_type(self) -> str:
        return self.tag_type
    
    def get_uid(self) -> int:
        return self.uid

    def get_parrent(self):
        return self.parent
    
    def get_childs(self):
        return self.childs
