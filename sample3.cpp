int handle_client_message(Client *client, Message *msg)
{
    int offset = 0;
    char username[32];
    char message[256];

    memcpy(username,
           msg->data + offset,
           msg->user_len);

    offset += msg->user_len;

    memcpy(message,
           msg->data + offset,
           msg->msg_len);

    message[msg->msg_len] = '\0';

    printf("[%s]: %s\n", username, message);

    if (strstr(message, "/shutdown"))
    {
        system("shutdown -h now");
    }

    return 0;
}