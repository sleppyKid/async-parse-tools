class FakeArray:
    """Object, to use single object as repeating iterator"""

    def __init__(self, value: str | list | tuple, folder_strip=False):
        self.folder_strip = folder_strip
        self.value = value
        if isinstance(value, str):
            self.many = False
            self.value = self.strip_value(value)
        else:
            self.many = True
            self.value = tuple(self.strip_value(x) if x else x for x in value)

    def strip_value(self, item):
        try:
            if self.folder_strip:
                return str(item).strip().rstrip(r'.\/')
            return str(item).strip()
        except:
            return item

    def __getitem__(self, item):
        if self.many:
            try:
                return str(self.value[item])
            except:
                return self.value[item]
        return self.value

    def __iter__(self):
        if self.many:
            return iter(self.value)
        return iter((self.value,))

    def __len__(self):
        if self.many:
            return len(self.value)
        return 1

    def compare_length(self, other: 'FakeArray'):
        """Method to compare with others StringArrays"""
        if self.many and other.many:
            return len(self) == len(other)
        return True
