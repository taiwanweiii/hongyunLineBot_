def check_number_type(number):
    match number:
        case 0:
            return "零"
        case 1:
            return "一"
        case 2:
            return "二"
        case _ if number % 2 == 0:
            return "偶數"
        case _:
            return "奇數"

# 測試
print(check_number_type(0))    # 輸出: 零
print(check_number_type(1))    # 輸出: 一
print(check_number_type(2))    # 輸出: 二
print(check_number_type(4))    # 輸出: 偶數
print(check_number_type(7))    # 輸出: 奇數
