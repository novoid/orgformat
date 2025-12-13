#!/usr/bin/env python3
# Find much more example calls in the unit test file orgformat_test.py
# -*- coding: utf-8; mode: python; -*-

import time
import datetime
import calendar
import logging
import re
from typing import List, Union, Tuple, Optional  # mypy: type checks


class TimestampParseException(Exception):
    """
    Own exception should be raised when
    strptime fails
    """

    def __init__(self, value: Union[ValueError, str]) -> None:
        self.value = value

    def __str__(self) -> str:
        return repr(self.value)


class OrgFormat(object):
    """
    Utility library for providing functions to generate and modify Org
    mode syntax elements like links, time-stamps, or date-stamps.
    """

    # FIXXME: this regular expression contains only English and German weekday names so far.
    # If this gets an issue, replace weekdays with 2-3 arbitrary characters or similar.
    SINGLE_ORGMODE_TIMESTAMP = r"([<\[]" + \
        r"([12]\d\d\d)-([012345]\d)-([012345]\d)" + \
        r"( (Mon|Tue|Wed|Thu|Fri|Sat|Sun|Mo|Di|Mi|Do|Fr|Sa|So|Mon|Die|Mit|Don|Fre|Sam|Son))?" + \
        r"( (([01]\d)|(20|21|22|23)):([012345]\d))?" + \
        r"[>\]])"
    TIMESTAMP_MATCH_GROUPS = 12

    ORGMODE_TIMESTAMP_REGEX = re.compile(SINGLE_ORGMODE_TIMESTAMP + "$")

    ORGMODE_TIMESTAMP_RANGE_REGEX = re.compile(
        SINGLE_ORGMODE_TIMESTAMP + "-(-)?" + SINGLE_ORGMODE_TIMESTAMP + "$")

    ISODATETIME_REGEX = re.compile(r'([12]\d\d\d-[012345]\d?-([012345]\d?))' +
                                   r'([T ]((\d\d?[:.][012345]\d?)([:.][012345]\d?)?))?')

    @staticmethod
    def orgmode_timestamp_to_datetime(orgtime: str) -> datetime.datetime:
        """
        Returns a datetime object containing the time-stamp of an Org mode time-stamp:

        OrgFormat.orgmode_timestamp_to_datetime('<1980-12-31 Wed 23:59>')
        -> datetime.datetime(1980, 12, 31, 23, 59, 0, tzinfo=None)

        FIXXME: this function should be modified so that '<1980-12-31 23:59>'
        with a missing day of week is accepted as well.

        @param orgtime: '<YYYY-MM-DD Sun HH:MM>' or an inactive one
        @param return: date time object
        """

        assert isinstance(orgtime, str)

        components = re.match(OrgFormat.ORGMODE_TIMESTAMP_REGEX, orgtime)
        if not components:
            raise TimestampParseException("string could not be parsed as " +
                                          "time-stamp of format \"<YYYY-MM-DD Sun " +
                                          "HH:MM>\" (including inactive ones): \"" +
                                          orgtime + "\"")

        year = int(components.group(2))    # type: ignore  # FIXXME why
        month = int(components.group(3))   # type: ignore  # FIXXME why
        day = int(components.group(4))     # type: ignore  # FIXXME why
        hour = int(components.group(8) or "0")    # type: ignore  # FIXXME why
        minute = int(components.group(11) or "0") # type: ignore  # FIXXME why

        return datetime.datetime(year, month, day, hour, minute, 0)

    @staticmethod
    def apply_timedelta_to_org_timestamp(orgtime: str, deltahours: Union[int, float]) -> str:
        """
        Returns a string containing an Org mode time-stamp
        with the given delta hours added.
        Also works for a time-stamp range which uses two strings <YYYY-MM-DD Sun HH:MM>
        concatenated with one or two dashes.

        OrgFormat.apply_timedelta_to_org_timestamp('<2019-11-05 Tue 23:59>', 1)
        -> '<2019-11-06 Wed 00:59>'

        OrgFormat.apply_timedelta_to_org_timestamp('<2020-01-01 Wed 01:30>--<2020-01-01 Wed 02:00>', -2.5)
        -> '<2019-12-31 Tue 23:00>--<2019-12-31 Tue 23:30>'

        FIXXME: implement support for inactive date/time ranges

        @param orgtime: '<YYYY-MM-DD Sun HH:MM>'
        @param deltahours: integer/float like, e.g., 3 or -2.5 (in hours)
        @param return: '<YYYY-MM-DD Sun HH:MM>'
        """

        assert isinstance(deltahours, (int, float))
        assert isinstance(orgtime, str)

        range_components = re.match(
            OrgFormat.ORGMODE_TIMESTAMP_RANGE_REGEX, orgtime)

        if range_components:
            return OrgFormat.date(
                OrgFormat.orgmode_timestamp_to_datetime(  # type: ignore  # FIXXME why? Argument 1 to "datetime" of "OrgFormat" has incompatible type "datetime"; expected "struct_time"
                    range_components.groups(0)[0]) +  # type: ignore  # FIXXME why
                datetime.timedelta(0, 0, 0, 0, 0, deltahours), show_time=True, inactive=False) + \
                "--" + \
                OrgFormat.date(
                    OrgFormat.orgmode_timestamp_to_datetime(  # type: ignore  # FIXXME why? Argument 1 to "datetime" of "OrgFormat" has incompatible type "datetime"; expected "struct_time"
                        range_components.groups(0)[OrgFormat.TIMESTAMP_MATCH_GROUPS]) +  # type: ignore  # FIXXME why
                    datetime.timedelta(0, 0, 0, 0, 0, deltahours), show_time=True, inactive=False)
        else:
            return OrgFormat.date(OrgFormat.orgmode_timestamp_to_datetime(orgtime) +  # type: ignore  # FIXXME why? Argument 1 to "datetime" of "OrgFormat" has incompatible type "datetime"; expected "struct_time"
                                  datetime.timedelta(0, 0, 0, 0, 0, deltahours),
                                  show_time=True, inactive=False)

    @staticmethod
    def struct_time_to_datetime(tuple_date: time.struct_time) -> datetime.datetime:
        """
        Converts a time.struct_time argument to a datetime.datetime object

        OrgFormat.struct_time_to_datetime(time.struct_time((2019, 12, 31, 23, 59, 0, 0, 0, 0)))
        -> datetime.datetime(2019, 12, 31, 23, 59, 0, tzinfo=None)

        @param struct_time with potential wrong day of week
        """

        assert isinstance(tuple_date, time.struct_time)
        return datetime.datetime(tuple_date.tm_year,
                                 tuple_date.tm_mon,
                                 tuple_date.tm_mday,
                                 tuple_date.tm_hour,
                                 tuple_date.tm_min,
                                 tuple_date.tm_sec)

    @staticmethod
    def datetime_to_struct_time(tuple_date: datetime.datetime) -> time.struct_time:
        """
        Converts a datetime.datetime argument to a time.struct_time object

        OrgFormat.datetime_to_struct_time(datetime.datetime(2019, 12, 31, 23, 59, 0, tzinfo=None))
        -> time.strptime("31 Dec 2019 23:59:00", "%d %b %Y %H:%M:%S"))

        returns time.struct_time which was generated from the datetime.datetime parameter
        @param datetime object
        """

        assert isinstance(tuple_date, datetime.datetime)
        return tuple_date.timetuple()

    @staticmethod
    def fix_struct_time_wday(tuple_date: time.struct_time) -> time.struct_time:
        """
        Correcting the given time.struct_time with the correct day of the week.

        OrgFormat.fix_struct_time_wday(time.struct_time([2013, 4, 3, 10, 54, 0, 0, 0, 0]))
        -> time.struct_time([2013, 4, 3, 10, 54, 0, 2, 0, 0])   # Notice the different tm_wday.

        returns struct_time timestamp with correct day of week
        @param struct_time with potential false day of week
        """

        assert isinstance(tuple_date, time.struct_time)
        datetimestamp = OrgFormat.struct_time_to_datetime(tuple_date)
        return time.struct_time((datetimestamp.year,
                                 datetimestamp.month,
                                 datetimestamp.day,
                                 datetimestamp.hour,
                                 datetimestamp.minute,
                                 datetimestamp.second,
                                 datetimestamp.weekday(),
                                 0, 0))

    @staticmethod
    def date(tuple_date: Union[time.struct_time, datetime.datetime],
             show_time: Optional[bool] = False,
             inactive: Optional[bool] = False,
             repeater_or_delay: Optional[str] = None) -> str:
        """
        Converts a given time.struct_time or datetime.datetime to an Org date- or time-stamp.

        OrgFormat.date(time.strptime("2011-11-02T20:38:42", "%Y-%m-%dT%H:%M:%S"))
        -> "<2011-11-02 Wed>"

        OrgFormat.date(time.strptime("2011-11-02T20:38:42", "%Y-%m-%dT%H:%M:%S"), show_time=True)
        -> "<2011-11-02 Wed 20:38>"

        @param tuple_date: has to be of type time.struct_time or datetime.datetime
        @param show_time: optional show time
        @param inactive: (boolean) True: use inactive time-stamp; else use active
        @param repeater_or_delay: string holding a repeater or a delay; e.g., '+2w' or '--5d'
        """
        # <YYYY-MM-DD hh:mm>
        assert (tuple_date.__class__ ==
                time.struct_time or tuple_date.__class__ == datetime.datetime)

        local_structtime = None  # : time.struct_time   # Variable annotation syntax is only supported in Python 3.6 and greater

        if isinstance(tuple_date, time.struct_time):
            # fix day of week in struct_time
            local_structtime = OrgFormat.fix_struct_time_wday(tuple_date)
        else:
            # convert datetime to struc_time
            local_structtime = OrgFormat.datetime_to_struct_time(tuple_date)

        result = ''
        if show_time:
            result = time.strftime("%Y-%m-%d %a %H:%M", local_structtime)
        else:
            result = time.strftime("%Y-%m-%d %a", local_structtime)
            
        if repeater_or_delay:
            result += ' ' + repeater_or_delay.strip()
            
        if inactive:
            return '[' + result + ']'
        else:
            return '<' + result + '>'

    @staticmethod
    def daterange(begin: time.struct_time, end: time.struct_time, show_time: bool = False, inactive: bool = False) -> str:
        """
        Converts two given time.struct_time or datetime.datetime to an Org range of date- or time-stamps.

        OrgFormat.daterange(
                time.strptime("2011-11-29", "%Y-%m-%d"),
                time.strptime("2011-11-30", "%Y-%m-%d"))
        -> "<2011-11-29 Tue>--<2011-11-30 Wed>")

        OrgFormat.daterange(
                time.strptime("2011-11-29T20:38:42", "%Y-%m-%dT%H:%M:%S"),
                time.strptime("2011-11-30T23:59:58", "%Y-%m-%dT%H:%M:%S"), show_time=True, inactive=True)
        -> "[2011-11-29 Tue 00:00]--[2011-11-30 Wed 00:00]"

        @param begin, end: have to be time.struct_time
        @param show_time: optional show time
        @param inactive: (boolean) True: use inactive time-stamps; else return active time-stamps
        """
        assert isinstance(begin, time.struct_time)
        assert isinstance(end, time.struct_time)
        return "%s--%s" % (OrgFormat.date(begin, show_time=show_time, inactive=inactive),
                           OrgFormat.date(end, show_time=show_time, inactive=inactive))

    @staticmethod
    def daterange_autodetect_time(begin_tuple: time.struct_time, end_tuple: time.struct_time, inactive: bool = False) -> str:
        """
        Converts two given time.struct_time or datetime.datetime to an Org range of date- or time-stamps.

        If both time parameters do not contain time information,
        result is a range of dates, else it results in time-ranges.

        OrgFormat.daterange_autodetect_time(
                time.strptime("2011-11-29", "%Y-%m-%d"),
                time.strptime("2011-11-30T23:59", "%Y-%m-%dT%H:%M"), inactive=True)
        -> "[2011-11-29 Tue 00:00]--[2011-11-30 Wed 23:59]"

        OrgFormat.daterange_autodetect_time(
                time.strptime("2011-11-29", "%Y-%m-%d"),
                time.strptime("2011-11-30", "%Y-%m-%d"), inactive=True)
        -> "[2011-11-29 Tue]--[2011-11-30 Wed]"

        @param begin,end: has to be a a time.struct_time
        @param inactive: (boolean) True: use inactive time-stamps; else return active time-stamps
        """

        if begin_tuple.tm_sec == 0 and \
                begin_tuple.tm_min == 0 and \
                begin_tuple.tm_hour == 0 and \
                end_tuple.tm_sec == 0 and \
                end_tuple.tm_min == 0 and \
                end_tuple.tm_hour == 0:

            return OrgFormat.daterange(begin_tuple, end_tuple,
                                       show_time=False, inactive=inactive)
        else:
            return OrgFormat.daterange(begin_tuple, end_tuple,
                                       show_time=True, inactive=inactive)

    @staticmethod
    def strdate(date_string: str,
                show_time: Optional[bool] = False,
                inactive: Optional[bool] = False,
                repeater_or_delay: Optional[str] = None) -> str:
        """
        Converts a ISO 8601 like time- or date-stamp into a time- or date-stamp in org format.

        OrgFormat.strdate('2011-11-3')
        -> '<2011-11-03 Thu>'

        OrgFormat.strdate('2011-11-03 23:59', inactive=True, show_time=True)
        -> '[2011-11-03 Thu 23:59]'

        @param date-string: has to be a str of the required format: '%Y-%M-%D (%H:%M(:%S))'
        @param show_time: optional show time
        @param inactive: (boolean) True: use inactive time-stamp; else use active
        @param repeater_or_delay: string holding a repeater or a delay; e.g., '+2w' or '--5d'
        """
        assert isinstance(date_string, str)
        components = re.match(OrgFormat.ISODATETIME_REGEX, date_string)
        if components:
            if components.group(1) and components.group(5):
                # found %Y-%m-%d %H:%M  ; don't care about the seconds
                try:
                    tuple_date = time.strptime(components.group(1) + 'T' +
                                               components.group(5).replace(':', '.'),
                                               "%Y-%m-%dT%H.%M")
                    return OrgFormat.date(tuple_date, show_time=show_time, inactive=inactive, repeater_or_delay=repeater_or_delay)
                except ValueError:
                    raise TimestampParseException('The provided time-stamp string does not match ' +
                                                  'the required format for %Y-%M-%D %H.%M(.%S) or ' +
                                                  'is an invalid date/time.')
            elif components.group(1):
                # found %Y-%m-%d
                tuple_date = time.strptime(components.group(1),
                                           "%Y-%m-%d")
                return OrgFormat.date(tuple_date, show_time=show_time, inactive=inactive, repeater_or_delay=repeater_or_delay)
        else:
            raise TimestampParseException('The provided date string does not match ' +
                                          'the required format for %Y-%M-%D (%H.%M(.%S)): ' +
                                          str(date_string))
        assert False  # to satisfy mypy 0.740: "Missing return statement"

    @staticmethod
    def parse_extended_iso_datetime(datetime_string: str) -> time.struct_time:
        """
        Parses any string containing date or time and return it as time.struct_time.

        OrgFormat.parse_extended_iso_datetime("2011-1-2")
        -> time.strptime('2011-01-02', '%Y-%m-%d')

        OrgFormat.parse_extended_iso_datetime("2011-1-2T3.4.5")
        -> time.strptime('2011-01-02 03.04.05', '%Y-%m-%d %H.%M.%S')

        OrgFormat.parse_extended_iso_datetime("2011-1-2 3:4")
        -> time.strptime('2011-01-02 03.04', '%Y-%m-%d %H.%M')

        @param datetime_string: YYYY-MM-DD([T ]HH[.:]MM([.:]SS)?)?
        """
        assert isinstance(datetime_string, str)

        components = re.match(OrgFormat.ISODATETIME_REGEX, datetime_string)
        if components:
            if components.group(1) and components.group(5) and components.group(6):
                # found %Y-%m-%d %H:%M:%S
                return time.strptime(components.group(1) + 'T' +
                                     components.group(4).replace(':', '.'),
                                     "%Y-%m-%dT%H.%M.%S")
            if components.group(1) and components.group(5):
                # found %Y-%m-%d %H:%M
                return time.strptime(components.group(1) + 'T' +
                                     components.group(5).replace(':', '.'),
                                     "%Y-%m-%dT%H.%M")
            elif components.group(1):
                # found %Y-%m-%d
                return time.strptime(components.group(1), "%Y-%m-%d")
        else:
            raise TimestampParseException('The provided date string does not match ' +
                                          'the required format for %Y-%M-%D (%H.%M(.%S)): ' +
                                          str(datetime_string))
        assert False  # to satisfy mypy 0.740: "Missing return statement"

    @staticmethod
    def parse_basic_iso_datetime(datetime_string: str) -> time.struct_time:
        """
        Converts an ISO 8601 basic format string with am optional trailing UTC
        zone designator ('Z') into a time.struct_time.

        OrgFormat.date(
                OrgFormat.parse_basic_iso_datetime('20111219T205510Z'), True
            )
        -> '<2011-12-19 Mon 21:55>'  (for TZ == "Europe/Vienna")

        @param datetime_string: YYYYMMDDTHHMMSSZ or
                                YYYYMMDDTHHMMSS or
                                YYYYMMDD
        """
        assert isinstance(datetime_string, str)
        string_length = len(datetime_string)

        # FIXXME: more intense checks on the datetime_string format using regex?

        try:
            if string_length == 16:
                # YYYYMMDDTHHMMSSZ
                return time.localtime(
                    calendar.timegm(
                        time.strptime(datetime_string, "%Y%m%dT%H%M%SZ")))
            elif string_length == 15:
                # YYYYMMDDTHHMMSS
                return time.strptime(datetime_string, "%Y%m%dT%H%M%S")
            elif string_length == 8:
                # YYYYMMDD
                return time.strptime(datetime_string, "%Y%m%d")
            elif string_length == 27:
                # 2011-11-02T14:48:54.908371Z
                datetime_string = datetime_string.split(".")[0] + "Z"
                return time.localtime(
                    calendar.timegm(
                        time.strptime(datetime_string,
                                      "%Y-%m-%dT%H:%M:%SZ")))
            else:
                raise TimestampParseException('datetime_string does not match expected format: ' +
                                              datetime_string)
        except ValueError as e:
            raise TimestampParseException(e)

        assert(False)  # dead code for assuring mypy that everything above is handled by a return or raising exception statement

    @staticmethod
    def link(link: str, description: Optional[str] = None, replacespaces: Optional[bool] = True) -> str:
        """
        returns link-string as an Org mode link

        FIXXME: rename to a better function name

        OrgFormat.link('file:foo/bar/some file.pdf'),
        -> '[[file:foo/bar/some%20file.pdf]]'

        OrgFormat.link('file:foo/bar/some file.pdf', 'my description')
        -> '[[file:foo/bar/some%20file.pdf][my description]]'

        OrgFormat.link('file:foo/bar/some file.pdf', 'my description', replacespaces=False),
        -> '[[file:foo/bar/some file.pdf][my description]]'

        @param link: link to, i.e., file which should end up such as '[[file:description]]'
        @param description: optional
        @param replacespaces: if True (default), spaces within link are being sanitized
        """

        if replacespaces:
            link = link.replace(" ", "%20")

        if description:
            return "[[" + link + "][" + description + "]]"
        else:
            return "[[" + link + "]]"

    @staticmethod
    def mailto_link(contact_mail_string: str) -> str:
        """
        Takes an email address within optional angle brackets and
        optional name and generates an Org mode mailto email link.

        - "Bob Bobby <bob.bobby@example.com>" or
        - <Bob@example.com>" or
        - Bob@example.com

        OrgFormat.mailto_link('Bob Bobby <bob.bobby@example.com>'
        -> '[[mailto:bob.bobby@example.com][Bob Bobby]]'

        OrgFormat.mailto_link('<Bob@example.com>'
        -> '[[mailto:Bob@example.com][Bob@example.com]]'

        Note that there is no check on the validy of the
        email address format.

        @param contact_mailto_string: the email information of a contact
        @return: Org mode mailto email link
        """

        delimiter = contact_mail_string.find("<")
        if delimiter != -1:
            name = contact_mail_string[:delimiter].strip()
            mail = contact_mail_string[delimiter + 1:][:-1].strip()
            if delimiter == 0:
                return OrgFormat.link("mailto:" + mail,
                                      description=mail,
                                      replacespaces=False)
            return OrgFormat.link("mailto:" + mail,
                                  description=name,
                                  replacespaces=False)
        else:
            return OrgFormat.link("mailto:" + contact_mail_string,
                                  description=contact_mail_string,
                                  replacespaces=False)

    @staticmethod
    def newsgroup_link(newsgroup_string: str) -> str:
        """

        OrgFormat.newsgroup_link('foo')
        -> '[[news:foo][foo]]'

        Note that there is no check on the validy or content of the
        input string.

        @param newsgroup_string: Usenet name
            i.e: news:comp.emacs
        @param return: [[news:comp.emacs][comp.emacs]]
        """
        assert newsgroup_string
        return OrgFormat.link("news:" + newsgroup_string,
                              description=newsgroup_string,
                              replacespaces=False)

    @staticmethod
    def hms_from_sec(sec: int) -> str:
        """
        Returns a string of hours:minutes:seconds from the seconds given.

        OrgFormat.hms_from_sec(9999)
        -> '2:46:39'

        @param sec: seconds
        @param return: h:mm:ss as string
        """

        assert isinstance(sec, int)

        seconds = sec % 60
        minutes = (sec // 60) % 60
        hours = (sec // (60 * 60))

        return str(hours) + ":" + str(minutes).zfill(2) + ":" + \
            str(seconds).zfill(2)

    @staticmethod
    def dhms_from_sec(sec: int) -> str:
        """
        Returns a string of days hours:minutes:seconds (like
        "9d 13:59:59") from the seconds given. If days is zero, omit
        the part of the days (like "13:59:59").

        OrgFormat.dhms_from_sec(123)
        -> '0:02:03'

        OrgFormat.dhms_from_sec(99999)
        -> '1d 3:46:39'

        @param sec: seconds
        @param return: xd h:mm:ss as string
        """

        assert isinstance(sec, int)

        seconds = sec % 60
        minutes = (sec // 60) % 60
        hours = (sec // (60 * 60)) % 24
        days = (sec // (60 * 60 * 24))

        if days > 0:
            daystring = str(days) + "d "
        else:
            daystring = ''
        return daystring + str(hours) + ":" + str(minutes).zfill(2) + \
            ":" + str(seconds).zfill(2)

    @staticmethod
    def generate_heading(level: int,
                         keyword: Optional[str] = None,
                         priority: Optional[str] = None,
                         title: Optional[str] = None,
                         tags: Optional[List[str]] = None,
                         scheduled_timestamp: Optional[str] = None,
                         deadline_timestamp: Optional[str] = None,
                         properties: Optional[List[Tuple[str, str]]] = None,
                         section: Optional[str] = None) -> str:
        """
        Returns a (potential multi-line) string with an Org mode heading that is generated
        from the data within the parameters given.

        The only mandatory parameter is the level of the heading since '** ' is a valid heading.

        No content or syntax validation is done here yet (FIXXME).

        Note: There is a Python wrapper script to use this method from command line:
        https://github.com/novoid/appendorgheading

        Parameter names are taken from https://orgmode.org/worg/dev/org-syntax.html if applicable:

        @param level: the level of the heading which is the amount of asterisks used
        @param keyword: is a TODO keyword, which has to belong to the list defined in org-todo-keywords-1. Case is significant.
        @param priority: is a priority cookie, a single letter - which will then preceded by a hash sign # and enclosed within square brackets.
        @param title: can be made of any character but a new line.
        @param tags: a list of valid tags without colons
        @param scheduled_timestamp: a string with a formatted date- or time-stamp
        @param deadline_timestamp: a string with a formatted date- or time-stamp
        @param properties: a list of name/value tuples
        @param section: the body of this heading
        @param return: the generated Org mode heading
        """

        result = '*' * level + ' '
        if keyword:
            result += keyword + ' '
        if priority:
            result += '[#' + priority + '] '
        if title:
            result += title
        if tags:
            result += '  :' + ':'.join(tags) + ':'

        result += '\n'

        if scheduled_timestamp:
            result += 'SCHEDULED: ' + scheduled_timestamp
            if deadline_timestamp:
                result += ' '
        if deadline_timestamp:
            result += 'DEADLINE: ' + deadline_timestamp
        if scheduled_timestamp or deadline_timestamp:
            result += '\n'

        if properties:
            result += ':PROPERTIES:\n'
            for myproperty in properties:
                result += ':' + myproperty[0] + ': ' + myproperty[1] + '\n'
            result += ':END:\n'

        if section:
            result += '\n' + section.rstrip() + '\n'

        return result

# Local Variables:
# End:
