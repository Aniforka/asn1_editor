class Asn1TreeElement:
    def __init__(
            self,
            parrent=None,
            decode_value=0,
            encode_value=0,
            tag_type=None,
            length=-1,
            offset=-1,
            uid=-1,
            primitive=False,
            encode_tag=None,
            encode_tag_number=None,
            encode_class=None,
            encode_offset=None)-> None:
        
        self.__parrent = parrent
        self.__childs = list()
        self.__decode_value = decode_value
        self.__encode_value = encode_value
        self.__tag_type = tag_type
        self.__length = length
        self.__offset = offset
        self.__uid = uid
        self.__is_primitive = primitive

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
        return self.__parrent
    
    def get_childs(self):
        return self.__childs
    
    def get_encode_tag(self):
        return self.__encode_tag
    
    def get_encode_tag_number(self):
        return self.__encode_tag_number
    
    def get_encode_class(self):
        return self.__encode_class

    def set_offset(self, new_offset):
        self.__offset = new_offset

    def set_length(self, new_length):
        self.__length = new_length

    def set_value(self, new_value):
        self.__decode_value = new_value

    def set_encode_value(self, new_value):
        self.__encode_value = new_value

    def is_primitive(self):
        return self.__is_primitive