# Junction Pay

## Overview

Junction Pay is the Junction's clearing house and handles all finance-related responsibilities between all the participants in Junction marketplace (for eg. providers and resellers). It is a part of Junction Go, and exposes its functionality over gRPC.\
Resellers can order based on their multi-modal travel offers they have received from Snowfall. This would be a single-payment per order. Each Order is a bundle of Bookings from various providers (as it could be multimodal travel) and also potentially other services. Snowfall maintains commercial relationships with each reseller and each provider and is able to include details of previously-existing relationships between them within the platform configuration, as needed.\
So essentially Junction Pay enables smooth receiving, managing and settlement of funds.

## Vision

Junction Pay aims to introduce a modern fintech approach to settlements in the travel industry with smooth payments and low fees.
The guiding principle of Junction’s payment solution is to provide a secure, transparent and flexible platform with a modular services approach.

Reseller | Provider
--- | ---
Receive client funds in multiple currencies | No integration required
All transaction details in one platform | Minimal onboarding
Instant FX to lock in market rate | Single invoice per duration
Seamless payment of invoices | Receive single payment for multiple resellers
Maintain existing relationships | Invoice payable in multiple currencies
Automate admin overheads for accounts payable | No integration required

## Concepts

### Quotation

Junction uses the term *Quotation* for the potential pricing which could eventually change to actual payments. The currency used by the Provider and the Reseller could differ. In this case we would need to convert the Provider price from a particular currency to a Reseller price in their own supported currency. This would require FX rate comparisons and hence called a quotation, as it would be fixed but valid only for a certain time. This (Snowfall) Quotation will have Provider price plus added costs like FX margins, related taxes and expenses.
Each reseller will have a different configuration for the price calculation depending on different margins set for each. A Quotation is valid for 15 minutes from the time it has been created ans session tokens are used to keep the same value for the duration of the quotation validity.

### Transaction

A *Bill* is similar to what is an *Order* at Junction GO side.\
As an *Order* has multiple *Bookings*, similarly, a *Bill* has many *Transactions*. So a *Transaction* is similar to a *Booking*.

```mermaid
    flowchart LR
    subgraph Junction GO
        subgraph Order
            B1(Booking1)
            B2(Booking2)
            B3(Booking3)
        end
    end

    subgraph Junction Pay
        subgraph Bill
            T1(Transaction1)
            T2(Transaction2)
            T3(Transaction3)
        end
    end
    B1<-->T1
    B2<-->T2
    B3<-->T3

```

## Junction Pay System Flow Diagram

```mermaid
    flowchart LR

        subgraph Client
            HA(Hub API)
            CA(Client API)
            MA(Mobile API)
        end

        users[(Users DB)]
        subgraph Authenticator
        O(ORY)
        end

        HA-->O
        CA-->O
        MA-->|user auth|users
        Client-->H

        subgraph AuthenticationServices
            Auth(Auth)
        end

        H(Adapters)

        H-->Vault
        H-->Auth
        H-->JG(Junction GO)
        H-->MS
        JG-->T

        Auth-->O

        subgraph MS[Microservices]
            direction LR
            CCS(CreditCardPaymentService)
            CS(CompaniesService)
            AS(AccountsService)
            CTCS(ContactsService)
            BNFS(BenefeciariesService)
            CCY(CurrenciesService)
            J(RatesService)
            RS(RefundsService)
            T(TransactionsService)
            QS(QuotationsService)
            CVS(ConversionsService)
            BS(BillsService)
            N(RedisCache)

            CTCS-->CS
            AS-->CS
            BNFS-->CS

            QS-->T
            BS-->T
            CVS-->T

            J-->N
            CCY-->N
        end

        CCS-->STP

        subgraph CCLDC[CurrencyCloud Client]
            S(CurrencyCloud Client)
        end

        MS-->O

        subgraph Pay
        MS-->CCLDC
        end

        subgraph EX[External]
            CC(CurrencyCloud)
            STP[Stripe]
        end

        S-->CC

```

In this flow diagram

* The Client for PAY in this case is Hub API, Mobile API and Client API.
* The Hub-API get authenticated by ORY and Mobile API users get autheticated by the local database -> users.
* Once authenticated the clients can call the adapter to access the relevant Junction Pay gRPC microservice.
* Relevent  secrets are retrieved using the Vault.
* The Adapters mediate the communication between the Client, Authentication Services and the Microservices.
* Some of the major Microservices include services like the Company Service, Refund Service, Transaction Service, CreditCardPayment service, CurrencyService and the Rates Service .
* The Microservices interacts with the external CurrencyCloud via the CurrencyCloud Client.

Note: PayAPI and AdminAPI has been deprecate. Admin API has been moved to Hub.

### Fetch Quotation API

This api will be consumed by clients to get the calculated amount based on currency pair. New amount will be calculated using the fx rates, Margins and Markups setup against the client's company.
below sequence diagram demonstrate the flow and components involved.

```mermaid
    sequenceDiagram

        participant Client
        participant PayAPI
        participant RedisCache
        participant AdminAPI
        participant Database
        participant CurrencyCloud
        participant BackgroundJob

        title Currency Pair Quotation Request and Currency Pair Rate Sync Job
        par apicall
            Client->>+PayAPI: Request Quotation for currency pair
            PayAPI->>+AdminAPI: Get Margins and Markups for company
            AdminAPI->>+Database: fetch Margins and Markups
            Database-->>-AdminAPI: Returns Margins and Markups
            AdminAPI-->>-PayAPI: Returns Margins and Markups
                critical currency rates
                option read from redis
                    PayAPI->>+RedisCache: Check if currency pair exists in cache
                    RedisCache-->>-PayAPI: Returns cached rate if exists
                option read from db
                    PayAPI->>+Database: Get rates for currency pair from database
                    Database-->>-PayAPI: Returns rates for currency pair
                    PayAPI->>+RedisCache: Saves rates in cache
                end
            PayAPI-->>-Client: Returns Quotation based on rates, Margins, and Markups
        end
        par async rate updates (job)
            Note over BackgroundJob: Sync FX rates every 15 mins
            BackgroundJob->>+CurrencyCloud: Sync FX rates every 15 mins
            CurrencyCloud->>+Database: Save synced rates to database
            Database-->>-CurrencyCloud: Returns success status
            CurrencyCloud->>-BackgroundJob: Returns synced rates
            BackgroundJob->>+RedisCache: Cache synced rates
            RedisCache-->>-BackgroundJob: Confirms cached rates
        end
```

### Create Transaction API

```mermaid
    sequenceDiagram
        participant Client
        participant PayAPI
        participant QuotationRepo
        participant TransactionRepo
        participant CurrencyCloud
        participant ConversionRepo
        participant BackgroundJob

        Client->>PayAPI: Initiate Transaction with Quotation ID and Booking Reference
        PayAPI->>PayAPI: Check if Quotation is valid
        alt Quotation is expired
            PayAPI-->>Client: Error - Quotation expired
        else Quotation is valid
            PayAPI->>QuotationRepo: Copy Quotation data to TransactionRepo with Transaction Details
            PayAPI-->>Client: Transaction UUID
        end

        PayAPI->>CurrencyCloud: Initiate FX Conversion (async)
        CurrencyCloud-->>PayAPI: Conversion Request initiated

        alt FX Conversion is successful
            PayAPI->>ConversionRepo: Save FX Conversion with status "Initiated"
        else FX Conversion failed
            PayAPI->>ConversionRepo: Save Failed FX Conversion Request
        end

        BackgroundJob->>ConversionRepo: Read Failed Conversion Requests
        loop for each failed request
            BackgroundJob->>CurrencyCloud: Process Failed Conversion Request
            alt FX Conversion is successful
                BackgroundJob->>ConversionRepo: Update Conversion Status to "Successful"
            else FX Conversion failed again
                BackgroundJob->>ConversionRepo: Update Conversion Status to "Failed"
            end
        end
```
