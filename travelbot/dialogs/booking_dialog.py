# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog

from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
from datetime import datetime

class BookingDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(BookingDialog, self).__init__(dialog_id or BookingDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(DateResolverDialog(DateResolverDialog.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.destination_step,
                    self.origin_step,
                    self.from_date_step,
                    self.to_date_step,
                    self.budget_step,
                    self.confirm_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__
        self.logger = None
        self.stats = stats_module.stats
        self.view_manager = self.stats.view_manager
        self.stats_recorder = self.stats.stats_recorder
        self.bot_measure = measure_module.MeasureInt("botdefects",
                                           "number of bot defects",
                                           "botdefects")
        self.bot_view = view_module.View("defect view",
                                    "number of bot defects",
                                    [],
                                    self.bot_measure,
                                    aggregation_module.CountAggregation())
        self.view_manager.register_view(self.bot_view)
        self.mmap = self.stats_recorder.new_measurement_map()
        self.tmap = tag_map_module.TagMap()
        self.metrics_exporter = None
        self.message_history = set()

    def set_logger(self, logger):
        self.logger = logger

    def set_metrics_exporter(self, metrics_exporter):
        self.metrics_exporter = metrics_exporter
        self.view_manager.register_exporter(metrics_exporter)

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a destination city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        self.message_history.add(step_context._turn_context.activity.text)
        print("from :",booking_details.origin)
        print("to :",booking_details.destination)
        print("from date  :",booking_details.from_date)
        print("to date  :",booking_details.to_date)
        print("budget :",booking_details.budget)

        if booking_details.destination is None:
            message_text = "Where would you like to travel to?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If an origin city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        print("User message : ",step_context._turn_context.activity.text)
        self.message_history.add(step_context._turn_context.activity.text)

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        if booking_details.origin is None:
            message_text = "From what city will you be travelling?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.origin)

   
    async def from_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a from date has not been provided, prompt for one.
        This will use the DATE_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        self.message_history.add(step_context._turn_context.activity.text)
        # Capture the results of the previous step
        booking_details.origin = step_context.result
        if not booking_details.from_date or self.is_ambiguous(
            booking_details.from_date
        ):
            return await step_context.begin_dialog(
                DateResolverDialog.__name__, {"field":booking_details.from_date,"booking_details":booking_details}
            )
        return await step_context.next(booking_details.from_date)

    async def to_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a to date has not been provided, prompt for one.
        This will use the DATE_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        self.message_history.add(step_context._turn_context.activity.text)

        # Capture the results of the previous step
        booking_details.from_date = step_context.result
        if not booking_details.to_date or self.is_ambiguous(
            booking_details.to_date
        ):
            return await step_context.begin_dialog(
                DateResolverDialog.__name__, {"field":booking_details.to_date,"booking_details":booking_details}
            )
        return await step_context.next(booking_details.to_date)

    async def budget_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a budget has not been provided, prompt for one.
        """
        booking_details = step_context.options
        booking_details.to_date = step_context.result
        self.message_history.add(step_context._turn_context.activity.text)

        if booking_details.budget is None:
            message_text = "What's your budget?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.budget)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        Confirm the information the user has provided.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        self.message_history.add(step_context._turn_context.activity.text)

        # Capture the results of the previous step
        booking_details.budget = step_context.result
        message_text = (
            f"Please confirm, I have you traveling from: { booking_details.origin } to: "
            f"{ booking_details.destination }  "
            f"(start: {booking_details.from_date} end: {booking_details.to_date}) "
            f"for a budget : {booking_details.budget}"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """
        if step_context.result:
            booking_details = step_context.options
            return await step_context.end_dialog(booking_details)

        properties = {'custom_dimensions': {'booking_details': step_context.options.get_details(),'message_history':str(self.message_history)}}

        self.logger.warning("User has not confirmed flight",extra=properties)
        self.mmap.measure_int_put(self.bot_measure, 1)
        self.mmap.record(self.tmap)
        metrics = list(self.mmap.measure_to_view_map.get_metrics(datetime.utcnow()))
        print(metrics[0].time_series[0].points[0])

        get_sorry_text = "Sorry about that !"
        get_sorry_message = MessageFactory.text(
            get_sorry_text, get_sorry_text, InputHints.ignoring_input
        )
        await step_context.context.send_activity(get_sorry_message)

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
