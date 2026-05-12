"""Constants used across the library.

Central registry for bank codes, UPI app mappings, IFSC prefixes,
date formats, and category keywords.
"""

from __future__ import annotations

# ── Bank Registry ────────────────────────────────────────────────────

SUPPORTED_BANKS: dict[str, str] = {
    "SBI": "State Bank of India",
    "HDFC": "HDFC Bank",
    "ICICI": "ICICI Bank",
    "AXIS": "Axis Bank",
}

# ── Unified Column Names ─────────────────────────────────────────────

UNIFIED_COLUMNS: list[str] = [
    "date",
    "value_date",
    "narration",
    "description",
    "amount",
    "withdrawal",
    "deposit",
    "closing_balance",
    "type",
    "payment_method",
    "category",
    "upi_merchant",
    "upi_app",
    "upi_vpa",
    "upi_ref",
    "upi_counterparty_bank",
    "balance_verified",
]

# ── Date Formats by Bank ─────────────────────────────────────────────

DATE_FORMATS: dict[str, list[str]] = {
    "SBI": ["%d/%m/%Y", "%d-%m-%Y", "%d %b %Y"],
    "HDFC": ["%d/%m/%y", "%d/%m/%Y", "%d-%m-%Y"],
    "ICICI": ["%d-%m-%Y", "%d/%m/%Y", "%d-%b-%Y"],
    "AXIS": ["%d-%m-%Y", "%d/%m/%Y"],
    "DEFAULT": ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %b %Y", "%d-%b-%Y"],
}

# ── VPA Suffix → UPI App Mapping ─────────────────────────────────────

VPA_APP_MAPPING: dict[str, str] = {
    # Google Pay
    "@okaxis": "Google Pay",
    "@okhdfcbank": "Google Pay",
    "@okicici": "Google Pay",
    "@oksbi": "Google Pay",
    "@okbizaxis": "Google Pay",
    "@axl": "Google Pay",
    # PhonePe
    "@ybl": "PhonePe",
    "@ibl": "PhonePe",
    "@axisb": "PhonePe",
    # Paytm
    "@paytm": "Paytm",
    # BHIM
    "@upi": "BHIM",
    # Amazon Pay
    "@apl": "Amazon Pay",
    "@yapl": "Amazon Pay",
    # WhatsApp Pay
    "@icici": "WhatsApp Pay",
    # CRED
    "@axisbank": "CRED",
    # Slice
    "@slc": "Slice",
    # Freecharge
    "@freecharge": "Freecharge",
    # MobiKwik
    "@ikwik": "MobiKwik",
    # Jupiter
    "@jupiteraxis": "Jupiter",
    # Fi Money
    "@fi": "Fi Money",
    # Bank direct
    "@sbi": "SBI Direct",
    "@yesbank": "Yes Bank Direct",
    "@hdfcbank": "HDFC Direct",
}

# ── IFSC Prefix → Bank Name Mapping ──────────────────────────────────

IFSC_BANK_MAPPING: dict[str, str] = {
    "SBIN": "State Bank of India",
    "HDFC": "HDFC Bank",
    "ICIC": "ICICI Bank",
    "UTIB": "Axis Bank",
    "KKBK": "Kotak Mahindra Bank",
    "YESB": "Yes Bank",
    "IDFB": "IDFC First Bank",
    "PUNB": "Punjab National Bank",
    "BARB": "Bank of Baroda",
    "CNRB": "Canara Bank",
    "UBIN": "Union Bank of India",
    "BKID": "Bank of India",
    "IOBA": "Indian Overseas Bank",
    "CBIN": "Central Bank of India",
    "INDB": "IndusInd Bank",
    "RATN": "RBL Bank",
    "FDRL": "Federal Bank",
    "SIBL": "South Indian Bank",
    "KVBL": "Karur Vysya Bank",
    "CITI": "Citibank",
    "HSBC": "HSBC",
    "SCBL": "Standard Chartered",
    "DBSS": "DBS Bank",
    "JAKA": "J&K Bank",
}

# ── Payment Method Detection Patterns ────────────────────────────────

PAYMENT_METHOD_PATTERNS: dict[str, list[str]] = {
    "UPI": ["UPI", "UPI-"],
    "NEFT": ["NEFT", "NEFT-"],
    "RTGS": ["RTGS", "RTGS-"],
    "IMPS": ["IMPS", "IMPS-"],
    "ACH": ["ACH", "ACH D-", "ACH C-", "NACH"],
    "ATM": ["ATM", "ATM-WDL", "ATM WDL", "CASH WDL"],
    "POS": ["POS", "POS-"],
    "CHEQUE": ["CHQ", "CHEQUE", "CLG"],
    "INTEREST": ["INT.PAID", "INTEREST", "INT PAID", "CR INTEREST"],
    "CHARGE": ["CHARGES", "SMS CHRG", "MIN BAL", "SERVICE CHARGE"],
}

# ── Category Keywords ────────────────────────────────────────────────
# Maps keywords found in narration/merchant to categories

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Food": [
        "ZOMATO",
        "SWIGGY",
        "DOMINOS",
        "PIZZA",
        "MCDONALD",
        "KFC",
        "BURGER",
        "RESTAURANT",
        "FOOD",
        "CAFE",
        "HOTEL",
        "HOSPITALITY",
        "BIRYANI",
        "KITCHEN",
        "DHABA",
        "BAKERY",
        "SWEET",
        "JUICE",
        "CHAI",
    ],
    "Groceries": [
        "BIGBASKET",
        "BLINKIT",
        "ZEPTO",
        "DMART",
        "GROFERS",
        "JIOMART",
        "GROCERY",
        "SUPERMARKET",
        "RELIANCE FRESH",
        "MORE RETAIL",
        "NATURE'S BASKET",
        "STAR BAZAAR",
    ],
    "Shopping": [
        "AMAZON",
        "FLIPKART",
        "MYNTRA",
        "AJIO",
        "NYKAA",
        "MEESHO",
        "SNAPDEAL",
        "SHOPCLUES",
        "TATA CLIQ",
        "RELIANCE",
    ],
    "Transport": [
        "OLA",
        "UBER",
        "RAPIDO",
        "METRO",
        "IRCTC",
        "RAILWAY",
        "REDBUS",
        "IXIGO",
        "MAKEMYTRIP",
        "GOIBIBO",
        "CLEARTRIP",
    ],
    "Fuel": [
        "PETROL",
        "DIESEL",
        "FUEL",
        "HPCL",
        "BPCL",
        "IOCL",
        "INDIAN OIL",
        "HP PETROL",
        "BHARAT PETROLEUM",
    ],
    "EMI": [
        "EMI",
        "LOAN",
        "BAJAJ FINANCE",
        "HDFC LTD",
        "HOME LOAN",
        "CAR LOAN",
        "PERSONAL LOAN",
    ],
    "Salary": [
        "SALARY",
        "SAL CR",
        "PAYROLL",
        "STIPEND",
        "WAGES",
    ],
    "Investment": [
        "MUTUAL FUND",
        "MF",
        "PRUDENT",
        "ZERODHA",
        "GROWW",
        "UPSTOX",
        "KUVERA",
        "SIP",
        "COIN",
        "DEMAT",
        "CAMS",
        "KARVY",
    ],
    "Insurance": [
        "LIC",
        "INSURANCE",
        "PREMIUM",
        "POLICY",
        "ICICI LOMBARD",
        "HDFC ERGO",
        "STAR HEALTH",
        "MAX LIFE",
    ],
    "Utilities": [
        "ELECTRICITY",
        "WATER",
        "GAS",
        "TORRENT",
        "ADANI",
        "BESCOM",
        "MSEDCL",
        "BILL",
        "BROADBAND",
        "WIFI",
        "INTERNET",
    ],
    "Recharge": [
        "RECHARGE",
        "JIO",
        "AIRTEL",
        "VI ",
        "VODAFONE",
        "BSNL",
        "PREPAID",
        "POSTPAID",
        "MOBILE",
    ],
    "Entertainment": [
        "NETFLIX",
        "HOTSTAR",
        "PRIME VIDEO",
        "SPOTIFY",
        "YOUTUBE",
        "BOOKMYSHOW",
        "PVR",
        "INOX",
        "MOVIE",
        "GAME",
    ],
    "Medical": [
        "PHARMACY",
        "MEDICAL",
        "HOSPITAL",
        "DOCTOR",
        "APOLLO",
        "MEDPLUS",
        "1MG",
        "PHARMEASY",
        "NETMEDS",
        "CLINIC",
    ],
    "Education": [
        "SCHOOL",
        "COLLEGE",
        "UNIVERSITY",
        "TUITION",
        "COACHING",
        "UDEMY",
        "COURSERA",
        "UNACADEMY",
        "BYJU",
    ],
    "Rent": [
        "RENT",
        "HOUSE RENT",
        "FLAT RENT",
    ],
    "ATM Withdrawal": [
        "ATM",
        "CASH WDL",
        "ATM WDL",
    ],
    "Charges": [
        "CHARGES",
        "SMS CHRG",
        "MIN BAL CHRG",
        "SERVICE CHARGE",
        "ANNUAL FEE",
        "MAINTENANCE",
    ],
    "Interest": [
        "INTEREST",
        "INT.PAID",
        "INT CREDIT",
    ],
    "Government": [
        "TAX",
        "GST",
        "INCOME TAX",
        "TDS",
        "GOVT",
        "STAMP DUTY",
        "CHALLAN",
        "MCA",
        "EPFO",
        "PF",
    ],
}

# ── Amount Cleaning ──────────────────────────────────────────────────

# Characters to strip from amount strings before parsing
AMOUNT_STRIP_CHARS = [",", " ", "₹", "INR", "Rs.", "Rs"]
