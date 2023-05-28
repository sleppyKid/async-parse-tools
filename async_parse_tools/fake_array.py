from collections.abc import Iterable


class FakeArray:
    """Object, to use single object as repeating iterator"""

    def __init__(self, value: object | list | tuple):
        self.many = isinstance(value, Iterable)
        self.value = value

    def __getitem__(self, item):
        if self.many:
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


class StringArray(FakeArray):
    def __init__(self, value: str | list | tuple, folder_strip=False):
        self.many = isinstance(value, str)
        self.folder_strip = folder_strip
        if self.many:
            self.value = tuple(self.strip_value(x) if x else x for x in value)
        else:
            self.value = self.strip_value(value)
        print(self.value)

    def strip_value(self, item):
        if self.folder_strip:
            return str(item).strip().rstrip('.\/')
        return str(item).strip()

    def __getitem__(self, item):
        if self.many:
            return str(self.value[item])
        return self.value