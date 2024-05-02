from collections.abc import Mapping
from typing import Literal, TypeGuard

import stripe

from snowfall.project.pay.service.payments.providers import interfaces
from snowfall.project.pay.service.payments.providers.stripe import repositories
from snowfall.project.pay.service.payments.v1 import credit_card_models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.logging import stdout

_logger = stdout.get_logger()


class Stripe(interfaces.CreditCardProvider):
    def __init__(
        self,
        stripe_users: repositories.PaymentUsersRepository,
        stripe_version: str,
        stripe_key: str,
    ):
        self._stripe_users = stripe_users
        self._stripe_version = stripe_version
        self._stripe_key = stripe_key
        stripe.api_key = stripe_key

    @property
    def name(self) -> str:
        return "stripe"

    def get_credit_card_payment(
        self,
        payment_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Retrieve payment intent."""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_id)
        except stripe._error.InvalidRequestError:  # noqa: SLF001
            return None
        intent_money = money.Money(
            payment_intent.amount,
            money.Currency(payment_intent.currency.upper()),
        )
        allow_redirect = ""
        if payment_intent.automatic_payment_methods:
            allow_redirect = payment_intent.automatic_payment_methods.get(
                "allow_redirects",
                "always",
            )

        return credit_card_models_pb2.CreditCardPayment(
            id=payment_intent.id,
            amount=intent_money.protobuf(),
            capture_method=payment_intent.capture_method,
            credit_card_holder_id=payment_intent.customer or "",  # type: ignore[arg-type]
            enable_automatic_payment_method=payment_intent.automatic_payment_methods[
                "enabled"
            ],  # type: ignore[index]
            allow_redirect=allow_redirect,
            secret=payment_intent.client_secret or "",
            status=payment_intent.status,
        )

    def create_credit_card_payment(  # noqa: WPS231
        self,
        payment: credit_card_models_pb2.CreditCardPayment,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Create payment intent in stripe."""
        if not self._is_valid_capture_method(payment.capture_method):
            raise ValueError

        automatic_payment_methods: stripe.PaymentIntent.CreateParamsAutomaticPaymentMethods = {
            "enabled": payment.enable_automatic_payment_method,
        }
        if self._is_valid_allow_redirect(payment.allow_redirect):
            automatic_payment_methods["allow_redirects"] = payment.allow_redirect
        elif payment.allow_redirect != "":
            raise ValueError

        intent_money = money.from_protobuf(payment.amount)
        if payment.credit_card_holder_id:
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=intent_money.amount,
                    currency=intent_money.currency.code,
                    capture_method=payment.capture_method,
                    customer=payment.credit_card_holder_id,
                    automatic_payment_methods=automatic_payment_methods,
                )
            except stripe._error.InvalidRequestError:  # noqa: SLF001
                return None
        else:
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=intent_money.amount,
                    currency=intent_money.currency.code,
                    capture_method=payment.capture_method,
                    automatic_payment_methods={
                        "enabled": payment.enable_automatic_payment_method,
                    },
                )
            except stripe._error.InvalidRequestError:  # noqa: SLF001
                return None

        payment.id = payment_intent.id
        payment.secret = payment_intent.client_secret or ""
        payment.status = payment_intent.status

        return payment

    def update_credit_card_payment(
        self,
        payment_id: str,
        amount: money.Money | None,
        receipt_email: str | None,
        metadata: Mapping[str, str] | None,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        try:
            updated_payment_intent = stripe.PaymentIntent.modify(
                payment_id,
                amount=amount.amount if amount else None,  # type: ignore[arg-type]
                receipt_email=receipt_email,  # type: ignore[arg-type]
                metadata=metadata,  # type: ignore[arg-type]
            )
        except stripe._error.InvalidRequestError:  # noqa: SLF001
            return None

        allow_redirect = ""
        if updated_payment_intent.automatic_payment_methods:
            allow_redirect = updated_payment_intent.automatic_payment_methods.get(
                "allow_redirects",
                "always",
            )

        return credit_card_models_pb2.CreditCardPayment(
            id=updated_payment_intent.id,
            amount=amount if amount is None else amount.protobuf(),
            capture_method=updated_payment_intent.capture_method,
            credit_card_holder_id=updated_payment_intent.customer or "",  # type: ignore[arg-type]
            enable_automatic_payment_method=updated_payment_intent.automatic_payment_methods[
                "enabled"
            ],  # type: ignore[index]
            allow_redirect=allow_redirect,
            secret=updated_payment_intent.client_secret or "",
            status=updated_payment_intent.status,
        )

    def cancel_credit_card_payment(
        self,
        payment_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        try:
            payment_intent = stripe.PaymentIntent.cancel(payment_id)
        except stripe.InvalidRequestError:
            return None

        intent_money = money.Money(
            payment_intent.amount,
            money.Currency(payment_intent.currency.upper()),
        )

        allow_redirect = ""
        if payment_intent.automatic_payment_methods:
            allow_redirect = payment_intent.automatic_payment_methods.get(
                "allow_redirects",
                "always",
            )

        return credit_card_models_pb2.CreditCardPayment(
            id=payment_intent.id,
            amount=intent_money.protobuf(),
            capture_method=payment_intent.capture_method,
            credit_card_holder_id=payment_intent.customer or "",  # type: ignore[arg-type]
            enable_automatic_payment_method=payment_intent.automatic_payment_methods[
                "enabled"
            ],  # type: ignore[index]
            allow_redirect=allow_redirect,
            secret=payment_intent.client_secret or "",
            status=payment_intent.status,
        )

    def capture_credit_card_payment(
        self,
        payment_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        try:
            payment_intent = stripe.PaymentIntent.capture(payment_id)
        except stripe.InvalidRequestError:
            return None

        intent_money = money.Money(
            payment_intent.amount,
            money.Currency(payment_intent.currency.upper()),
        )

        allow_redirect = ""
        if payment_intent.automatic_payment_methods:
            allow_redirect = payment_intent.automatic_payment_methods.get(
                "allow_redirects",
                "always",
            )

        return credit_card_models_pb2.CreditCardPayment(
            id=payment_intent.id,
            amount=intent_money.protobuf(),
            capture_method=payment_intent.capture_method,
            credit_card_holder_id=payment_intent.customer or "",  # type: ignore[arg-type]
            enable_automatic_payment_method=payment_intent.automatic_payment_methods[
                "enabled"
            ],  # type: ignore[index]
            allow_redirect=allow_redirect,
            secret=payment_intent.client_secret or "",
            status=payment_intent.status,
        )

    def process_credit_card_payment(
        self,
        payment_id: str,
        payment_method_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        try:
            payment_intent = stripe.PaymentIntent.confirm(
                payment_id,
                payment_method=payment_method_id,
            )
        except stripe.InvalidRequestError:
            return None

        intent_money = money.Money(
            payment_intent.amount,
            money.Currency(payment_intent.currency.upper()),
        )

        allow_redirect = ""
        if payment_intent.automatic_payment_methods:
            allow_redirect = payment_intent.automatic_payment_methods.get(
                "allow_redirects",
                "always",
            )

        return credit_card_models_pb2.CreditCardPayment(
            id=payment_intent.id,
            amount=intent_money.protobuf(),
            capture_method=payment_intent.capture_method,
            credit_card_holder_id=payment_intent.customer or "",  # type: ignore[arg-type]
            enable_automatic_payment_method=payment_intent.automatic_payment_methods[
                "enabled"
            ],  # type: ignore[index]
            allow_redirect=allow_redirect,
            secret=payment_intent.client_secret or "",
            status=payment_intent.status,
        )

    async def get_credit_card_holder(
        self,
        user_id: str,
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        """Get customer id and ephemeral key."""
        stripe_user = await self._stripe_users.get(user_id)
        credit_card_holder = credit_card_models_pb2.CreditCardHolder()
        ephemeral_key_secret = ""
        if stripe_user:
            customer = stripe.Customer.retrieve(stripe_user.id)
            ephemeral_key_secret = stripe.EphemeralKey.create(  # type: ignore[no-untyped-call]
                customer=stripe_user.id,
                stripe_version=self._stripe_version,
            ).secret

            credit_card_holder.id = stripe_user.id
            credit_card_holder.version = self._stripe_version
            credit_card_holder.email = customer.email or ""
            credit_card_holder.name = customer.name or ""

        return credit_card_holder, ephemeral_key_secret

    async def get_setup_client_secret(
        self,
        customer_id: str,
    ) -> str | None:
        try:
            client_secret = stripe.SetupIntent.create(
                customer=customer_id,
                automatic_payment_methods={"enabled": True},
            ).client_secret
        except stripe.StripeError:
            client_secret = None

        return client_secret

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
            id=customer.id,
            internal_user_id=user_id,
        )

        await self._stripe_users.insert(stripe_user)

        ephemeral_key_secret = stripe.EphemeralKey.create(  # type: ignore[no-untyped-call]
            customer=customer.id,
            stripe_version=self._stripe_version,
        ).secret

        credit_card_holder.id = customer.id
        credit_card_holder.version = self._stripe_version

        return credit_card_holder, ephemeral_key_secret

    def create_refund(
        self,
        amount: int,
        credit_card_payment_id: str,
    ) -> credit_card_models_pb2.Refund | None:
        """Create refund in stripe."""
        try:
            stripe_refund = stripe.Refund.create(
                amount=amount,
                payment_intent=credit_card_payment_id,
            )
        except stripe.StripeError:
            return None

        return credit_card_models_pb2.Refund(
            external_reference_id=stripe_refund.stripe_id,  # type: ignore[arg-type]
            credit_card_payment_id=credit_card_payment_id,
            amount=money.Money(
                amount=amount,
                currency=money.Currency(stripe_refund["currency"].upper()),
            ).protobuf(),
        )

    def get_refund(
        self,
        external_reference_id: str,
    ) -> credit_card_models_pb2.Refund | None:
        """Get refund from stripe."""
        try:
            stripe_refund = stripe.Refund.retrieve(external_reference_id)
        except stripe.StripeError:
            return None

        return credit_card_models_pb2.Refund(
            external_reference_id=stripe_refund.stripe_id,  # type: ignore[arg-type]
            credit_card_payment_id=stripe_refund["payment_intent"],
            amount=money.Money(
                amount=int(stripe_refund["amount"]),
                currency=money.Currency(stripe_refund["currency"].upper()),
            ).protobuf(),
        )

    def get_payment_method(self, payment_id: str) -> str:
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_id)
        except stripe.StripeError:
            return ""

        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=payment_intent.customer,  # type: ignore[arg-type]
                type="card",
            )
        except stripe.StripeError:
            return ""
        payment_card_methods = payment_methods["data"]

        if not payment_card_methods:
            _logger.error("There is no attached payment method", payment_id=payment_id)
            return ""

        if len(payment_card_methods) > 1:
            _logger.error(
                "Attached more than one payment methods",
                payment_id=payment_id,
            )
            return ""

        return payment_card_methods[0].id  # type: ignore[index]

    def _is_valid_capture_method(
        self,
        value: str,
    ) -> TypeGuard[Literal["automatic", "automatic_async", "manual"]]:
        return value in {"automatic", "automatic_async", "manual"}

    def _is_valid_allow_redirect(
        self,
        value: str,
    ) -> TypeGuard[Literal["never", "always"]]:
        return value in {"never", "always"}
