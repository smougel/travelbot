# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    def __init__(
        self,
        destination: str = None,
        origin: str = None,
        travel_date: str = None,
        unsupported_airports=None,
        from_date: str=None,
        to_date: str=None,
        budget: str=None
    ):
        if unsupported_airports is None:
            unsupported_airports = []
        self.destination = destination
        self.origin = origin
        self.travel_date = travel_date
        self.from_date = from_date
        self.to_date = to_date
        self.budget = budget
        self.unsupported_airports = unsupported_airports
