Role: You are a developer of a workflow system.

Task: Convert the following Standard Operating Procedure (SOP) into a structured workflow JSON format.

Core Constraints (Non-Negotiable):
- Return a valid JSON string only
- Output raw text only, no markdown.
- Use the exact schema: id, steps
- Each step must have: id, type, name, next (optional)
- Step IDs must be unique and use alphanumeric characters with hyphens

JSON schema
- give the workflow a meaningful id based on the SOP
- id is mandatory
- a "step" field contains a list of step
- each step has mandatory id
- each step has a fixed attribute: "type": "action"
- given each step a reasonable long name
- if the step has next steps, populate field "next" with the id of the next step

Example of JSON string with correct schema:
{
"id": "customer-support-workflow",
"steps": [
    {
        "id": "receive-request",
        "type": "action",
        "name": "Receive customer support request",
        "next": "categorize-issue"
    },
    {
        "id": "categorize-issue",
        "type": "action",
        "name": "Assign to appropriate team"
    }
  ]
}
end of the example

The SOP is as Following:

