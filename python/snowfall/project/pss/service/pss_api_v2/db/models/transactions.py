from sqlalchemy import DECIMAL, Boolean, Column, Date, Integer, String

from snowfall.project.pss.service.pss_api_v2.db.db import Base


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    external_id = Column(String)
    external_reference = Column(String)
    stripe_token = Column(String)
    stripe_email = Column(String)
    stripe_charge = Column(String)
    token = Column(String, nullable=False)
    channel = Column(String)
    transaction_status_id = Column(Integer, nullable=False)
    invoiced = Column(Boolean, default=False)
    psp_id = Column(Integer, nullable=False, default=1)
    products_token = Column(String)
    payment_type_id = Column(Integer)
    affiliate_id = Column(Integer)
    account_id = Column(Integer)
    booking_id = Column(Integer)
    booking_reference = Column(String)
    agreement_id = Column(Integer)
    reference = Column(String)
    amount = Column(DECIMAL)
    net = Column(DECIMAL)
    vat = Column(DECIMAL)
    tax = Column(DECIMAL, default=0)
    outbound_date = Column(Date)
    outbound_origin_id = Column(Integer)
    outbound_destination_id = Column(Integer)
    outbound_schedule_id = Column(Integer)
    outbound_product_id = Column(Integer)
    inbound_date = Column(Date)
    inbound_origin_id = Column(Integer)
    inbound_destination_id = Column(Integer)
    inbound_schedule_id = Column(Integer)
    inbound_product_id = Column(Integer)
    refund = Column(Boolean, nullable=False, default=False)
    payment_pending = Column(Boolean, nullable=False, default=False)
    payed_date = Column(Integer)
    created = Column(Integer)
    modified = Column(Integer)


class TransactionStatus(Base):
    __tablename__ = "transaction_statuses"
    id = Column(Integer, primary_key=True)
