
# LinkedIn Messaging API Documentation

This document describes the LinkedIn messaging API endpoints and their usage patterns based on analysis of browser network calls.

## Overview

LinkedIn's messaging system uses multiple API endpoints to handle different aspects of messaging functionality:
- **voyagerMessagingGraphQL**: GraphQL-based messaging queries
- **voyagerMessagingDashMessengerMessageDeliveryAcknowledgements**: Message delivery acknowledgments
- **voyagerMessagingDashMessagingBadge**: Message badge management
- **voyagerMessagingDashRecipientSuggestions**: Recipient suggestions
- **voyagerMessagingDashAffiliatedMailboxes**: Mailbox management

## Core Messaging Endpoints

### 1. Message Delivery Acknowledgments

**Endpoint**: `POST /voyager/api/voyagerMessagingDashMessengerMessageDeliveryAcknowledgements`

**Purpose**: Sends delivery acknowledgments for specific messages


**Omitted due to lack of relevancy**

### 2. Seen Receipts Query

**Endpoint**: `GET /voyager/api/voyagerMessagingGraphQL/graphql`

**Purpose**: Retrieves seen receipts for a conversation

**Query ID**: `messengerSeenReceipts.dc29d9bcecad524b9dd264acbbde3b5c`

**Variables**:
```
conversationUrn: urn:li:msg_conversation:(urn:li:fsd_profile:ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY,2-ZWRiMzc5NjYtZDkzNC00OWFkLTg4N2QtYzAxYzQ4NDkxYzI5XzEwMA==)
```

**Response**:
```json
{
  "data": {
    "_recipeType": "com.linkedin.33851ce67c1a444c09e057014b5c4d81",
    "_type": "com.linkedin.33851ce67c1a444c09e057014b5c4d81",
    "messengerSeenReceiptsByConversation": {
      "_type": "com.linkedin.restli.common.CollectionResponse",
      "_recipeType": "com.linkedin.610dc666c5c0bd249902fc4a6e29137d",
      "elements": []*
    }
  }
}
```

**Response Overview**: `messengerSeenReceiptsByConversation` field provides a collection of seen receipts, where each element would contain details about which messages have been seen by participants. In this example, the `elements` array is empty, indicating no seen receipts are currently available for this conversation. The response includes LinkedIn's internal type information (`_recipeType`, `_type`) for data structure validation.

### 3. Quick Replies Query

**Endpoint**: `GET /voyager/api/voyagerMessagingGraphQL/graphql`

**Purpose**: Retrieves quick replies for a conversation

**Query ID**: `messengerQuickReplies.4338d226319203b5b08920ab7621fa45`

**Variables**:
```
conversationUrn: urn:li:msg_conversation:(urn:li:fsd_profile:ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY,2-ZWRiMzc5NjYtZDkzNC00OWFkLTg4N2QtYzAxYzQ4NDkxYzI5XzEwMA==)
```

**Response**:
```json
{
  "data": {
    "_recipeType": "com.linkedin.4c7816368899aefc0404a81a21b89aad",
    "_type": "com.linkedin.4c7816368899aefc0404a81a21b89aad",
    "messengerQuickRepliesByConversation": {
      "_type": "com.linkedin.restli.common.CollectionResponse",
      "_recipeType": "com.linkedin.b6e858f35d83d6cf5dfa51c1f4e9cf33",
      "elements": []
    }
  }
}
```

**Response Overview**: This response provides quick reply suggestions for a conversation. The `messengerQuickRepliesByConversation` field contains a collection of suggested quick replies that users can select from when responding to messages. In this example, the `elements` array is empty, indicating no quick replies are currently available for this conversation. When populated, each element would contain pre-defined response options that LinkedIn's AI suggests based on the conversation context.

### 4. Message Badge Management

**Endpoint**: `POST /voyager/api/voyagerMessagingDashMessagingBadge`

**Purpose**: Marks all messages as seen

**Parameters**:
- `action=markAllMessagesAsSeen`

**Response Overview**: This endpoint typically returns a `204 No Content` response, indicating that all messages have been successfully marked as seen. The response confirms that the user's message badge has been updated to reflect that all messages in their inbox have been read, which would clear any unread message indicators in the UI.

### 5. Recipient Suggestions

**Endpoint**: `GET /voyager/api/graphql`

**Purpose**: Retrieves recipient suggestions for messaging

**Query ID**: `voyagerMessagingDashRecipientSuggestions.0623e89a6faf64755e04151fc3d5dced`

**Variables**:
```
count: 20,
start: 0,
companyUrn: urn:li:fsd_company:9414302
```

**Response Overview**: This response contains recipient suggestions for messaging within a company context. The response includes a collection of suggested recipients (`messagingDashRecipientSuggestionsByCompany`) with elements that would contain profile information such as names, profile pictures, and URNs of potential message recipients. The suggestions are typically based on company connections, recent interactions, or LinkedIn's recommendation algorithms. The response also includes extensive metadata about profile types, entity URNs, and LinkedIn's internal data structures.

### 6. Affiliated Mailboxes

**Endpoint**: `GET /voyager/api/graphql`

**Purpose**: Retrieves affiliated mailboxes for messaging

**Query ID**: `voyagerMessagingDashAffiliatedMailboxes.da7e8047e61ae87c4b97ee31fed7d934`

**Response Overview**: This response provides information about affiliated mailboxes for messaging. The `messagingDashAffiliatedMailboxesAll` field contains a collection of mailbox types including page mailboxes, recruiter mailboxes, and sales mailboxes. Each mailbox element includes unread message counts (`aggregatedUnreadCount`) and mailbox-specific information. In the example response, only page mailboxes are present with an unread count of 0, while recruiter and sales mailboxes are null, indicating the user doesn't have access to those mailbox types.

## API Flow for Message Retrieval

Based on the observed network calls, here's the typical flow for retrieving message information:

### Step 1: Get Conversation URN
The system first needs to identify the conversation using a conversation URN in the format:
```
urn:li:msg_conversation:(urn:li:fsd_profile:PROFILE_ID,CONVERSATION_ID)
```

### Step 2: Retrieve Message URNs
The system retrieves individual message URNs in the format:
```
urn:li:msg_message:(urn:li:fsd_profile:PROFILE_ID,MESSAGE_ID)
```

### Step 3: Query Message Details
Using the conversation URN, the system makes GraphQL queries to retrieve:
- **Seen Receipts**: Track which messages have been seen
- **Quick Replies**: Get suggested quick reply options
- **Message Content**: Actual message data (not visible in this HAR file)

### Step 4: Send Delivery Acknowledgments
For each message URN, the system sends delivery acknowledgments to confirm message receipt.

### Step 5: Update Message Badges
The system updates message badges to reflect read status.

## URN Structure

### Conversation URN
```
urn:li:msg_conversation:(urn:li:fsd_profile:PROFILE_ID,CONVERSATION_ID)
```

### Message URN
```
urn:li:msg_message:(urn:li:fsd_profile:PROFILE_ID,MESSAGE_ID)
```

### Profile URN
```
urn:li:fsd_profile:PROFILE_ID
```

## Headers and Authentication

All messaging API calls include:
- **X-LI-Track**: Client tracking information
- **User-Agent**: Browser identification
- **Authorization**: Session-based authentication
- **Content-Type**: `application/graphql` for GraphQL queries, `text/plain;charset=UTF-8` for acknowledgments

## Rate Limiting and Caching

- Responses include `cf-cache-status` headers indicating caching behavior
- Some endpoints return `204 No Content` for successful operations
- GraphQL responses include metadata about schema versions and types

## Error Handling

- Successful operations return appropriate HTTP status codes
- GraphQL responses include error information in the `errors` field if present
- Failed requests may include retry mechanisms based on response headers
`