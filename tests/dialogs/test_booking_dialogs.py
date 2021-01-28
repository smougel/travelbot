from travelbot.dialogs import BookingDialog

class TestBookingDialog():

    def test_set_logger(self):
        bd = BookingDialog()
        bd.set_logger("a")

        assert bd.logger == "a"

    def test_is_ambiguous(self):

        bd = bd = BookingDialog()
        ret = bd.is_ambiguous("what")
        
        assert ret

        ret = bd.is_ambiguous("2020-01-01")
        
        assert not ret

    def test_set_metrics_exporter(self):
        
        bd = bd = BookingDialog()
        bd.set_metrics_exporter("something")
        
        assert bd.metrics_exporter == "something"