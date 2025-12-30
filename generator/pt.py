import random
import math

def linear_equation(difficulty_level):
    # Предварительный кэширование функций в локальный контекст
    # Это дает ощутимый прирост в циклах
    rand = random.random
    _math_gcd = math.gcd
    _abs = abs

    # Быстрый выбор переменной (быстрее чем randint или choice)
    vars_pool = ("x", "y", "z", "a", "b")
    var = vars_pool[int(rand() * 5)]
    
    problem = ""
    answer_val = 0

    if difficulty_level == 1:
        # Убираем циклы while, заменяя их на математический сдвиг диапазона
        a = int(rand() * 14) - 6 # [-6, 7]
        if a >= 0: a += 1        # Исключаем 0
        x = int(rand() * 9) - 2
        
        left, right = f"{a}{var}", str(a * x)
        if rand() > 0.5:
            problem = left + " = " + right
        else:
            problem = right + " = " + left
        answer_val = x

    elif difficulty_level == 2:
        eq_type = int(rand() * 3)
        if eq_type == 0:
            a = int(rand() * 10) + 1
            x = int(rand() * 11) - 5
            b = int(rand() * 15) + 1
            is_plus = rand() > 0.5
            
            res = (a * x + b) if is_plus else (a * x - b)
            vt = f"{a}{var}" if a != 1 else var
            op = " + " if is_plus else " - "
            
            # Конкатенация через + часто быстрее f-строк для простых соединений
            left = (vt + op + str(b)) if rand() > 0.5 else (str(b if is_plus else -b) + " + " + vt)
            problem = (left + " = " + str(res)) if rand() > 0.5 else (str(res) + " = " + left)
            answer_val = x
            
        elif eq_type == 1:
            a, x, op_val = int(rand()*8)+1, int(rand()*9)-4, int(rand()*10)+1
            res = a * (x + op_val)
            problem = f"{a}({var} + {op_val}) = {res}"
            answer_val = x
        else:
            a = int(rand() * 8) + 1
            c = int(rand() * 8) + 1
            if a == c: c = (a % 8) + 1
            x, b = int(rand() * 7) - 3, int(rand() * 12) + 1
            op1_p, op2_p = rand() > 0.5, rand() > 0.5
            
            left_val = (a * x + b) if op1_p else (a * x - b)
            d = (left_val - c * x) if op2_p else -(left_val - c * x)
            
            vt1 = f"{a}{var}" if a != 1 else var
            left = (vt1 + (" + " if op1_p else " - ") + str(b)) if rand() > 0.5 else (str(b if op1_p else -b) + " + " + vt1)
            
            vt2 = f"{c}{var}" if c != 1 else var
            if d == 0:
                right = vt2
            else:
                ad = _abs(d)
                right = (vt2 + (" + " if op2_p else " - ") + str(ad)) if rand() > 0.5 else (str(d) + " + " + vt2)
            problem = (left + " = " + right) if rand() > 0.5 else (right + " = " + left)
            answer_val = x

    else: # HARD
        eq_type = int(rand() * 3)
        if eq_type == 0:
            x, c = int(rand()*9)-4, int(rand()*5)+2
            a = min(8, max(1, c + (int(rand()*4)-1)))
            op1_p, op2_p = rand()>0.5, rand()>0.5
            d = int(rand()*6)+1
            rv = c * (x + d) if op2_p else c * (x - d)
            b = (rv - a * x) if op1_p else (a * x - rv)
            
            vt1 = f"{a}{var}" if a != 1 else var
            left = (vt1 + (" + " if op1_p else " - ") + str(_abs(b))) if rand() > 0.5 else (str(b) + " + " + vt1)
            right = f"{c}({var} {'+ ' if op2_p else '- '}{d})"
            problem = (left + " = " + right) if rand() > 0.5 else (right + " = " + left)
            answer_val = x
            
        elif eq_type == 1:
            x, a, d = int(rand()*7)-3, int(rand()*4)+2, int(rand()*4)+2
            o1, o2, o3 = rand()>0.5, rand()>0.5, rand()>0.5
            b, c = int(rand()*5)+1, int(rand()*8)+1
            ls = (a * ((x + b) if o1 else (x - b)) + (c if o2 else -c))
            e = (ls - d * x) if o3 else (d * x - ls)
            
            br_t = f"{a}({var} {'+ ' if o1 else '- '}{b}) {'+ ' if o2 else '- '}{c}"
            vt = (f"{d}{var}" if d != 1 else var)
            right = vt if e == 0 else (vt + (" + " if o3 else " - ") + str(_abs(e)))
            problem = (br_t + " = " + right) if rand() > 0.5 else (right + " = " + br_t)
            answer_val = x
            
        else: # Fractions
            b, x = int(rand()*4)+2, int(rand()*6)+1
            # Быстрый поиск коэффициента 'a' без цикла
            a = next(i for i in range(1, 9) if (i * x) % b == 0)
            
            op_p, cv = rand() > 0.5, int(rand()*6)+1
            dv = (a * x) // b + (cv if op_p else -cv)
            
            gcd = _math_gcd(a, b)
            if a % b == 0:
                ft = f"{a//b}{var}" if a//b != 1 else var
            else:
                ft = f"{(a//gcd) if a//gcd != 1 else ''}{var}/{b//gcd}"
            
            left = (ft + (" + " if op_p else " - ") + str(cv)) if rand() > 0.5 else (str(cv if op_p else -cv) + " + " + ft)
            problem = (left + " = " + str(dv)) if rand() > 0.5 else (str(dv) + " = " + left)
            answer_val = x

    # Финальная склейка через f-строку один раз
    return f"{problem}|{var} = {answer_val}"