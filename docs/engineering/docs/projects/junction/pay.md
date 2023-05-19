# Junction Pay

Junction pay System Flow Diagram

```mermaid
    flowchart LR

        subgraph Client
            A(Client)
        end

        subgraph Firewall
            B(Firewall)
        end

        subgraph PayAPI
            direction LR
            C(Pay API)
            E(Vault)
            I(transaction repo)
            U(quotation repo)
            V(fx Conversion repo)
            W(Company Repo)
            C --> E
            C --> I
            C --> U
            C --> V
            C --> W
        end

        subgraph AdminAPI
            direction LR
            D(Admin API)
            X(Vault)
            Y(transaction repo)
            Z(quotation repo)
            A1(fx Conversion repo)
            B2(Company Repo)

            D --> X
            D --> Y
            D --> Z
            D --> A1
            D --> B2
        end

        subgraph AuthenticationServices
            F(Authentication Services)
            G(MongoDB)
            F --> G
        end

        subgraph Adapters
            H(Adapters)
        end

        subgraph Microservices
            direction LR
                J(Rates Service)
                K(Rates Repo)
                L(Currencies Service)
                M(CurrenciesRepo)
                N(Redis Cache)
                O(Accounts)
                P(Accounts Repo)
                Q(Payment Service)
                R(Payment Repo)
                O --> P
                J --> K
                J --> N
                L --> N
                L --> M
                Q --> R
        end

        subgraph CurrencyCloud Client
            S(CurrencyCloud Client)
        end

        subgraph Firewall Outbound
            T(Firewall)
        end

        A --> B
        B --> PayAPI
        B --> AdminAPI
        PayAPI --> S
        PayAPI --> Adapters
        AdminAPI --> Adapters
        Adapters --> AuthenticationServices
        Adapters --> Microservices
        Microservices --> S
        S --> T
        T --> CurrencyCloud

        AdminAPI --> S
```

In this flow diagram

* The Client (A) communicates to Pay and admin API via inbound Firewall (B).
* The Pay API (C) retrieves secrets using the Vault (E) and will use quotation, transaction and fx conversion repos, this will be used by Go to create Quotations and Transactions.
* The Admin API (D) retrieves secrets using the Vault (E) and will use quotation, transaction and fx conversion repos. admin api will be used by Hub to list down quotations, transactions, and fx conversions
* The Adapters (H) mediate the communication between the Pay API, Admin API, Authentication Services, and the Microservices.
* The Authentication Services (F) have a connection to the User Repository (G).
* The Microservices include the Rates Service (J), Rates Repository (K), Currencies Service (L), Currencies Repository (M), Redis Cache (N), Accounts (O), Accounts Repository (P), Payment Service (Q), and Payment Repository (R).
* The Microservices interacts with the CurrencyCloud Client (S).
* The FirewallOutbound (T) represents the outbound traffic from the Firewall.

Quotation API:

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
