import enum


class PaymentMethod(enum.Enum):
    demand_note = "demand_note"
    credit_card = "credit_card"
    sepa_direct_debit = "sepa_direct_debit"
    paypal = "paypal"
