def active_section(request):
    path = request.path
    if '/listings/cards' in path:
        section = 'cards'
    elif '/listings/' in path:
        section = 'listings'
    elif '/accounts/' in path:
        section = 'dashboard'
    else:
        section = ''
    return {'active_section': section}
