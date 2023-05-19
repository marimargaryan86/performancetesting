# Junction Pay

Junction pay System Flow Diagram

```mermaid
    flowchart LR

        subgraph Client
            A(Client)
        end

        subgraph Firewall
            B(Firewall)
            style Firewall fill:#ff595e
        end

        subgraph PayAPI
            direction TB
            C(Pay API)
            E(Vault)
            I(Mongodb)
            C --> E
            C --> I
        end

        subgraph AdminAPI
            D(Admin API)
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
        PayAPI --> Adapters
        AdminAPI --> Adapters
        Adapters --> AuthenticationServices
        Adapters --> Microservices
        PayAPI --> S
        Microservices --> S
        S --> T
        T --> CurrencyCloud
```

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
