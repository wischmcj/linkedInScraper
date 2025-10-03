# Followed Companies Endpoint

## Overview

The `followed_companies` endpoint retrieves a list of companies that the authenticated user is following on LinkedIn. This endpoint is used to get the user's followed companies list, which serves as a data source for other endpoints that need company information.

## Endpoint Details

**Path**: `graphql`
**Query ID**: `voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357`
**Method**: GET

## Request Parameters

### Variables
- **pagedListComponent**: URL-encoded component URN for the followed companies list
- **paginationToken**: Pagination token (typically "null" for first page)
- **start**: Starting index for pagination (uses `$start` placeholder)
- **count**: Number of items per page (uses `BATCH_SIZE` from configuration)

### Example Request
```
GET /voyager/api/graphql?includeWebMetadata=true&variables=(pagedListComponent:urn%3Ali%3Afsd_profilePagedListComponent%3A(ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY,INTERESTS_VIEW_DETAILS,urn%3Ali%3Afsd_profileTabSection%3ACOMPANIES_INTERESTS,NONE,en_US),paginationToken:null,start:0,count:20)&queryId=voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357
```

## Response Structure

### Data Selector
The response data is located at: `data.identityDashProfileComponentsByPagedListComponent.elements`

### Key Data Fields

#### Company Information
- **entityUrn**: Company URN in format `urn:li:fsd_company:COMPANY_ID`
- **company_id**: Extracted from entityUrn (last part after colon)
- **companyName**: Company name from titleV2.text.attributesV2.detailData

#### Pagination
- **paging.total**: Total number of followed companies
- **paging.start**: Starting index of current page
- **paging.count**: Number of items in current page

### Example Response Structure
```json
{
  "data": {
    "identityDashProfileComponentsByPagedListComponent": {
      "elements": [
        {
          "components": {
            "entityComponent": {
              "titleV2": {
                "text": {
                  "attributesV2": [
                    {
                      "detailData": {
                        "companyName": "Company Name"
                      }
                    }
                  ]
                }
              }
            }
          },
          "entityUrn": "urn:li:fsd_company:123456"
        }
      ],
      "paging": {
        "total": 50,
        "start": 0,
        "count": 20
      }
    }
  }
}
```

## Data Mapping

### Extracted Fields
- **company_id**: Extracted from `entityUrn` by splitting on ":" and taking the last part
- **company_name**: Retrieved from nested title structure
- **entity_urn**: Full company URN for reference

### Column Transformations
The endpoint applies the following transformations:
- Extracts company ID from the entity URN
- Maps company name from the nested title structure
- Preserves the full entity URN for downstream processing

## Dependencies

This endpoint has no dependencies and serves as a primary data source for:
- `company_details`: Uses company IDs from followed companies
- `jobs_by_company`: Uses company IDs to filter job searches
- `company_jobs`: Uses company IDs for company-specific job queries

## Use Cases

### Primary Use Cases
1. **Company Discovery**: Get list of companies user is following
2. **Data Source**: Provide company IDs for other endpoint queries
3. **User Preferences**: Track user's company interests and following behavior

### Integration with Other Endpoints
- Company details retrieval using extracted company IDs
- Job search filtering by followed companies
- Company-specific job listing queries

## Pagination

### Pagination Strategy
- Uses LinkedIn's standard pagination with `start` and `count` parameters
- Supports pagination token for cursor-based pagination
- Total count available in response for calculating total pages

### Batch Processing
- Default batch size controlled by `BATCH_SIZE` configuration
- Supports processing large lists of followed companies
- Efficient for users following many companies

## Error Handling

### Common Issues
- **Authentication Required**: User must be logged in to access followed companies
- **Empty Results**: Users with no followed companies return empty elements array
- **Rate Limiting**: Subject to LinkedIn's API rate limits

### Response Validation
- Validates entity URN format before processing
- Handles missing company names gracefully
- Ensures pagination parameters are within valid ranges

## Performance Considerations

### Response Size
- Relatively small responses (typically < 10KB)
- Efficient for frequent polling of followed companies list
- Minimal data transfer overhead

### Caching
- Can be cached for short periods to reduce API calls
- Company list changes infrequently for most users
- Consider cache invalidation on user activity

## Security and Privacy

### Data Sensitivity
- Contains user's private company following preferences
- Requires proper authentication and authorization
- Subject to LinkedIn's privacy policies

### Access Control
- Only accessible to authenticated user
- Cannot access other users' followed companies
- Respects LinkedIn's API access controls
