class Calendar():

    def __init__(self):

        self.year = 1
        self.month = 1
        self.day = 1

    def advance_day(self):
        self.day += 1

        if self.day > 21:
            self.day = 1
            self.month += 1

        if self.month > 12:
            self.month = 1
            self.year += 1

    def __str__(self) -> str:
        return "Y{}M{}D{}".format(self.year,self.month,self.day)