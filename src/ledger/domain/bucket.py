class AccountingBucket:
    def __init__(self, identifier: str):
        self.identifier = identifier
        self.debit = 0.0
        self.credit = 0.0

    def is_debit_value(self, value: float):
        return value >= 0.0

    def is_credit_value(self, value: float):
        return value <= 0.0

    @property
    def sum(self):
        return self.debit + self.credit

    def add_value(self, value: float):
        if self.is_debit_value(value):
            self.debit += value
        elif self.is_credit_value(value):
            self.credit += value

    @classmethod
    def create(cls, identifier):
        """
        Creates a new accounting bucket with
        given identifier

        Args:
            identifier(str): Identifier for the accounting bucket
        Returns:
            bucket(AccountingBucket): New AccountingBucket with
                the given identifier
        """
        return cls(identifier)