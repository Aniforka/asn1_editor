class Asn1TreeElement:
    def __init__(
            self,
            decode_value=None,
            encode_value=None, tag_type=None,
            length=None,
            offset=None,
            uid=None)-> None:
        self.childs = None
        self.decode_value = decode_value
        self.encode_value = encode_value
        self.tag_type = tag_type
        self. length = length
        self.offset = offset
        self.uid = uid