import collections
import itertools
from pathlib import Path
import re
import statistics
import sys

from bs4 import BeautifulSoup, NavigableString
import termcolor


with open(f"vpns.txt") as f:
    VPNS = f.read().splitlines()


VPN_RES = tuple(re.compile(f"(?<!\w)({vpn})(?!\w)", flags=re.IGNORECASE) for vpn in VPNS)
VALID_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]


def pairwise(iterable, fillvalue=None):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.zip_longest(a,b, fillvalue=fillvalue)

# def lowest_common_ancestor(n1, n2):
    # ancestors1 = [n1] + list(n1.parents)
    # check1 = [an.name for an in ancestors1]
    # ancestors2 = [n2] + list(n2.parents)
    # check2 = [an.name for an in ancestors2]
    # for an in ancestors2:
        # if an in ancestors1:
            # print(an == n1)
            # # breakpoint()
            # return an



def text_between(cur, end):
    while cur and cur != end:
        if isinstance(cur, NavigableString) and (text := cur.text.strip()):
            yield text
        cur = cur.next_element


# def filter_by_most_common(xs, key=lambda x: x):
    # elem = statistics.mode(key(x) for x in xs)
    # return [x for x in xs if key(x) == elem], elem


def get_matches(tag):
    matches = []
    for vpn_name, vpn_re in zip(VPNS, VPN_RES):
        if match_ := vpn_re.search(tag.get_text()):
            matches.append(vpn_name)
    # if len(matches) > 1:
        # breakpoint()
    return matches


def prettify(match_):
    return re.sub("\\\\", "", re.sub("[\(\)?]", "", re.sub("\|.*","", re.sub("\\\\s[*+]", " ", match_)))).lower()

Result = collections.namedtuple("Result", ["tag", "match_"])

def extract(fname):
    with open(fname) as f:
        soup = BeautifulSoup(f, "lxml")

    tags = soup.body.find_all(VALID_TAGS)
    found = []
    so_far = set()
    for tag in tags:
        matches = get_matches(tag)
        if not matches:
            continue
        if len(matches) > 1:
            breakpoint()
        assert len(matches) == 1, "matches > 1!!!!"
        if matches[0] not in so_far:
            found.append(Result(tag=tag, match_=matches[0]))
        so_far.add(matches[0])

    if not found:
        return {}

    most_common_name = statistics.mode(result.tag.name for result in found)
    term_tags = VALID_TAGS[:VALID_TAGS.index(most_common_name)+1]
    terminator = Result(tag=found[-1].tag.findNext(term_tags), match_=None)
    # results.append(terminator)


    return {cur.match_ : " ".join(text_between(cur.tag, next.tag))
                for cur, next in pairwise(found, fillvalue=terminator)}



def main():
    all_results = {}
    for file in sys.argv[1:]:
        dir = Path(Path(file).stem)
        dir.mkdir(exist_ok=True)
        termcolor.cprint(f"{'-'*20}{file}{'-'*20}", "blue")
        results = extract(file)

        if not results:
            termcolor.cprint("NO RESULTS", "red")

        all_results[file] = results
        for match_, text in results.items():
            with open(dir / prettify(match_), "w") as f:
                f.write(text)
            termcolor.cprint(prettify(match_), "green")
            termcolor.cprint(text, "yellow")


if __name__ == "__main__":
    main()
