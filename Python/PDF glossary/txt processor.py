import re

def build_dictionary(file_path):
    dictionary = {}
    stack = []
    pattern = re.compile(r'^([\t\n\r\f\vЕёА-я~\s_)(-]*)\s+(.*)(?=[A-z]*)$', re.UNICODE)

    # Read all lines and handle line continuations
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    full_lines = []
    current_line = ''
    for line in lines:
        line = line.rstrip('\n')
        if line.endswith('-'):
            current_line += line[:-1].rstrip()
        else:
            current_line += line
            full_lines.append(current_line)
            current_line = ''

    # Process the full_lines
    for line in full_lines:
        line = line.strip()
        if line.startswith('~'):
            # Count the number of '~'
            level = 0
            while line.startswith('~'):
                level += 1
                line = line[1:].lstrip()
            # Match Russian and English parts
            match = pattern.match(line)
            if match:
                russian = match.group(1)
                english = match.group(2)
                # Adjust the stack to the current level
                if level > len(stack):
                    pass  # Invalid, sub-term level higher than stack depth
                else:
                    stack = stack[:level]
                    stack.append(russian)
                full_russian = ' '.join(stack)
                dictionary[full_russian] = english
                # Update stack
                stack = stack[:level] + [russian]
        else:
            # Main term
            match = pattern.match(line)
            if match:
                russian = match.group(1)
                english = match.group(2)
                stack = [russian]
                dictionary[russian] = english
    return dictionary

# Example usage
if __name__ == "__main__":
    dir = "C:\\Users\\Igor\\Desktop\\работа\\pdf\\"
    file_path = dir+'factored_text.txt'
    russian_to_english = build_dictionary(file_path)
    # Print the dictionary
    for key, value in russian_to_english.items():
        print(f"{key}: {value}")
