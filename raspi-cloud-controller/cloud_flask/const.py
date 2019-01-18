AMAZON_TOKEN_REQUEST = 'https://api.amazon.com/auth/o2/token'
AMAZON_PROFILE_REQUEST = 'https://api.amazon.com/user/profile'

ALL_ENDPOINTS = [  # TODO HARDCODED
    {
        "endpointId": "tv-01",
        "friendlyName": "Philips TV",
        "description": "Philips 6008 TV controlled by RasPi",
        "manufacturerName": "Philips by RasPi",
        "displayCategories": [
            "TV"
        ],
        'capabilities': {
            'Alexa.PowerController': ['powerState'],
            'Alexa.InputController': ['HDMI 1', 'HDMI 2', 'HDMI 3', 'XBOX'],
            'Alexa.PlaybackController': ["Play", "Pause", "Stop"],
            'Alexa.Speaker': ['volume', 'muted'],
            'Alexa.EndpointHealth': ['connectivity'],
        }
    }
    # ,
    # {
    #     "endpointId": "tree-01",
    #     "friendlyName": "Tree11",
    #     "description": "Christmas Tree controlled by RasPi",
    #     "manufacturerName": "NoName",
    #     "displayCategories": [
    #         "OTHER"
    #     ],
    #     'capabilities': {
    #         'Alexa.ModeController': [1, 2, 3, 4, 5, 6, 7, 8]
    #     }
    # }
]