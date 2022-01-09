
class AccountingBucket:
    def __init__(self, identifier: str):
        self.identifier = identifier
        self.debit = 0.0
        self.credit = 0.0

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