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
