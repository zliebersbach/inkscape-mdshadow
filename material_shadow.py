#!/usr/bin/env python
#-*- coding: utf-8 -*-
# inkscape-material-shadow, an Inkscape extension for creating Material Design shadows.
# Copyright (C) 2017  Kevin Boxhoorn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import copy
import inkex
import os
import random
import sys
from lxml import etree

inkex.localize()

def xpath(e, path):
    return e.xpath(path, namespaces=inkex.NSS)

class MaterialShadow(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("-e", "--elevation", action="store", type="int", dest="elevation", default=1, help="Elevation of the shadow.")

    def effect(self):
        # Parse filters.svg.
        filter_path = os.path.join(os.environ["HOME"], ".config", "inkscape", "extensions", "filters.svg")
        try:
            stream = open(filter_path, "r")
        except Exception:
            inkex.errormsg(_("Unable to open specified file: %s") % filter_path)
            sys.exit()
        p = etree.XMLParser(huge_tree=True)
        filter_doc = etree.parse(stream, parser=p)
        stream.close()

        # Get elevation value.
        elevation = self.options.elevation

        filter_ids = self.ensure_filters(filter_doc)
        if len(self.selected) == 0:
            pass
        else:
            for i, element in self.selected.iteritems():
                self.add_shadow(element, filter_ids)

    def get_label(self, element):
        xpath_result = xpath(element, "@inkscape:label")
        assert len(xpath_result)
        return xpath_result[0]

    def ensure_new_id(self, element, exclude_ids):
        orig_id = element.get("id")
        while element.get("id") in exclude_ids:
            element.set("id", "%s_%d" % (orig_id, random.randint(1000, 9999)))

    def ensure_filters(self, filter_doc):
        root = self.document.getroot()

        # Create defs if non existent.
        if len(xpath(root, "//svg:svg/svg:defs")) == 0:
            root.insert(0, etree.Element("defs"))
        root_defs = xpath(root, "//svg:svg/svg:defs")
        assert len(root_defs)

        # Add filters.
        filter_ids = []
        filter_defs = xpath(filter_doc.getroot(), "//svg:svg/svg:defs/svg:filter")
        root_filter_defs = xpath(root, "//svg:svg/svg:defs/svg:filter")
        for filter_e in filter_defs:
            root_filter_ids = []
            filter_e_label = self.get_label(filter_e)
            filter_found = False
            for e in root_filter_defs:
                root_filter_ids.append(e.get("id"))
                e_label = self.get_label(e)
                if filter_e_label == e_label:
                    filter_ids.append(e.get("id"))
                    filter_found = True
                    break

            if not filter_found:
                self.ensure_new_id(filter_e, root_filter_ids)
                root_defs[0].append(filter_e)
                filter_ids.append(filter_e.get("id"))

        return filter_ids

    def add_shadow(self, element, filter_ids):
        parent = element.getparent()
        parent.remove(element)
        group = etree.Element("g")
        group_loop = group

        for i in filter_ids:
            group_current = etree.Element("g")
            group_current.set("style", "filter:url(#%s)" % i)
            group_loop.append(group_current)
            group_loop = group_current

        group_loop.append(element)
        parent.append(group)

if __name__ == "__main__":
    ex = MaterialShadow()
    ex.affect()
