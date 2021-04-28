cards = [
    {
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {
            "type": "TextBlock",
            "text": "Cum ati nota prima parte a evenimentului?",
            "wrap": True,
            "separator": True,
            "fontType": "Default",
            "size": "Medium",
            "weight": "Bolder",
            "isSubtle": True,
            "horizontalAlignment": "Center",
            "spacing": "Medium"
        },
        {
            "type": "Input.ChoiceSet",
            "id": "Keynote_One",
            "quantity": "5",
            "title": "Please rate your experience",
            "choices": [
                {
                    "title": "⭐⭐⭐⭐⭐",
                    "value": "5"
                },
                {
                    "title": "⭐⭐⭐⭐",
                    "value": "4"
                },
                {
                    "title": "⭐⭐⭐",
                    "value": "3"
                },
                {
                    "title": "⭐⭐",
                    "value": "2"
                },
                {
                    "title": "⭐",
                    "value": "1"
                }
            ]
        }
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Submit"
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
}
]