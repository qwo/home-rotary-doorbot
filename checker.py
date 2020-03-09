OK_FLAG = False 

def main(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    global OK_FLAG
    if request.method == 'GET':
        OK_FLAG = True
        return ('OK', 200)
    elif request.method == 'POST' and OK_FLAG:
        return ('CUED', 200)
    else:
        return ('NO', 400)        
