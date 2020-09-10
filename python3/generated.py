class MyFormatter:

    def __init__(self):
        self.tags = SequencePersistence(SequenceConfig().set_name('tags').
            set_start('[').set_finish(']').set_separator(' '))
        self.emails = SequencePersistence(SequenceConfig().set_name(
            'emails').set_start('[').set_finish(']').set_separator(' '))
        self.items = SequencePersistence(SequenceConfig().set_name('items')
            .set_start('[').set_finish(']').set_separator(','))

    def from_int(self, value: int) ->str:
        return str(value)

    def from_float(self, value: float) ->str:
        return str(value)

    def from_url(self, value: str) ->str:
        return value.strip()

    def from_id(self, value: str) ->str:
        return value.strip()

    def from_tag(self, value: str) ->str:
        return value.strip()

    def from_email(self, value: str) ->str:
        return value.strip()

    def from_fraction(self, value: Fraction) ->str:
        return str(value)

    def from_tags(self, values: List[str]) ->str:
        return self.tags.to_csv_string([self.from_tag(value) for value in
            values])

    def from_emails(self, values: List[str]) ->str:
        return self.emails.to_csv_string([self.from_email(value) for value in
            values])

    def from_items(self, values: List[str]) ->str:
        return self.items.to_csv_string(values)
