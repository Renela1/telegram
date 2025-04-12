def remove_consecutive_duplicates(s):
    string = f"{s[0]}"
    if not s:

        return ""

    result = s[0]  

    for char in s[1:]:

        if char != result[-1]:

            result += char
            print(result)
            string += char

    return string

output_string = remove_consecutive_duplicates("AAABBCCCDDDDAABC")

print("خروجی:", (output_string))

