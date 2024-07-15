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
        tag_length = 1
        # Читаем номер тега
        tag_number = tag & 0x1F
        if tag_number == 0x1F:
            tag_number = 0
            while True:
                byte = data[offset]
                offset += 1
                tag_length += 1
                tag_number = (tag_number << 7) | (byte & 0x7F)
                if not byte & 0x80:
                    break

        # Читаем длину значения
        length = data[offset]
        offset += 1
        length_len = 1
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

        displayed_offset = offset - tag_length - length_len
        displayed_offset -= 1 if length_len > 1 else 0
        # print(Asn1Parser.is_valid_asn1(data[offset:offset + length]))
        # костыль
        encode_info = [tag, tag_number, class_ >> 6, offset]
        if tag_type == "OCTET STRING" and Asn1Parser.is_valid_asn1(data[offset:offset + length]):
            try: 
                _, _, tmp_tag_type, _, _, _, _, _ = Asn1Parser.decode(data, offset)
            except: pass
            else:
                if not "Private" in tmp_tag_type:
                    constructed = True
                    return (offset, displayed_offset, tag_type, length, value, decoded_value, constructed, encode_info)
        # костыль

        # Обработка значения
        if not constructed:
            # Декодируем значение для primitive типов
            value = data[offset : offset + length]

            decoded_value = Asn1Parser.decode_primitive_value(tag_type, value, length)

            offset += length

        return (offset, displayed_offset, tag_type, length, value, decoded_value, constructed, encode_info)


    @staticmethod
    def get_tag_info(tag: int):
        class_ = tag & 0xC0
        constructed = tag & 0x20

        # Читаем номер тега
        tag_number = tag & 0x1F
        tag_class = ["Universal", "Application", "Context-specific", "Private"][
            class_ >> 6
        ]
        tag_type = Asn1Parser.__get_tag_type(tag_class, tag_number)

        return (tag_number, class_ >> 6, constructed, tag_type, tag_class)


    @staticmethod
    def encode(length: int, tag_number: int, class_: int, value=None, constructed=False) -> bytes:
        """
        Кодирует тег ASN.1, длину и значение, если оно есть.

        Args:
            length: Длина значения.
            tag_number: Номер тега ASN.1.
            class_: Класс тега ASN.1 (0 - Universal, 1 - Application, 2 - Context-specific, 3 - Private).
            value: Значение для кодирования (может быть None).

        Returns:
            Строку байтов, представляющую закодированный тег, длину и значение (если есть).
        """
        # print(class_)
        if class_ < 0 or class_ > 3:
            raise ValueError("Неверный класс тега. Допустимые значения: 0, 1, 2, 3.")
        
        tag_class = ["Universal", "Application", "Context-specific", "Private"][class_]

        tag = (class_ << 6) | tag_number
        if constructed:
            tag |= 0x20  # Установить 6-й бит (constructed flag)

        encoded_data = bytearray()
        encoded_data.append(tag)
        encoded_data.extend(Asn1Parser.__encode_length(length))
        # print(Asn1Parser.__get_tag_type(tag_class, tag_number), tag_class, tag_number, class_)

        if value is not None and length:
            tag_type = Asn1Parser.__get_tag_type(tag_class, tag_number)
            # print(tag_type)
            encoded_value = Asn1Parser.encode_value(value, tag_type)
            encoded_data.extend(encoded_value)

        # print(encoded_data.hex().upper())
        return bytes(encoded_data)


    @staticmethod
    def encode_value(value, tag_type: str) -> bytes:
        """Кодирует значение в соответствии с типом тега."""
        if tag_type == "INTEGER":
            value = value.replace(" ", '')
            value = (len(value) % 2 != 0) * '0' + value
            return bytes.fromhex(value)
        elif tag_type == "OCTET STRING":
            value = value.replace(" ", '')
            return bytes.fromhex(value)
        elif tag_type == "OBJECT IDENTIFIER":
            # print(value)
            oid = core.ObjectIdentifier(value=value)
            return oid.dump()[2:]  # Убираем первые два байта (тег и длина)
        elif tag_type in ("UTF8String", "PrintableString", "IA5String", "VisibleString", "NumericString"):
            return value.encode("utf-8")
        elif tag_type == "UTCTime":
            return value.encode("ascii")
        elif tag_type == "GeneralizedTime":
            return value.encode("ascii")
        else:
            value = value.replace(" ", '')
            return bytes.fromhex(value)


    @staticmethod
    def __encode_length(length: int) -> bytes:
        """Кодирует длину значения."""
        if length < 128:
            return bytes([length])
        else:
            length_bytes = length.to_bytes((length.bit_length() + 7) // 8, byteorder="big")
            return bytes([0x80 | len(length_bytes)]) + length_bytes


    @staticmethod
    def get_length_len(length: int) -> int:
        return len(Asn1Parser.__encode_length(length))


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
    def decode_primitive_value(tag_type: str, value, length: int):
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
