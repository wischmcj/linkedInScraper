# LinkedIn Organization API Documentation

This document describes the LinkedIn organization API endpoints and their usage patterns based on analysis of browser network calls.

## Overview

LinkedIn's organization system uses GraphQL endpoints to handle different aspects of company and organization functionality:
- **voyagerOrganizationDashCompanies**: Company information retrieval and management
- Multiple query variants for different use cases (by ID, universal name, etc.)

## Core Organization Endpoints

### 1. Company Information by URNs

**Endpoint**: `GET /voyager/api/graphql`

**Purpose**: Retrieves company information using company URNs

**Query ID**: `voyagerOrganizationDashCompanies.32a7cdaea60de8f9ce50df019654c45d`

**Variables**:
```
companyUrns: List(urn:li:fsd_company:9414302)
```

**Response Overview**: This response contains comprehensive company information including company details, employee counts, industry information, and organizational data. The response includes extensive metadata about company types, premium page information, employee experience content visibility, and various organizational features. The data structure includes LinkedIn's internal type information for data validation and extensive schema metadata.

**Example Response**:
```json
{
  "data": {
    "data": {
      "*organizationDashCompaniesByIds": ["urn:li:fsd_company:9414302"],
      "$recipeTypes": ["com.linkedin.6050cec604ca0b05eb6f8c88c02ffa9c"],
      "$type": "com.linkedin.6050cec604ca0b05eb6f8c88c02ffa9c"
    },
    "extensions": {
      "webMetadata": {}
    }
  },
  "meta": {
    "microSchema": {
      "isGraphQL": true,
      "version": "2.1",
      "types": {
        "com.linkedin.d7876378ce775bf9ae24c0907b82be61": {
          "fields": {
            "customSpotlight": {
              "type": "com.linkedin.85e3b5a709591ab7797464027ec6ab07"
            }
          },
          "baseType": "com.linkedin.voyager.dash.organization.PremiumPageTopCard"
        }
      }
    }
  }
}
```

### 2. Company Information by Universal Name (Numeric)

**Endpoint**: `GET /voyager/api/graphql`

**Purpose**: Retrieves company information using numeric universal name

**Query ID**: `voyagerOrganizationDashCompanies.bd2de7b53b2079072f92b55ac1bae2f3`

**Variables**:
```
universalName: 9414302
```

**Response Overview**: This response provides company information when accessed via numeric universal name. The response typically contains basic company data and may include redirect information or company profile details. The response size is smaller compared to the URN-based query, indicating it provides more focused company information.

**Example Response**:
```json
{
  "data": {
    "data": {
      "organizationDashCompaniesByUniversalName": {
        "$recipeTypes": ["com.linkedin.2154e2309f3b4858a170a257892fb190"],
        "elements": [],
        "$type": "com.linkedin.restli.common.CollectionResponse"
      },
      "$recipeTypes": ["com.linkedin.da32cd8f480d35da7b6a8569df0a0b38"],
      "$type": "com.linkedin.da32cd8f480d35da7b6a8569df0a0b38"
    },
    "extensions": {
      "webMetadata": {}
    }
  },
  "meta": {
    "microSchema": {
      "isGraphQL": true,
      "version": "2.1",
      "types": {
        "com.linkedin.73ceb8b8e1a04add01d6a814d5893dbe": {
          "fields": {
            "stockQuote": {
              "type": "com.linkedin.b8b7d8541f6c259913c4bad5b9994611"
            },
            "entityUrn": {
              "type": "com.linkedin.voyager.dash.common.CompanyUrn"
            }
          },
          "baseType": "com.linkedin.voyager.dash.organization.Company"
        }
      }
    }
  }
}
```

### 3. Company Information by URN

**Endpoint**: `GET /voyager/api/graphql`

**Purpose**: Retrieves company information using single company URN

**Query ID**: `voyagerOrganizationDashCompanies.c8e32edb664b01bdf00c968aca69ba3d`

**Variables**:
```
companyUrn: urn:li:fsd_company:9414302
```

**Response Overview**: This response contains detailed company information for a single company identified by its URN. The response includes comprehensive organizational data, company profile information, and related metadata. The response size indicates it provides substantial company details including organizational structure and company-specific information.

**Example Response**:
```json
{
  "data": {
    "data": {
      "$recipeTypes": ["com.linkedin.e729d5f3f872e3aafbe4da0d884e65d8"],
      "*organizationDashCompaniesById": "urn:li:fsd_company:9414302",
      "$type": "com.linkedin.e729d5f3f872e3aafbe4da0d884e65d8"
    },
    "extensions": {
      "webMetadata": {}
    }
  },
  "meta": {
    "microSchema": {
      "isGraphQL": true,
      "version": "2.1",
      "types": {
        "com.linkedin.f477fe49156b58a25c03e9f0027a50ba": {
          "fields": {
            "shouldSkipMemoryFetch": {
              "type": "boolean"
            },
            "pageContext": {
              "type": "com.linkedin.a241de3953635c7732e44765fd8e7046"
            },
            "customContext": {
              "type": {
                "array": "com.linkedin.8369806fb88214aebd599b9ade5d32d0"
              },
              "isMap": true
            }
          },
          "baseType": "com.linkedin.voyager.dash.common.guide.GuideQueryContext"
        }
      }
    }
  }
}
```

### 4. Company Information by Universal Name (Text)

**Endpoint**: `GET /voyager/api/graphql`

**Purpose**: Retrieves company information using text-based universal name

**Query ID**: `voyagerOrganizationDashCompanies.9907aa2e96789c8c1ed6ca06bb3bd33b`

**Variables**:
```
universalName: progyny
```

**Response Overview**: This response provides company information when accessed via text-based universal name (company slug). The response contains company profile data, organizational information, and company-specific details. This endpoint is typically used when accessing companies via their URL-friendly names.

**Example Response**:
```json
{
  "data": {
    "data": {
      "organizationDashCompaniesByUniversalName": {
        "*elements": ["urn:li:fsd_company:9414302"],
        "$recipeTypes": ["com.linkedin.c625dc47da6993141aad45afd72f62fc"],
        "$type": "com.linkedin.restli.common.CollectionResponse"
      },
      "$recipeTypes": ["com.linkedin.64e2aba16707df82b227b7dad9f77f0b"],
      "$type": "com.linkedin.64e2aba16707df82b227b7dad9f77f0b"
    },
    "extensions": {
      "webMetadata": {}
    }
  },
  "meta": {
    "microSchema": {
      "isGraphQL": true,
      "version": "2.1",
      "types": {
        "com.linkedin.09033b8aaf36c6922fe6db0e24d6c50f": {
          "fields": {
            "locations": {
              "type": {
                "array": "com.linkedin.f755c5660f94aaf376dc360c50ecce96"
              }
            },
            "latLong": {
              "type": "com.linkedin.a47fcf68f4aa53ef7ccdf1e2b849fcf0"
            },
            "localizedName": {
              "type": "string"
            }
          }
        }
      }
    }
  }
}
```

### 5. Company Information by Universal Name (Alternative)

**Endpoint**: `GET /voyager/api/graphql`

**Purpose**: Alternative endpoint for retrieving company information by universal name

**Query ID**: `voyagerOrganizationDashCompanies.f8854567952d792166f11b3e1483233f`

**Variables**:
```
universalName: progyny
```

**Response Overview**: This response provides an alternative method for retrieving company information using universal names. The response contains company data and organizational information, potentially with different data structure or additional fields compared to the primary universal name endpoint.

**Example Response**:
```json
{
  "data": {
    "data": {
      "organizationDashCompaniesByUniversalName": {
        "*elements": ["urn:li:fsd_company:9414302"],
        "$recipeTypes": ["com.linkedin.2154e2309f3b4858a170a257892fb190"],
        "$type": "com.linkedin.restli.common.CollectionResponse"
      },
      "$recipeTypes": ["com.linkedin.da32cd8f480d35da7b6a8569df0a0b38"],
      "$type": "com.linkedin.da32cd8f480d35da7b6a8569df0a0b38"
    }
  },
  "included": [
    {
      "stockQuote": null,
      "entityUrn": "urn:li:fsd_company:9414302",
      "$recipeTypes": ["com.linkedin.73ceb8b8e1a04add01d6a814d5893dbe"],
      "$type": "com.linkedin.voyager.dash.organization.Company"
    }
  ]
}
```

## API Flow for Company Information Retrieval

Based on the observed network calls, here's the typical flow for retrieving company information:

### Step 1: Identify Company Identifier
The system can use different identifiers to retrieve company information:
- **Company URN**: `urn:li:fsd_company:COMPANY_ID`
- **Universal Name (Numeric)**: `9414302`
- **Universal Name (Text)**: `progyny`

### Step 2: Choose Appropriate Endpoint
Based on the available identifier, the system selects the appropriate GraphQL query:
- Use URN-based queries for comprehensive company data
- Use universal name queries for basic company information
- Use list-based queries for multiple companies

### Step 3: Retrieve Company Data
The system makes GraphQL queries to retrieve:
- **Company Profile Information**: Basic company details, description, industry
- **Organizational Data**: Employee counts, company size, structure
- **Premium Features**: Premium page information, custom spotlight content
- **Employee Experience**: Content visibility settings, verification requirements
- **Company Metadata**: Internal type information, schema validation data

### Step 4: Process Response Data
The response includes extensive metadata and schema information for data validation and processing.

## URN Structure

### Company URN
```
urn:li:fsd_company:COMPANY_ID
```

### Universal Name Formats
- **Numeric**: `9414302`
- **Text**: `progyny`

## Headers and Authentication

All organization API calls include:
- **X-LI-Track**: Client tracking information
- **User-Agent**: Browser identification
- **Authorization**: Session-based authentication
- **Content-Type**: `application/vnd.linkedin.normalized+json+2.1`
- **X-LI-PEM-Metadata**: Page element metadata for tracking

## Response Characteristics

- **Content-Type**: `application/vnd.linkedin.normalized+json+2.1`
- **Response Size**: Varies from ~300 bytes to ~200KB depending on query type
- **Schema Version**: 2.1 with extensive type definitions
- **Caching**: Dynamic responses with no-cache headers
- **Compression**: Gzip encoding for large responses

## Error Handling

- Successful operations return `200 OK` status
- GraphQL responses include error information in the `errors` field if present
- Failed requests may include retry mechanisms based on response headers
- Responses include server timing and performance metrics

## Use Cases

### Company Profile Pages
- Display comprehensive company information
- Show employee counts and company size
- Present organizational structure and industry details

### Company Search and Discovery
- Find companies by name or URN
- Retrieve basic company information for search results
- Access company metadata for filtering and sorting

### Organizational Management
- Access premium company features
- Manage employee experience settings
- Configure company visibility and verification requirements
