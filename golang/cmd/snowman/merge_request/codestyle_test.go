package merge_request

import (
	"errors"
	"github.com/xanzy/go-gitlab"
	"testing"
)

func TestFindLinesWithNewIgnores(t *testing.T) {
	diff := gitlab.Diff{
		Diff: `@@ -5,6 +5,7 @@ from typing import cast
 import grpc
 from pymongo.errors import DuplicateKeyError

+from snowfall.project.junction.go.adapter.errors import NotFoundError
 from snowfall.project.pay.adapter import currencies
 from snowfall.project.pay.service.companies import repositories
 from snowfall.project.pay.service.companies.v1alpha import (
@@ -340,34 +341,46 @@ class BeneficiariesService(  # noqa: WPS214
         request: grpc_pb2.CreateBeneficiaryRequest,
         context: grpc.aio.ServicerContext,
     ) -> grpc_pb2.CreateBeneficiaryResponse:
-        await self._currencies_client.get(request.beneficiary.currency)
+        try:
+            await self._currencies_client.get(request.beneficiary.currency)
+        except NotFoundError:
+            await rich_status.abort_with_rich_status(
+                context=context,
+                status=rich_status.build_bad_request(
+                    field_name="currency",
+                    field_description="Currency not supported",
+                ),
+            )
         account = await self._accounts.find_by_id(request.beneficiary.account_id)
         if not account:
             await rich_status.abort_with_rich_status(
                 context=context,
                 status=rich_status.build_bad_request(
                     field_name="account_id",
-                    field_description="Account is not found",
+                    field_description="Account not found",
                 ),
             )

         company = await self._companies.find_by_id(account.company_id)

         if not company:
-            await context.abort(
-                grpc.StatusCode.INVALID_ARGUMENT,
-                details="Company is not found",
+            await rich_status.abort_with_rich_status(
+                context=context,
+                status=rich_status.build_bad_request(
+                    field_name="account.company_id",
+                    field_description="Company not found",
+                ),
             )

         beneficiary_validate_request = self._get_beneficiary_validate_model(
             request.beneficiary.currency,
             request.beneficiary.meta_data,
-            company_name=company.name,  # type: ignore[union-attr]
+            company_name=company.name,
         )
         beneficiary_request = self._get_beneficiary_model(
             request.beneficiary.meta_data,
             beneficiary_validate_request,
-            company_name=company.name,  # type: ignore[union-attr]
+            company_name=company.name,
         )

         try:  # noqa: WPS229
@@ -399,54 +412,67 @@ class BeneficiariesService(  # noqa: WPS214
                 currency=created_beneficiary.currency,
             ),
         )
+        beneficiary.MergeFrom(request.beneficiary)

         return grpc_pb2.CreateBeneficiaryResponse(beneficiary=beneficiary)

-    async def UpdateBeneficiary(  # type: ignore[override] # noqa: N802, WPS217, WPS210, WPS231
+    async def UpdateBeneficiary(  # type: ignore[override] # noqa: N802, WPS217, WPS210, WPS231, WPS213
         self,
         request: grpc_pb2.UpdateBeneficiaryRequest,
         context: grpc.aio.ServicerContext,
     ) -> grpc_pb2.UpdateBeneficiaryResponse:
         beneficiary = await self._beneficiaries.find_by_id(request.beneficiary.id)
-        if not beneficiary:
+        if beneficiary is None:
             await context.abort(grpc.StatusCode.NOT_FOUND)

+        beneficiary = cast(models_pb2.Beneficiary, beneficiary)
+
         if (  # noqa: WPS337
             request.beneficiary.currency
-            and request.beneficiary.currency != beneficiary.currency  # type: ignore[union-attr]
+            and request.beneficiary.currency != beneficiary.currency
         ):
-            await self._currencies_client.get(request.beneficiary.currency)
+            try:
+                await self._currencies_client.get(request.beneficiary.currency)
+            except NotFoundError:
+                await rich_status.abort_with_rich_status(
+                    context=context,
+                    status=rich_status.build_bad_request(
+                        field_name="currency",
+                        field_description="Currency not supported",
+                    ),
+                )
         company_name = None
         if (  # noqa: WPS337
             request.beneficiary.account_id
-            and request.beneficiary.account_id != beneficiary.account_id  # type: ignore[union-attr]
+            and request.beneficiary.account_id != beneficiary.account_id
         ):
-            account = await self._accounts.find_by_id(
-                request.beneficiary.account_id,
-            )
+            account = await self._accounts.find_by_id(request.beneficiary.account_id)
             if not account:
                 await rich_status.abort_with_rich_status(
                     context=context,
                     status=rich_status.build_bad_request(
                         field_name="account_id",
-                        field_description="Account is not found",
+                        field_description="Account not found",
                     ),
                 )

             company = await self._companies.find_by_id(account.company_id)
             if not company:
-                await context.abort(
-                    grpc.StatusCode.INVALID_ARGUMENT,
-                    details="Company is not found",
+                await rich_status.abort_with_rich_status(
+                    context=context,
+                    status=rich_status.build_bad_request(
+                        field_name="account.company_id",
+                        field_description="Company not found",
+                    ),
                 )
-            company_name = company.name  # type: ignore[union-attr]
+            company_name = company.name

         if request.beneficiary.HasField("meta_data"):
             beneficiary_validate_request = self._get_beneficiary_validate_model(
                 (
                     request.beneficiary.currency
                     if request.beneficiary.currency
-                    else beneficiary.currency  # type: ignore[union-attr]
+                    else beneficiary.currency
                 ),
                 request.beneficiary.meta_data,
                 company_name=company_name,
@@ -458,17 +484,18 @@ class BeneficiariesService(  # noqa: WPS214
             )

             await self._payment_client.update_beneficiary(
-                beneficiary_id=beneficiary.external_reference,  # type: ignore[union-attr]
+                beneficiary_id=beneficiary.external_reference,
                 new_beneficiary=beneficiary_request,
             )

-        request.beneficiary.ClearField("meta_data")
-        beneficiary.MergeFrom(request.beneficiary)  # type: ignore[union-attr]
+        beneficiary.MergeFrom(request.beneficiary)
+        beneficiary.ClearField("meta_data")

         await self._beneficiaries.update(
-            beneficiary.id,  # type: ignore[union-attr]
-            beneficiary,  # type: ignore[arg-type]
+            beneficiary.id,
+            beneficiary,
         )
+        beneficiary.MergeFrom(request.beneficiary)

         return grpc_pb2.UpdateBeneficiaryResponse(beneficiary=beneficiary)

@@ -480,7 +507,9 @@ class BeneficiariesService(  # noqa: WPS214
         beneficiary = await self._beneficiaries.find_by_id(request.id)

         if not beneficiary:
-            await context.abort(grpc.StatusCode.NOT_FOUND)
+            await context.abort(
+                grpc.StatusCode.NOT_FOUND,
+            )

         cc_beneficiary = await self._payment_client.get_beneficiary(
             beneficiary_id=beneficiary.external_reference,  # type: ignore[union-attr]`,
		NewPath:     "python/snowfall/project/pay/service/companies/grpc.py",
		OldPath:     "python/snowfall/project/pay/service/companies/grpc.py",
		AMode:       "100644",
		BMode:       "100644",
		NewFile:     false,
		RenamedFile: false,
		DeletedFile: false,
	}

	lines, err := FindLinesWithNewIgnores(diff)

	if err != nil {
		t.Error(err)
	}

	if len(lines) != 1 || lines[0].LineNumber != 417 {
		t.Error(errors.New("received an unexpected diff"))
	}
}
