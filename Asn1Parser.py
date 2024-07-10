from asn1crypto import core

class Asn1Parser:
    types_dict = {
        1: "BOOLEAN",
        2: "INTEGER",
        3: "BIT STRING",
        4: "OCTET STRING",
        5: "NULL",
        6: "OBJECT IDENTIFIER",
        7: "ObjectDescriptor",
        8: "INSTANCE OF",
        9: "REAL",
        10: "ENUMERATED",
        11: "EMBEDDED PDV",
        12: "UTF8String",
        13: "RelativeOID",
        14: "TIME",
        15: "reserved",
        16: "SEQUENCE",
        17: "SET",
        18: "NumericString",
        19: "PrintableString",
        20: "T61String",
        21: "VideotexString",
        22: "IA5String",
        23: "UTCTime",
        24: "GeneralizedTime",
        25: "GraphicString",
        26: "VisibleString",
        27: "GeneralString",
        28: "UniversalString",
        29: "CHARACTER STRING",
        30: "BMPString"
    }

    @staticmethod
    def decode(data: bytes, offset: int) -> tuple:
        value = None
        decoded_value = None

        # Читаем тег
        tag = data[offset]
        offset += 1

        # Определяем тип класса и constructed/primitive
        class_ = tag & 0xC0
        constructed = tag & 0x20

        # Читаем номер тега
        tag_number = tag & 0x1F
        if tag_number == 0x1F:
            tag_number = 0
            while True:
                byte = data[offset]
                offset += 1
                tag_number = (tag_number << 7) | (byte & 0x7F)
                if not byte & 0x80:
                    break

        # Читаем длину значения
        length = data[offset]
        offset += 1
        length_len = 0
        if length & 0x80:
            length_len = length & 0x7F
            length = 0
            for _ in range(length_len):
                length = (length << 8) | data[offset]
                offset += 1

        # Определяем тип данных по тегу
        tag_class = ["Universal", "Application", "Context-specific", "Private"][
            class_ >> 6
        ]
        tag_type = Asn1Parser.__get_tag_type(tag_class, tag_number)
        # print(offset, tag_type, f"({tag_number})", length, data[offset : offset + length].hex().upper())

        displayed_offset = offset - 1 - length_len if length_len else offset - 2
        # print(Asn1Parser.is_valid_asn1(data[offset:offset + length]))
        # костыль
        if tag_type == "OCTET STRING" and Asn1Parser.is_valid_asn1(data[offset:offset + length]):
            try: 
                _, _, tmp_tag_type, _, _, _, _ = Asn1Parser.decode(data, offset)
            except: pass
            else:
                if not "Private" in tmp_tag_type:
                    constructed = True
                    return (offset, displayed_offset, tag_type, length, value, decoded_value, constructed)
        # костыль



        # Обработка значения
        if not constructed:
            # Декодируем значение для primitive типов
            value = data[offset : offset + length]

            decoded_value = Asn1Parser.__decode_primitive_value(tag_type, value, length)

            offset += length

        return (offset, displayed_offset, tag_type, length, value, decoded_value, constructed)


    @staticmethod
    def encode(value, type, length):
        pass

    def is_valid_asn1(data: bytes) -> bool:
        """
        Рекурсивно проверяет, является ли входная строка байтов валидной ASN.1 структурой.

        Args:
            data: Строка байтов для проверки.

        Returns:
            True, если строка байтов является валидной ASN.1 структурой, False в противном случае.
        """

        def _validate_element(offset: int) -> int:
            """
            Вспомогательная функция для рекурсивной проверки элемента ASN.1.

            Args:
                offset: Смещение текущего элемента в строке байтов.

            Returns:
                Смещение следующего элемента в строке байтов, 
                или -1, если обнаружена ошибка.
            """
            if offset >= len(data):
                return -1

            tag = data[offset]
            length = data[offset + 1]
            offset += 2

            if length & 0x80:
                # Длина закодирована с продолжением
                length_bytes = length & 0x7F
                if offset + length_bytes > len(data):
                    return -1
                length = 0
                for i in range(offset, offset + length_bytes):
                    length = (length << 8) | data[i]
                offset += length_bytes

            if offset + length > len(data):
                return -1

            # Рекурсивная проверка вложенных элементов (кроме примитивных типов)
            if tag & 0x20:  # Проверка бита Constructed
                inner_offset = offset
                while inner_offset < offset + length:
                    inner_offset = _validate_element(inner_offset)
                    if inner_offset == -1:
                        return -1

            return offset + length

        return _validate_element(0) == len(data)

    # @staticmethod
    # def is_asn1(value: bytes) -> bool:
    #     """
    #     Проверяет, является ли входная строка байтов ASN.1.

    #     Args:
    #         data: Строка байтов для проверки.

    #     Returns:
    #         True, если строка байтов является ASN.1, False в противном случае.
    #     """
    
    #     print(value[:20].hex().upper())
    #     if len(value) < 2:
    #         return False

    #     tag = value[0] & 0x1F  # Извлечение тега

    #     # Проверка на допустимый тег
    #     if tag == 0x1F:
    #         return False  # Зарезервированный тег

    #     # Проверка длины
    #     length = value[1]

    #     if length & 0x80:
    #         # Длина кодируется с продолжением
    #         length_bytes = length & 0x7F

    #         if len(value) < 2 + length_bytes:
    #             return False

    #         length = 0

    #         for i in range(2, 2 + length_bytes):
    #             length = (length << 8) | value[i]

    #     if len(value) < 2 + length:
    #         return False

    #     return True

    # @staticmethod
    # def __is_asn1type(value, offset):
    #     tag = value[offset]
    #     offset += 1

    #     # Проверка допустимости класса и метода
    #     class_number = (tag >> 6) & 0x03
    #     method_number = (tag >> 5) & 0x01

    #     # Проверка на допустимые комбинации класса и метода
    #     if class_number == 0:  # Universal class
    #         if method_number == 1 and tag & 0x1F == 0:
    #             # Constructed, tag 0 не допустим для universal class
    #             return False
    #     elif class_number == 2:  # Context-specific class
    #         if method_number == 0:
    #             # Primitive method не допустим для context-specific class с tag 0
    #             if tag & 0x1F == 0:
    #                 return False
    #     else:  # Application and private classes
    #         # Не делаем дополнительных проверок
    #         pass 

    #     tag_number = tag & 0x1F

    #     if tag_number == 0x1F:
    #         tag_number = 0
    #         while True:
    #             byte = value[offset]
    #             offset += 1
    #             tag_number = (tag_number << 7) | (byte & 0x7F)
    #             if not byte & 0x80:
    #                 break

    #     print("Tag", tag_number)
    #     if Asn1Parser.types_dict.get(tag_number, None) is None:
    #         return False
        
    #     return True

    @staticmethod
    def __decode_primitive_value(tag_type: str, value, length: int):
        """Декодирует значение примитивного типа ASN.1."""
        if tag_type == "INTEGER":
            return hex(int.from_bytes(value, byteorder="big", signed=True))[2:].upper()
        if tag_type == "OCTET STRING":
            return value.hex().upper()
        if tag_type == "OBJECT IDENTIFIER":
            oid_bytes = bytearray()
            oid_bytes.append(0x06)  # Тег OBJECT IDENTIFIER
            oid_bytes.append(length)  # Длина значения OID
            oid_bytes.extend(value) # Само значение OID
            try:
                return core.ObjectIdentifier.load(bytes(oid_bytes)).dotted
            except ValueError:
                return f"Invalid OID: {value.hex()}" 
        if tag_type in ("UTF8String", "PrintableString", "IA5String", "VisibleString"):
            return value.decode("utf-8", errors="replace")
        if tag_type == "UTCTime":
            try:
                return value.decode("ascii") 
            except ValueError:
                return f"Invalid UTCTime: {value.hex()}"
        if tag_type == "GeneralizedTime":
            try:
                # return core.GeneralizedTime.load(value).strftime("%Y-%m-%d %H:%M:%S")
                return value.decode("ascii") 
            except ValueError:
                return f"Invalid GeneralizedTime: {value.hex()}"
        return value.hex().upper()  # По умолчанию возвращаем шестнадцатеричное представление

    @staticmethod
    def __get_tag_type(tag_class: str, tag_number: int) -> str:
        """Возвращает строковое представление типа тега."""
        if tag_class == "Universal":
            return Asn1Parser.types_dict.get(tag_number, f"Unknown ({tag_number})")
        elif tag_class in ("Application", "Context-specific", "Private"):
            # Для этих классов нет предопределенных типов,
            # поэтому возвращаем просто номер тега
            return f"{tag_class} ({tag_number})"
        else:
            return f"Unknown Class ({tag_class}), Tag ({tag_number})"
