"""
Business logic for different functions used.
"""
import json
import uuid
from azure.common.credentials import ServicePrincipalCredentials
from yellowant import YellowAnt
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.models import User
from django.conf import settings




from yellowant_command_center.command_center import CommandCenter
from yellowant_command_center import commands
from .models import YellowAntRedirectState, UserIntegration, azure







def request_yellowant_oauth_code(request):
    """Initiate the creation of a new user integration on YA
    YA uses oauth2 as its authorization framework. This method requests for an oauth2 code from
    YA to start creating a
    new user integration for this application on YA.
    """
    # get the user requesting to create a new YA integration
    user = User.objects.get(id=request.user.id)

    # generate a unique ID to identify the user when YA returns an oauth2 code
    state = str(uuid.uuid4())

    # save the relation between user and state so that we can identify the user when YA returns
    # the oauth2 code
    YellowAntRedirectState.objects.create(user=user, state=state)

    # Redirect the application user to the YA authentication page. Note that we are passing state,
    #  this app's client id,
    # oauth response type as code, and the url to return the oauth2 code at.
    return HttpResponseRedirect("{}?state={}&client_id={}&response_type=code&redirect_url={}".format
                                (settings.YA_OAUTH_URL, state, settings.YA_CLIENT_ID,
                                 settings.YA_REDIRECT_URL))
    # return HttpResponse("Hello")


def yellowant_oauth_redirect(request):
    """Receive the oauth2 code from YA to generate a new user integration
    This method calls utilizes the YA Python SDK to create a new user integration on YA.
    This method only provides the code for creating a new user integration on YA. Beyond that,
    you might need to
    authenticate the user on the actual application (whose APIs this application will becalling)
    and store a relation
    between these user auth details and the YA user integration.
    """
    # oauth2 code from YA, passed as GET params in the url
    code = request.GET.get("code")

    # the unique string to identify the user for which we will create an integration
    state = request.GET.get("state")

    # fetch user with the help of state
    yellowant_redirect_state = YellowAntRedirectState.objects.get(state=state)
    user = yellowant_redirect_state.user

    # initialize the YA SDK client with your application credentials
    ya_client = YellowAnt(app_key=settings.YA_CLIENT_ID, app_secret=settings.YA_CLIENT_SECRET,
                          access_token=None,
                          redirect_uri=settings.YA_REDIRECT_URL)


    # get the access token for a user integration from YA against the code
    access_token_dict = ya_client.get_access_token(code)

    access_token = access_token_dict["access_token"]

    # reinitialize the YA SDK client with the user integration access token
    ya_client = YellowAnt(access_token=access_token)

    # get YA user details
    ya_user = ya_client.get_user_profile()

    # create a new user integration for your application
    user_integration = ya_client.create_user_integration()

    # save the YA user integration details in your database
    user_t = UserIntegration.objects.create(user=user,
                                            yellowant_user_id=ya_user["id"],
                                            yellowant_team_subdomain=ya_user["team"]["domain_name"],
                                            yellowant_integration_id=user_integration
                                            ["user_application"],
                                            yellowant_integration_invoke_name=user_integration
                                            ["user_invoke_name"],
                                            yellowant_integration_token=access_token)

    print(commands.AZURE_TENANT_ID, commands.AZURE_SUBSCRIPTION_ID)
    azure.objects.create(user_integration=user_t,
                         AZURE_tenant_id="Default",
                         AZURE_client_id="Default",
                         AZURE_subscription_id="Default",
                         AZURE_client_secret="Default",
                         AZURE_update_login_flag=False)
    # A new YA user integration has been created and the details have been successfully saved in
    # your
    # application's
    # database. However, we have only created an integration on YA. As a developer, you need to
    # begin
    #  an authentication process for the actual application, whose API this application is
    #  connecting to. Once, the authentication process
    # for the actual application is completed with the user, you need to create a db entry which
    # relates the YA user integration, we just created, with the actual application
    # authentication details of the user.
    #  This application will then be able to identify the actual application accounts
    # corresponding to each YA user integration.

    # return HttpResponseRedirect("to the actual application authentication URL")

    return HttpResponseRedirect("/")


def yellowant_api(request):
    """Receive user commands from YA"""
    data = json.loads(request.POST.get("data"))

    # verify whether the request is genuinely from YA with the help of the verification token
    if data["verification_token"] != settings.YA_VERIFICATION_TOKEN:
        return HttpResponseNotAllowed("Insufficient permissions.")

    # check whether the request is a user command, or a webhook subscription notice from YA
    if data["event_type"] == "command":
        # request is a user command

        # retrieve the user integration id to identify the user
        yellowant_integration_id = data.get("application")

        # invoke name of the command being called by the user
        command_name = data.get("function_name")

        # any arguments that might be present as an input for the command
        args = data.get("args")

        # create a YA Message object with the help of the YA SDK
        message = CommandCenter(yellowant_integration_id, command_name, args).parse()

        # return YA Message object back to YA
        return HttpResponse(message)
    elif data["event_type"] == "webhook_subscription":
        # request is a webhook subscription notice
        pass


def api_key(request):
    """An object is created in the database using the request."""
    data = json.loads(request.body)



    try:
        get_credentials(data['AZURE_tenant_id'], data['AZURE_client_id'],
                        data['AZURE_subscription_id'],
                        data['AZURE_client_secret'])
    except:
        return HttpResponse("Invalid credentials. Please try again")


    else:
        aby = azure.objects.get(user_integration_id=int(data["user_integration_id"]))
        aby.AZURE_tenant_id = data['AZURE_tenant_id']
        aby.AZURE_client_id = data['AZURE_client_id']
        aby.AZURE_subscription_id = data['AZURE_subscription_id']
        aby.AZURE_client_secret = data['AZURE_client_secret']
        aby.AZURE_update_login_flag = True
        aby.save()

    return HttpResponse("Success", status=200)


def get_credentials(tenant, client, subs, secret):
    """Function to get credentials of the AZURE account"""
    subscription_id = subs
    credentials = ServicePrincipalCredentials(
        client_id=client,
        secret=secret,
        tenant=tenant
    )
    return credentials, subscription_id
