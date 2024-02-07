import re


def format_cnpj(cnpj):
    string_cnpj = re.sub(r'\D', '', cnpj)
    return re.sub(
        r'^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$',
        r'\1.\2.\3/\4-\5', string_cnpj
    )


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
