from bs4 import BeautifulSoup, NavigableString
import re
import collections
import itertools

import statistics
import sys

import termcolor

VPNS = ("Nord\s*VPN" , "Surfshark" , "Private\s+Internet\s+Access|PIA" , "Proton(\s*VPN)?" , "CyberGhost" , "Tunnel\s*Bear" , "Express\s*VPN" , "IVPN" , "Mullvad" , "Mozilla\s*VPN" , "IPVanish" , "Hotspot Shield" , "Norton(\s+Secure)?" , "Pure\s*VPN" , "Strong\s*VPN" , "Hide\.Me" , "HMA|Hide\s*My\s*Ass" , "Vypr\s*VPN" , "Bitdefender" , "Ivacy" , "AVG( Secure)?" , "Personal\s*VPN" , "VPN Unlimited" , "FastestVPN" , "OVPN" , "Windscribe" , "Private\s*VPN" , "Speedify" , "VPNCity" ,
        "Clear\s*VPN" , "Malwarebytes" , "TorGuard" , "VeePN" , "Ace\s*VPN" , "SurfEasy" , "ESET Security Premium" , "ib\s*VPN" , "Cactus\s*VPN" , "Safer\s*VPN" , "Tiger\s*VPN" , "VPN Shield" , "Astrill" , "SpyOff" , "Boleh" , "Hideman" , "Freedome" , "Le VPN" , "Zoog" , "Slick" , "Perfect Privacy" , "Zen\s*mate" , "VPN\s*Area" , "VPN\.ac" , "Trust\.Zone" , "Atlas\s*VPN" , "UTunnel" , "VPN4All" , "iPro\s*VPN" , "RUSVPN" , "Ultra\s*VPN" , "Proxy\.sh" , "Earth\s*VPN" , "HideIPVPN" , "VPN\.ht"
        , "Goose\s*VPN" , "VPN\s*Secure" , "Ghost\s*Path" , "Switch\s*VPN" , "Namecheap" , "KeepSolid" , "iTop" , "Acti" , "Air\s*VPN" , "Anonymous\s*VPN" , "Anonine\s*VPN" , "Avira" , "Azire" , "Anonymizer\s*VPN" , "VPN\s*Secure" , "Gom\s*VPN" , "BG\s*VPN" , "APlus" , "Ananoos" , "55\s*VPN" , "Bee\s*VPN" , "Better\s*VPN")

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
        if match := vpn_re.search(tag.get_text()):
            matches.append(vpn_name)
    # if len(matches) > 1:
        # breakpoint()
    return matches


def extract(fname):
    with open(fname) as f:
        soup = BeautifulSoup(f, "lxml")

    tags = soup.body.find_all(VALID_TAGS)
    found_tags = []
    so_far = set()
    for tag in tags:
        if matches := get_matches(tag):
            if len(matches) != 1:
                breakpoint()
                raise ValueError("matches > 1")
            if matches[0] not in so_far:
                found_tags.append(tag)
            so_far.add(matches[0])

    if not found_tags:
        return {}

    most_common_name = statistics.mode(result.name for result in found_tags)
    term_tags = VALID_TAGS[:VALID_TAGS.index(most_common_name)+1]
    terminator = found_tags[-1].findNext(term_tags)
    # results.append(terminator)


    results = {}
    for cur, next in pairwise(found_tags, fillvalue=terminator):
        results[cur] = " ".join(text_between(cur, next))

    return results



def main():
    for file in sys.argv[1:]:
        termcolor.cprint(f"{'-'*20}{file}{'-'*20}", "blue")
        results = extract(file)

        if not results:
            termcolor.cprint("NO RESULTS", "red")

        for tag, text in results.items():
            termcolor.cprint(tag.get_text().strip(), "green")
            termcolor.cprint(text, "yellow")

if __name__ == "__main__":
    main()
