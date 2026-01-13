def get_response_or_raise(result, index:int = 1) -> dict:
    if 'messages' in result:
        messages = result['messages']
        if len(messages) > index:
            ai_message = messages[index]
            return {
                "messages": [ai_message.text]
            }

    raise ValueError("invalid response")
