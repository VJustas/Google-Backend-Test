"""Hello World API implemented using Google Cloud Endpoints.

Defined here are the ProtoRPC messages needed to define Schemas for methods
as well as those methods defined in an API.
"""
#An Endpoints API is an RPC service that provides remote methods accessible to external clients.

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

WEB_CLIENT_ID = 'replace this with your web client application ID'
ANDROID_CLIENT_ID = 'replace this with your Android client ID'
IOS_CLIENT_ID = 'replace this with your iOS client ID'
ANDROID_AUDIENCE = WEB_CLIENT_ID

package = 'Hello'


class Greeting(messages.Message):
    """Greeting that stores a message."""
    message = messages.StringField(1)


class GreetingCollection(messages.Message):
    """Collection of Greetings."""
    items = messages.MessageField(Greeting, 1, repeated=True)


STORED_GREETINGS = GreetingCollection(items=[
    Greeting(message='hello world!'),
    Greeting(message='goodbye world!'),
])

#for GET requests
@endpoints.api(name='helloworld', version='v1', #The name and version of the API
               allowed_client_ids=[WEB_CLIENT_ID, ANDROID_CLIENT_ID,
                                   IOS_CLIENT_ID, endpoints.API_EXPLORER_CLIENT_ID], #kaip suprantu endpoints.API_EXPLORER_CLIENT_ID reikalingas, kad veiktu API exploreryje 
               audiences=[ANDROID_AUDIENCE],
               scopes=[endpoints.EMAIL_SCOPE])
class HelloWorldApi(remote.Service):
    """helloworld API v1.""" 
    """
    The greetings.multiply method supporting POST uses a ResourceContainer instead 
    of a simple message class type, because the method must 
    support requests containing an argument in the URL path.
    """
    MULTIPLY_METHOD_RESOURCE = endpoints.ResourceContainer(
        Greeting,
        times=messages.IntegerField(2, variant=messages.Variant.INT32,
                                    required=True))

    @endpoints.method(MULTIPLY_METHOD_RESOURCE, Greeting,
                  path='hellogreeting/{times}', http_method='POST',
                  name='greetings.multiply')
    def greetings_multiply(self, request):
        return Greeting(message=request.message * request.times)

    @endpoints.method(message_types.VoidMessage, GreetingCollection,
                      path='hellogreeting', http_method='GET',
                      name='greetings.listGreeting')
    def greetings_list(self, unused_request):
        return STORED_GREETINGS



    ID_RESOURCE = endpoints.ResourceContainer( #ResourceContainer is used because method supports a request containing an argument in query string
            message_types.VoidMessage,
            id=messages.IntegerField(1, variant=messages.Variant.INT32))

    @endpoints.method(ID_RESOURCE, Greeting,
                      path='hellogreeting/{id}', http_method='GET',
                      name='greetings.getGreeting')
    def greeting_get(self, request):
        try:
            return STORED_GREETINGS.items[request.id]
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Greeting %s not found.' %
                                              (request.id,))

        @endpoints.method(message_types.VoidMessage, Greeting,
                  path='hellogreeting/authed', http_method='POST',
                  name='greetings.authed')
        def greeting_authed(self, request):
            current_user = endpoints.get_current_user()
            email = (current_user.email() if current_user is not None
                     else 'Anonymous')
            return Greeting(message='hello %s' % (email,))

APPLICATION = endpoints.api_server([HelloWorldApi])