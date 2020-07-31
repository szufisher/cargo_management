import datetime

import easypost
import frappe
import pytz


class EasypostAPIError(easypost.Error):
    """
    Child Class to personalize API Error
    https://www.easypost.com/errors-guide/python
    """
    pass


class EasypostAPI(object):
    """ Easypost methods to control class API and parse data. """

    easypost.api_key = frappe.get_single('Parcel Settings').easypost_api_key

    @staticmethod
    def create_package(tracking_number, carrier):
        """
        Create a Tracking Resource on Easypost API

        @param tracking_number: String Tracking Number
        @param carrier: String Code of Carrier
        @return: EasyPostObject
        """

        # TODO: Try to find a carrier before creating the tracker
        return easypost.Tracker.create(
            tracking_code=tracking_number,
            carrier=carrier
        )

    @staticmethod
    def get_package_data(easypost_id):

        return easypost.Tracker.retrieve(
            easypost_id=easypost_id
        )

    @staticmethod
    def naive_dt_to_local_dt(dt_str, uses_utc):
        """
        Convert naive datetime to local datetime if using UTC. else just return the naive because is already local date
        @param dt_str: EasyPost datetime format: 2020-06-015T06:00:00Z
        @param uses_utc: Boolean if time is UTC
        @return: datetime

        Some carriers already return datetime without UTC, its localized:
        https://www.easypost.com/does-your-api-return-time-according-to-the-package-destinations-time-zone
        https://www.easypost.com/why-are-there-time-zone-discrepancies-on-trackers
        """
        if not dt_str:  # Sometimes datetime string if empty for some values, so return None value.
            return

        # Parse datetime from string. At this moment we do not know if it is in UTC or local.
        naive_datetime = datetime.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%SZ')

        if not uses_utc:  # API already give us local datetime. So no need to convert to local from UTC
            return naive_datetime

        # TODO: Make this conversion warehouse location aware!. For now we're pretending only Miami is local timezone
        local_tz = pytz.timezone('America/New_York')  # https://stackoverflow.com/a/32313111/3172310

        # Use local timezone to convert UTC naive datetime to local datetime+timezone. Then return naive local datetime.
        return local_tz.fromutc(naive_datetime).replace(tzinfo=None)

    @staticmethod
    def convert_weight_to_lb(weight=0):
        """ In easypost weight comes in ounces. """
        return weight/16 if weight else None


@frappe.whitelist(allow_guest=True)
def easypost_webhook(**kwargs):
    """
    =/api/method/parcel_management.parcel_management.doctype.parcel.easypost_api.easypost_webhook
    """
    parcel_data = kwargs['result']

    # TODO: Finish!
    frappe.db.set_value('Parcel', parcel_data['tracking_number'], {
        'status': parcel_data['status'],
        'status_detail': parcel_data['status_detail'],
    })

    return True
