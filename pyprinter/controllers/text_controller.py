import re


def format_cpf_cnpj(document):
    string_document = re.sub(r'\D', '', document)
    if len(string_document) == 11:
        return re.sub(
            r'^(\d{3})(\d{3})(\d{3})(\d{2})$',
            r'\1.\2.\3-\4', string_document
        )
    elif len(string_document) == 14:
        return re.sub(
            r'^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$',
            r'\1.\2.\3/\4-\5', string_document
        )

    return "\nNao Identificado"


def line_break(text, limit, sep=" "):
    lines = text.splitlines()
    lines_broken = []
    for line in lines:
        words = line.split(sep)
        line_broken = ''
        for word in words:
            if len(line_broken + word) <= limit:
                line_broken += word + ' '
            else:
                lines_broken.append(line_broken.strip())
                line_broken = word + ' '
        lines_broken.append(line_broken.strip())

    return "\n".join(lines_broken)


def description_break(text, limit):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) <= limit:
            if current_line:
                current_line += " "
            current_line += word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    return lines
