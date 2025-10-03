# Company Jobs Endpoint

## Overview

The `company_jobs` endpoint retrieves job listings filtered by specific companies. This endpoint searches for jobs posted by companies that the user is following, providing a focused view of job opportunities from companies of interest.

## Endpoint Details

**Path**: `graphql`
**Query ID**: `voyagerJobsDashJobCards.67b88a170c772f25e3791c583e63da26`
**Method**: GET

## Request Parameters

### Variables
- **query**: Job search query object containing:
  - **origin**: Search origin context (`JOB_SEARCH_PAGE_JOB_FILTER`)
  - **locationUnion**: Geographic filter with geo URN
  - **selectedFilters**: Company filter with list of company IDs
  - **spellCorrectionEnabled**: Boolean for spell correction
- **includeWebMetadata**: Set to "true"

### Example Request
```
GET /voyager/api/graphql?includeWebMetadata=true&variables=(query:(origin:JOB_SEARCH_PAGE_JOB_FILTER,locationUnion:(geoUrn:urn%3Ali%3Afsd_geo%3A92000000),selectedFilters:List((key:company,value:List(9414302))),spellCorrectionEnabled:true))&queryId=voyagerJobsDashJobCards.67b88a170c772f25e3791c583e63da26
```

## Response Structure

### Data Selector
The response data structure follows LinkedIn's job search format with job cards containing job posting information.

### Key Data Fields

#### Job Search Results
- **elements**: Array of job search result objects
- **paging**: Pagination information
  - **total**: Total number of job results
  - **start**: Starting index of current page
  - **count**: Number of results in current page

#### Job Card Information
Each job card contains:
- **jobPostingCard**: Main job posting data
  - **jobPostingUrn**: Job posting URN
  - **jobPostingTitle**: Job title
  - **primaryDescription**: Primary job description text
  - **secondaryDescription**: Secondary job description (location, type)
  - **logo**: Company logo information
  - **jobPosting**: Detailed job posting data
    - **entityUrn**: Job posting entity URN
    - **posterId**: Company ID that posted the job

### Example Response Structure
```json
{
  "data": {
    "voyagerJobsDashJobCards": {
      "elements": [
        {
          "jobCardUnion": {
            "jobPostingCard": {
              "jobPostingUrn": "urn:li:fsd_jobPosting:4209649973",
              "jobPostingTitle": "Software Engineer",
              "primaryDescription": {
                "text": "Company Name"
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
        "total": 25,
        "start": 0,
        "count": 20
      }
    }
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
- **is_remote**: Detected by presence of "remote" in secondary description
- **is_hybrid**: Detected by presence of "hybrid" in secondary description

## Dependencies

This endpoint depends on:
- **followed_companies**: Uses company IDs from the followed companies list

## Use Cases

### Primary Use Cases
1. **Company-Specific Job Search**: Find jobs posted by followed companies
2. **Job Discovery**: Discover new opportunities from companies of interest
3. **Career Planning**: Track job openings at target companies
4. **Market Research**: Analyze job posting patterns by company

### Filtering Capabilities
- **Company Filter**: Filter jobs by specific company IDs
- **Location Filter**: Geographic filtering by location URN
- **Spell Correction**: Automatic correction of search terms
- **Origin Context**: Search context for better results

## Geographic Filtering

### Location Union
- **geoUrn**: Geographic URN for location filtering
- **Default**: `urn:li:fsd_geo:92000000` (United States)
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
- Total count available for calculating total pages

### Batch Processing
- Default batch size controlled by configuration
- Efficient for processing large numbers of job results
- Supports continuous pagination through all results

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
- **jobs_by_company**: Alternative endpoint for company-specific job searches

### Data Flow
1. Get company IDs from `followed_companies`
2. Use company IDs to filter job search in `company_jobs`
3. Extract job URNs for detailed job information
4. Use job URNs in `job_description` for full job details
