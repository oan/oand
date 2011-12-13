from twisted.protocols import amp

class notify(amp.Command):
    arguments = []
    response = [('value', amp.String())]

class send(amp.Command):
    arguments = [("data", amp.String())]
    response = [('value', amp.String())]
