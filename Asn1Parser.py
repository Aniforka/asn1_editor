from asn1crypto import core

class Asn1Parser:

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
            for i in range(length_len):
                length = (length << 8) | data[offset]
                offset += 1

        # Определяем тип данных по тегу
        tag_class = ["Universal", "Application", "Context-specific", "Private"][
            class_ >> 6
        ]
        tag_type = Asn1Parser.__get_tag_type(tag_class, tag_number)

        displayed_offset = offset - 1 - length_len if length_len else offset - 2

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
            return {
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
            }.get(tag_number, f"Unknown ({tag_number})")
        elif tag_class in ("Application", "Context-specific", "Private"):
            # Для этих классов нет предопределенных типов,
            # поэтому возвращаем просто номер тега
            return f"{tag_class} ({tag_number})"
        else:
            return f"Unknown Class ({tag_class}), Tag ({tag_number})"

    
