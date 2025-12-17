
# --------------------------------------------------
# CONFIGURATION - THEME: NEON AURORA
# --------------------------------------------------
import os

FILE_PATH = "output/clustered_output/final_output.csv"
SEGMENT_COL = "segment_id"

SEGMENT_MAP = {
    0: "Needs Attention",       # Was At-Risk
    1: "Occasional Shoppers",   # Was Low-Value
    2: "Champions",             # Was VIP
    3: "Loyalists"              # Was Loyal
}

# Professional Modern Palette (Luxury Dark)
SEGMENT_COLORS = {
    "Champions": "#FACC15",           # Gold (Luxury Highlight)
    "Loyalists": "#22D3EE",           # Electric Cyan (Primary Accent)
    "Occasional Shoppers": "#8B5CF6", # Royal Purple (Secondary Accent)
    "Needs Attention": "#F43F5E"      # Crimson Red (Danger)
}

# Contextual Aliases for visual variety
SEGMENT_ALIASES = {
    "Revenue": {
        "Champions": "Top 1% Spenders",
        "Loyalists": "Steady Income",
        "Occasional Shoppers": "Low Ticket",
        "Needs Attention": "Revenue Bleed"
    },
    "Activity": {
        "Champions": "Super Active",
        "Loyalists": "Weekly Visitors",
        "Occasional Shoppers": "One-Time Visits",
        "Needs Attention": "Dormant Users"
    },
    "Risk": {
        "Champions": "Secure",
        "Loyalists": "Stable",
        "Occasional Shoppers": "Uncertain",
        "Needs Attention": "High Flight Risk"
    }
}

# Advanced Color Scales for Heatmaps/Gradients
COLOR_SCALES = {
    "primary": [[0, '#121212'], [0.5, '#2c2c2c'], [1, '#424242']], # Minimalist Dark
    "diverging": "RdBu",
    "sequential_purple": "Purples",
    "sequential_cyan": "Blues"
}

# Recommendations (Updated Keys)
RECOMMENDATIONS = {
    "Champions": {
        "priority": "🔥 HIGH PRIORITY",
        "actions": [
            "Invite to exclusive 'Black Card' beta program",
            "Assign dedicated 24/7 concierge support",
            "Send personalized annual impact report",
            "Offer equity/investment tier rewards"
        ],
        "expected_impact": "20-30% CLV Increase"
    },
    "Loyalists": {
        "priority": "⚡ OPPORTUNITY",
        "actions": [
            "Gamify loyalty points (Double XP days)",
            "Unlock early access to flash sales",
            "Incentivize video reviews/UGC",
            "Create 'Brand Ambassador' badges"
        ],
        "expected_impact": "15% Order Frequency Boost"
    },
    "Needs Attention": {
        "priority": "🚨 CRITICAL ALERT",
        "actions": [
            "Trigger 'We Miss You' dynamic discount flow",
            "Offer free shipping on next single order",
            "Survey: 'What went wrong?' for feedback",
            "Retargeting ads with high-converting items"
        ],
        "expected_impact": "Recover 35% of Churn Risk"
    },
    "Occasional Shoppers": {
        "priority": "🌱 INCUBATE",
        "actions": [
            "Bundle offers to increase Basket Size",
            "Educational drip campaign on product value",
            " Social proof popup implementation",
            "Limited time entry-level discounts"
        ],
        "expected_impact": "10% AOV Growth"
    }
}
