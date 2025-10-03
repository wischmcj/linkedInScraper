# Company Details Endpoint

## Overview

The `company_details` endpoint retrieves comprehensive information about specific companies using their company URNs. This endpoint provides detailed company profiles including organizational data, employee counts, industry information, locations, funding data, and more.

## Endpoint Details

**Path**: `graphql`
**Query ID**: `voyagerOrganizationDashCompanies.32a7cdaea60de8f9ce50df019654c45d`
**Method**: GET

## Request Parameters

### Variables
- **companyUrns**: List of company URNs in format `List(urn%3Ali%3Afsd_company%3A{company_id})`
- **includeWebMetadata**: Set to "false" for this endpoint

### Example Request
```
GET /voyager/api/graphql?includeWebMetadata=false&variables=(companyUrns:List(urn%3Ali%3Afsd_company%3A9414302))&queryId=voyagerOrganizationDashCompanies.32a7cdaea60de8f9ce50df019654c45d
```

## Response Structure

### Data Selector
The response data is located at: `data.organizationDashCompaniesByIds[*]`

### Key Data Fields

#### Basic Company Information
- **entityUrn**: Company URN in format `urn:li:fsd_company:COMPANY_ID`
- **name**: Company name
- **websiteUrl**: Company website URL
- **description**: Company description text

#### Organizational Data
- **employeeCountRange**: Company size range (start/end values)
- **industry**: Primary industry information
- **industryV2Taxonomy**: Secondary industry classifications
- **hashtag**: Company hashtags and tags

#### Location Information
- **groupedLocations**: Company office locations
  - **name**: Location name
  - **entityUrn**: Location URN
  - **latLong**: Latitude and longitude coordinates
  - **city**: City name
  - **country**: Country name

#### Funding and Financial Data
- **crunchbaseFundingData**: Funding information from Crunchbase
  - **lastFundingRound**: Most recent funding round details
    - **leadInvestors**: Lead investor names
    - **moneyRaised**: Amount raised in funding round
    - **announcedOn**: Funding announcement date (month/year)
    - **numberOfOtherInvestors**: Count of additional investors
    - **fundingRoundUrl**: URL to funding round details
    - **investorsUrl**: URL to investors information
  - **organizationUrl**: Company's Crunchbase URL
  - **fundingRoundsUrl**: URL to all funding rounds

#### Similar Organizations
- **similarOrganizations**: Related companies
  - **name**: Similar company name
  - **entityUrn**: Similar company URN
  - **industry**: Industry classification
  - **industry_urn**: Industry URN
  - **url**: Company URL

#### Social and Following Data
- **followingState**: User's following status
  - **following**: Boolean indicating if user follows this company

### Example Response Structure
```json
{
  "data": {
    "organizationDashCompaniesByIds": [
      {
        "entityUrn": "urn:li:fsd_company:9414302",
        "name": "Company Name",
        "websiteUrl": "https://company.com",
        "employeeCountRange": {
          "start": 100,
          "end": 500
        },
        "industry": [
          {
            "name": "Technology",
            "entityUrn": "urn:li:fsd_industry:6"
          }
        ],
        "groupedLocations": [
          {
            "name": "San Francisco, CA",
            "entityUrn": "urn:li:fsd_geo:92000000",
            "latLong": {
              "latitude": 37.7749,
              "longitude": -122.4194
            },
            "city": "San Francisco",
            "country": "United States"
          }
        ],
        "crunchbaseFundingData": {
          "lastFundingRound": {
            "leadInvestors": ["Investor Name"],
            "moneyRaised": 10000000,
            "announcedOn": {
              "month": 6,
              "year": 2023
            },
            "numberOfOtherInvestors": 5,
            "fundingRoundUrl": "https://crunchbase.com/funding-round",
            "investorsUrl": "https://crunchbase.com/investors"
          },
          "organizationUrl": "https://crunchbase.com/organization/company",
          "fundingRoundsUrl": "https://crunchbase.com/funding-rounds"
        },
        "similarOrganizations": {
          "elements": [
            {
              "name": "Similar Company",
              "entityUrn": "urn:li:fsd_company:123456",
              "industry": {
                "name": "Technology"
              },
              "url": "https://similar-company.com"
            }
          ]
        },
        "followingState": {
          "following": true
        }
      }
    ]
  }
}
```

## Data Mapping

### Extracted Fields
- **company_id**: Extracted from `entityUrn` by splitting on ":" and taking the last part
- **company_name**: Retrieved from `name` field
- **size_range_min**: Employee count range start value
- **size_range_max**: Employee count range end value
- **industry**: Primary industry name(s)
- **industry_urn**: Industry URN(s)
- **secondary_industry**: Secondary industry classifications
- **hashtag**: Company hashtags
- **website**: Company website URL
- **following**: User's following status

### Location Data
- **locations**: Array of location objects with:
  - **name**: Location name
  - **urn**: Location entity URN
  - **latitude**: Geographic latitude
  - **longitude**: Geographic longitude
  - **city**: City name
  - **country**: Country name

### Funding Data
- **last_funding_data**: Object containing:
  - **lead_investors**: Array of lead investor names
  - **money_raised**: Funding amount
  - **announced_on_month**: Month of funding announcement
  - **announced_on_year**: Year of funding announcement
  - **number_of_other_investors**: Count of additional investors
  - **funding_round_url**: URL to funding round details
  - **investors_url**: URL to investors information
  - **organization_url**: Company's Crunchbase URL
  - **funding_rounds_url**: URL to all funding rounds

### Similar Organizations
- **similar_organizations**: Array of related companies with:
  - **name**: Company name
  - **urn**: Company entity URN
  - **industry**: Industry classification
  - **industry_urn**: Industry URN
  - **url**: Company URL

## Dependencies

This endpoint depends on:
- **followed_companies**: Uses company IDs from the followed companies list

## Use Cases

### Primary Use Cases
1. **Company Research**: Get comprehensive company information for analysis
2. **Due Diligence**: Access detailed company profiles including funding data
3. **Market Analysis**: Analyze company size, industry, and location data
4. **Competitive Intelligence**: Access similar organizations and industry data

### Data Analysis Applications
- Company size analysis and categorization
- Industry classification and taxonomy analysis
- Geographic distribution of company locations
- Funding history and investment analysis
- Competitive landscape mapping

## Column Filtering

### Dropped Columns
The following columns are excluded from the final output:
- **similar_organizations**: Dropped to reduce data size
- Various internal LinkedIn fields (viewerPermissions, socialProofInsight, etc.)

### Retained Columns
- Core company information (name, description, website)
- Organizational data (size, industry)
- Location information
- Funding data
- Following status

## Pagination

### Pagination Strategy
- No pagination required (single company per request)
- Can process multiple companies in batch via companyUrns list
- Efficient for bulk company data retrieval

### Batch Processing
- Supports multiple company URNs in single request
- Optimal for processing lists of companies from followed_companies endpoint
- Reduces API calls when retrieving multiple company details

## Error Handling

### Common Issues
- **Invalid Company URN**: Malformed or non-existent company URNs
- **Private Companies**: Limited data for private companies
- **Rate Limiting**: Subject to LinkedIn's API rate limits

### Response Validation
- Validates company URN format before processing
- Handles missing optional fields gracefully
- Ensures data integrity for critical fields

## Performance Considerations

### Response Size
- Large responses (typically 50-200KB per company)
- Contains extensive company metadata
- Consider compression for bulk operations

### Caching
- Company details change infrequently
- Suitable for long-term caching
- Consider cache invalidation strategies

## Security and Privacy

### Data Sensitivity
- Contains public company information
- Some data may be premium/restricted
- Subject to LinkedIn's API access controls

### Access Control
- Requires proper authentication
- Respects LinkedIn's data access policies
- May have usage limitations based on account type
