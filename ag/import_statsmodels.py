import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

# 生成模拟用户消费数据
np.random.seed(42)
months = pd.date_range(start='2023-01-01', end='2023-12-31', freq='M')
data = {
    'datum': months,
    'Living_expense': np.random.randint(500, 1000, len(months)),
    'Allowance': np.random.randint(200, 400, len(months)),
    'Income': np.random.randint(3000, 5000, len(months)),
    'Tuition': np.random.randint(0, 500, len(months)),
    'Housing': np.random.randint(1000, 2000, len(months)),
    'Food': np.random.randint(300, 600, len(months)),
    'Transportation': np.random.randint(50, 150, len(months)),
    'Study_material': np.random.randint(0, 300, len(months)),
    'Entertainment': np.random.randint(100, 500, len(months)),
    'Personal_care': np.random.randint(50, 150, len(months)),
    'Technology': np.random.randint(0, 300, len(months)),
    'Apparel': np.random.randint(0, 300, len(months)),
    'Travel': np.random.randint(0, 1000, len(months)),
    'Others': np.random.randint(50, 300, len(months))
}
df = pd.DataFrame(data)
df['Total_spending'] = df[[
    'Living_expense', 'Allowance', 'Housing', 'Food', 'Transportation',
    'Study_material', 'Entertainment', 'Personal_care', 'Technology',
    'Apparel', 'Travel', 'Others'
]].sum(axis=1)

# 设置时间索引
df['datum'] = pd.to_datetime(df['datum'])
df.set_index('datum', inplace=True)

# 创建空字典存储预测结果
forecast_results = {}

# 遍历每个消费类别进行 ARIMA 预测
for column in df.columns:
    if column != 'Total_spending':
        # 提取列数据
        data_series = df[column]
        
        # 检查数据平稳性
        from statsmodels.tsa.stattools import adfuller
        if adfuller(data_series)[1] > 0.05:
            data_series = data_series.diff().dropna()

        # 构建 ARIMA 模型
        model = ARIMA(data_series, order=(2, 1, 2))
        model_fit = model.fit()

        # 预测未来一个月（30 天）的数据
        future_steps = 30
        forecast = model_fit.get_forecast(steps=future_steps)
        forecast_mean = forecast.predicted_mean.clip(lower=0)  # 强制将负值设为 0
        forecast_results[column] = forecast_mean

# 提供用户交互选择模式
print("请选择输出模式：")
print("1: 月均值模式")
print("2: 每日预测模式")
choice = input("请输入选项编号 (1 或 2): ").strip()

if choice == "1":
    # 月均值模式
    print("\nNext Month Predict (Monthly Average):")
    for category, predictions in forecast_results.items():
        avg_prediction = predictions.mean()  # 计算平均值
        print(f"{category.capitalize()}: {avg_prediction:.2f}")

elif choice == "2":
    # 每日预测模式
    print("\nDaily Predictions:")
    daily_results = pd.DataFrame(forecast_results)
    daily_results.index = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=30, freq='D')
    print(daily_results.round(2))

else:
    print("无效输入，请选择 1 或 2。")
