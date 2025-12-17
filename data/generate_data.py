# generate_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
num_customers = 500
output_path = "data/customer_data.csv"

# --------------------------------------------------
# GENERATE CUSTOMER DATA
# --------------------------------------------------
np.random.seed(42)

customer_ids = np.arange(1000, 1000 + num_customers)
invoice_nos = np.random.randint(100000, 999999, size=num_customers)
invoice_dates = [datetime.today() - timedelta(days=int(x)) for x in np.random.randint(1, 365, size=num_customers)]
total_prices = np.round(np.random.uniform(20, 1000, size=num_customers), 2)

# Additional numeric features
loyalty_scores = np.random.randint(1, 101, size=num_customers)
avg_basket_size = np.round(np.random.uniform(1, 10, size=num_customers), 2)
returns = np.random.randint(0, 5, size=num_customers)
support_tickets = np.random.randint(0, 10, size=num_customers)
referral_count = np.random.randint(0, 20, size=num_customers)
avg_session_time = np.round(np.random.uniform(5, 120, size=num_customers), 2)
age = np.random.randint(18, 70, size=num_customers)
gender = np.random.choice(["Male", "Female", "Other"], size=num_customers)
region = np.random.choice(["North", "South", "East", "West"], size=num_customers)
device_type = np.random.choice(["Mobile", "Desktop", "Tablet"], size=num_customers)
last_login_days = np.random.randint(0, 365, size=num_customers)
newsletter_subscribed = np.random.choice([0, 1], size=num_customers)
premium_member = np.random.choice([0, 1], size=num_customers)
campaign_response_rate = np.round(np.random.uniform(0, 1, size=num_customers), 2)
avg_discount_used = np.round(np.random.uniform(0, 50, size=num_customers), 2)
avg_time_between_purchases = np.round(np.random.uniform(1, 60, size=num_customers), 2)
preferred_category = np.random.choice(["Electronics", "Clothing", "Home", "Beauty"], size=num_customers)

# Create DataFrame
df = pd.DataFrame({
    "CustomerID": customer_ids,
    "InvoiceNo": invoice_nos,
    "InvoiceDate": invoice_dates,
    "TotalPrice": total_prices,
    "LoyaltyScore": loyalty_scores,
    "AvgBasketSize": avg_basket_size,
    "Returns": returns,
    "SupportTickets": support_tickets,
    "ReferralCount": referral_count,
    "AvgSessionTime": avg_session_time,
    "Age": age,
    "Gender": gender,
    "Region": region,
    "DeviceType": device_type,
    "LastLoginDays": last_login_days,
    "NewsletterSubscribed": newsletter_subscribed,
    "PremiumMember": premium_member,
    "CampaignResponseRate": campaign_response_rate,
    "AvgDiscountUsed": avg_discount_used,
    "AvgTimeBetweenPurchases": avg_time_between_purchases,
    "PreferredCategory": preferred_category
})

# Save CSV
df.to_csv(output_path, index=False)
print(f"✅ Synthetic customer data generated at {output_path}")
