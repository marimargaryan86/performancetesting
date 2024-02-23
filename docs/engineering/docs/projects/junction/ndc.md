# Junction NDC

## Introduction
#### NDC - New Distribution Capability
NDC, an API standard by IATA (https://www.iata.org), streamlines direct connections between airlines and travel agencies, bypassing GDSs like Amadeus and Sabre.  This standard allows companies like Snowfall to easily access and  integrate with airline inventories, such as British Airways, enabling a quicker time to market for new airline inventory and services.

#### Junction NDC - https://git.snowfall.se/junction/snowfall-ndc
Junction NDC is a standalone repo that serves as Snowfall's internal NDC API to which NDC airline provider services make their API requests. The Snowfall NDC API then routes the requests to the relevant Airline NDC API, handle any differences between providers and translating both the requests and responses from JSON to XML and XML to JSON. Currently, only British Airways is supported.



## NDC API Request-Response Lifecycle Flowchart
```mermaid
    flowchart LR

      subgraph Client Request
          A(Client Request)
      end

      subgraph NDC Providers/Vendors
          B(Provider 1)
          C(Provider 2)
          D(Provider 3)
          A --> B
          A --> C
          A --> D
      end

      subgraph Junction NDC
          E(Junction NDC)
          B --> E
          C --> E
          D --> E
      end

      subgraph Airline NDC APIs
          F(Airline 1)
          G(Airline 2)
          H(Airline 3)
          E --> F
          E --> G
          E --> H
      end

      subgraph Junction NDC
          I(Junction NDC)
          F --> I
          G --> I
          H --> I
      end

      subgraph NDC Providers/Vendors
          J(Provider 1)
          K(Provider 2)
          L(Provider 3)
          I --> J
          I --> K
          I --> L
      end

      subgraph Client Response
          M(Client Response)
          J --> M
          K --> M
          L --> M
      end
```
