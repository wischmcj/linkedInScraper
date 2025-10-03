# Job Description Endpoint

## Overview

The `job_description` endpoint retrieves detailed information about specific job postings, including full job descriptions, salary information, benefits, and other job-related details. This endpoint provides comprehensive job information for individual job postings identified by their URNs.

## Endpoint Details

**Path**: `graphql`
**Query ID**: `voyagerJobsDashJobPostingDetailSections.3b2647d9e7ecb085c570a16f9e70d1cc`
**Method**: GET

## Request Parameters

### Variables
- **cardSectionTypes**: List of job card types to retrieve
  - `JOB_DESCRIPTION_CARD`: Full job description and requirements
  - `SALARY_CARD`: Salary information and compensation details
- **jobPostingUrn**: Job posting URN in format `urn:li:fsd_jobPosting:JOB_ID`
- **includeSecondaryActionsV2**: Set to "true" for additional action data

### Example Request
```
GET /voyager/api/graphql?includeWebMetadata=true&variables=(cardSectionTypes:List(JOB_DESCRIPTION_CARD,SALARY_CARD),jobPostingUrn:urn%3Ali%3Afsd_jobPosting%3A4209649973,includeSecondaryActionsV2:true)&queryId=voyagerJobsDashJobPostingDetailSections.3b2647d9e7ecb085c570a16f9e70d1cc
```

## Response Structure

### Data Selector
The response data is located at: `data.jobsDashJobPostingDetailSectionsByCardSectionTypes.elements.[*].jobPostingDetailSection.[*].jobDescription`

### Key Data Fields

#### Job Description Information
- **descriptionText**: Full job description text
  - **text**: The actual job description content
- **jobPosting**: Job posting details
  - **description**: Job description object
    - **text**: Job description text content
  - **entityUrn**: Job posting entity URN

#### Job Card Types
The endpoint can retrieve different types of job information:
- **JOB_DESCRIPTION_CARD**: Complete job description and requirements
- **SALARY_CARD**: Salary range and compensation information
- **JOB_SEGMENT_ATTRIBUTES_CARD**: Job attributes and characteristics
- **JOB_APPLICANT_INSIGHTS**: Applicant insights and statistics
- **BANNER_CARD**: Job banner and visual elements
- **COMPANY_CARD**: Company information within job context
- **BENEFITS_CARD**: Benefits and perks information
- **COMPANY_INSIGHTS_CARD**: Company insights and data
- **HOW_YOU_MATCH_CARD**: Job matching criteria
- **TOP_CARD**: Top-level job information
- **HOW_YOU_FIT_CARD**: Job fit assessment

### Example Response Structure
```json
{
  "data": {
    "jobsDashJobPostingDetailSectionsByCardSectionTypes": {
      "elements": [
        {
          "jobPostingDetailSection": [
            {
              "jobDescription": {
                "descriptionText": {
                  "text": "We are looking for a Senior Software Engineer to join our team..."
                },
                "jobPosting": {
                  "description": {
                    "text": "We are looking for a Senior Software Engineer to join our team..."
                  },
                  "entityUrn": "urn:li:fsd_jobPosting:4209649973"
                }
              }
            }
          ]
        }
      ]
    }
  }
}
```

## Data Mapping

### Extracted Fields
- **descriptionText**: Full job description text from `descriptionText.text`
- **description**: Job description from `jobPosting.description.text`
- **job_posting_urn**: Job posting entity URN from `jobPosting.entityUrn`

### Job Card Type Configuration
The endpoint is configured to retrieve specific job card types:
- **JOB_DESCRIPTION_CARD**: Primary job description content
- **SALARY_CARD**: Salary and compensation information

Additional card types can be enabled by modifying the `job_card_types` configuration:
```python
job_card_types = [
    "JOB_DESCRIPTION_CARD",
    "SALARY_CARD",
    # Additional types can be added here
]
```

## Dependencies

This endpoint depends on:
- **jobs_by_company**: Uses job URNs from the jobs by company results
- **company_jobs**: Alternative source for job URNs

## Use Cases

### Primary Use Cases
1. **Job Analysis**: Analyze detailed job descriptions and requirements
2. **Salary Research**: Access salary information and compensation details
3. **Job Matching**: Compare job requirements with candidate qualifications
4. **Market Research**: Study job descriptions for market trends

### Detailed Job Information
- **Full Job Descriptions**: Complete job posting content
- **Requirements Analysis**: Job requirements and qualifications
- **Salary Information**: Compensation ranges and benefits
- **Company Context**: Company information within job context

## Job Card Types

### Available Card Types
- **JOB_DESCRIPTION_CARD**: Core job description and requirements
- **SALARY_CARD**: Salary ranges and compensation information
- **BENEFITS_CARD**: Employee benefits and perks
- **COMPANY_CARD**: Company information and context
- **HOW_YOU_MATCH_CARD**: Job matching criteria and requirements
- **HOW_YOU_FIT_CARD**: Job fit assessment and compatibility

### Card Type Selection
The endpoint allows flexible selection of job card types:
- Configure `job_card_types` list to include desired card types
- Each card type provides different information about the job
- Can be customized based on specific data needs

## Pagination

### Pagination Strategy
- No pagination required (single job per request)
- Processes individual job postings by URN
- Efficient for detailed job information retrieval

### Batch Processing
- Can process multiple job URNs sequentially
- Optimal for retrieving detailed information for job lists
- Supports bulk job description retrieval

## Error Handling

### Common Issues
- **Invalid Job URN**: Malformed or non-existent job URNs
- **Private Job Postings**: Limited access to private job postings
- **Rate Limiting**: Subject to LinkedIn's API rate limits
- **Missing Card Types**: Some card types may not be available for all jobs

### Response Validation
- Validates job posting URNs before processing
- Handles missing job descriptions gracefully
- Ensures data integrity for critical fields

## Performance Considerations

### Response Size
- Moderate response size (typically 5-20KB per job)
- Depends on job description length and card types requested
- Efficient for detailed job information retrieval

### Caching
- Job descriptions change infrequently
- Suitable for medium-term caching
- Consider cache invalidation on job updates

## Security and Privacy

### Data Sensitivity
- Contains detailed job posting information
- May include salary and compensation data
- Subject to LinkedIn's API access controls

### Access Control
- Requires proper authentication
- Respects LinkedIn's job data access policies
- May have usage limitations based on account type

## Integration with Other Endpoints

### Upstream Dependencies
- **jobs_by_company**: Primary source for job URNs
- **company_jobs**: Alternative source for job URNs

### Data Flow
1. Get job URNs from `jobs_by_company` or `company_jobs`
2. Use job URNs to retrieve detailed job information
3. Process job descriptions and salary information
4. Extract relevant job details for analysis

### Job URN Encoding
- Job URNs are URL-encoded for use in API requests
- Format: `urn%3Ali%3Afsd_jobPosting%3AJOB_ID`
- Encoding handled automatically by the pipeline

## Special Considerations

### Secondary Actions
- **includeSecondaryActionsV2**: Set to "true" for additional action data
- Provides additional job-related actions and options
- May include application links and job interactions

### Job Description Processing
- Job descriptions may contain HTML formatting
- Text extraction handles formatting appropriately
- Preserves important job information while cleaning formatting

### Salary Information
- Salary data may be limited for some job postings
- Compensation information varies by job and company
- Some salary data may be premium/restricted content
