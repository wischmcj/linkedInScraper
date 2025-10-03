# Jobs by Company Endpoint

## Overview

The `jobs_by_company` endpoint retrieves job listings specifically from companies that the user is following. This endpoint uses LinkedIn's job search API with company-specific filtering to find job opportunities posted by followed companies.

## Endpoint Details

**Path**: `voyagerJobsDashJobCards`
**Decoration ID**: `com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-87`
**Method**: GET

## Request Parameters

### Query Parameters
- **q**: Search query type (`jobSearch`)
- **decorationId**: Decoration ID for response format
- **query**: Job search query object containing:
  - **origin**: Search origin context (`COMPANY_PAGE_JOBS_CLUSTER_EXPANSION`)
  - **locationUnion**: Geographic filter with geo ID
  - **selectedFilters**: Company filter with list of company IDs
  - **spellCorrectionEnabled**: Boolean for spell correction
  - **servedEventEnabled**: Event serving flag (set to "False")
- **start**: Starting index for pagination (uses `$start` placeholder)
- **count**: Number of items per page (uses `BATCH_SIZE` from configuration)

### Example Request
```
GET /voyager/api/voyagerJobsDashJobCards?q=jobSearch&decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-87&query=(origin:COMPANY_PAGE_JOBS_CLUSTER_EXPANSION,locationUnion:(geoId:92000000),selectedFilters:(company:List(9414302)),spellCorrectionEnabled:true,servedEventEnabled:False)&start=0&count=20
```

## Response Structure

### Data Selector
The response data is located at: `elements.[*].jobCardUnion.jobPostingCard`

### Key Data Fields

#### Job Search Results
- **elements**: Array of job search result objects
- **paging**: Pagination information
  - **total**: Total number of job results
  - **start**: Starting index of current page
  - **count**: Number of results in current page

#### Job Card Information
Each job card contains:
- **jobPostingUrn**: Job posting URN
- **jobPostingTitle**: Job title
- **primaryDescription**: Primary job description text (typically company name)
- **secondaryDescription**: Secondary job description (location, work type)
- **logo**: Company logo information
  - **attributes**: Array of logo attributes
    - **detailDataUnion**: Logo data union
      - **companyLogo**: Company logo URN
- **jobPosting**: Detailed job posting data
  - **entityUrn**: Job posting entity URN
  - **posterId**: Company ID that posted the job

### Example Response Structure
```json
{
  "elements": [
    {
      "jobCardUnion": {
        "jobPostingCard": {
          "jobPostingUrn": "urn:li:fsd_jobPosting:4209649973",
          "jobPostingTitle": "Senior Software Engineer",
          "primaryDescription": {
            "text": "Tech Company Inc."
          },
          "secondaryDescription": {
            "text": "San Francisco, CA (Remote)"
          },
          "logo": {
            "attributes": [
              {
                "detailDataUnion": {
                  "companyLogo": "urn:li:fsd_company:9414302"
                }
              }
            ]
          },
          "jobPosting": {
            "entityUrn": "urn:li:fsd_jobPosting:4209649973",
            "posterId": "9414302"
          }
        }
      }
    }
  ],
  "paging": {
    "total": 15,
    "start": 0,
    "count": 20
  }
}
```

## Data Mapping

### Extracted Fields
- **job_posting_title**: Job title from `jobPostingTitle`
- **entity_urn**: Job posting entity URN
- **job_id**: Extracted from entity URN (removes `urn:li:fsd_jobPosting:` prefix)
- **company_logo_urn**: Company logo URN from logo attributes
- **company_id**: Extracted from company logo URN (removes `urn:li:fsd_company:` prefix)
- **primary_description**: Primary job description text
- **secondary_description**: Secondary job description text
- **location**: Cleaned location text (removes work type indicators)
- **company_name**: Company name (currently mapped from primary description)
- **is_remote**: Boolean indicating if job is remote
- **is_hybrid**: Boolean indicating if job is hybrid
- **job_urn_encoded**: URL-encoded job posting URN for use in other endpoints

### Location Processing
The endpoint processes location information by:
- Removing work type indicators: `(On-site)`, `(Hybrid)`, `(Remote)`
- Extracting clean location text from secondary description
- Identifying remote and hybrid work arrangements

### Work Type Detection
- **is_remote**: Detected by presence of "remote" in secondary description (case-insensitive)
- **is_hybrid**: Detected by presence of "hybrid" in secondary description (case-insensitive)

### Company ID Extraction
- **company_id**: Extracted from company logo URN by removing `urn:li:fsd_company:` prefix
- **job_id**: Extracted from job posting URN by removing `urn:li:fsd_jobPosting:` prefix

## Dependencies

This endpoint depends on:
- **followed_companies**: Uses company IDs from the followed companies list

## Use Cases

### Primary Use Cases
1. **Company-Specific Job Discovery**: Find jobs posted by followed companies
2. **Career Opportunity Tracking**: Monitor job openings at target companies
3. **Job Market Analysis**: Analyze job posting patterns by company
4. **Recruitment Research**: Research job opportunities at specific companies

### Search Capabilities
- **Company Filtering**: Filter jobs by specific company IDs
- **Geographic Filtering**: Filter by geographic location (geo ID: 92000000 for US)
- **Spell Correction**: Automatic correction of search terms
- **Origin Context**: Company page context for better results

## Geographic Filtering

### Location Union
- **geoId**: Geographic ID for location filtering
- **Default**: `92000000` (United States)
- **Customizable**: Can be set to specific geographic regions

### Location Options
- Global search (no location filter)
- Country-level filtering
- City-level filtering
- Custom geographic regions

## Pagination

### Pagination Strategy
- Uses LinkedIn's standard pagination with `start` and `count` parameters
- Supports large result sets with efficient pagination
- Total count available in `paging.total` for calculating total pages

### Batch Processing
- Default batch size controlled by `BATCH_SIZE` configuration
- Efficient for processing large numbers of job results
- Supports continuous pagination through all results

### Total Path
The total number of results is available at: `paging.total`

## Error Handling

### Common Issues
- **No Results**: Empty results when no jobs match criteria
- **Invalid Company IDs**: Non-existent or invalid company IDs
- **Rate Limiting**: Subject to LinkedIn's API rate limits
- **Geographic Restrictions**: Some jobs may not be available in all regions

### Response Validation
- Validates job posting URNs before processing
- Handles missing job descriptions gracefully
- Ensures company ID extraction is successful
- Validates work type detection logic

## Performance Considerations

### Response Size
- Moderate response size (typically 10-50KB)
- Depends on number of job results returned
- Efficient for regular job monitoring

### Caching
- Job results change frequently
- Short-term caching recommended
- Consider cache invalidation on regular intervals

## Security and Privacy

### Data Sensitivity
- Contains public job posting information
- May include company-specific job details
- Subject to LinkedIn's API access controls

### Access Control
- Requires proper authentication
- Respects LinkedIn's job search limitations
- May have usage restrictions based on account type

## Integration with Other Endpoints

### Downstream Usage
- **job_description**: Uses job URNs from this endpoint for detailed job information

### Data Flow
1. Get company IDs from `followed_companies`
2. Use company IDs to filter job search in `jobs_by_company`
3. Extract job URNs for detailed job information
4. Use job URNs in `job_description` for full job details

### Alternative Endpoints
- **company_jobs**: Alternative GraphQL-based endpoint for company-specific job searches
- Both endpoints serve similar purposes but use different API structures

## Special Considerations

### Decoration ID
- Uses specific decoration ID for response formatting
- Ensures consistent response structure
- May affect available fields in response

### Origin Context
- Uses `COMPANY_PAGE_JOBS_CLUSTER_EXPANSION` origin
- Optimized for company page job listings
- May provide different results than general job search
