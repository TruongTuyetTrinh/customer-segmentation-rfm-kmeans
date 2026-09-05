import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import seaborn as sns
import os
import sys
import re

# Đặt mã hóa cho console
sys.stdout.reconfigure(encoding='utf-8')


# Hàm trích xuất số từ chuỗi, nếu không có số thì trả về trung bình BILL hợp lệ
def extract_number_or_mean(value, mean_bill):
    try:
        if isinstance(value, (int, float)):
            return float(value)
        number = re.findall(r'\d+\.?\d*', str(value))
        if number:
            return float(''.join(number))
        return mean_bill
    except:
        return mean_bill

# Giai đoạn 1: Thu thập dữ liệu
def load_data(file_path):
    try:
        data = pd.read_excel(file_path)
        data['dates'] = pd.to_datetime(data['dates'], format='%d/%m/%Y', errors='coerce')
        if data['dates'].isna().any():
            print("Cảnh báo: Một số giá trị trong cột 'dates' không thể chuyển đổi sang định dạng datetime.")
            print(f"Số dòng có dates không hợp lệ: {data['dates'].isna().sum()}")
        
        print(f"Số dòng có BILL không phải số trước khi xử lý: {len(data[~data['BILL'].apply(lambda x: isinstance(x, (int, float)))])}")
        mean_bill = data[data['BILL'].apply(lambda x: isinstance(x, (int, float)))]['BILL'].mean()
        data['BILL'] = data['BILL'].apply(lambda x: extract_number_or_mean(x, mean_bill))
        print(f"Số dòng có BILL không phải số sau khi xử lý: {len(data[~data['BILL'].apply(lambda x: isinstance(x, (int, float)))])}")
        
        print(f"Tổng số giao dịch: {len(data)}")
        print(f"Số customer_id duy nhất: {data['customer_id'].nunique()}")
        return data
    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu: {e}")
        return None

# Giai đoạn 2: Tiền xử lý dữ liệu và tính RFM
def calculate_rfm(data, reference_date, remove_outliers=False):
    reference_date = pd.to_datetime(reference_date, format='%d/%m/%Y')
    data = data.dropna(subset=['dates'])
    print(f"Số giao dịch sau khi loại bỏ dates null: {len(data)}")
    
    rfm = data.groupby('customer_id').agg({
        'dates': lambda x: (reference_date - x.max()).days,
        'BILL': 'count',
        'WEIGHT CHARGE': 'sum'
    }).reset_index()
    
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    print(f"Số customer_id sau khi gộp: {len(rfm)}")
    
    # In thống kê RFM trước khi xử lý ngoại lai
    print("\n=== Thống kê RFM trước khi xử lý ngoại lai ===")
    print(rfm[['recency', 'frequency', 'monetary']].describe().round(2).to_string())
    
    # In top 5 và bottom 5 cho recency, frequency, monetary
    print("\n=== Top 5 and Bottom 5 Rows of Recency Data (Sorted by Recency) ===")
    print(rfm[['customer_id', 'recency']].sort_values(by='recency', ascending=False).head(5).to_string(index=False))
    print("\n...")
    print(rfm[['customer_id', 'recency']].sort_values(by='recency', ascending=False).tail(5).to_string(index=False))
    print(f"{rfm.shape[0]} rows x 2 columns")
    
    print("\n=== Top 5 and Bottom 5 Rows of Frequency Data (Sorted by Frequency) ===")
    print(rfm[['customer_id', 'frequency']].sort_values(by='frequency', ascending=False).head(5).to_string(index=False))
    print("\n...")
    print(rfm[['customer_id', 'frequency']].sort_values(by='frequency', ascending=False).tail(5).to_string(index=False))
    print(f"{rfm.shape[0]} rows x 2 columns")
    
    print("\n=== Top 5 and Bottom 5 Rows of Monetary Data (Sorted by Monetary) ===")
    print(rfm[['customer_id', 'monetary']].sort_values(by='monetary', ascending=False).head(5).to_string(index=False))
    print("\n...")
    print(rfm[['customer_id', 'monetary']].sort_values(by='monetary', ascending=False).tail(5).to_string(index=False))
    print(f"{rfm.shape[0]} rows x 2 columns")
    
    # Vẽ histogram và boxplot trước khi xử lý ngoại lai
    plt.figure(figsize=(15, 5))
    for i, col in enumerate(['recency', 'frequency', 'monetary'], 1):
        plt.subplot(1, 3, i)
        sns.histplot(rfm[col], bins=30, kde=True)
        plt.title(f'Histogram của {col} (Trước ngoại lai)')
        plt.xlabel(col)
        plt.ylabel('Số lượng')
    plt.tight_layout()
    plt.savefig('rfm_histogram_before_outliers.png')
    plt.close()
    
    plt.figure(figsize=(15, 5))
    for i, col in enumerate(['recency', 'frequency', 'monetary'], 1):
        plt.subplot(1, 3, i)
        sns.boxplot(y=rfm[col])
        plt.title(f'Boxplot của {col} (Trước ngoại lai)')
        plt.ylabel(col)
    plt.tight_layout()
    plt.savefig('rfm_boxplot_before_outliers.png')
    plt.close()
    
    # Loại bỏ dữ liệu ngoại lai bằng IQR (chỉ cho recency và monetary)
    rfm_no_outliers = rfm.copy()
    if remove_outliers:
        def remove_outliers(df, column):
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 2.0 * IQR
            upper_bound = Q3 + 2.0 * IQR
            filtered_df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
            print(f"Số customer_id sau khi loại bỏ ngoại lai cho {column}: {len(filtered_df)}")
            return filtered_df
        
        # Lưu trữ các khách hàng có frequency cao trước khi loại ngoại lai
        high_frequency_customers = rfm_no_outliers[rfm_no_outliers['frequency'] >= rfm_no_outliers['frequency'].quantile(0.95)]
        for col in ['recency', 'monetary']:
            rfm_no_outliers = remove_outliers(rfm_no_outliers, col)
        # Gộp lại các khách hàng có frequency cao
        rfm_no_outliers = pd.concat([rfm_no_outliers, high_frequency_customers]).drop_duplicates(subset='customer_id')
        print(f"Số customer_id sau khi giữ lại khách hàng có frequency cao: {len(rfm_no_outliers)}")
    
    # In thống kê RFM sau khi xử lý ngoại lai
    print("\n=== Thống kê RFM sau khi xử lý ngoại lai ===")
    print(rfm_no_outliers[['recency', 'frequency', 'monetary']].describe().round(2).to_string())
    
    # Vẽ histogram và boxplot sau khi xử lý ngoại lai
    plt.figure(figsize=(15, 5))
    for i, col in enumerate(['recency', 'frequency', 'monetary'], 1):
        plt.subplot(1, 3, i)
        sns.histplot(rfm_no_outliers[col], bins=30, kde=True)
        plt.title(f'Histogram của {col} (Sau ngoại lai)')
        plt.xlabel(col)
        plt.ylabel('Số lượng')
    plt.tight_layout()
    plt.savefig('rfm_histogram_after_outliers.png')
    plt.close()
    
    plt.figure(figsize=(15, 5))
    for i, col in enumerate(['recency', 'frequency', 'monetary'], 1):
        plt.subplot(1, 3, i)
        sns.boxplot(y=rfm_no_outliers[col])
        plt.title(f'Boxplot của {col} (Sau ngoại lai)')
        plt.ylabel(col)
    plt.tight_layout()
    plt.savefig('rfm_boxplot_after_outliers.png')
    plt.close()
    
    # Áp dụng log transform cho frequency và monetary
    rfm_no_outliers['frequency'] = np.log1p(rfm_no_outliers['frequency'])
    rfm_no_outliers['monetary'] = np.log1p(rfm_no_outliers['monetary'])
    
    # Chuẩn hóa dữ liệu RFM
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_no_outliers[['recency', 'frequency', 'monetary']])
    rfm_scaled = pd.DataFrame(rfm_scaled, columns=['recency', 'frequency', 'monetary'])
    rfm_scaled['customer_id'] = rfm_no_outliers['customer_id'].values
    
    print(f"Số customer_id cuối cùng: {len(rfm_no_outliers)}")
    return rfm, rfm_scaled

# Giai đoạn 3: Phân cụm bằng K-means và phương pháp Elbow
def kmeans_clustering(rfm_scaled):
    if rfm_scaled.empty or len(rfm_scaled) < 2:
        print("Lỗi: Dữ liệu RFM sau khi xử lý rỗng hoặc quá ít để phân cụm.")
        return None, None
    
    inertia = []
    silhouette_scores = []
    K = range(3, min(15, len(rfm_scaled)))  # Kiểm tra từ 3 đến 14 cụm
    
    for k in K:
        kmeans = KMeans(n_clusters=k, n_init=20, max_iter=500, random_state=42)
        kmeans.fit(rfm_scaled[['recency', 'frequency', 'monetary']])
        inertia.append(kmeans.inertia_)
        score = silhouette_score(rfm_scaled[['recency', 'frequency', 'monetary']], kmeans.labels_)
        silhouette_scores.append(score)
    
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(K, inertia, 'bx-')
    plt.xlabel('Số cụm (k)')
    plt.ylabel('Inertia')
    plt.title('Phương pháp Elbow')
    
    plt.subplot(1, 2, 2)
    plt.plot(K, silhouette_scores, 'rx-')
    plt.xlabel('Số cụm (k)')
    plt.ylabel('Silhouette Score')
    plt.title('Silhouette Score theo số cụm')
    plt.tight_layout()
    plt.savefig('elbow_silhouette_plot.png')
    plt.close()
    
    # Ép số cụm là 4
    optimal_k = 4
    kmeans = KMeans(n_clusters=optimal_k, n_init=20, max_iter=500, random_state=42)
    rfm_scaled['cluster'] = kmeans.fit_predict(rfm_scaled[['recency', 'frequency', 'monetary']])
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=rfm_scaled, x='recency', y='monetary', hue='cluster', size='frequency', 
                    sizes=(20, 200), palette='deep')
    plt.title('Phân cụm khách hàng dựa trên RFM')
    plt.xlabel('Recency (chuẩn hóa)')
    plt.ylabel('Monetary (chuẩn hóa)')
    plt.savefig('cluster_visualization.png')
    plt.close()
    
    return rfm_scaled, optimal_k

# Giai đoạn 4: Đề xuất chiến lược marketing
# Đề xuất chiến lược marketing
def propose_marketing_strategies(rfm, rfm_scaled):
    if rfm_scaled is None or rfm is None:
        print("Lỗi: Không thể đề xuất chiến lược vì dữ liệu RFM hoặc phân cụm không hợp lệ.")
        return None, None
    
    rfm['cluster'] = rfm_scaled['cluster']
    
    # Thêm phân tích khu vực
    rfm['country'] = rfm['customer_id'].str.split('_').str[-1]
    country_summary = rfm.groupby(['cluster', 'country'])['customer_id'].count().unstack().fillna(0)
    print("\n=== Số lượng khách hàng theo quốc gia trong mỗi cụm ===")
    print(country_summary.round(2))
    
    # Thêm phân tích theo thành phố
    rfm['city'] = rfm['customer_id'].str.split('_').str[-2]
    city_summary = rfm.groupby(['cluster', 'city'])['customer_id'].count().unstack().fillna(0)
    print("\n=== Số lượng khách hàng theo thành phố trong mỗi cụm ===")
    print(city_summary.round(2))
    
    # Vẽ biểu đồ cột cho phân bố khách hàng theo top 5 thành phố
    top_cities = city_summary.sum().nlargest(5).index
    city_summary_top = city_summary[top_cities]
    city_summary_top.plot(kind='bar', stacked=True, figsize=(10, 6))
    plt.title('Phân bố khách hàng theo cụm và top 5 thành phố')
    plt.xlabel('Cụm')
    plt.ylabel('Số lượng khách hàng')
    plt.legend(title='Thành phố')
    plt.savefig('cluster_city_distribution.png')
    plt.close()
    
    cluster_summary = rfm.groupby('cluster').agg({
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean',
        'customer_id': 'count'
    }).round(2)
    
    print("\n=== Đặc điểm từng cụm ===")
    print(cluster_summary)
    
    # In 3-4 khách hàng tiêu biểu trong mỗi cụm
    print("\n=== Khách hàng tiêu biểu trong mỗi cụm ===")
    for cluster in cluster_summary.index:
        print(f"\nCụm {cluster}:")
        cluster_customers = rfm[rfm['cluster'] == cluster][['customer_id', 'recency', 'frequency', 'monetary']]
        # Sắp xếp theo monetary giảm dần và lấy top 3-4 khách hàng
        top_customers = cluster_customers.sort_values(by='monetary', ascending=False).head(4)
        print(top_customers.to_string(index=False))
    
    # Tùy chỉnh chiến lược cho 4 lớp khách hàng
    strategies = {}
    for cluster in cluster_summary.index:
        recency = cluster_summary.loc[cluster, 'recency']
        frequency = cluster_summary.loc[cluster, 'frequency']
        monetary = cluster_summary.loc[cluster, 'monetary']
        
        recency_mean = rfm['recency'].mean()
        frequency_mean = rfm['frequency'].mean()
        monetary_75 = rfm['monetary'].quantile(0.75)
        recency_50 = rfm['recency'].quantile(0.50)
        frequency_90 = rfm['frequency'].quantile(0.90)
        monetary_90 = rfm['monetary'].quantile(0.90)
        recency_75 = rfm['recency'].quantile(0.75)
        
        if recency < recency_mean and frequency >= frequency_90 and monetary >= monetary_90:
            strategies[cluster] = "Khách hàng VIP: Cung cấp chương trình khách hàng thân thiết, ưu đãi độc quyền, sản phẩm cao cấp."
        elif recency < recency_50 and frequency <= frequency_mean and monetary <= monetary_75:
            strategies[cluster] = "Khách hàng mới: Gửi ưu đãi chào mừng, khuyến khích giao dịch tiếp theo."
        elif recency >= recency_75 and frequency <= frequency_mean:
            strategies[cluster] = "Khách hàng lâu không giao dịch: Tăng cường quảng cáo, ưu đãi lớn để thu hút quay lại."
        else:
            strategies[cluster] = "Khách hàng chi tiêu khá: Gửi email tái kích hoạt, ưu đãi đặc biệt để tăng tần suất."
    
    print("\n=== Chiến lược marketing ===")
    for cluster, strategy in strategies.items():
        print(f"Cụm {cluster}: {strategy}")
    
    # Lưu danh sách khách hàng theo từng cụm
    for cluster, strategy in strategies.items():
        cluster_customers = rfm[rfm['cluster'] == cluster][['customer_id', 'recency', 'frequency', 'monetary', 'cluster', 'country', 'city']]
        if "VIP" in strategy:
            filename = f'vip_customers_cluster{cluster}.csv'
        elif "mới" in strategy:
            filename = f'new_customers_cluster{cluster}.csv'
        elif "chi tiêu khá" in strategy:
            filename = f'good_spenders_cluster{cluster}.csv'
        else:
            filename = f'inactive_customers_cluster{cluster}.csv'
        cluster_customers.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\nDanh sách khách hàng {strategy.split(':')[0]} (Cụm {cluster}) đã được lưu vào {filename} ({len(cluster_customers)} khách hàng).")
    
    return cluster_summary, strategies

# Hàm chính
def main():
    file_path = 'E:/DATA/rfm_data_corrected.xlsx'
    reference_date = '09/06/2025'
    
    data = load_data(file_path)
    if data is None:
        return
    
    # Phân tích RFM với bỏ ngoại lai
    print("\n===== Phân tích RFM với bỏ ngoại lai =====")
    rfm_with_outliers, rfm_scaled_with_outliers = calculate_rfm(data, reference_date, remove_outliers=True)
    rfm_scaled_with_outliers, optimal_k_with_outliers = kmeans_clustering(rfm_scaled_with_outliers)
    if rfm_scaled_with_outliers is not None:
        cluster_summary_with_outliers, strategies_with_outliers = propose_marketing_strategies(rfm_with_outliers, rfm_scaled_with_outliers)
    
    # Phân tích RFM không bỏ ngoại lai
    print("\n===== Phân tích RFM không bỏ ngoại lai =====")
    rfm_no_outliers, rfm_scaled_no_outliers = calculate_rfm(data, reference_date, remove_outliers=False)
    rfm_scaled_no_outliers, optimal_k_no_outliers = kmeans_clustering(rfm_scaled_no_outliers)
    if rfm_scaled_no_outliers is not None:
        cluster_summary_no_outliers, strategies_no_outliers = propose_marketing_strategies(rfm_no_outliers, rfm_scaled_no_outliers)
    
    # Lưu kết quả
    rfm_with_outliers.to_csv('rfm_results_with_outliers.csv', index=False, encoding='utf-8-sig')
    rfm_scaled_with_outliers.to_csv('rfm_scaled_clustered_with_outliers.csv', index=False, encoding='utf-8-sig')
    rfm_no_outliers.to_csv('rfm_results_no_outliers.csv', index=False, encoding='utf-8-sig')
    rfm_scaled_no_outliers.to_csv('rfm_scaled_clustered_no_outliers.csv', index=False, encoding='utf-8-sig')
    print("\nKết quả đã được lưu vào các file CSV.")

if __name__ == "__main__":
    main()