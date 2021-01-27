from travelbot.dialogs import BookingDialog

class TestBookingDialog():

    def test_set_logger(self):
        bd = BookingDialog()
        bd.set_logger("a")

        assert bd.logger == "a"