from flask import Flask, render_template, request, make_response
from operator import add, sub, mul, truediv

app = Flask(__name__)
application = app

operations = {'+': add, '-': sub, '*': mul, '/': truediv}


@app.route('/')
def index():
    url = request.url
    return render_template('index.html', url=url)


@app.route('/args')
def args():
    return render_template('args.html')


@app.route('/headers')
def headers():
    return render_template('headers.html')


@app.route('/cookies')
def cookies():
    response = make_response()
    if "Supersecretcookie" in request.cookies:
        response.delete_cookie("Supersecretcookie")
    else:
        response.set_cookie("Supersecretcookie", "1")
    response.set_data(render_template('cookies.html'))
    return response


@app.route('/form', methods=['GET', 'POST'])
def form():
    return render_template('form.html')


@app.route('/calc', methods=['GET', 'POST'])
def calc():
    error = ""
    result = ""
    if request.method == "POST":
        try:
            number1 = request.form.get("number1", '0')
            number2 = request.form.get("number2", '0')
            operation = request.form.get("operation", '')
            number1, number2 = list(map(int, (number1, number2)))
            result = operations[operation](number1, number2)
        except ValueError:
            error = "Числа введены неверно"
        except ZeroDivisionError:
            error = "Деление на 0 не определено"
        except KeyError:
            error = "Данная операция не поддерживается"
        except Exception as e:
            error = f"Неопределенная ошибка: {e}"
    return render_template('calc.html', error=error, result=result, operations=operations.keys())


@app.route('/phone', methods=['GET', 'POST'])
def phone():
    result = ""
    error = ""
    if request.method == "POST":
        try:
            num = request.form.get("num", '0')
            cleaned_number = ''.join(filter(lambda x: x.isdigit(), num))
            if len(cleaned_number) not in (10, 11):
                raise ValueError("Недопустимый ввод. Неверное количество цифр.")

            if not all(char.isdigit() or char in '+()-. ' for char in num):
                raise ValueError("Недопустимый ввод. В номере телефона встречаются недопустимые символы.")

            result = ('8-' + cleaned_number[-10:-7] + '-' + cleaned_number[-7:-4] + '-'
                                + cleaned_number[-4:-2] + '-' + cleaned_number[-2:])

        except Exception as e:
            error = e

    return render_template('phone.html', error=error, result=result)
# python -m venv ve
# . ve/bin/activate -- Linux
# ve\Scripts\activate -- Windows
# pip install flask python-dotenv
# cd app
# flask run
