class Asn1TreeElement:
    def __init__(
            self,
            parent=None,
            decode_value=None,
            encode_value=None,
            tag_type=None,
            length=-1,
            offset=-1,
            uid=-1,
            encode_tag=None,
            encode_tag_number=None,
            encode_class=None,
            encode_offset=None)-> None:
        
        self.__parent = parent
        self.__childs = list()
        self.__decode_value = decode_value
        self.__encode_value = encode_value
        self.__tag_type = tag_type
        self.__length = length
        self.__offset = offset
        self.__uid = uid

        self.__encode_tag = encode_tag
        self.__encode_tag_number = encode_tag_number
        self.__encode_class = encode_class
        self.__encode_offset = encode_offset

    def add_child(self, element) -> None:
        self.__childs.append(element)

    def get_length(self) -> int:
        return self.__length

    def get_offset(self) -> int:
        return self.__offset

    def get_decode_value(self) -> str:
        return self.__decode_value
    
    def get_encode_value(self):
        return self.__encode_value
    
    def get_tag_type(self) -> str:
        return self.__tag_type
    
    def get_uid(self) -> int:
        return self.__uid

    def get_parrent(self):
        return self.__parent
    
    def get_childs(self):
        return self.__childs
    
    def get_encode_tag(self):
        return self.__encode_tag
    
    def get_encode_tag_number(self):
        return self.__encode_tag_number
    
    def get_encode_class(self):
        return self.__encode_class
