def validate_phone_number(phone_number):
    print(phone_number, "phone_number")

    cleaned_number = ''.join(filter(lambda x: x.isdigit(), phone_number))
    if len(cleaned_number) not in (10, 11):
        return "Недопустимый ввод. Неверное количество цифр."

    if not all(char.isdigit() or char in '+()-. ' for char in cleaned_number):
        return "Недопустимый ввод. В номере телефона встречаются недопустимые символы."

    formatted_number = ('8-' + cleaned_number[-10:-7] + '-' + cleaned_number[-7:-4] + '-'
                        + cleaned_number[-4:-2] + '-' + cleaned_number[-2:])

    return formatted_number


print(validate_phone_number("+7 (123) 456-75-90"))
print(validate_phone_number("8(123)4567590"))
print(validate_phone_number("123.456.75.90"))

try:
    num = "+7 (123) 456-75-90"
    cleaned_number = ''.join(filter(lambda x: x.isdigit(), num))
    if len(cleaned_number) not in (10, 11):
        error = "Недопустимый ввод. Неверное количество цифр."

    if not all(char.isdigit() or char in '+()-. ' for char in cleaned_number):
        error = "Недопустимый ввод. В номере телефона встречаются недопустимые символы."

    result = ('8-' + cleaned_number[-10:-7] + '-' + cleaned_number[-7:-4] + '-'
              + cleaned_number[-4:-2] + '-' + cleaned_number[-2:])

except Exception as e:
    error = e