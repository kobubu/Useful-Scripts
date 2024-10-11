import pandas as pd

# Load the Excel file
df = pd.read_excel('C:/Users/Igor/Downloads/Эмоджи 32 бита.xlsx')


def utf32_to_utf16(utf32_code_point):
    # Remove the '\\u' prefix from the string
    hex_code_point = utf32_code_point.replace('\\u', '')

    # Convert the UTF-32 code point to an integer
    code_point = int(hex_code_point, 16)

    # Check if the code point is in the Basic Multilingual Plane (U+0000 to U+FFFF)
    if code_point <= 0xFFFF:
        # No need for a surrogate pair, just encode as UTF-16
        utf16_bytes = code_point.to_bytes(2, byteorder='little')
        utf16_str = utf16_bytes.decode('utf-16')
    else:
        # Calculate the surrogate pair
        code_point -= 0x10000
        high_surrogate = (code_point >> 10) + 0xD800
        low_surrogate = (code_point & 0x3FF) + 0xDC00

        # Encode the surrogate pair as UTF-16
        utf16_str = f"\\u{high_surrogate:04x}\\u{low_surrogate:04x}"

    return utf16_str




# Convert each code point in the 'emoji_utf_32' column to UTF-16
# Use a lambda function to extract the hexadecimal part of the string
df['emoji_utf_16'] = df['emoji_utf_32'].apply(lambda x: utf32_to_utf16(x))

# Save the DataFrame back to an Excel file
df.to_excel('C:/Users/Igor/Downloads/Эмоджи 16 бита.xlsx')

# Print the first few rows of the DataFrame
print(df.head())
