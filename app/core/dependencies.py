from ..services.twilio_service import TwilioService

# from ..services.time_globe_service import TimeGlobeService


def get_twilio_service() -> TwilioService:
    return TwilioService()


# def get_time_globe_service() -> TimeGlobeService:
#     return TimeGlobeService()
