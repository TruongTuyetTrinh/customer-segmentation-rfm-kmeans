# Phân Tích Dữ Liệu Hành Vi Khách Hàng & Đề Xuất Chiến Lược Kinh Doanh Tại Nasco Express
*(Customer Behavior Analysis and Business Strategy Proposal at Nasco Express)*

---

## 📌 1. Bối Cảnh & Mục Tiêu Dự Án (Project Overview)
Trong ngành dịch vụ vận chuyển và chuyển phát nhanh, việc thấu hiểu hành vi giao dịch giúp doanh nghiệp chuyển dịch từ quản lý cảm tính sang **ra quyết định dựa trên dữ liệu (Data-driven decision making)**.

Dự án này tập trung vào việc:
* Khai thác và xử lý dữ liệu giao dịch thực tế của khách hàng tại **Nasco Express**.
* Mô hình hóa hành vi khách hàng bằng phương pháp **RFM** kết hợp thuật toán phân cụm **K-Means Clustering**.
* Nhận diện các nhóm khách hàng cốt lõi (khách hàng trung thành, tiềm năng, có nguy cơ rời bỏ).
* Đề xuất các giải pháp sản phẩm, chính sách giá và chiến lược chăm sóc cá nhân hóa nhằm tối ưu tỷ lệ chuyển đổi (**Conversion Rate**) và gia tăng giá trị trọn đời (**LTV**).

---

## 🛠 2. Công Nghệ & Thư Viện (Tech Stack)
* **Ngôn ngữ:** Python 3.x
* **Thư viện xử lý dữ liệu:** `pandas`, `numpy`
* **Học máy & Phân cụm:** `scikit-learn` (KMeans, StandardScaler, PCA)
* **Trực quan hóa dữ liệu:** `matplotlib`, `seaborn`
* **Công cụ hỗ trợ:** Jupyter Notebook, Google Sheets / Excel

---

## ⚙️ 3. Phương Pháp Tiếp Cận & Quy Trình Thực Hiện (Workflow)

```text
[Dữ liệu giao dịch thô] 
      └──> [Làm sạch & Tiền xử lý dữ liệu] 
              └──> [Tính toán chỉ số RFM] 
                      └──> [Chuẩn hóa & Gom cụm K-Means] 
                              └──> [Đánh giá & Đề xuất chiến lược]
