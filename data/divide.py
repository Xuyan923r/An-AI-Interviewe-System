import pandas as pd

# 读取 .xlsx 文件
file_path = "/Users/xuyanye/Desktop/AI-interviewers/data/data.xlsx"
xls = pd.ExcelFile(file_path)

# 获取所有表单的名称
sheet_names = xls.sheet_names

# 遍历所有表单并保存每个表单为新的 .csv 文件
for sheet in sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet)  # 读取单个表单
    df.to_csv(f"{sheet}.csv", index=False, encoding="utf-8-sig")  # 保存为新的 .csv 文件
    print(f"已保存 {sheet}.csv")
