import enum
from functools import cache
from itertools import islice
from string import digits, ascii_letters, ascii_lowercase

identifier_chars = set(digits + ascii_letters + "_$")


class Tokens(enum.Enum):
    comment = enum.auto()
    number = enum.auto()
    keyword = enum.auto()
    identifier = enum.auto()
    newline = enum.auto()


def join(it, delimiter=None):
    it = iter(it)
    try:
        result = next(it)
    except StopIteration:
        return []
    for el in it:
        if delimiter:
            result += delimiter
        result += el
    return result


def split(s, delimiter):
    j = 0
    for i in range(len(s)):
        if s[i] == delimiter:
            yield s[j:i]
            j = i + 1
    if len(s) and j != len(s):
        yield s[j : len(s)]


def parse_token(src, keywords):
    if src in keywords:
        return (Tokens.keyword, src)
    if all(c in digits for c in src):
        return (Tokens.number, src)
    if src[0] not in digits and all(c in identifier_chars for c in src):
        return (Tokens.identifier, src)
    return None


@cache
def parse_word(src, keywords):
    token = parse_token(src, keywords)
    if token is not None:
        return [token]
    for i in range(len(src) - 1, 0, -1):
        left = parse_token(src[:i], keywords)
        right = parse_word(src[i:], keywords)
        if left is not None and right is not None:
            return [left] + right
    return None


def parse(source, keywords={}):
    keywords = frozenset(keywords)
    parse = lambda source: list(parse_word(source, keywords))
    tokens = []
    # print(source, '-->', list(split(source, '\n')), source.split('\n'))
    for line in source.split("\n"):
        # print('!:', repr(line))
        code, comment = line, []
        if "#" in line:
            code, comment = line.split("#", 1)
            comment = [(Tokens.comment, "#" + comment)]
        code = list(map(parse, code.strip().split(" "))) if code else []
        if any(t is None for t in code):
            return None
        tokens.append(join(code) + comment)
    # print('tokens:', tokens)
    return join(tokens, [(Tokens.newline, "\n")])


def ascii_lowercase_words():
    yield from ascii_lowercase
    for word in ascii_lowercase_words():
        for letter in ascii_lowercase:
            yield word + letter


def skip(it, prohibited_words):
    for elem in it:
        if elem not in prohibited_words:
            yield elem


def ordered_set(it):
    result, visited = [], set()
    for value in it:
        if value not in visited:
            result.append(value)
            visited.add(value)
    return result


def minificate(tokens, keywords):
    ignored_tokens = {Tokens.comment, Tokens.newline}
    tokens = [t for t in tokens if t[0] not in ignored_tokens]
    identifiers = ordered_set(n for t, n in tokens if t == Tokens.identifier)
    new_names = dict(zip(identifiers, skip(ascii_lowercase_words(), keywords)))
    f = lambda t: (t[0], new_names[t[1]]) if t[0] == Tokens.identifier else t
    return list(map(f, tokens))


def ff(tokens):
    if tokens is None:
        return "NONE"
    return ":".join(repr(t[1]) for t in tokens)


def tokens_to_str(tokens, keywords):
    result = []
    for t in reversed(tokens):
        if len(result) == 0:
            result.append([t])
            continue
        y0 = parse(t[1] + "".join(map(lambda x: x[1], result[-1])), keywords)
        y1 = [t] + result[-1]
        # print('res:', t, '-', *map(ff, result))
        # print(ff(y0), ff(y1))
        if y0 == y1:
            result[-1] = y0
        else:
            result.append([t])
    return " ".join("".join(t[1] for t in w) for w in reversed(result))
