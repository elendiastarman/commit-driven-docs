import sys


class CodeRanges:
  def __init__(self, raw=[]):
    self.ranges = []

    if not raw:
      return

    if isinstance(raw, CodeRanges):
      self.ranges = raw.ranges

    if isinstance(raw, str):
      first_level = list(map(str.strip, raw.split(',')))

      for element in first_level:
        second_level = list(map(lambda x: int(str.strip(x)), element.split('-')))

        self.ranges.append(second_level * (3 - len(second_level)))

    elif isinstance(raw, int):
      self.ranges = [[raw, raw]]

    elif isinstance(raw, list):
      self.ranges = raw

    self.ranges.sort()

    # simplify to canonical form (e.g. [[2, 4], [4, 6]] => [[2, 6]])
    canonical = [self.ranges[0]]
    for block in self.ranges:
      if block[0] <= canonical[-1][1] + 1:
        canonical[-1][1] = block[1]
      else:
        canonical.append(block)

    self.ranges = canonical

  def __repr__(self):
    return repr(self.ranges)
  __str__ = __repr__

  def __len__(self):
    return len(self.ranges)

  def __getitem__(self, index):
    return self.ranges[index]

  def __add__(self, other):  # union
    if not isinstance(other, CodeRanges):
      other = CodeRanges(other)

    index1 = 1
    index2 = 0

    combined = [self[0]]
    while index1 < len(self) or index2 < len(other):
      if index1 < len(self) and (index2 >= len(other) or self[index1][0] < other[index2][0]):

        if self[index1][0] <= combined[-1][1] + 1:
          combined[-1][1] = self[index1][1]
        else:
          combined.append(self[index1])
        index1 += 1

      else:

        if other[index2][0] <= combined[-1][1] + 1:
          combined[-1][1] = other[index2][1]
        else:
          combined.append(other[index2])
        index2 += 1

    return CodeRanges(combined)

  def __mul__(self, other):  # intersection
    if not isinstance(other, CodeRanges):
      other = CodeRanges(other)

    index1 = 0
    index2 = 0

    combined = []
    while index1 < len(self) and index2 < len(other):
      if other[index2][0] > self[index1][1]:
        index1 += 1

      else:
        combined.append([other[index2][0], min(self[index1][1], other[index2][1])])
        index2 += 1

    return CodeRanges(combined)

  def __sub__(self, other):  # difference
    if not isinstance(other, CodeRanges):
      other = CodeRanges(other)

    pass

  def __eq__(self, other):
    if not isinstance(other, CodeRanges):
      return False
    else:
      return self.ranges == other.ranges


class CodeRangesTest:
  def __init__(self):
    self.tests = []
    for d in dir(self):
      if d.startswith('test_'):
        self.tests.append(d)

  def run_tests(self):
    for test in self.tests:
      self.__getattribute__(test)()

  def assert_equal(self, item1, item2):
    try:
      assert item1 == item2
    except AssertionError:
      print("ERROR: {} is not equal to {}".format(item1, item2))
      raise

  def test_init(self):
    cr = CodeRanges()
    self.assert_equal(cr.ranges, [])

    cr = CodeRanges(50)
    self.assert_equal(cr.ranges, [[50, 50]])

    cr = CodeRanges("50")
    self.assert_equal(cr.ranges, [[50, 50]])

    cr = CodeRanges("50, 50")
    self.assert_equal(cr.ranges, [[50, 50]])

    cr = CodeRanges(" 50 - 50 ")
    self.assert_equal(cr.ranges, [[50, 50]])

    cr = CodeRanges("0, 2-4, 6, 8-11, 10-20")
    self.assert_equal(cr.ranges, [[0, 0], [2, 4], [6, 6], [8, 20]])

    cr = CodeRanges("0, 10-20, 6, 2-4, 8-11, 10-20")  # out of order and with a duplicate
    self.assert_equal(cr.ranges, [[0, 0], [2, 4], [6, 6], [8, 20]])

    cr = CodeRanges("1, 2-4, 5, 6, 7-9, 8-20")
    self.assert_equal(cr.ranges, [[1, 20]])

    cr = CodeRanges("1, 2-4, 5, 6, 7-9, 8-20")
    self.assert_equal(cr, CodeRanges(cr))
    self.assert_equal(cr, CodeRanges(cr.ranges))

  def test_add(self):
    self.assert_equal(CodeRanges("1") + CodeRanges("2"), CodeRanges("1-2"))
    self.assert_equal(CodeRanges("1, 2") + CodeRanges("2, 1"), CodeRanges("1-2"))
    self.assert_equal(CodeRanges("1, 3") + CodeRanges("2"), CodeRanges("1-3"))
    self.assert_equal(CodeRanges("1-3, 6-9") + CodeRanges("2-8"), CodeRanges("1-9"))
    self.assert_equal(CodeRanges("1, 5, 9") + CodeRanges("3, 7"), CodeRanges("1, 3, 5, 7, 9"))

  def test_mul(self):
    self.assert_equal(CodeRanges("1") * CodeRanges("2"), CodeRanges(""))
    self.assert_equal(CodeRanges("1, 2") * CodeRanges("2, 1"), CodeRanges("1-2"))
    self.assert_equal(CodeRanges("1-5") * CodeRanges("3-7"), CodeRanges("3-5"))
    self.assert_equal(CodeRanges("1-9") * CodeRanges("2, 5"), CodeRanges("2, 5"))
    self.assert_equal(CodeRanges("1-9") * CodeRanges("2-3, 5-6, 8-10, 12-15"), CodeRanges("2-3, 5-6, 8-9"))

  def test_sub(self):
    pass


if __name__ == '__main__':
  if len(sys.argv) > 1:
    if sys.argv[1] == 'test':
      CodeRangesTest().run_tests()
