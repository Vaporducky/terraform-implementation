Publishes the required data in a PubSub topic. It assumes that the project ID and the topic ID are stored as environment variables.

This CF contains two functions:

- parse_requests; Expects a JSON payload having the start date and end date for the query
- publish_parameters; Publishes the message to a PubSub topic. Message ordering is enabled as we'd like to get *only* the most recent request
