import torch
import json
import re
import os
import matplotlib.pyplot as plt

def is_valid_json(json_str):
    try:
        # 尝试加载 JSON 字符串
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False


cnt=0;
normal={}
abnormal={}


# 指定目录路径
directory = r'D:\DAppFL\data\processed'

# 获取目录下的所有文件
files = [f for f in os.listdir(directory) if f.endswith('.pt')]

# 遍历文件列表
for file in files:
    # 构建完整的文件路径
    file_path = os.path.join(directory, file)
    data = torch.load(file_path)
    edge_index=data[('Case', 'cover', 'FunctionDefinition')]['edge_index']
    lable_list=data['FunctionDefinition'].y.tolist()
    edge_list=edge_index[1].tolist()


    for index in edge_list:
        pos=data['FunctionDefinition']['position'][index]
        add=pos.split("#")
        pos=add[0]
        num=add[2].split(":")
        down = int(num[0])
        up = down+int(num[1])
        file_path = f'D:\\DAppFL\\data\\cache\\source\\{pos}.json'
        with open(file_path ,'r') as f:
            source=json.load(f)
        if is_valid_json(source['SourceCode']):
            std_json = json.loads(source['SourceCode'][1:-1])
        else:
            std_json = source['SourceCode']
        if isinstance(std_json, dict):
            content=std_json['sources'][add[1]]['content'][down:up]
        elif isinstance(std_json, str):
            content=std_json[down:up]
        else:
            break

        #rlt = re.search(r'function\s+(\w+)\s*\(', content)
        rlt = re.search(r'function (.*?)\(',content)
        if rlt:
            if lable_list[index]==0:
                if rlt.group(1) not in normal.keys() :
                    normal[rlt.group(1)] = 0
                    normal[rlt.group(1)] += 1
                elif rlt.group(1) in normal.keys() :
                    normal[rlt.group(1)] += 1
            else:
                if rlt.group(1) not in abnormal.keys() :
                    abnormal[rlt.group(1)] = 0
                    abnormal[rlt.group(1)] += 1
                elif rlt.group(1) in abnormal.keys() :
                    abnormal[rlt.group(1)] += 1
            cnt+=1



sorted_normal = dict(sorted(normal.items(), key=lambda item: item[1], reverse=True)[:20])

# 将 abnormal 字典的元素添加到 sorted_normal 字典中
combined_data = {**sorted_normal, **abnormal}

# 对合并后的字典进行排序
sorted_combined_data = dict(sorted(combined_data.items(), key=lambda item: item[1], reverse=True))

print(sorted_combined_data.values())

# 计算每个元素的占比
percentages = [value / cnt for value in sorted_combined_data.values()]

# 准备数据
labels = list(sorted_combined_data.keys())
values = list(sorted_combined_data.values())

# 确定每个条形的颜色
colors = ['black' if label in sorted_normal else 'red' for label in labels]

# 创建条形图
plt.figure(figsize=(14, 8))  # 设置图形大小
bars = plt.bar(labels, percentages, color=colors)  # 创建条形图

# 添加标题和标签
plt.title('Comparison of Normal and Abnormal Function Occurrence Statistics (Percentage)')
plt.xlabel('Function Name')
plt.ylabel('Percentage')

# 添加数值标签
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

# 显示图形
plt.xticks(rotation=45, ha='right')  # 旋转x轴标签，便于阅读
plt.tight_layout()  # 自动调整子图参数，使之填充整个图像区域
plt.show()
