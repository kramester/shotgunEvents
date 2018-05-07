import os
# import shotgun_api3
from slackclient import SlackClient

slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_user_token = os.environ["SLACK_USER_TOKEN"]
sc_bot = SlackClient(slack_bot_token)
sc_user = SlackClient(slack_user_token)


def send_message(channel, message):
    """
    Sends a message as the the bot user.

    :param channel: A slack channel ID or user ID.
    :param message: The slack message.
    """
    slack_message = sc_bot.api_call("chat.postMessage", channel=channel, as_user=True, text=message)
    return slack_message


def create_channel(channel_name):
    """
    Creates a new slack channel and returns the channel ID if successful.

    :param channel_name: the slack channel name.
    """
    new_channel = sc_user.api_call("channels.create", name=channel_name)
    return new_channel


def invite_to_channel(user, channel):
    """
    Invites a user to a channel.

    :param user: A slack user ID.
    :param channel: A slack channel ID.
    """
    invite = sc_user.api_call("channels.invite", user=user, channel=channel)
    return invite


def kick_from_channel(user, channel):
    """
    Removes a user from a channel.

    :param user: A slack user ID.
    :param channel: A slack channel ID.
    """
    kick = sc_user.api_call("channels.kick", name=user, channel=channel)
    return kick


def get_slack_user_id(sg, shotgun_id):
    """
    Looks up the shotgun user in slack by matching email address
    and returns the slack user ID.

    :param sg: A shotgun connection instance.
    :param shotgun_id: The shotgun user ID.
    """

    sg_user = sg.find_one(
        "HumanUser",
        [["id", "is", shotgun_id]],
        ["email", "sg_slack_id"]
    )

    # if users slack ID is in thier shotgun record, just return that
    if sg_user["sg_slack_id"]:
        return sg_user["sg_slack_id"]
    # otherwise, look up the slack user by matching email
    else:
        slack_user = sc_bot.api_call(
            "users.lookupByEmail",
            email=sg_user["email"]
        )

        # if a slack user is found, return the ID and record it
        # in the users shotgun record so we dont query slack next time
        if slack_user["ok"]:
            slack_id = slack_user["user"]["id"]
            sg.update("HumanUser", shotgun_id, {"sg_slack_id": slack_id})
            return slack_id
        else:
            return None