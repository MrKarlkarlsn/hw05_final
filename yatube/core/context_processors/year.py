import datetime as dt


def year(request):
    data = dt.datetime.now()
    day = data.strftime('%d')
    months = data.strftime('%m')
    year = data.strftime('%Y')

    return dict(day=day, months=months, year=year)
