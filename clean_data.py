import pandas as pd
import sys
import re

# Đảm bảo console hỗ trợ UTF-8 để tránh lỗi Unicode
sys.stdout.reconfigure(encoding='utf-8')

# Bảng ánh xạ quốc gia để chuẩn hóa DEST
country_mapping = {
    # Châu Mỹ
    'us': 'United States', 'usa': 'United States', 'u.s.': 'United States', 'united states': 'United States',
    'ca': 'Canada', 'can': 'Canada', 'canada': 'Canada',
    'mx': 'Mexico', 'mex': 'Mexico', 'mexico': 'Mexico',
    'br': 'Brazil', 'bra': 'Brazil', 'brazil': 'Brazil',
    'ar': 'Argentina', 'arg': 'Argentina', 'argentina': 'Argentina',
    'cl': 'Chile', 'chl': 'Chile', 'chile': 'Chile',
    'co': 'Colombia', 'col': 'Colombia', 'colombia': 'Colombia',
    'pe': 'Peru', 'per': 'Peru', 'peru': 'Peru',
    've': 'Venezuela', 'ven': 'Venezuela', 'venezuela': 'Venezuela',
    'ec': 'Ecuador', 'ecu': 'Ecuador', 'ecuador': 'Ecuador',
    
    # Châu Âu
    'uk': 'United Kingdom', 'gb': 'United Kingdom', 'u.k.': 'United Kingdom', 'united kingdom': 'United Kingdom',
    'fr': 'France', 'fra': 'France', 'france': 'France',
    'de': 'Germany', 'deu': 'Germany', 'germany': 'Germany',
    'it': 'Italy', 'ita': 'Italy', 'italy': 'Italy',
    'es': 'Spain', 'esp': 'Spain', 'spain': 'Spain',
    'nl': 'Netherlands', 'nld': 'Netherlands', 'netherlands': 'Netherlands',
    'se': 'Sweden', 'swe': 'Sweden', 'sweden': 'Sweden',
    'ch': 'Switzerland', 'che': 'Switzerland', 'switzerland': 'Switzerland',
    'be': 'Belgium', 'bel': 'Belgium', 'belgium': 'Belgium',
    'at': 'Austria', 'aut': 'Austria', 'austria': 'Austria',
    'dk': 'Denmark', 'dnk': 'Denmark', 'denmark': 'Denmark',
    'no': 'Norway', 'nor': 'Norway', 'norway': 'Norway',
    'fi': 'Finland', 'fin': 'Finland', 'finland': 'Finland',
    'pl': 'Poland', 'pol': 'Poland', 'poland': 'Poland',
    'ru': 'Russia', 'rus': 'Russia', 'russia': 'Russia',
    
    # Châu Á
    'vn': 'Vietnam', 'vnm': 'Vietnam', 'viet nam': 'Vietnam', 'vietnam': 'Vietnam',
    'cn': 'China', 'chn': 'China', 'china': 'China',
    'jp': 'Japan', 'jpn': 'Japan', 'japan': 'Japan',
    'kr': 'South Korea', 'kor': 'South Korea', 'south korea': 'South Korea',
    'sg': 'Singapore', 'sgp': 'Singapore', 'singapore': 'Singapore',
    'hk': 'Hong Kong', 'hkg': 'Hong Kong', 'hong kong': 'Hong Kong',
    'tw': 'Taiwan', 'twn': 'Taiwan', 'taiwan': 'Taiwan',
    'th': 'Thailand', 'tha': 'Thailand', 'thailand': 'Thailand',
    'my': 'Malaysia', 'mys': 'Malaysia', 'malaysia': 'Malaysia',
    'id': 'Indonesia', 'idn': 'Indonesia', 'indonesia': 'Indonesia',
    'ph': 'Philippines', 'phl': 'Philippines', 'philippines': 'Philippines',
    'in': 'India', 'ind': 'India', 'india': 'India',
    'sa': 'Saudi Arabia', 'sau': 'Saudi Arabia', 'saudi arabia': 'Saudi Arabia',
    'ae': 'United Arab Emirates', 'are': 'United Arab Emirates', 'uae': 'United Arab Emirates',
    'kp': 'North Korea', 'prk': 'North Korea', 'north korea': 'North Korea',
    'pk': 'Pakistan', 'pak': 'Pakistan', 'pakistan': 'Pakistan',
    'bd': 'Bangladesh', 'bgd': 'Bangladesh', 'bangladesh': 'Bangladesh',
    
    # Châu Đại Dương
    'au': 'Australia', 'aus': 'Australia', 'australia': 'Australia',
    'nz': 'New Zealand', 'nzl': 'New Zealand', 'new zealand': 'New Zealand',
    
    # Châu Phi
    'za': 'South Africa', 'zaf': 'South Africa', 'south africa': 'South Africa',
    'ng': 'Nigeria', 'nga': 'Nigeria', 'nigeria': 'Nigeria',
    'ke': 'Kenya', 'ken': 'Kenya', 'kenya': 'Kenya',
    'eg': 'Egypt', 'egy': 'Egypt', 'egypt': 'Egypt',
    'ma': 'Morocco', 'mar': 'Morocco', 'morocco': 'Morocco',
    
    # Các quốc gia khác
    'tr': 'Turkey', 'tur': 'Turkey', 'turkey': 'Turkey',
    'il': 'Israel', 'isr': 'Israel', 'israel': 'Israel',
    'qa': 'Qatar', 'qat': 'Qatar', 'qatar': 'Qatar',
    'kw': 'Kuwait', 'kwt': 'Kuwait', 'kuwait': 'Kuwait',
    'om': 'Oman', 'omn': 'Oman', 'oman': 'Oman',
    'jo': 'Jordan', 'jor': 'Jordan', 'jordan': 'Jordan',
    'lk': 'Sri Lanka', 'lka': 'Sri Lanka', 'sri lanka': 'Sri Lanka',
    'mm': 'Myanmar', 'mmr': 'Myanmar', 'myanmar': 'Myanmar',
    'kh': 'Cambodia', 'khm': 'Cambodia', 'cambodia': 'Cambodia',
    'la': 'Laos', 'lao': 'Laos', 'laos': 'Laos'
}

# File path to the Excel file
file_path = "DỮ LIỆU THÁNG .xlsx"
output_file_path = "cleaned_data.xlsx"
try:
    # Read all sheets from the Excel file
    all_sheets = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
    
    # Combine all sheets into a single DataFrame
    df = pd.concat(all_sheets.values(), ignore_index=True)
    
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found. Please ensure the file is in the correct directory.")
    sys.exit(1)
except Exception as e:
    print(f"Error reading Excel file: {str(e)}")
    sys.exit(1)

# Step 1: Filter valid transactions (non-null DATES or BILL)
df = df.dropna(subset=['DATES', 'BILL'], how='all')

# Step 2: Remove rows where Status is missing
df = df.dropna(subset=['Status'])

# Step 3: Remove unnecessary columns
columns_to_drop = ['tracking_number', 'NAME CS', 'TÊN KHÁCH HÀNG', 'TÊN KHÁCH HÀNG''',
                   'From (Shipper)', 'Document and parcel worldwide express', 'SGN170708200'] + \
                  [col for col in df.columns if col.startswith('Unnamed')]
df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

# Step 4: Convert data types
df['DATES'] = pd.to_datetime(df['DATES'], format='%d/%m/%Y', errors='coerce')
df['est_delivery_date'] = pd.to_datetime(df['est_delivery_date'], errors='coerce').dt.tz_localize(None)  # Convert to datetime64[ns]
df['WEIGHT'] = pd.to_numeric(df['WEIGHT'], errors='coerce')

# Step 5: Handle missing values for WEIGHT CHARGE
# Bảng giá cho 0.5–20 kg
weight_price_table = {
    0.5: 1210000, 1.0: 1350000, 1.5: 1600000, 2.0: 1790000, 2.5: 2050000,
    3.0: 2130000, 3.5: 2380000, 4.0: 2490000, 4.5: 2720000, 5.0: 2860000,
    5.5: 3070000, 6.0: 3150000, 6.5: 3390000, 7.0: 3470000, 7.5: 3680000,
    8.0: 3750000, 8.5: 3960000, 9.0: 4010000, 9.5: 4190000, 10.0: 4240000,
    10.5: 4350000, 11.0: 4400000, 11.5: 4540000, 12.0: 4580000, 12.5: 4680000,
    13.0: 4700000, 13.5: 4780000, 14.0: 4830000, 14.5: 4910000, 15.0: 4940000,
    15.5: 5010000, 16.0: 5040000, 16.5: 5140000, 17.0: 5170000, 17.5: 5270000,
    18.0: 5300000, 18.5: 5380000, 19.0: 5430000, 19.5: 5510000, 20.0: 5530000
}

def calculate_weight_charge(row):
    weight = row['WEIGHT']
    content = str(row['Content']).lower() if pd.notnull(row['Content']) else ''
    
    if pd.isna(weight):
        return None
    
    # For weights <= 20 kg
    if weight <= 20:
        # Find the closest weight key in the table
        weight_keys = list(weight_price_table.keys())
        closest_weight = min(weight_keys, key=lambda x: abs(x - weight))
        return weight_price_table[closest_weight]
    
    # For weights >= 22 kg
    if 'clothing' in content or 'books' in content or 'vải' in content or 'toys' in content or 'home & kitchen' in content:
        if 22 <= weight <= 30:
            return weight * 240000
        elif 31 <= weight <= 44:
            return weight * 240000
        elif 45 <= weight <= 70:
            return weight * 230000
        elif 71 <= weight <= 99:
            return weight * 220000
        else:  # > 100 kg
            return weight * 210000
    elif 'category' in content or 'food' in content:
        if 22 <= weight <= 30:
            return weight * 250000
        elif 31 <= weight <= 44:
            return weight * 250000
        elif 45 <= weight <= 70:
            return weight * 240000
        elif 71 <= weight <= 99:
            return weight * 230000
        else:  # > 100 kg
            return weight * 220000
    elif 'beauty' in content or 'electronics' in content or 'bột' in content or 'hạt sấy khô' in content:
        # Since DELIVERY_DAYS is not available, use default price for fast delivery
        if 22 <= weight <= 30:
            return weight * 450000
        elif 31 <= weight <= 44:
            return weight * 315000
        elif 45 <= weight <= 70:
            return weight * 310000
        elif 71 <= weight <= 99:
            return weight * 295000
        else:  # > 100 kg
            return weight * 290000
    else:  # Default for other items
        return weight * 240000

# Apply function to fill missing WEIGHT CHARGE
df['WEIGHT CHARGE'] = df.apply(
    lambda row: calculate_weight_charge(row) if pd.isna(row['WEIGHT CHARGE']) else row['WEIGHT CHARGE'], axis=1
)

# Convert WEIGHT CHARGE to float
df['WEIGHT CHARGE'] = pd.to_numeric(df['WEIGHT CHARGE'], errors='coerce')

# Step 6: Standardize DEST using country_mapping
def standardize_country(country):
    if pd.isna(country):
        return 'Unknown'
    country = country.lower().strip()
    return country_mapping.get(country, country)  # Keep original value if not in country_mapping

df['DEST'] = df['DEST'].apply(standardize_country)

# Step 7: Handle other missing values
df['Local'] = df['Local'].fillna('Unknown')
df['done'] = df['done'].fillna('delivered')  # Fill with 'delivered' as requested
df['BILL'] = df['BILL'].fillna('Unknown')
df['ATTN'] = df['ATTN'].fillna('Unknown')

# Step 8: Create customer_id based on ATTN, Local, and DEST
def standardize_name(name):
    if pd.isna(name) or name == 'Unknown':
        return 'Unknown'
    # Remove titles (Mrs, Mr, Ms, etc.), special characters, and normalize
    name = re.sub(r'^(Mrs|Mr|Ms|Miss|Dr)\.?\s+', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name.strip())
    # Remove periods in abbreviations (e.g., "Kim G." -> "Kim G")
    name = re.sub(r'\.\s*', ' ', name)
    # Sort words to handle cases like "Kim Gamez" vs "Gamez Kim"
    words = name.split()
    words.sort()
    return ' '.join(words).lower()

# Apply standardization to ATTN
df['ATTN_standardized'] = df['ATTN'].apply(standardize_name)

# Create customer_id by combining standardized ATTN, Local, and DEST
df['customer_id'] = df.apply(
    lambda x: f"{x['ATTN_standardized']}_{x['Local'].lower()}_{x['DEST'].lower().replace(' ', '_')}", axis=1
)

# Drop temporary ATTN_standardized column
df = df.drop(columns=['ATTN_standardized'])
try:
    df.to_excel(output_file_path, index=False, engine='openpyxl')
    print(f"Cleaned data has been exported to '{output_file_path}'")
except Exception as e:
    print(f"Error exporting to Excel: {str(e)}")
    sys.exit(1)
# Step 8.5: Display first 5 and last 5 rows of cleaned data with dimensions
print("\n=== First 5 and Last 5 Rows of Cleaned Data ===")
print(df.head(5).to_string(index=False))
print("\n...")
print(df.tail(5).to_string(index=False))
print(f"{df.shape[0]} rows x {df.shape[1]} columns")
# Step 9: Raw Data Check after cleaning
print("=== Cleaned Data Check ===")
print("Number of rows:", len(df))
print("Columns:", df.columns.tolist())
print("Data types:\n", df.dtypes)
print("Missing values:\n", df.isnull().sum())
# Display unique customer_id values in sample
sample_customer_ids = df['customer_id'].drop_duplicates().head(10).reset_index(drop=True)
print("\nSample customer_id values:\n", sample_customer_ids)
print("Unique customer_ids:", df['customer_id'].nunique())
# Step 9: Chuẩn bị dữ liệu cho RFM và Apriori

# Hàm tách Status thành Delivery_Status và Delivery_Method
def split_status(status):
    try:
        delivery_status, delivery_method = status.split(': ', 1)
        return pd.Series([delivery_status, delivery_method])
    except:
        return pd.Series([status, 'Unknown'])

# Tách cột Status
df[['Delivery_Status', 'Delivery_Method']] = df['Status'].apply(split_status)

# 9.1. Dữ liệu cho thuật toán RFM
print("\n=== Tách dữ liệu cho RFM ===")
rfm_cols = ['customer_id', 'DATES', 'BILL', 'WEIGHT CHARGE']
rfm_data = df[rfm_cols]
rfm_data.to_excel('E:/DATA/rfm_data.xlsx', index=False, engine='openpyxl')
print(f"RFM data has been exported to 'E:/DATA/rfm_data.xlsx'")
print(rfm_data.head(5).to_string(index=False))
print("\n...")
print(rfm_data.tail(5).to_string(index=False))
print(f"{rfm_data.shape[0]} rows x {rfm_data.shape[1]} columns")

# 9.2. Dữ liệu cho thuật toán Apriori
print("\n=== Tách dữ liệu cho Apriori ===")
apriori_cols = ['SERVICE', 'customer_id', 'DEST', 'Content', 'Delivery_Status', 'Delivery_Method', 'done']
apriori_data = df[apriori_cols].drop_duplicates()
apriori_data.to_excel('E:/DATA/apriori_data.xlsx', index=False, engine='openpyxl')
print(f"Apriori data has been exported to 'E:/DATA/apriori_data.xlsx'")
print(apriori_data.head(5).to_string(index=False))
print("\n...")
print(apriori_data.tail(5).to_string(index=False))
print(f"{apriori_data.shape[0]} rows x {apriori_data.shape[1]} columns")









