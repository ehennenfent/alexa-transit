from api_calls import GetStopDepartures, GetNamedStopDepartures

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.cc6864c6-9f37-45c1-8722-de3959f08362"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetNamedStopDepartures":
        return handle_named_departure(intent, session)
    elif intent_name == "GetStopDepartures":
        return handle_stop_departures(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome to Transit"
    speech_output = "Welcome to Transit for CUMTD!"
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session))


def handle_named_departure(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = True

    try:
        data = GetNamedStopDepartures(int(intent['slots']['Route']['value']), intent['slots']['Stop']['value'])
        speech_output = "The {bus} is expected at {stop} in {time} minutes".format(bus=data[0]['headsign'], stop=intent['slots']['Stop']['value'], time=data[0]['expected_mins'])
    except:
        speech_output = "I couldn't find any buses scheduled for this stop."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def handle_stop_departures(intent, session):
    session_attributes = {}
    should_end_session = True

    try:
        data = GetStopDepartures(intent['slots']['Stop']['value'])
        if(len(data) > 1):
            speech_output = "At {stop}, ".format(stop=intent['slots']['Stop']['value']) + "".join("the {bus} is expected in {time} minutes, ".format(bus=departure['headsign'], time=departure['expected_mins']) for departure in data)
        else:
            speech_output = "The {bus} is expected at {stop} in {time} minutes".format(bus=data[0]['headsign'], stop=intent['slots']['Stop']['value'], time=data[0]['expected_mins'])
    except:
        speech_output = "I couldn't find any buses scheduled for this stop."

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, None, should_end_session))

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
