"""
    Now modified to convert a generic csv to the same .xml format
    Author: Henning Surmeier
    License: MIT
    Date: 12.06.2018

    This module converts contacts exported from gmail as .csv to an .xml that
    can be imported as phonebook on a FritzBox 6360 Cable.

    Author: Matthias Manhertz
    License: MIT
    Date: 15.03.2017
"""

from __future__ import unicode_literals

import argparse
import re
from time import time
import math

import pandas as pd

XML_TEMPLATE = '''<?xml version="1.0" encoding="utf-8"?>
<phonebooks>
    <phonebook>
        {contacts}
    </phonebook>
</phonebooks>
'''

CONTACT_TEMPLATE = '''
<contact>
    <category>0</category>
    <person>
        <realName>{name}</realName>
    </person>
    {telephony}
    <services />
    <setup />
    <features doorphone="0" />
    <mod_time>{mod_time}</mod_time>
    <uniqueid>{unique_id}</uniqueid>
</contact>
'''

TELEPHONY_TEMPLATE = '''
<telephony nid="{num_count}">
    {numbers}
</telephony>
'''

NUMBER_TEMPLATE = '''
<number type="{type}" prio="{prio}" id="{id}">{number}</number>
'''

def csv2fritzbox(in_path, out_path):
    df = pd.read_csv(in_path, sep=',',dtype=str)

    xml_contacts = []
    for c in df.itertuples(name=None):
        xml_contacts.append(contact2xml(c))

    xml = XML_TEMPLATE.format(contacts='\n'.join(xml_contacts))

    with open(out_path, 'w') as f:
        f.write(xml)

def contact2xml(entry):
    numbers = []
    id = entry[0]
    name = " ".join([ item for item in entry[1:3] if not type(item) is float ])
    numbers.append(entry[3:6])
    return CONTACT_TEMPLATE.format(
        name=name,
        telephony=numbers2xml(numbers),
        unique_id=id,
        mod_time=int(time()),
    )


def numbers2xml(numbers):
    xml_numbers = []
    number_name = {
        0: "home",
        1: "mobile",
        2: "work"
    }

    index_shift = 0

    for index, number in enumerate(numbers[0]):
        if not math.isnan(float(number)):
            xml_numbers.append(number2xml(number, number_name[index], index - index_shift))
        else:
            index_shift += 1

    print(index_shift)

    return TELEPHONY_TEMPLATE.format(
        num_count=3-index_shift,
        numbers='\n'.join(xml_numbers)
    )


def number2xml(number, ntype, id):
    return NUMBER_TEMPLATE.format(
        type=ntype.lower(),
        number=number,
        id=id,
        prio=1 if id == 0 else 0,
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('inpath', help='Filepath to the input .csv file.')
    parser.add_argument('outpath', help='Filepath to the output .xml file.')

    args = parser.parse_args()

    csv2fritzbox(args.inpath, args.outpath)


