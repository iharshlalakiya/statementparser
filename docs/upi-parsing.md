# UPI Parsing

The UPI parser extracts structured metadata from UPI narration strings.

## Input Format

```
UPI-Hari Enterprises-gpay-11244530509@okbizaxis-UTIB0000553-121864632957-UPI
Value Dt 19/04/2026 Ref 121864632957
```

## Output

```python
UPIDetail(
    merchant="Hari Enterprises",
    app="Google Pay",
    vpa="11244530509@okbizaxis",
    ifsc="UTIB0000553",
    counterparty_bank="Axis Bank",
    upi_ref="121864632957",
    phone=None,
)
```

## VPA → App Mapping

| VPA Suffix | App |
|-----------|-----|
| `@ybl` | PhonePe |
| `@okbizaxis`, `@okaxis`, `@oksbi` | Google Pay |
| `@paytm` | Paytm |
| `@slc` | Slice |
| `@upi` | BHIM |
| `@apl`, `@yapl` | Amazon Pay |
| `@yesbank` | Yes Bank Direct |

## IFSC → Bank Mapping

The first 4 characters of an IFSC code identify the bank:
- `SBIN` → State Bank of India
- `HDFC` → HDFC Bank
- `UTIB` → Axis Bank
- `YESB` → Yes Bank
- `CBIN` → Central Bank of India
- ... and 20+ more
