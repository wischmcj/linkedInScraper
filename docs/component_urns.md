## Understanding `components

LinkedIn's internal APIs often use saved queries that are capable of returning data for specific page element categories. Paged_list_components, for example, contains a list of items with some set of common traits; Companies - each with a name and location, jobs- each with a company and title, etc. The idea is that the data returned will vary, but will always match a the format for that given component. Often both the data needed and the content of that data can be described using a component type and a handful of input variables.Here, we show an example of how these are constructed.

## Paged_list_component

This is a request for data returned within a `paged_list_component`. This format makes it easy for LinkedIn's frontend to generate HTML to display the data on page. In this case the data is used to populate the "Followed Companies" list within the "Interests" section of a user's profile.

### Structure of (this particular) `paged_list_component`

```
paged_list_component =
    "urn:li:fsd_profilePagedListComponent:(ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY,INTERESTS_VIEW_DETAILS,urn:li:fsd_profileTabSection:COMPANIES_INTERESTS,NONE,en_US)"
```

The `paged_list_component` variable is a string that encodes several pieces of information, separated by commas and wrapped in a specific URN format. Inputs are:

* The urn of the profile for which the component is requested
* The profile card the content is for
* The tab within the card data is needed for
* Additional styling on the card (not used here)
* Language of the data returned


### Components of the followed companies profile component
component_type = "urn:li:fsd_profilePagedListComponent"
profile_urn = "ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY"
card_type = "INTERESTS_VIEW_DETAILS"
card_tab_urn = "urn:li:fsd_profileTabSection:COMPANIES_INTERESTS"
styling = "NONE"  # styling?
language = "en_US"

followed_companies_profile_component = f"{component_type}:({profile_urn},{card_type},{card_tab_urn},{styling},{language})"
