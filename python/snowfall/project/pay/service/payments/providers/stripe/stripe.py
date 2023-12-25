import stripe

from snowfall.project.pay.service.payments.providers import interfaces
from snowfall.project.pay.service.payments.providers.stripe import repositories
from snowfall.project.pay.service.payments.v1 import credit_card_models_pb2
from snowfall.stdlib import money


class Stripe(interfaces.CreditCardProvider):
    def __init__(
        self,
        stripe_users: repositories.PaymentUsersRepository,
        stripe_version: str,
    ):
        self._stripe_users = stripe_users
        self._stripe_version = stripe_version

    def get_credit_card_payment(
        self,
        payment_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment:
        """Retrieve payment intent."""
        payment_intent = stripe.PaymentIntent.retrieve(payment_id)
        intent_money = money.from_string(
            str(payment_intent.amount),
            money.Currency(payment_intent.currency),
        )

        return credit_card_models_pb2.CreditCardPayment(
            id=payment_intent.stripe_id or "",
            amount=intent_money.protobuf(),
            capture_method=payment_intent.capture_method,
            credit_card_holder_id=payment_intent.customer or "",  # type: ignore[arg-type]
            enable_automatic_payment_method=payment_intent.automatic_payment_methods.eabled,  # type: ignore[union-attr]
        )

    def create_credit_card_payment(
        self,
        payment: credit_card_models_pb2.CreditCardPayment,
    ) -> credit_card_models_pb2.CreditCardPayment:
        """Create payment intent in stripe."""
        intent_money = money.from_protobuf(payment.amount)
        payment_intent = stripe.PaymentIntent.create(
            amount=intent_money.amount,
            currency=intent_money.currency.code,
            capture_method=payment.capture_method,
            customer=payment.credit_card_holder_id,
            automatic_payment_methods={
                "enabled": payment.enable_automatic_payment_method,
            },
        )

        payment.id = payment_intent.stripe_id or ""

        return payment

    async def get_credit_card_holder(
        self,
        user_id: str,
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        """Get customer id and ephemeral key."""
        stripe_user = await self._stripe_users.get(user_id)
        credit_card_holder = credit_card_models_pb2.CreditCardHolder()
        ephemeral_key_secret = ""
        if stripe_user:
            ephemeral_key_secret = stripe.EphemeralKey.create(  # type: ignore[no-untyped-call]
                customer=stripe_user.id,
                stripe_version=self._stripe_version,
            ).secret

            credit_card_holder.id = stripe_user.id
            credit_card_holder.version = self._stripe_version

        return credit_card_holder, ephemeral_key_secret

    async def create_credit_card_holder(
        self,
        user_id: str,
        credit_card_holder: credit_card_models_pb2.CreditCardHolder,
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        """Create Customer in stripe and save the id in the DB."""
        customer = stripe.Customer.create(
            email=credit_card_holder.email,
            name=credit_card_holder.name,
        )

        stripe_user = credit_card_models_pb2.PaymentUser(
            id=customer.stripe_id or "",
            internal_user_id=user_id,
        )

        await self._stripe_users.insert(stripe_user)

        ephemeral_key_secret = stripe.EphemeralKey.create(  # type: ignore[no-untyped-call]
            customer=customer.stripe_id,
            stripe_version=self._stripe_version,
        ).secret

        credit_card_holder.id = customer.stripe_id or ""
        credit_card_holder.version = self._stripe_version

        return credit_card_holder, ephemeral_key_secret
